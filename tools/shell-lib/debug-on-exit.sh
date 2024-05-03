# Grab some info in case of failure, essentially usefull to troubleshoot CI, fell free to add your own commands while troubleshooting

unset KUBECONFIG

# list of kinds to dump
#
# for some resources, we add the apiGroup because there are resources
# with same names in CAPI and Rancher provisioning.cattle.io/management.cattle.io API groups
# we want the CAPI Cluster ones (e.g. Clusters.*cluster.x-k8s.io) rather than
# the Rancher one (e.g Clusters.provisioning.cattle.io)
additional_resources="
  Namespaces
  HelmReleases
  HelmRepositories
  HelmCharts
  GitRepositories
  Kustomizations
  StatefulSets
  Jobs
  CronJobs
  PersistentVolumes
  PersistentVolumeClaims
  ConfigMaps
  Nodes
  Services
  Ingresses
  HeatStacks
  Clusters.*cluster.x-k8s.io
  MachineDeployments
  Machines
  KubeadmControlPlanes
  KubeadmConfigTemplates
  KubeadmConfigs
  RKE2ControlPlanes
  RKE2ConfigTemplates
  RKE2Configs
  DockerClusters
  DockerMachineTemplates
  DockerMachines
  VSphereClusters.*infrastructure.cluster.x-k8s.io
  VSphereMachineTemplates.*infrastructure.cluster.x-k8s.io
  VSphereMachines.*infrastructure.cluster.x-k8s.io
  OpenStackClusters
  OpenStackMachineTemplates
  OpenStackMachines
  Metal3Clusters
  Metal3MachineTemplates
  Metal3Machines
  Metal3DataTemplates
  BaremetalHosts
"

function dump_additional_resources() {
    local cluster_dir=$1
    shift
    for cr in $@; do
      echo "Dumping resources $cr in the whole cluster"
      if kubectl api-resources | grep -qi $cr ; then
        base_filename=$cluster_dir/${cr/.\**/}
        kind=${cr/\*/}  # transform the .* used for matching kubectl api-resource, into a plain '.'
                        # (see Clusters.*cluster.x-k8s.io above)

        if [[ $kind == HelmReleases || $kind == Kustomizations ]]; then
            flux get ${kind,,} -A > $base_filename.summary.txt
        else
            kubectl get $kind -A -o wide > $base_filename.summary.txt
        fi

        kubectl get $kind -A -o yaml --show-managed-fields > $base_filename.yaml
      fi
    done
}


function format_and_sort_events() {
  # this sorts events by lastTimestamp (when defined)
  yq '[.items[] |
       [.firstTimestamp // .eventTime,
        .lastTimestamp // .firstTimestamp // .eventTime,
        .involvedObject.kind,
        .involvedObject.name,
        .count,
        .reason,
        .message // "" | sub("\n","\n        ")]
       ]
      | sort_by(.1)
      | @tsv'
}

function cluster_info_dump() {
  local cluster=$1
  local dump_dir=$cluster-cluster-dump

  echo "Checking if $cluster cluster is reachable"
  if ! timeout 10s kubectl get nodes > /dev/null 2>&1 ;then
    echo "$cluster cluster is unreachable - aborting dump"
    return 0
  fi
  echo "Dumping resources for $cluster cluster in $dump_dir"

  kubectl cluster-info dump -A -o yaml --output-directory=$dump_dir

  # produce a readable ordered log of events for each namespace
  for events_yaml in $(find $dump_dir -name events.yaml); do
    format_and_sort_events < $events_yaml > ${events_yaml//.yaml}.log
  done

  # same in a single file
  kubectl get events -A -o yaml | format_and_sort_events > $dump_dir/events.log

  dump_additional_resources $dump_dir $additional_resources

  # dump CAPI secrets
  kubectl get secret -A --field-selector=type=cluster.x-k8s.io/secret &&\
  kubectl get secret -A --field-selector=type=infrastructure.cluster.x-k8s.io/secret                               > $dump_dir/Secrets-capi.summary.txt
  kubectl get secret -A --field-selector=type=cluster.x-k8s.io/secret -o yaml --show-managed-fields &&\
  kubectl get secret -A --field-selector=type=infrastructure.cluster.x-k8s.io/secret -o yaml --show-managed-fields > $dump_dir/Secrets-capi.yaml

  # list secrets
  kubectl get secret -A > $dump_dir/Secrets.summary.txt
  echo "note: secrets are purposefully not dumped" > $dump_dir/Secrets-censored.yaml

  echo -e "\nDisplay cluster resources usage per node"
  # From https://github.com/kubernetes/kubernetes/issues/17512
  kubectl get nodes --no-headers | awk '{print $1}' | xargs -I {} sh -c 'echo {} ; kubectl describe node {} | grep Allocated -A 5 | grep -ve Event -ve Allocated -ve percent -ve -- ; echo '
}

echo "Start debug-on-exit at: $(date -Iseconds)"

echo -e "\nDocker containers"
docker ps
echo -e "\nDocker containers resources usage"
docker stats --no-stream --all

echo -e "\nSystem info"
free -h
df -h || true

if [[ $(kind get clusters) =~ $KIND_CLUSTER_NAME ]]; then
  cluster_info_dump bootstrap
  echo -e "\nDump bootstrap node logs"
  docker ps -q -f name=control-plane* | xargs -I % -r docker exec % journalctl -e > bootstrap-cluster-dump/bootstap_node.log
fi

if [[ -f $BASE_DIR/management-cluster-kubeconfig ]]; then
    export KUBECONFIG=${KUBECONFIG:-$BASE_DIR/management-cluster-kubeconfig}

    echo -e "\nGet nodes in management cluster"
    kubectl --request-timeout=3s get nodes

    echo -e "\nGet pods in management cluster"
    kubectl --request-timeout=3s get pods -A

    cluster_info_dump management

    workload_cluster_name=$(kubectl get cluster.cluster -A -o jsonpath='{ $.items[?(@.metadata.namespace != "sylva-system")].metadata.name }')
    if [[ -z "$workload_cluster_name" ]]; then
        echo -e "There's no workload cluster for this deployment. All done"
    else
        echo -e "We'll check next workload cluster $workload_cluster_name"
        workload_cluster_namespace=$(kubectl get cluster.cluster --all-namespaces -o=custom-columns=NAME:.metadata.name,NAMESPACE:.metadata.namespace | grep "$workload_cluster_name" | awk -F ' ' '{print $2}')
        kubectl -n $workload_cluster_namespace get secret $workload_cluster_name-kubeconfig -o jsonpath='{.data.value}' | base64 -d > $BASE_DIR/workload-cluster-kubeconfig

        if timeout 10s kubectl --kubeconfig=$BASE_DIR/workload-cluster-kubeconfig get nodes > /dev/null 2>&1; then
          export KUBECONFIG=$BASE_DIR/workload-cluster-kubeconfig
        else
          # in case of baremetal emulation workload cluster is only accessible from Rancher
          # and rancher API certificates does not match expected (so kubectl must be used with insecure-skip-tls-verify)
          ./tools/shell-lib/get-wc-kubeconfig-from-rancher.sh $workload_cluster_name > $BASE_DIR/workload-cluster-kubeconfig-rancher
          yq -i e '.clusters[].cluster.insecure-skip-tls-verify = true' $BASE_DIR/workload-cluster-kubeconfig-rancher
          yq -i e 'del(.clusters[].cluster.certificate-authority-data)' $BASE_DIR/workload-cluster-kubeconfig-rancher
          export KUBECONFIG=$BASE_DIR/workload-cluster-kubeconfig-rancher
        fi

        cluster_info_dump workload
    fi
fi

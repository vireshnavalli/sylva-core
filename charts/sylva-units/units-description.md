<!-- markdownlint-disable MD044 -->
| name | full description | maturity | internal | source | version |
| :----- | :----- | :----- | :----- | :----- | :----- |
| **cabpk** | installs Kubeadm CAPI bootstrap provider | core-component |  | [Kustomize](https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.6.1/bootstrap-components.yaml) | v1.6.1 |
| **cabpr** | installs RKE2 CAPI bootstrap provider | core-component |  | [Kustomize](https://github.com/rancher-sandbox/cluster-api-provider-rke2/releases/download/v0.2.4/bootstrap-components.yaml) | v0.2.4 |
| **capd** | installs Docker CAPI infra provider | core-component |  | [Kustomize](https://github.com/kubernetes-sigs/cluster-api//test/infrastructure/docker/config/default/?ref=v1.6.1) | v1.6.1 |
| **capi** | installs Cluster API core operator | core-component |  | [Kustomize](https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.6.1/core-components.yaml) | v1.6.1 |
| **capm3** | installs Metal3 CAPI infra provider, for baremetal | core-component |  | [Kustomize](https://github.com/metal3-io/cluster-api-provider-metal3/releases/download/v1.6.0/infrastructure-components.yaml) | v1.6.0 |
| **capo** | installs OpenStack CAPI infra provider | core-component |  | [Kustomize](https://github.com/kubernetes-sigs/cluster-api-provider-openstack/config/default?ref=75ffe73f88544dbc26c6636a491bca5b3f63c3d4) | 75 |
| **capv** | installs vSphere CAPI infra provider | core-component |  | [Kustomize](https://github.com/kubernetes-sigs/cluster-api-provider-vsphere/releases/download/v1.9.0/infrastructure-components.yaml) | v1.9.0 |
| **cert-manager** | installs cert-manager, an X.509 certificate controller | core-component |  | [Helm](https://charts.jetstack.io) | v1.13.3 |
| **cluster** | holds the Cluster API definition for the cluster | core-component |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster.git) | 0.1.45 |
| **flux-system** | contains Flux definitions *to manage the Flux system itself via gitops*<br/><br/>Note that Flux is always installed on the current cluster as a pre-requisite to installing the chart | core-component |  | [Kustomize](https://github.com/fluxcd/flux2/releases/download/v2.2.3/install.yaml) | v2.2.3 |
| **heat-operator** | installs OpenStack Heat operator | core-component |  | [Kustomize](https://gitlab.com/sylva-projects/sylva-elements/heat-operator.git/config/default?ref=0.0.7) | 0.0.7 |
| **calico** | install Calico CNI | stable |  | [Helm](https://rke2-charts.rancher.io) | v3.25.001, v3.26.101 |
| **capo-contrail-bgpaas** | installs CAPO Contrail BGPaaS controller | stable |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/capo-contrail-bgpaas.git) | 1.0.3 |
| **cinder-csi** | installs OpenStack Cinder CSI | stable |  | [Helm](https://kubernetes.github.io/cloud-provider-openstack) | 2.28.1 |
| **cis-operator** | install CIS operator | stable |  | [Helm](https://charts.rancher.io) | 4.0.0 |
| **external-secrets-operator** | installs the External Secrets operator | stable |  | [Helm](https://charts.external-secrets.io) | 0.9.13 |
| **flux-webui** | installs Weave GitOps Flux web GUI | stable |  | [Helm](https://github.com/weaveworks/weave-gitops.git) | v0.38.0 |
| **gitea** | installs Gitea | stable |  | [Helm](https://dl.gitea.com/charts/) | 9.5.1 |
| **gitea-postgresql-ha** | installs PostgreSQL HA cluster for Gitea | stable |  | [Helm](https://charts.bitnami.com/bitnami) | 11.9.8 |
| **gitea-redis** | installs Redis cluster for Gitea | stable |  | [Helm](https://charts.bitnami.com/bitnami) | 9.1.1 |
| **ingress-nginx** | installs Nginx ingress controller | stable |  | [Helm](https://rke2-charts.rancher.io) | 4.5.202, 4.6.101 |
| **k8s-gateway** | installs k8s gateway (coredns + plugin to resolve external service names to ingress IPs)<br/><br/>is here only to allow for DNS resolution of Ingress hosts (FQDNs), used for importing workload clusters into Rancher and for flux-webui to use Keycloak SSO | stable |  | [Helm](https://ori-edge.github.io/k8s_gateway/) | 2.3.0 |
| **keycloak** | initializes and configures Keycloak | stable |  | [Kustomize](https://raw.githubusercontent.com/keycloak/keycloak-k8s-resources/23.0.6/kubernetes/keycloaks.k8s.keycloak.org-v1.yml) | 23.0.6 |
| **keycloak-legacy-operator** | installs Keycloak "legacy" operator | stable |  | [Kustomize](https://raw.githubusercontent.com/keycloak/keycloak-realm-operator/1.0.0/deploy/crds/legacy.k8s.keycloak.org_externalkeycloaks_crd.yaml) | 1.0.0 |
| **kyverno** | installs Kyverno | stable |  | [Helm](https://kyverno.github.io/kyverno) | 3.1.4 |
| **libvirt-metal** | installs libvirt for baremetal emulation<br/><br/>this unit is used in bootstrap cluster for baremetal testing | stable |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/container-images/libvirt-metal.git) | 0.1.8 |
| **local-path-provisioner** | installs local-path CSI | stable |  | [Helm](https://github.com/rancher/local-path-provisioner.git) | v0.0.24 |
| **longhorn** | installs Longhorn CSI | stable |  | [Helm](https://charts.rancher.io/) | 103.2.1+up1.5.3 |
| **metal3** | install Metal3 operator | stable |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/metal3.git) | 0.7.3 |
| **metallb** | installs MetalLB operator | stable |  | [Helm](https://metallb.github.io/metallb) | 0.13.12 |
| **monitoring** | installs monitoring stack | stable |  | [Helm](https://charts.rancher.io/) | 102.0.2+up40.1.2 |
| **multus** | installs Multus | stable |  | [Helm](https://rke2-charts.rancher.io/) | v3.9.3-build2023010901 |
| **os-image-server** | Deploys a web server on management cluster which serves OS images for baremetal clusters. | stable |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/os-image-server.git) | 1.8.0 |
| **postgres** | installs Postgresql for Keycloak | stable |  | [Helm](https://charts.bitnami.com/bitnami) | 14.0.5 |
| **rancher** | installs Rancher | stable |  | [Helm](https://releases.rancher.com/server-charts/latest) | 2.8.2 |
| **sriov** | installs SRIOV operator | stable |  | [Helm](https://charts.rancher.io/) | 102.1.0+up0.1.0 |
| **vault** | installs Vault<br/><br/>Vault assumes that the certificate vault-tls has been issued | stable |  | [Kustomize](https://raw.githubusercontent.com/banzaicloud/bank-vaults/1.19.0/operator/deploy/rbac.yaml) | 1.19.0 |
| **vault-config-operator** | installs Vault config operator | stable |  | [Helm](https://redhat-cop.github.io/vault-config-operator) | v0.8.25 |
| **vault-operator** | installs Vault operator | stable |  | [Helm](https://github.com/bank-vaults/vault-operator.git) | v1.21.2 |
| **vsphere-csi-driver** | installs Vsphere CSI | stable |  | [Kustomize](https://raw.githubusercontent.com/kubernetes-sigs/vsphere-csi-driver/v3.1.2/manifests/vanilla/vsphere-csi-driver.yaml) | v3.1.2 |
| **ceph-csi-cephfs** | Installs Ceph-CSI | beta |  | [Helm](https://ceph.github.io/csi-charts) | 3.9.0 |
| **flux-webui-init** | initializes and configures flux-webui | beta | True | Kustomize | N/A |
| **harbor** | installs Harbor | beta |  | [Helm](https://helm.goharbor.io) | 1.14.0 |
| **kubevirt** | installs kubevirt | beta |  | [Helm](https://suse-edge.github.io/charts) | 0.2.1 |
| **logging** | installs Rancher Fluentbit/Fluentd logging stack, for log collecting and shipping | beta |  | [Helm](https://charts.rancher.io/) | 102.0.1+up3.17.10 |
| **loki** | installs Loki log storage<br/><br/>installs Loki log storage in simple scalable mode | beta |  | Helm | v2.9.2 |
| **metal3-suse** | installs SUSE-maintained Metal3 operator | beta |  | [Helm](https://suse-edge.github.io/charts) | 0.6.0 |
| **minio-monitoring-tenant** | creates a MinIO tenant for the monitoring stack<br/><br/>Loki and Thanos will use this MinIO S3 storage | beta |  | Helm | v5.0.11 |
| **minio-operator** | install MinIO operator<br/><br/>MinIO operator is used to manage multiple S3 tenants | beta |  | Helm | v5.0.11 |
| **neuvector** | installs Neuvector | beta |  | [Helm](https://neuvector.github.io/neuvector-helm) | 2.6.6 |
| **rancher-init** | initializes and configures Rancher | beta | True | Kustomize | N/A |
| **snmp-exporter** | installs SNMP exporter | beta |  | [Helm](https://prometheus-community.github.io/helm-charts) | 1.8.1 |
| **sylva-prometheus-rules** | installs prometheus rules using external helm chart & rules git repo | beta |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-prometheus-rules.git) | 0.0.7 |
| **sylva-units-operator** | installs sylva-units operator | experimental |  | [Kustomize](https://gitlab.com/sylva-projects/sylva-elements/sylva-units-operator.git/config/default?ref=0.0.0-pre4) | 0.0.0-pre4 |
| **thanos** | installs Thanos | beta |  | [Helm](https://charts.bitnami.com/bitnami) | 12.16.1 |
| **trivy-operator** | installs Trivy operator | beta |  | [Helm](https://aquasecurity.github.io/helm-charts/) | 0.20.0 |
| **workload-cluster-operator** | installs Sylva operator for managing workload clusters | experimental |  | [Kustomize](https://gitlab.com/sylva-projects/sylva-elements/workload-cluster-operator.git/config/default?ref=0.0.0-pre3) | 0.0.0-pre3 |
| **bootstrap-local-path** | installs localpath CSI in bootstrap cluster |  | True | Kustomize | N/A |
| **capd-metallb-config** | configures MetalLB in a capd context |  | True | Kustomize | N/A |
| **capi-providers-pivot-ready** | checks if management cluster is ready for pivot<br/><br/>This unit only has dependencies, but does not create resources. It is here only to have a single thing to look at to determine if everything is ready for pivot (see bootstrap.values.yaml pivot unit) |  | True | Kustomize | N/A |
| **capi-rancher-import** | installs the capi-rancher-import operator, which let's us import Cluster AIP workload clusters in management cluster's Rancher |  | True | Helm | N/A |
| **capo-cluster-resources** | installs OpenStack Heat stack for CAPO cluster prerequisites |  | True | Kustomize | N/A |
| **cis-operator-scan** | allows for running a CIS scan for management cluster<br/><br/>it generates a report which can be viewed and downloaded in CSV from the Rancher UI, at https://rancher.sylva/dashboard/c/local/cis/cis.cattle.io.clusterscan |  | True | Kustomize | N/A |
| **cluster-creator-login** | configures Rancher account used for workload cluster imports |  | True | Kustomize | N/A |
| **cluster-creator-policy** | Kyverno policy for cluster creator<br/><br/>This units defines a Kyverno policy to distribute the Kubeconfig of cluster creator<br/>in all workload cluster namespaces, to allow the import of workload clusters in<br/>Rancher. |  | True | Kustomize | N/A |
| **cluster-garbage-collector** | installs cronjob responsible for unused CAPI resources cleaning |  | True | Kustomize | N/A |
| **cluster-import** | imports workload cluster into Rancher |  | True | Kustomize | N/A |
| **cluster-reachable** | ensure that created clusters are reachable, and make failure a bit more explicit if it is not the case<br/><br/>This unit will be enabled in bootstrap cluster to check connectivity to management cluster and in various workload-cluster namespaces in management cluster to check connectivity to workload clusters |  | True | Kustomize | N/A |
| **cluster-ready** | unit to check readiness of cluster CAPI objects |  | True | Kustomize | N/A |
| **coredns** | configures DNS inside cluster |  | True | Kustomize | N/A |
| **eso-secret-stores** | defines External Secrets stores |  | True | Kustomize | N/A |
| **first-login-rancher** | configure Rancher authentication for admin |  | True | Kustomize | N/A |
| **get-openstack-images** | Automatically push openstack images to cinder |  | True | Kustomize | N/A |
| **gitea-eso** | write secrets in gitea namespace in gitea expected format |  | True | Kustomize | N/A |
| **gitea-keycloak-resources** | deploys Gitea OIDC client in Sylva's Keycloak realm |  | True | Kustomize | N/A |
| **gitea-secrets** | create random secret that will be used by gitea application. secrets are sync with vault. |  | True | Kustomize | N/A |
| **harbor-init** | sets up Harbor prerequisites<br/><br/>it generates namespace, certificate, admin password, OIDC configuration |  | True | Kustomize | N/A |
| **keycloak-add-client-scope** | configures Keycloak client-scope<br/><br/>a job to manually add a custom client-scope to sylva realm (on top of default ones) while CRD option does not yet provide good results (overrides defaults) |  | True | Kustomize | N/A |
| **keycloak-oidc-external-secrets** | configures OIDC secrets for Keycloack |  | True | Kustomize | N/A |
| **keycloak-resources** | configures keycloak resources |  | True | Kustomize | N/A |
| **kubevirt-test-vms** | deploys kubevirt VMs for testing |  | True | Kustomize | N/A |
| **kyverno-policies** | configures Kyverno policies |  | True | Kustomize | N/A |
| **logging-config** | Configures rancher-logging to ship logs to Loki |  | True | Kustomize | N/A |
| **loki-init** | sets up Loki certificate<br/><br/>it generate certificate |  | True | Kustomize | N/A |
| **management-cluster-configs** | copies configuration object in management cluster during bootstrap |  | True | Kustomize | N/A |
| **management-cluster-flux** | installs flux in management cluster during bootstrap |  | True | Kustomize | N/A |
| **management-sylva-units** | installs sylva-units in management cluster during bootstrap |  | True | Helm | N/A |
| **metal3-init** | generates Metal3 random credentials |  | True | Kustomize | N/A |
| **metal3-sync-secrets** | configures secrets for Metal3 components |  | True | Kustomize | N/A |
| **minio-monitoring-tenant-init** | sets up MinIO certificate for minio-monitoring-tenant<br/><br/>it generate certificate |  | True | Kustomize | N/A |
| **minio-operator-init** | sets up MinIO certificate for minio-operator<br/><br/>it generate certificate |  | True | Kustomize | N/A |
| **multus-ready** | checks that Multus is ready<br/><br/>This unit only has dependencies, it does not create resources. It performs healthchecks outside of the multus unit, in order to properly target workload cluster when we deploy multus in it. |  | True | Kustomize | N/A |
| **namespace-defs** | creates sylva-system namespace and other namespaces to be used by various units |  | True | Kustomize | N/A |
| **neuvector-init** | sets up Neuvector prerequisites<br/><br/>it generates namespace, certificate, admin password, policy exception for using latest tag images (required for the pod managing the database of vulnerabilities since this DB is updated often) |  | True | Kustomize | N/A |
| **os-images-info** | Creates a list of os images<br/><br/>This unit creates a configmap containing the os images (and their details in the case of Sylva diskimage-builder ones)<br/>to be further served by os-image-server |  | True | Kustomize | N/A |
| **pivot** | moves ClusterAPI objects from bootstrap cluster to management cluster |  | True | Kustomize | N/A |
| **postgres-init** | initializes Postgresql for Keycloak |  | True | Kustomize | N/A |
| **rancher-keycloak-oidc-provider** | configures Rancher for Keycloak OIDC integration |  | True | Kustomize | N/A |
| **rancher-monitoring-clusterid-inject** | injects Rancher cluster ID in Helm values of Rancher monitoring chart |  | True | Kustomize | N/A |
| **sandbox-privileged-namespace** | creates the sandbox namespace used to perform privileged operations like debugging a node |  | True | Kustomize | N/A |
| **shared-workload-clusters-settings** | manages parameters which would be shared between management and workload clusters |  | True | Kustomize | N/A |
| **single-replica-storageclass** | Create a longhorn storage class with a single replica |  | True | Kustomize | N/A |
| **sriov-resources** | configures SRIOV resources |  | True | Helm | N/A |
| **sylva-ca** | provides a Certificate Authority for units of the Sylva stack |  | True | Kustomize | N/A |
| **sylva-dashboards** | adds Sylva-specific Grafana dashboards |  |  | [Helm](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-dashboards.git) | 0.0.2 |
| **synchronize-secrets** | allows secrets from Vault to be consumed other units, relies on ExternalSecrets |  | True | Kustomize | N/A |
| **thanos-init** | sets up thanos certificate<br/><br/>it generates a multiple CN certificate for all Thanos components |  | True | Kustomize | N/A |
| **tigera-clusterrole** | is here to allow for upgrading Calico chart when upgrading cluster<br/><br/>For v1.25.x to v1.26.x, see https://gitlab.com/sylva-projects/sylva-core/-/issues/664 |  | True | Kustomize | N/A |
| **vault-oidc** | configures Vault to be used with OIDC |  | True | Kustomize | N/A |
| **vault-secrets** | generates random secrets in vault, configure password policy, authentication backends, etc... |  | True | Kustomize | N/A |
| **vsphere-cpi** | configures Vsphere Cloud controller manager |  | True | Helm | N/A |

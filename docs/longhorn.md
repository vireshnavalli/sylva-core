# Longhorn in Sylva

## How to define baremetal node drives as Longhorn disks in values.yaml

In Sylva we have the ability to specify which disks are used for Longhorn _on a per-server basis for baremetal servers_, because servers may have different hardware topologies. <br/>
This can be achieved through a special annotation `sylvaproject.org/default-longhorn-disks-config=<customized default disks>` set at **`baremetal_hosts.x.bmh_metadata.annotations`** [`sylva-units`](../charts/sylva-units/) values level, that uses the value format of the `node.longhorn.io/default-disks-config=<customized default disks>` node annotation, defined by [Longhorn default disks and node configuration](https://github.com/longhorn/longhorn/blob/master/enhancements/20200319-default-disks-and-node-configuration.md#design). <br/>
An example is available below:

```yaml

baremetal_hosts:
  my-bmh-foo:
    bmh_metadata:
      annotations:
        sylvaproject.org/default-longhorn-disks-config: '[ { "path":"/var/longhorn/disks/disk_by-path_pci-0000:18:00.0-scsi-0:3:111:0", "storageReserved":0, "allowScheduling":true, "tags":[ "ssd", "fast" ] }, { "path":"/var/longhorn/disks/sde", "storageReserved":0, "allowScheduling":true, "tags":[ "hdd", "slow" ] } ]'  # define longhorn disks, will result in mounting each /dev/x disk at /var/longhorn/disks/x (e.g /var/longhorn/disks/sde, /var/longhorn/disks/disk_by-path_pci-0000:18:00.0-scsi-0:3:111:0)
```

The keys in the JSON array elements in this annotation are defined in [this file](https://github.com/longhorn/longhorn-manager/blob/88c792f7df38383634c2c8401f96d999385458c1/k8s/pkg/apis/longhorn/v1beta2/node.go#L60-L74), and the mandatory ones for having Longhorn schedule PVs on a disk are:

- `"path": "/var/longhorn/disks/x` - where x is recommended to be the disk referenced by PCI addresses, which is consistent through node restarts (e.g. `/var/longhorn/disks/disk_by-path_pci-0000:00:0b.0`). This represents the mount point of the disk x and it **needs to start with `/var/longhorn/disks/`**;

- `"allowScheduling":true` - enable replica scheduling for the disk. Please note that if this is missed, the default value for this is `false`. **For this reason, it's very important to use the `"allowScheduling"` inside the `sylvaproject.org/default-longhorn-disks-config` annotation value, as this parameter would indicate to Longhorn manager whether the user enabled/disabled replica scheduling for the particular disk.**

> **_IMPORTANT NOTICE:_** A prerequisite for having the ability to use this BMH annotation to define Longhorn disk consumption is the usage in environment-values of:

```yaml
cluster:
  enable_longhorn: true
```

> **_IMPORTANT NOTICE:_** With this we've also dropped the support for the `node.longhorn.io/create-default-disk: true` node label (since a fixed value of `"config"` is needed for Longhorn controllers to act upon based on the node annotation), and it cannot be used anymore by stack operators. It also means it is mandatory to use dedicated disks for Longhorn. The OS disk cannot be used.

## Sylva implementation for Longhorn disk configuration

### Need for declarative Longhorn settings and Sylva context

According to the [documentation](https://longhorn.io/docs/1.5.3/advanced-resources/default-disk-and-node-config/#customizing-default-disks-for-new-nodes), depending on whether a node’s label `node.longhorn.io/create-default-disk: 'config'` is present, Longhorn will check for the `node.longhorn.io/default-disks-config` annotation (which allows a [rich set of settings](https://longhorn.io/docs/1.5.3/advanced-resources/default-disk-and-node-config/#customizing-default-disks-for-new-nodes)) and create default disks according to it. <br/>
So in order to configure to define the disks to be consumed by Longhorn for Persistent Storage since cluster creation time, we'd need to:

1. be able to label and annotate Kubernetes Nodes declaratively

1. be able to mount the disks somewhere - Longhorn does not take of that _at all_.

To address the first point, starting with its `v0.2.0` version, the [`cluster-api-provider-rke2`](https://github.com/rancher-sandbox/cluster-api-provider-rke2), aka `CABPR`, supports injecting node annotations via `RKE2ControlPlane.spec.agentConfig.nodeAnnotations` for control-plane nodes (for worker nodes the `RKE2ConfigTemplate.spec.template.spec.agentConfig.nodeAnnotations` is not effective, but is being worked-around within [`sylva-capi-cluster`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster) according to https://gitlab.com/sylva-projects/sylva-core/-/issues/417#note_1668330146) on top of the existent support for injecting node labels, through `RKE2ControlPlane.spec.agentConfig.nodeLabels` and `RKE2ConfigTemplate.spec.template.spec.agentConfig.nodeLabels`. <br/>
All this is made available by `sylva-units` (through [`sylva-capi-cluster`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster)) chart values like:

```yaml

cluster:
  rke2:
    nodeLabels:
      node.longhorn.io/create-default-disk: "config"
    nodeAnnotations:
      node.longhorn.io/default-disks-config: '[{..}]'

  control_plane:
    rke2:
      nodeLabels:
        node.longhorn.io/create-default-disk: "config"
    nodeAnnotations:
      node.longhorn.io/default-disks-config: '[{..}]'

  machine_deployment_default:
    rke2:
      nodeLabels:
        node.longhorn.io/create-default-disk: "config"
    nodeAnnotations:
      node.longhorn.io/default-disks-config: '[{..}]'

  machine_deployments:
    md0:
      rke2:
        nodeLabels:
          node.longhorn.io/create-default-disk: "config"
      nodeAnnotations:
        node.longhorn.io/default-disks-config: '[{..}]'

```

On the other hand, the kubeadm bootstrap provider - aka CABPK, does not have any native support for setting node labels or annotations, so we work it out with CAPI post-bootstrap `kubectl annotate node $(hostname)` and `kubectl label node $(hostname)` cloud-init (`/var/lib/cloud/instance/scripts/runcmd`) commands, provided by [`sylva-capi-cluster`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster). <br/>

Similarly, in pre-bootstrap cloud-init commands (also provided by [`sylva-capi-cluster`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster)) we handle the disk mounting part, where the convention is to use as mount point the value of of the `"path"` key inside JSON array elements. For example:

```yaml

baremetal_hosts:
  my-bmh-foo:
    bmh_metadata:
      annotations:
        sylvaproject.org/default-longhorn-disks-config: '[ { "path":"/var/longhorn/disks/disk_by-path_pci-0000:00:0b.0", "allowScheduling":true, "tags":[ "ssd", "fast" ] }, { "path":"/var/longhorn/disks/sde"} ]'

```

would:

- mount `/dev/sde` at `/var/longhorn/disks/sde`;

- mount `/dev/disk/by-path/pci-0000:00:0b.0` at `/var/longhorn/disks/disk_by-path_pci-0000:00:0b.0`.

We needed the ability to specify which disks are used for Longhorn _on a per-server basis for baremetal servers_. This per-node granularity is critical to have, because experience has proven that it's not reasonable to expect all nodes in a given group (control nodes, or workers of a given MachineDeployment) would have same disk hardware or PCI topology. <br/>

To provide this, we've introduced a special annotation `sylvaproject.org/default-longhorn-disks-config=<customized default disks>` set **on BareMetalHost resources**, that uses the value format of the `node.longhorn.io/default-disks-config=<customized default disks>` node annotation. With this single BMH annotation we're:

1) mounting the disks for Longhorn

2) annotating the node created by the Machine consuming the BareMetalHost with `node.longhorn.io/default-disks-config=<customized default disks>`.

3) label the node created by the Machine consuming the BareMetalHost with `node.longhorn.io/create-default-disk: 'config'`.

The rest falls to the `longhorn` unit responsibility.

## What we see with developer glasses

To have the implementation picture in mind, we propagate this individual BMH metadata (annotation `sylvaproject.org/default-longhorn-disks-config=<customized default disks>`) to consumer CAPI machine (to achieve per-node granularity), to be further used for both disk configuration/mounting and setting annotations and label inside cloud-init. <br/>
To achieve this propagation, we need to rely on the "BMH -\> Metal3 metadata -\> ds.metadata" channel and set the node annotation based on the said BMH annotation running a `kubectl annotate $(hostname) node.longhorn.io/default-disks-config=<customized default disks>` command on each node. <br/>
This workflow is:

- use the following `sylva-units` values to annotate the BMH:

```yaml

cluster:
  baremetal_hosts:
    my-bmh-foo:
      bmh_metadata:
        annotations:
          sylvaproject.org/default-longhorn-disks-config: '[ { "path":"/var/longhorn/disks/disk_by-path_pci-0000:18:00.0-scsi-0:3:111:0", "allowScheduling":true, "storageReserved":0, "tags":[ "ssd", "fast" ] }, { "path":"/var/longhorn/disks/sde", "storageReserved":0, "allowScheduling":true, "tags":[ "hdd", "slow" ] } ]'

```

- which allows `Metal3DataTemplate.spec.metaData.fromAnnotations` to read it based on:

```yaml

metaData:
  :
  fromAnnotations:
  - key: sylva_longhorn_disks
    object: baremetalhost
    annotation: sylvaproject.org/default-longhorn-disks-config
  {{- end }}

```

- to further use it inside cloud-init for both CP and MD nodes (facilitated by [`sylva-capi-cluster`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster)'s named template [`shell-longhorn-node-metadata`](https://gitlab.com/sylva-projects/sylva-elements/helm-charts/sylva-capi-cluster/-/blob/0.1.31/templates/_helpers.tpl?ref_type=tags#L378-462)), with something like:

```yaml

postRKE2Commands:
  :
  - /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml annotate node $(hostname) {{ printf "%s=%s" "node.longhorn.io/default-disks-config" `{{ ds.meta_data.sylva_longhorn_disks }}` }}
  - /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml label node $(hostname) node.longhorn.io/create-default-disk=config
```

- which will result in a bootstrapped node like:

```yaml

apiVersion: v1
kind: Node
metadata:
  annotations:
    node.longhorn.io/default-disks-config: '[{"path":"/var/longhorn/disks/disk_by-path_pci-0000:18:00.0-scsi-0:3:111:0",
      "storageReserved":0, "allowScheduling":true, "tags":[ "ssd", "fast" ]}, {"path":"/var/longhorn/disks/sde", "storageReserved":0, "allowScheduling":true, "tags":[ "hdd", "slow" ]}]'
    :
    rke2.io/node-args: '["server","--cluster-cidr","100.72.0.0/16","--cni","calico","--kubelet-arg","anonymous-auth=false","--kubelet-arg","provider-id=metal3://sylva-system/mgmt-cluster-my-bmh-foo/mgmt-cluster-cp-056108e4c3-5b9sj","--node-label","--node-label","node.longhorn.io/create-default-disk=config","--profile","cis-1.23","--service-cidr","100.73.0.0/16","--tls-san","172.18.0.2","--tls-san","192.168.100.2","--token","********"]'
  labels:
    :
    node.longhorn.io/create-default-disk: config

```

```shell

# checking the mounted disks
root@gmt-cluster-my-bmh-foo:/# lsblk
NAME  MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
vda   252:0    0   50G  0 disk
├─vda1
│     252:1    0  550M  0 part /boot/efi
├─vda2
│     252:2    0    8M  0 part
├─vda3
│     252:3    0 49.4G  0 part /
└─vda4
      252:4    0   65M  0 part
vdb   252:16   0   50G  0 disk
vdc   252:32   0   50G  0 disk /var/longhorn/disks/disk_by-path_pci-0000:18:00.0-scsi-0:3:111:0
root@gmt-cluster-my-bmh-foo:/#

```

```shell

# checking the PVs mounted on the node
$ kubectl get node management-cluster-md0-hnjtc-6j49q -o yaml | yq .status.volumesInUse
- kubernetes.io/csi/driver.longhorn.io^pvc-17e5863f-4d15-419c-bf20-48e2547d64fc
- kubernetes.io/csi/driver.longhorn.io^pvc-1b91ddb0-15a4-4c50-af90-c33280e7cdfa
- kubernetes.io/csi/driver.longhorn.io^pvc-1cb0e490-d030-42ea-a16f-60a9b19f1e3a
- kubernetes.io/csi/driver.longhorn.io^pvc-1dc68632-3587-48a5-b481-d0f5f5b5dd43
- kubernetes.io/csi/driver.longhorn.io^pvc-68dc4c38-ecef-48d2-a02b-fe69d4ff1e26
- kubernetes.io/csi/driver.longhorn.io^pvc-7f0ec91b-dec6-4f53-a277-4d6c62279760
- kubernetes.io/csi/driver.longhorn.io^pvc-9c103ae6-c68f-42a2-8e88-dfe41f6c4c25
- kubernetes.io/csi/driver.longhorn.io^pvc-c3095a2c-ba1f-49a7-8796-7dc7dfc5f2de

```

When passing the value of this annotation to the BMH, we base64 encode it to avoid issues with parsing the complex JSON structure during cloud-init init phase. We base64 decode it during cloud-init commands injection.

```terminal

$ kubectl get secrets sylva-units-values -o yaml | yq .data.values | base64 -d | yq '.cluster.baremetal_hosts."management-cp".bmh_metadata.annotations'
sylvaproject.org/default-longhorn-disks-config: '[{"path":"/var/longhorn/disks/disk_by-path_pci-0000:00:0b.0", "storageReserved":0, "allowScheduling":true, "tags":[ "ssd", "fast" ]}]'
$
$ kubectl get bmh mgmt-cluster-management-cp -o yaml | yq .metadata.annotations
meta.helm.sh/release-name: cluster
meta.helm.sh/release-namespace: sylva-system
sylvaproject.org/default-longhorn-disks-config: W3sicGF0aCI6Ii92YXIvbG9uZ2hvcm4vZGlza3MvZGlza19ieS1wYXRoX3BjaS0wMDAwOjAwOjBiLjAiLCAic3RvcmFnZVJlc2VydmVkIjowLCAiYWxsb3dTY2hlZHVsaW5nIjp0cnVlLCAidGFncyI6WyAic3NkIiwgImZhc3QiIF19XQ==
$

```

# What is kubevirt

KubeVirt provides additional functionality to a Kubernetes cluster, enabling it to manage virtual machine workloads.
KubeVirt is a collection of custom resource definitions (CRDs) and controllers.
With KubeVirt, you can use the Kubernetes platform to run and manage application containers and VMs side-by-side.

## Why Kubevirt in Sylva

### Unified Orchestration Platform

Running both your VMs and containerized applications within a Kubernetes cluster simplifies your orchestration needs. Any needs of VNF along with CNF, on k8s cluster will provide a unified platform.

### Application Modernization

Reduce hurdles by resolving the legacy and running legacy new apps on same platform using both VMs and containers

### VNF Modernization

Moving your NFV workloads into VMs with KubeVirt allows you to move to Kubernetes, and host your NFV VMs alongside other already containerized applications.

## Kubevirt Networking in Sylva

By default, the VMs you create with KubeVirt use the native networking already configured in the pod.
Typically, this means that the bridge option is selected, and your VM has the IP address of the pod. This
approach makes interoperability possible. The VM can integrate with different cases like sidecar containers
and pod masquerading. When using pod masquerading, there is a defined CIDR chosen by yourself for
which VM’s are not assigned a private IP, and instead use NAT behind the pod IP.

### Kubevirt with Multus

Multus is a secondary network that uses Multus-CNI. Multus allows a user to attach multiple network interfaces to pods in Kubernetes. If you use Multus as your network, you need to ensure that you have installed Multus across your cluster and that you have created a NetworkAttachmentDefinition CRD. (Creating Virtual Machines | Interfaces and Networks)

Multus can be enabled via environment's values.yaml

```shell
units:
  multus:
    enabled: true
```

### Kubevirt with sriov

Kubevirt with sriov can be used together to enhance the performance and flexibility of virtualized environments.

Sriov is optional feature which can be enabled in sylva and it can be used with/without kubevirt.
Sriov can be enabled via environment's values.yaml with some configuration setting. Below is example, user can modify as per requirement

```shell

units:
  sriov:
    enabled: true
  sriov-resources:
    enabled: true

sriov:
  node_policies:
    dl360-sriov:
      resourceName: sriov
      numVfs: 16
      deviceType: "vfio-pci"
      nicSelector:
        pfNames:
          - ens2f0

cluster:
  kubelet_extra_args:
    max-pods: "228"
    #node-labels: "feature.node.kubernetes.io/network-sriov.capable=true" ##should be set automatically by rancher-nfd
    feature-gates: "TopologyManager=true,CPUManager=true"
    topology-manager-policy: "best-effort"
    cpu-manager-policy: "static"
    system-reserved: "cpu=100m"
    kube-reserved: "cpu=100m"
```

### Kubevirt with dpdk(TBD)

### Kubevirt with feature gates (Work in progress)

These are the available [feature gates](https://github.com/kubevirt/kubevirt/blob/main/pkg/virt-config/feature-gates.go#L26) for kubevirt, which can be set in kubevirt as per requirement

Sylva is set with below optional feature gates:

  1. NUMA
  2. CPUManager
  3. Snapshot

## Units in Sylva

### kubevirt

kubevirt is kept as optional unit which can be enabled from environment-values and it is by default enabled for sylva CI under `deploy-misc-units-in-capo` pipeline

### kubevirts-test-vms

kubevirt-test-vms is kept as optional unit which can be enabled from environment and it is by default enabled for sylva CI under `deploy-misc-units-in-capo` pipeline. This is dependent on kubevirt unit and multus unit. Some of example VMS will be created with multus. So kept `kubevirt-test-vms` as dependent on multus

There are some examples of creating VMS:

[Kubevirt VM with cirros image](https://gitlab.com/sylva-projects/sylva-core/-/blob/main/kustomize-units/kubevirt-test-vms/cirros-vm.yaml)

[Kubevirt centos VM with multus](https://gitlab.com/sylva-projects/sylva-core/-/blob/main/kustomize-units/kubevirt-test-vms/multus-vm.yaml)

This VM is created with multus which required multus unit enabled in cluster.
Multus unit will enable the api `k8s.cni.cncf.io/v1` in cluster.

To create VM with Mutlus needs `NetworkAttachmentDefinition` which will be created in `kubevirt-test-vms unit`.

It will help in attaching the second network with VM.

## How to use in sylva

A KubeVirt virtual machine is a Pod running a KVM instance in a container.

Associated  with the Pod is a VirtualMachineInstance, which links the Pod to a VirtualMachine, and provides an endpoint for some advanced operations like migration and disk hotplug operations.

At the top level is a VirtualMachine which is the primary resource for interacting with a virtual machine.

We have a unit(`kubevirt-test-vms`) in place for kubevirt, using which we intend to create VMs on management and workload clusters, either running on dedicated hosts or hosts hosting a mix of pods and VMs (according to the use case)
This is typically aimed for Baremetal Workload clusters for performance reasons.

## How to create vm

Some of VMs are already created as example, which are part of `kubevirt-test-vms`. User can apply VM manifests on cluster enabled with kubevirt.

Example: cirros-vm.yaml

```shell
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: sylva-tests-cirros-vm
spec:
  running: true
  template:
    metadata:
      labels:
        kubevirt.io/size: small
        kubevirt.io/domain: testvm
    spec:
      domain:
        devices:
          disks:
            - name: containerdisk
              disk:
                bus: virtio
            - name: cloudinitdisk
              disk:
                bus: virtio
          interfaces:
          - name: default
            masquerade: {}
        resources:
          requests:
            memory: 64M
      networks:
      - name: default
        pod: {}
      volumes:
        - name: containerdisk
          containerDisk:
            image: quay.io/kubevirt/cirros-container-disk-demo
        - name: cloudinitdisk
          cloudInitNoCloud:
            userDataBase64: SGkuXG4=
```

### VM creation

```shell
kubectl apply -f cirros-vm.yaml
```

### Start/Stop  the VM:​

```shell
kubectl patch virtualmachine sylva-tests-cirros-vm --type merge -p '{"spec":{"running":true}}'

kubectl patch virtualmachine sylva-tests-cirros-vm --type merge -p '{"spec":{"running":false}}'
```

### Interact using virtctl CLI:​

​User can also interact with virctl, by enabling or installing it's binary

```shell
virtctl console/start/stop <vm-name>
```

### Accessing VMs

Connect to the serial console of the Cirros VM. Hit return / enter a few times and login with the displayed username and password.

```shell
virtctl console <vm name>
```

### Check status of vms

User can check the vm state.

```shell
kubectl get vms -n <namespace>
```

### Patch on vms

Patch can be applied on vms for any operations like start/stop

Start the VM:

```shell
kubectl patch virtualmachine <vm name> --type merge -p \
    '{"spec":{"running":true}}'
```

Stop the VM:

```shell

kubectl patch virtualmachine <vm name> --type merge -p \
    '{"spec":{"running":false}}
```

### Delete VM

To delete a Virtual Machine:

```shell
kubectl delete vm <vm name>
```

## How to test

Using nested virtualization we can implement and test it on CAPO for management cluster and baremetal/capo for workload cluster. We can have CI runs to validate it's working.
Also User can run their own customized templates for vms where kubeviert unit
is enabled or templates can be create under `kubevirt-test-vms` unit.

### Images used by kubevirt(TBD)

# Debug in Sylva environment

For debugging or testing purpose, you might need to run privileged pods. With RKE2, namespaces don't have permission to run privileged workload.

For such a case, `sylva-core` is providing a unit named `sandbox-privileged-namespace` deploying a namespace  called `sandbox` in which the restrictions are lift.

To enable the unit, please add the following code as part of your settings.

```yaml
units:
  sandbox-privileged-namespace:
    enabled: true
```

Apply the configuration on the management cluster.

```shell
./apply.sh environment-values/<your environment name>
```

You can then launch a debug pod for a node using the following command:

```shell
# Get node name
kubectl get nodes

# lauch debug pod
kubectl debug node/<name-of-your-node> --image alpine:3.16 -n sandbox -it
```

# Ceph-csi-cephfs in Sylva

Within Sylva, [`Ceph-csi-cephfs`](https://github.com/ceph/ceph-csi/tree/devel/charts/ceph-csi-cephfs#ceph-csi-cephfs) can be used to provide persistent storage for the workload clusters.

An existing, centrally located, Ceph cluster can be integrated to allow workload clusters store their data in it.

Persistent volumes with different access modes, like ReadWriteOnce and ReadWriteMany, can be created as per requirements.

::: Info: Ceph-csi-Cephfs doesn't support true multi-tenancy. We can create a separate filesystem for each workload cluster and can segregate the data for each workload cluster, but as per the official doc of ceph-csi-cephfs, Ceph user needs mgr read-write capabilities to create SC and PVC.
Having such capabilities, a user can access or modify any data present on any of the Ceph file-systems.
:::

## How a management/workload cluster can consume Ceph

### Ceph config

* Create new Ceph file system

```shell
ceph fs volume create <filesystem_name>
```

* List down the file system

```shell
ceph fs ls
ceph osd pool ls detail
```

* Verify MDS status

```shell
ceph -s
ceph mds status
```

* Create new user with below permissions, following [CephFS authentication capabilities](https://docs.ceph.com/en/reef/cephfs/client-auth/)

```shell
ceph auth get-or-create client.CEPH_USER}\
   mds 'allow rw fsname=${CEPH_FS}' \
   mgr 'allow rw' \
   mon 'allow r fsname=${CEPH_FS}' \
   osd 'allow rw pool=cephfs.${CEPH_FS}.data, allow rw pool=cephfs.${CEPH_FS}.metadata' \
   -o /etc/ceph/ceph.client.{CEPH_USER}.keyring
```

* Verify the capabilities.

```shell
ceph auth get client.foo
[client.foo]
      key = AQDFakeTokenFakeTokenFakeTokenGSoSbLkA==
      caps mds = "allow rw fsname=cephfs_a"
      caps mgr = "allow rw"
      caps mon = "allow r fsname=cephfs_a"
      caps osd = "allow rw pool=cephfs.cephfs_a.data, allow rw pool=cephfs.cephfs_a.meta"
```

## Consuming Cephfs for a cluster

* Make sure that Ceph monitor IPs are reachable from each Sylva cluster trying to provide Persistent Storage via `ceph-csi-cephfs` unit.
* New Ceph user and file system should be created for each cluster.
* Define your environment-values for the ceph secrets and ceph config as follows:

```shell
# for a management cluster, e.g. in environment-values/my-rke2-capo-
env/values.yaml
# or for a workload cluster, e.g. in environment-values/workload-clusters/my-rke2-capm3-env/values.yaml

ceph:
  cephfs_csi:
    clusterID: "72451b38-2d3c-11ee-80a2-652991486dfa"
    fs_name: "ceph-fs"
    monitors_ips:
      - "192.168.128.45"
      - "192.168.128.46"
      - "192.168.128.47"

units:
  ceph-csi-cephfs:
    enabled: yes

# for a management cluster, e.g. in environment-values/my-rke2-capo-
env/secrets.yaml
# or for a workload cluster, e.g. in environment-values/workload-clusters/my-rke2-capm3-env/secrets.yaml

ceph:
  cephfs_csi:
    adminID: "user-1"
    adminKey: "AQDFakeTokenFakeTokenFakeTokenGSoSbLkA=="
```

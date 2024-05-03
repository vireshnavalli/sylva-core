---
title: How to use sylva-core
slug: /
---

## Access UIs when in CAPD behind Proxy

```shell

# if the CAPD host is a Linux machine with address 172.20.129.247 behind the http://192.168.200.188:3128 proxy, one could use:
boburciu@WX-5CG020BDT2:~$  ssh -i ~/.ssh/boburciu_key_pair_rocket.pem -l ubuntu 172.20.129.247 -o ProxyCommand='socat - PROXY:192.168.200.188:%h:%p,proxyport=3128' -D 8887
ubuntu@sylva-core-capd-bb:~$ docker ps | grep management-cluster
d6272b7f2b52   registry.gitlab.com/sylva-projects/sylva-elements/container-images/rke2-in-docker:v1-24-4-rke2r1   "/usr/local/bin/entr…"   2 weeks ago    Up 2 weeks    9345/tcp, 44847/tcp, 127.0.0.1:44847->6443/tcp   management-cluster-control-plane-pphgf
zsh:1: command not found: q
ubuntu@sylva-core-capd-bb:~$
ubuntu@sylva-core-capd-bb:~$ docker exec -it management-cluster-control-plane-pphgf sh -c "/var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml  get ing -A"
NAMESPACE       NAME                      CLASS    HOSTS           ADDRESS        PORTS     AGE
cattle-system   rancher                   <none>   rancher.sylva   172.27.0.5     80, 443   9m
flux-system     flux-webui-weave-gitops   nginx    flux.sylva      172.19.0.100   80        14m
vault           vault                     <none>   vault.sylva     172.19.0.100   80, 443   13m
ubuntu@sylva-core-capd-bb:~$ cat /etc/hosts | grep rancher.sylva
172.27.0.5 rancher.sylva flux.sylva vault.sylva   # DNS mapping for Ingress URLs to the relevant IP address
ubuntu@sylva-core-capd-bb:~$ docker ps | grep management-cluster

# and the just use the browser with a SOCKS v5 host for 127.0.0.1:8887 and enable "Proxy DNS when using SOCKS v5". The UIs will then be available.
```

## Move past Docker Hub rate limiting

You can [run a local registry mirror](https://docs.docker.com/registry/recipes/mirror/#run-a-registry-as-a-pull-through-cache) and have the management cluster be configured with a `docker.io` registry mirror to point to it by configuring `registry_mirrors` in environment-values with its endpoint.

```yaml
registry_mirrors:
  hosts_config:
    docker.io:
    - mirror_url: http://your.mirror/docker
```

## Expose management cluster API through floatingIP for bootstrap in CAPO

When deploying management cluster in OpenStack, you can specify to which network you want the cluster nodes VMs (their OpenStack ports) to be attached by using `cluster.capo.network_id`.

In some cases, this virtual network (VN) will not be accessible to the bootstrap cluster (like when deploying the VMs on an isolated network behind an OpenStack router with Source NAT enabled and using a remote bootstrap machine without direct connectivity inside `cluster.capo.network_id` defined VN), so bootstrap cluster is not able to reach the Kubernetes API to confirm that node is ready.

You can specify `openstack.external_network_id` to create a floating IP. This floating IP will be used by default to access to cluster API and allows the bootstrap cluster to access management cluster API as well.

## Use upstream IPA Downloader container in Metal3 chart

By default the chart `metal3` uses our custom IPA Downloader container which directly embeds the IPA ramdisk image.

However if a more recent IPA ramdisk image is required, it's possible to override our custom container to use an upstream one which retreives from Internet the IPA ramdisk image. In certain circumstances, to be able to reach it, the container must be configured with proxy settings like this:

```shell

units:
  metal3:
    helmrelease_spec:
      values:
        images:
          ironicIPADownloader:
            repository: <upstream_image>
        httpProxy: <upstream http proxy, value set under proxies.http_proxy>
        httpsProxy: <upstream http proxy, value set under proxies.https_proxy>
```

## Using nip.io dns records in order to avoid editing hosts file

The following trick can be used to generate a dynamic cluster domain, avoiding to edit the system hosts file manually:

```yaml
cluster_domain: '{{ .Values.display_external_ip }}.nip.io'
```

As result you got something like:

```txt
🌱 You can access following UIs
NAMESPACE       NAME                      CLASS    HOSTS                            ADDRESS                                                          PORTS     AGE
cattle-system   rancher                   nginx    rancher.172.49.112.148.nip.io    192.168.128.120,192.168.128.121,192.168.128.49,192.168.129.244   80, 443   15m
flux-system     flux-webui-weave-gitops   nginx    flux.172.49.112.148.nip.io       192.168.128.120,192.168.128.121,192.168.128.49,192.168.129.244   80, 443   11m
keycloak        keycloak-ingress          <none>   keycloak.172.49.112.148.nip.io   192.168.128.120,192.168.128.121,192.168.128.49,192.168.129.244   80, 443   33m
vault           vault                     <none>   vault.172.49.112.148.nip.io      192.168.128.120,192.168.128.121,192.168.128.49,192.168.129.244   80, 443   33m

🎉 All done
```

and you should be able to directly access UIS as `https://rancher.172.49.112.148.nip.io` in your browser

Notes:

- If your are behind a proxy, you need to be able to resolve Internet hostnames.
- Depending of your proxy config, you also may need to add `.nip.io` in `proxy.no_proxy`

{{/*

cluster-healthchecks

This named template generates the content of healthChecks field for a Flux CD Kustomization, with
reference to CAPI resources for the current CAPI cluster defined in the 'cluster' unit, with the
'sylva-capi-cluster' chart.

The background is that:
* the HelmRelease resource instantiating sylva-capi-cluster has no health check (FluxCD HelmReleases don't have that)
* we hence want to do the checks in the Kustomization that creates that HelmRelease
* the list of resource cannot be static, because it depends on:
  - which control plane provider is used
  - which infra provider is used
  - what are the machine deployments defined

Depending on the context, this template can be used to generate the references to the MachineDeployments or not.

This is because in the kubeadm case we can't wait for the MachineDeployemts in "cluster" unit, or this prevents
deploying the CNI, and the CNI itself is needed before the MachineDeployment nodes can be considered ready by CAPI.

*/}}

{{ define "cluster-healthchecks" }}

{{- $ns := .ns -}}  {{/* this corresponds to .Release.Namespace */}}
{{- $cluster := .cluster -}}  {{/* this corresponds to .Values.cluster */}}
{{- $includeMDs := . | dig "includeMDs" true -}}

{{/* the healtchecks is a list, we wrap it into a dict to overcome the
     fact that fromYaml can't return anything else than a dict
*/}}
result:

{{/*

Wait for Cluster resource:

*/}}

    - apiVersion: cluster.x-k8s.io/v1beta1
      kind: Cluster
      name: {{ $cluster.name }}
      namespace: {{ $ns }}

{{/*

Wait for infra provider Cluster

*/}}

{{- $cluster_kind := "" -}}
{{- $cluster_apiVersion := "" -}}
{{- if $cluster.capi_providers.infra_provider | eq "capo" -}}
  {{- $cluster_kind = "OpenStackCluster" -}}
  {{- $cluster_apiVersion = "infrastructure.cluster.x-k8s.io/v1alpha6" -}}
{{- else if $cluster.capi_providers.infra_provider | eq "capv" -}}
  {{- $cluster_kind = "VSphereCluster" -}}
  {{- $cluster_apiVersion = "infrastructure.cluster.x-k8s.io/v1beta1" -}}
{{- else if $cluster.capi_providers.infra_provider | eq "capm3" -}}
  {{- $cluster_kind = "Metal3Cluster" -}}
  {{- $cluster_apiVersion = "infrastructure.cluster.x-k8s.io/v1beta1" -}}
{{- else if $cluster.capi_providers.infra_provider | eq "capd" -}}
  {{- $cluster_kind = "DockerCluster" -}}
  {{- $cluster_apiVersion = "infrastructure.cluster.x-k8s.io/v1beta1" -}}
{{- else -}}
  {{- fail (printf "sylva-units cluster-healthchecks named template would need to be extended to support CAPI infra provider %s" $cluster.capi_providers.infra_provider) -}}
{{- end }}

    - apiVersion: {{ $cluster_apiVersion }}
      kind: {{ $cluster_kind }}
      name: {{ $cluster.name }}
      namespace: {{ $ns }}

{{/*

We determine which control plane object to look at depending
on the CAPI bootstrap provider being used.

*/}}

{{- $cp_kind := "" -}}
{{- $cp_apiVersion := "" -}}
{{- if $cluster.capi_providers.bootstrap_provider | eq "cabpk" -}}
  {{- $cp_kind = "KubeadmControlPlane" -}}
  {{- $cp_apiVersion = "controlplane.cluster.x-k8s.io/v1beta1" -}}
{{- else if $cluster.capi_providers.bootstrap_provider | eq "cabpr" -}}
  {{- $cp_kind = "RKE2ControlPlane" -}}
  {{- $cp_apiVersion = "controlplane.cluster.x-k8s.io/v1alpha1" -}}
{{- else -}}
  {{- fail (printf "sylva-units cluster-healthchecks named template would need to be extended to support CAPI bootstrap provider %s" $cluster.capi_providers.bootstrap_provider) -}}
{{- end }}

    - apiVersion: {{ $cp_apiVersion }}
      kind: {{ $cp_kind }}
      name: {{ $cluster.name }}-control-plane
      namespace: {{ $ns }}

{{/*

If $includeMDs was specified, we include all the MachineDeployments in the healthChecks.

*/}}

{{ if $includeMDs -}}
    {{- range $md_name,$_ := $cluster.machine_deployments }}
    - apiVersion: cluster.x-k8s.io/v1beta1
      kind: MachineDeployment
      name: {{ $cluster.name }}-{{ $md_name }}
      namespace: {{ $ns }}
    {{ end -}}
{{- end -}}

{{/*

All the above is subject to a race condition: if Flux checks the status too early
it concludes, because CAPI resources aren't fully kstatus compliant, that the resource is ready

Waiting for the cluster kubeconfig Secret is a workaround

*/}}

    - apiVersion: v1
      kind: Secret
      name: {{ $cluster.name }}-kubeconfig
      namespace: {{ $ns }}

{{ if .sleep_job }}
    - apiVersion: batch/v1
      kind: Job
      name: dummy-deps-cluster-ready-sleep
      namespace: {{ $ns }}
{{ end }}

{{ end -}}

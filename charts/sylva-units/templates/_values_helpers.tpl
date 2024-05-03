{{/*
Ensure that no_proxy covers everything that we need by adding the values defined in no_proxy_base.
(Default values will be add only if the user set at least one of no_proxy or no_proxy_additional field) 
*/}}
{{- define "sylva-units.no_proxy" -}}
  {{- $envAll := index . 0 -}}

  {{/* this function accepts an optional second parameter to override entries from no_proxy_additional) */}}
  {{- $overrides := dict -}}
  {{- if gt (len .) 1 -}}
      {{- $overrides = index . 1 -}}
  {{- end -}}

  {{/* we start building the list of no_proxy items, accumulating them in $no_proxy_list... */}}
  {{- $no_proxy_list := concat $envAll.Values.cluster.cluster_pods_cidrs $envAll.Values.cluster.cluster_services_cidrs -}}
  {{- if $envAll.Values.cluster.capm3 -}}
    {{- if $envAll.Values.cluster.capm3.primary_pool_network -}}
      {{- $no_proxy_list = append $no_proxy_list (printf "%s/%s" $envAll.Values.cluster.capm3.primary_pool_network $envAll.Values.cluster.capm3.primary_pool_prefix) -}}
    {{- end -}}
    {{- if $envAll.Values.cluster.capm3.provisioning_pool_network -}}
      {{- $no_proxy_list = append $no_proxy_list (printf "%s/%s" $envAll.Values.cluster.capm3.provisioning_pool_network $envAll.Values.cluster.capm3.provisioning_pool_prefix) -}}
    {{- end -}}
    {{- range $envAll.Values.cluster.baremetal_hosts -}}
      {{- $bmc_mgmt := urlParse (tuple $envAll .bmh_spec.bmc.address | include "interpret-as-string") -}}
      {{- $no_proxy_list = append $no_proxy_list ($bmc_mgmt.host | splitList ":" | first) -}}
    {{- end -}}
  {{- end -}}

  {{- $no_proxy_list = concat $no_proxy_list (splitList "," $envAll.Values.proxies.no_proxy) -}}

  {{/* we merge 'no_proxy_additional_rendered' with 'overrides'
       note well that we do this after *interpreting* any go templating
  */}}
  {{- $no_proxy_additional_rendered := dict -}}
  {{- range $no_proxy_item,$val := $envAll.Values.no_proxy_additional -}}
    {{- $_ := set $no_proxy_additional_rendered (tuple $envAll $no_proxy_item | include "interpret-as-string") $val -}}
  {{- end -}}
  {{- range $no_proxy_item,$val := $overrides -}}
    {{- $_ := set $no_proxy_additional_rendered (tuple $envAll $no_proxy_item | include "interpret-as-string") $val -}}
  {{- end -}}

  {{/* we add to the list the no_proxy items that are enabled
       and remove the disabled ones
  */}}
  {{- range $no_proxy_item, $val := $no_proxy_additional_rendered -}}
    {{- if $val -}}
      {{- $no_proxy_list = append $no_proxy_list $no_proxy_item -}}
    {{- else -}}
      {{- $no_proxy_list = without $no_proxy_list $no_proxy_item -}}
    {{- end -}}
  {{- end -}}

  {{/* render final list */}}
  {{- without $no_proxy_list "" | uniq | join "," -}}
{{- end -}}

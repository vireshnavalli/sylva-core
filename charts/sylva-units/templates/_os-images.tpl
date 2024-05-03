{{- define "generate-os-images" -}}
osImages:
{{- $sylva_dib_images := .Values.sylva_diskimagebuilder_images }}
{{- $sylva_dib_version := .Values.sylva_diskimagebuilder_version }}
{{- $sylva_base_oci_registry := (tuple . .Values.sylva_base_oci_registry | include "interpret-as-string") }}
{{- if (.Values.os_images) }}
  {{- range $os_image_name, $os_image_props := .Values.os_images }}
  {{ $os_image_name }}:
    {{- range $prop_key, $prop_value := $os_image_props }}
    {{ $prop_key }}: {{ $prop_value | quote }}
    {{- end }}
  {{- end }}
  {{- range $os_image_name, $os_image_props := $sylva_dib_images }}
    {{- if ($os_image_props.enabled) }}
  {{ $os_image_name }}:
    uri: {{ $sylva_base_oci_registry }}/sylva-elements/diskimage-builder/{{ $os_image_name }}:{{ $sylva_dib_version }}
    {{- end }}
  {{- end }}
{{- else }}
  {{- range $os_image_name, $os_image_props := $sylva_dib_images }}
    {{- if (or ($os_image_props.enabled) ($os_image_props.default_enabled)) }}
  {{ $os_image_name }}:
    uri: {{ $sylva_base_oci_registry }}/sylva-elements/diskimage-builder/{{ $os_image_name }}:{{ $sylva_dib_version }}
    {{- end }}
  {{- end }}
{{- end }}
{{- end }}

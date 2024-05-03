{{/*

This template interprets sylva-units values and dumps the result.

It is an helper to ease the elaboration of gotpl expression in sylva-unit values.

You can simply run it (from sylva-core base directory) using following command:

    helm template interpret charts/sylva-units --show-only templates/extras/interpreted-values.tpl

You can provide extra values files using the --values flag, to ovverride the
chart default values. If you intent to elaborate a specific expression, you
can also use the third_party value that is not validated by schema.

For example you can define the following file that defines various gotpl expressions:

cat <<EOF > values.sanbox.yaml
third_party:
  condition: true
  set_list_only_if:
    - one
    - '{{ tuple "two" .Values.third_party.condition | include "set-only-if" }}'
  some_dict:
    one: two
  derived:
    value: '{{ .Values.third_party.some_dict | include "preserve-type" }}'
  inline_template: >-
    {{- if .Values.third_party.some_dict }}
    {{- .Values.third_party.some_dict | include "preserve-type" }}
    {{- end }}
EOF

And check how these expressions renders using the following command

    helm template interpret charts/sylva-units --show-only templates/extras/interpreted-values.tpl --values values.sanbox.yaml | yq .third_party

*/}}
{{- if (eq .Release.Name "interpret") -}}
{{ include "interpret-values-gotpl" . | fromJson | toYaml }}
{{- end }}

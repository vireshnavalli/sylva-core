GET https://{{vault_url}}/v1/secret/data/harbor
X-Vault-Token: {{token}}
HTTP 200
[Captures]
password_harbor: jsonpath "$.data.data.password"

GET https://{{harbor_url}}/service/token?service=harbor-registry
[BasicAuth]
admin: {{password_harbor}}
HTTP 200

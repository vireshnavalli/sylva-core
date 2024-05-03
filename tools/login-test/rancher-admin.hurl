GET https://{{vault_url}}/v1/secret/data/rancher
X-Vault-Token: {{token}}
HTTP 200
[Captures]
password_rancher: jsonpath "$.data.data.bootstrapPassword"

POST https://{{rancher_url}}/v3-public/localProviders/local?action=login
{"username":"admin",
"password":"{{password_rancher}}",
"ttl":100}
HTTP 201

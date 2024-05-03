GET https://{{vault_url}}/v1/secret/data/sso-account
X-Vault-Token: {{token}}
HTTP 200
[Captures]
password_sso: jsonpath "$.data.data.password"
user_sso:  jsonpath "$.data.data.login"

POST https://{{keycloak_url}}/realms/sylva/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded
[FormParams]
username: {{user_sso}}
password: {{password_sso}}
grant_type: password
client_id: admin-cli
HTTP 200

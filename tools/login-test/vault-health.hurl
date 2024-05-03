GET https://{{vault_url}}/v1/sys/health
HTTP 200
Content-Type: application/json
[Asserts]
jsonpath "$.initialized" == true
jsonpath "$.sealed" == false

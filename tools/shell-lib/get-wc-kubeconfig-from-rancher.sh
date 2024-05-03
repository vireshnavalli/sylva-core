#!/bin/bash

# Get workload cluster kubeconfig from Rancher API
# parameter: workload cluster name

set -eu

WORKLOAD_CLUSTER_NAME=$1

echo >&2 "-- Retrieving kubeconfig for cluster $WORKLOAD_CLUSTER_NAME from Rancher API"

RANCHER_URL=$(kubectl get ingress -n cattle-system rancher -o jsonpath='{ .spec.tls[].hosts[] }')
echo >&2 "RANCHER_URL = $RANCHER_URL"
BOOTSTRAP_PASSWORD=$(kubectl -n cattle-system get secret bootstrap-secret -o jsonpath='{.data.bootstrapPassword}' | base64 -d)
TOKEN=$(curl --insecure -s https://$RANCHER_URL/v3-public/localProviders/local?action=login -H 'content-type: application/json' --data-binary '{"username":"admin","password":"'$BOOTSTRAP_PASSWORD'","ttl":60000}' | yq eval .token -)
KUBECONFIG_URL=$(curl --insecure -s https://$RANCHER_URL/v3/clusters/  -H "Authorization: Bearer $TOKEN" | yq eval '.data[] | select (.name=="'$WORKLOAD_CLUSTER_NAME-capi'") | .actions.generateKubeconfig' - | tr -d '"')

curl --insecure -s -X POST $KUBECONFIG_URL -H "Authorization: Bearer $TOKEN" | yq eval .config -

#!/bin/bash

set -e
set -o pipefail

echo "Initiate ConfigMap manifest file"

configmap_file=/tmp/os-image-details.yaml

cat <<EOF >> $configmap_file
apiVersion: v1
kind: ConfigMap
metadata:
  name: ${OUTPUT_CONFIGMAP}
  namespace: ${TARGET_NAMESPACE}
  labels:
    sylva.os-images-info: ""
data:
  values.yaml: |
    osImages:
EOF

echo "Looping over OS images..."

yq '.osImages | keys | .[]' /opt/images.yaml | while read os_image_key; do
  echo "-- processing image $os_image_key"
  export os_image_key
  echo "      $os_image_key:" >> $configmap_file
  # Check if the artifact is a Sylva diskimage-builder artifact
  uri=$(yq '.osImages.[env(os_image_key)].uri' /opt/images.yaml)
  if [[ "$uri" == *"sylva-elements/diskimage-builder"* ]]; then
    echo "This is a Sylva diskimage-builder image. Updating image details from artifact at $uri"
    url=$(echo $uri| sed 's|oci://||')
    # Get artifact annotations and insert them as image details
    insecure=$([[ $oci_registry_insecure == "true" ]] && echo "--insecure" || true)
    manifest=$(oras manifest fetch $url $insecure)
    echo $manifest | yq '.annotations |with_entries(select(.key|contains("sylva")))' -P | sed "s|.*/|        |" >> $configmap_file
  fi
  echo "Adding user provided details"
  yq '.osImages.[env(os_image_key)]' /opt/images.yaml | sed 's/^/        /' >> $configmap_file
  echo ---
done

# Duplicate values to support both os_images and osImages
yq -i '(.data."values.yaml" | fromyaml) as $values | .data."values-s-c-c.yaml" = ({"os_images":$values.osImages} | toyaml)' $configmap_file

# Update configmap
echo "Updating ${OUTPUT_CONFIGMAP} configmap"
# Unset proxy settings, if any were needed for oras tool, before connecting to local bootstrap cluster
unset https_proxy
kubectl apply -f $configmap_file

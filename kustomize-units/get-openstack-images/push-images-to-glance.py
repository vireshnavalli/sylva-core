#!/usr/bin/env python
#
# This script can be tested with:
#
#   OS_IMAGES_INFO_PATH=my-os-images.info.yaml OS_CLOUD=falcon kustomize-units/get-openstack-images/push-images-to-glance.py
#
# With my-os-images.info.yaml having content similar as the one produced by the os-images-info unit:
#
#   kubectl get configmap os-images-info -o yaml | yq '.data."values.yaml"' > my-os-images.info.yaml


from kubernetes import client, config
from kubernetes.client.rest import ApiException
import openstack
import oras.client
import oras.provider
import logging
import os
import shutil
import tarfile
import gzip
import sys
import yaml

from distutils.util import strtobool

class MyProvider(oras.provider.Registry):
    def pull_image(self, artifact_uri):
        try:
            res = self.pull(target=artifact_uri)
            if len(res) > 1:
                raise ValueError("Expected only one file, but multiple files were found.")
                sys.exit(1)
            return res[0]
        except Exception as e:
            logger.error(f"upsie... {e}")
            return None

def cleanup_image(file_path):
    parent_dir = os.path.dirname(file_path)
    # Check if the file path exists and is a directory
    if os.path.exists(parent_dir) and os.path.isdir(parent_dir):
        shutil.rmtree(parent_dir)
        return f"Directory '{parent_dir}' has been removed."
    else:
        return f"The path '{file_path}' does not exist or is not a directory."

def unzip_artifact(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        logger.warning(f"The file '{file_path}' does not exist.")
        return None
    # Determine the extraction path
    extraction_path = os.path.dirname(file_path)
    # Extract the tar.gz file
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path=extraction_path)
        logger.info(f"Extracted '{file_path}' to '{extraction_path}'.")

    # Initialize a variable to hold the path of a non-gzipped file, if found
    non_gz_file_path = None

    # Find and gunzip the .gz file or identify .raw/.qcow file
    for root, dirs, files in os.walk(extraction_path):
        for file in files:
            if file.endswith(".gz"):
                gz_file = os.path.join(root, file)
                extracted_file_path = gz_file[:-3]  # Removes the .gz extension
                with gzip.open(gz_file, 'rb') as f_in, open(extracted_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    logger.info(f"Gunzipped '{gz_file}' to '{extracted_file_path}'")
                return extracted_file_path
            elif file.endswith(".raw") or file.endswith(".qcow2"):
                # Store the path but do not return immediately to prioritize .gz extraction
                # If no .gz file found but a .raw or .qcow file was found, return its path
                non_gz_file_path = os.path.join(root, file)
                logger.info(f"Found non-gzipped file '{non_gz_file_path}'.")
                return non_gz_file_path

    # If no .gz, .raw, or .qcow file found, return None
    logger.info(f"no .gz, .raw, or .qcow file found: {', '.join([f[0] for f in os.walk(extraction_path)])}")
    return None


def image_exists_in_glance(checksum, _image_name):
    try:
        matching_images = [image for image in conn.image.images(tags=[f"sylva-md5-{checksum}"]) if image.properties is not None and image.get('checksum') == checksum]
        if _image_name in [i['name'] for i in matching_images]:
            logger.warning(f"Image with name '{_image_name}' already exists.")
        return matching_images
    except Exception as e:
        logger.warning(f"Following exception occurred: {e}")
        return None


def push_image_to_glance(file, manifest, image_name, image_format):
    # Create an image resource without custom properties
    with open(file, 'rb') as image_data:
        try:
            _checksum = manifest['md5']
            logger.info(f"{image_name}: creating image")
            image = conn.image.create_image(
                name=image_name,
                data=image_data,
                disk_format=image_format,
                md5=_checksum,
                allow_duplicates=True
            )
            logger.info(f"  Image UUID: {image.id}")

            # Update the image with custom properties
            logger.info(f"  Updating image properties on image...")
            image_properties = {f"sylva/{k}": v for k, v in manifest.items()}

            logger.info(f"  {image_properties}")
            updated_image = conn.image.update_image(
                image.id,
                properties=image_properties,
            )
            tag = f"sylva-md5-{_checksum}"
            logger.info(f"  Tagging image with {tag}...")
            conn.image.add_tag(image.id, tag)
            return updated_image
        except Exception as e:
            logger.error(f"upsie... {e}")
            raise

# Set namspace var
NAMESPACE = os.environ.get('TARGET_NAMESPACE')
# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s')
logger = logging.getLogger(__name__)

# Create empty configmap
configmap = {}

##############################
# Parse the YAML string resulted from loading the contents of the ConfigMap/os-images-info-xxxx  (produced by the os-images-info unit)
os_images_info_path = os.environ.get("OS_IMAGES_INFO_PATH", '/opt/config/os-images-info.yaml')
with open(os_images_info_path, 'r') as file:
    os_images = yaml.safe_load(file.read())
os_images = os_images['osImages']
logger.info(f"os_images: {os_images}")

##############################

# Initialize openstack connection
try:
  cloud_name = os.environ.get("OS_CLOUD","capo_cloud")  # 'capo-cloud' is the cloud name we hardcode for CAPO in Sylva
except KeyError:
  raise Exception("no OS_CLOUD environment variable specified")
conn = openstack.connect(cloud=cloud_name, verify=False)

# Initialize oras class
insecure_tls = strtobool(os.environ.get('ORAS_INSECURE_CLIENT','false'))
oras_client = MyProvider(tls_verify=not insecure_tls)

for os_name, os_image_info in os_images.items():
    artifact = os_image_info["uri"]
    md5_checksum = os_image_info['md5']
    image_format = os_image_info['image-format']
    logger.info(f"Working on image: {os_name} with MD5 checksum {md5_checksum}")
    is_image_in_glance = image_exists_in_glance(md5_checksum,os_name)
    if not is_image_in_glance:
        logger.info(f"image not in Glance: {os_name} / md5 {md5_checksum}" )
        logger.info(f"Pulling image: {os_name} from artifact uri: {artifact}")
        oras_pull_path = oras_client.pull_image(artifact)

        logger.info(f"Unzipping artifact...")
        unzipped_image = unzip_artifact(oras_pull_path)

        try:
            logger.info("Pushing image to Glance...")
            image = push_image_to_glance(unzipped_image, os_image_info, os_name, image_format)
            logger.info(f"Image pushed to glance with image ID {image['id']}")
            logger.info(f"Cleaning up files")
            cleanup_image(oras_pull_path)
        except Exception as e:
            logger.warning(f"{e}")
            pass

        logger.info("Updating configmap")
        configmap.update({os_name: {'openstack_glance_uuid': image['id']}})
    else:
        logger.info('\n'.join([f"Image already in glance: Name: {image.name}, UUID: {image.id}, OS Name: {os_name}" for image in is_image_in_glance if image.get('checksum') == md5_checksum])) # add image name in manifest without tag and get it from there if needed.
        configmap.update({os_name: {'openstack_glance_uuid': is_image_in_glance[0]['id']}})
    logger.info(f"Finished processing image: {os_name}")

logger.info(f"Images UUID map:\n {configmap}")

logger.info(f"Pushing ConfigMap to Kubernetes...")

# Initialize Kube config
# Load Kubernetes configuration
try:
    config.load_incluster_config()
except:  # this is meant to allow testing this script manually out of a pod, assuming that KUBECONFIG points to your kubeconfig
    config.load_kube_config()
api_instance = client.CoreV1Api()

# Define the metadata for the ConfigMap
metadata = client.V1ObjectMeta(
    name="openstack-images-uuids",
    namespace=NAMESPACE
)

# Convert configmap to yaml-formatted string
yaml_string = yaml.dump({'os_images': configmap}, default_flow_style=False)  # os_images is the key expected for sylva-capi-cluster chart values

# Create a ConfigMap object
body = client.V1ConfigMap(
    api_version="v1",
    kind="ConfigMap",
    metadata=metadata,
    data={'values.yaml': yaml_string}
)

def create_or_update_configmap(api_instance, namespace, body):
    try:
        # Check if the ConfigMap exists
        api_instance.read_namespaced_config_map(name=body.metadata.name, namespace=namespace)
        # If exists, update the ConfigMap
        api_response = api_instance.replace_namespaced_config_map(name=body.metadata.name, namespace=namespace, body=body)
        logger.info(f"ConfigMap updated. Name: {api_response.metadata.name}")
    except ApiException as e:
        if e.status == 404:
            # If not exists, create the ConfigMap
            api_response = api_instance.create_namespaced_config_map(namespace=namespace, body=body)
            logger.info(f"ConfigMap created. Name: {api_response.metadata.name}")
        else:
            # Handle other exceptions
            logger.error(f"Exception occurred: {e}")
            raise

# Create the ConfigMap in the specified namespace
try:
    create_or_update_configmap(api_instance, NAMESPACE, body)
except Exception as e:
    logger.error(f"upsie.. : {e}")
    raise

logger.info(f"We're done")

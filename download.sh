#!/bin/bash

DATA_DIR=data
YAML_DIR=config

set -x
# Download and process each config file
ls -1 ${YAML_DIR} | sed -r 's/\.yaml//' | xargs -I {} swarmpal batch ${YAML_DIR}/{}.yaml ${DATA_DIR}/{}.nc4

# Update the registry
md5sum ${DATA_DIR}/*.nc4 | sed -r "s/([a-z0-9]+)\ \ (.*)/\2 md5:\1/" > registry.txt

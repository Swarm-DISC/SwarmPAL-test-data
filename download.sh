#!/bin/bash

DATA_DIR=data
YAML_DIR=config

# Download and process each config file
if [ $# -eq 0 ]; then
	ls -1 ${YAML_DIR} | sed -r 's/\.yaml//' | xargs -I {} swarmpal batch ${YAML_DIR}/{}.yaml ${DATA_DIR}/{}.nc4
else
	while [ $# -gt 0 ]; do
		out=$(echo $1 | sed -e "s/\.yaml/.nc4/; s/${YAML_DIR}/${DATA_DIR}/")
		swarmpal batch $1 $out
		shift;
	done
fi


# Update the registry
md5sum ${DATA_DIR}/*.nc4 | sed -r "s/([a-z0-9]+)\ \ (.*)/\2 md5:\1/" > registry.txt
md5sum ${YAML_DIR}/*.yaml | sed -r "s/([a-z0-9]+)\ \ (.*)/\2 md5:\1/" >> registry.txt

echo "Update md5 sum for registry.txt in SwarmPAL/tests/test_data.py to:"
echo -n "md5:"
md5sum registry.txt | cut -f 1 -d ' '

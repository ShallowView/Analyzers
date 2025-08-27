#!/bin/bash

#shellcheck source=dockerUtils.sh
source "bin/dockerUtils.sh"
#shellcheck source=config.sh
source "bin/config.sh"

# ---
sector=${1-"analysis"}
mode=${2-"prod"}

echo "$sector"

if [[ $sector != "analysis" && $sector != "preprocess" ]]; then
	echo "No such sector $sector;"
	exit 3
fi

# ---
stop $DOCKER_CONTAINER_NAME

removeImage $DOCKER_IMAGE_REFERENCE
buildImage $DOCKER_IMAGE_REFERENCE "bin/$1/$DOCKER_FILE" .

createVolumes $DOCKER_OUTPUT_VOLUME_NAME

createContainer $DOCKER_CONTAINER_NAME $DOCKER_IMAGE_REFERENCE "$mode" \
	-v $DOCKER_OUTPUT_VOLUME_NAME:/usr/src/preprocess/out
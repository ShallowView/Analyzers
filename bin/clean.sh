#!/bin/bash

#shellcheck source=dockerUtils.sh
source "bin/dockerUtils.sh"
#shellcheck source=config.sh
source "bin/config.sh"

# ---
clean $DOCKER_CONTAINER_NAME $DOCKER_OUTPUT_VOLUME_NAME
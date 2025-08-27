#!/bin/bash

isContainerExist(){
	docker container inspect "$1" &>/dev/null
	return
}
isNetworkExist(){
	docker network inspect "$1" &>/dev/null
	return
}
isVolumeExist(){
	docker volume inspect "$1" 	&>/dev/null
	return
}

buildImage(){
	image=$1
	file=$2
	dir=$3

	removeImage "$image"

	echo "# BUILDING IMAGE ($image)"
	docker build -t "$image" -f "$file" \
		--progress=plain \
		"$dir"
}
createContainer(){
	container=$1
	image=$2
	debug=$([[ $3 == "debug" ]] && echo 1 || echo 2)
	args=()

	for i in $(seq 4 $#); do
		args+=("${!i}")
	done

	echo "# RUNNING CONTAINER ($container; With image $image)"
	if ! isContainerExist "$container"; then
		docker run "${args[@]}" \
			"$([[ $debug == 1 ]] && echo "-it" || echo "-d")" \
			--name "$container" --rm "$image"
	else
		echo "$container container already exist."
	fi
}

createNetwork(){
	network=$1
	subnet=$2
	gateway=$3

	echo "# CREATING NETWORK ($network)"
	if ! isNetworkExist "$network"; then
		docker network create \
			--subnet "$subnet" --gateway "$gateway" \
			--ipv6=false \
			"$network"
	else
		echo "$network network already exist."
	fi
}
createVolumes(){
	volumes=("${@}")

	echo "${volumes[@]}"

	echo "# CREATING VOLUMES (${volumes[*]})"
	for v in "${volumes[@]}"; do
		if ! isVolumeExist "$v"; then
			docker volume create "$v"
		else
			echo "$v volume already exist."
		fi
	done
}

stop(){
	container=$1

	echo "# STOPPING CONTAINER ($container)"
	if isContainerExist "$container"; then
		docker container stop "$container"
	else
		echo "$container wasn't started."
	fi
}

removeImage(){
	image=$1

	echo "# DELETING OLD IMAGE ($image)"
	docker image rm -f "$image"
}
clean(){
	container=$1
	volumes=()

	for i in $(seq 2 $#); do
		volumes+=("${!i}")
	done

	stop "$container"

	echo "# DELETING CONTAINER VOLUMES ($DOCKER_CONTAINER_NAME)"
	docker volume rm -f "${volumes[@]}"
}
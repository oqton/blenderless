#!/bin/bash

set -ex

IMAGE=blender-builder

BLENDER_VERSION_MAJOR=2
BLENDER_VERSION_MINOR=92
BLENDER_VERSION_PATCH=0
BLENDER_VERSION=$BLENDER_VERSION_MAJOR.$BLENDER_VERSION_MINOR.$BLENDER_VERSION_PATCH
PYTHON_VERSION=3.8

docker_build_args=(
    --build-arg BLENDER_VERSION_MAJOR=$BLENDER_VERSION_MAJOR
    --build-arg BLENDER_VERSION_MINOR=$BLENDER_VERSION_MINOR
    --build-arg BLENDER_VERSION_PATCH=$BLENDER_VERSION_PATCH
    --build-arg PYTHON_VERSION=$PYTHON_VERSION
)

docker build ${docker_build_args[@]} -t ${IMAGE} .
docker run -it --rm -v$(pwd):/output ${IMAGE} bash -c "cp /blender_ws/bpy-$BLENDER_VERSION-python$PYTHON_VERSION-x86_64-linux-gnu.tar.zst /output/"

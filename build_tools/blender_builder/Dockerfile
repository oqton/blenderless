FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y build-essential git subversion cmake libx11-dev libxxf86vm-dev libxcursor-dev libxi-dev libxrandr-dev libxinerama-dev libegl-dev

RUN mkdir /blender_ws

WORKDIR /blender_ws

ARG BLENDER_VERSION_MAJOR=2
ARG BLENDER_VERSION_MINOR=92
ARG BLENDER_VERSION_PATCH=0
ARG BLENDER_VERSION=$BLENDER_VERSION_MAJOR.$BLENDER_VERSION_MINOR.$BLENDER_VERSION_PATCH

RUN git clone --branch v$BLENDER_VERSION --depth 1 https://github.com/blender/blender.git \
    && cd blender \
    && git submodule update --init --recursive

RUN mkdir lib \
    && cd lib \
    && svn checkout https://svn.blender.org/svnroot/bf-blender/tags/blender-$BLENDER_VERSION_MAJOR.$BLENDER_VERSION_MINOR-release/lib/linux_centos7_x86_64

ARG PYTHON_VERSION=3.8

RUN apt-get install -y \
        ninja-build \
        libpython$PYTHON_VERSION-dev \
        python$PYTHON_VERSION \
        zstd

RUN mkdir build \
    && cd build \
    && cmake -C ../blender/build_files/cmake/config/bpy_module.cmake \
        -DWITH_HEADLESS=ON \
        -DWITH_INSTALL_PORTABLE=ON \
        -DPYTHON_INCLUDE_DIR=/usr/include/python$PYTHON_VERSION \
        -DPYTHON_LIBRARY=/usr/lib/python$PYTHON_VERSION/config-$PYTHON_VERSION-x86_64-linux-gnu/libpython$PYTHON_VERSION-pic.a \
        -DCMAKE_INSTALL_PREFIX=/blender_ws/install \
        -G Ninja ../blender \
    && ninja -j12

RUN cd build && ninja install

RUN tar --zstd -cf bpy-$BLENDER_VERSION-headless-python$PYTHON_VERSION-x86_64-linux-gnu.tar.zst install/

RUN cd install && python$PYTHON_VERSION -c "import bpy"

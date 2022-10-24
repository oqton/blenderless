""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "853c163881bbaf7c20e70f6df7a52a8e1ab0320be751d8986dbf649fd0e12a09",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-2.92.0-python3.8/bpy-2.92.0-headless-python3.8-x86_64-linux-gnu-39bef315.tar.zst",
    )

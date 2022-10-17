""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "837dce978427a1b496d0c536f9365e88446eeb0faa3480d62a6f2f4c99c31cfd",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-2.92.0-python3.8/bpy-2.92.0-headless-python3.8-x86_64-linux-gnu.tar.zst",
    )

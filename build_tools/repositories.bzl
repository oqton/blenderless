""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "a21124c640bc65b0cff0b17e8d23ad7b7e943a77df802a5f3d643ebf2ab7bc05",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-3.3.6-python3.10/bpy-3.3.6-headless-python3.10-x86_64-linux-gnu.tar.zst",
    )

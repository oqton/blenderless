""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "53c76a81fa47b4f6f62f5c762b13d15095be02634bf926f8020b98d5edd99ce2",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-2.92.0-python3.8/bpy-2.92.0-python3.8-x86_64-linux-gnu.tar.zst",
    )

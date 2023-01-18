""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "90dd048a90bcdc5a026ba9856a96722c0378de0e34fbd97ef1043658369820fe",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-3.4.1-python3.10/bpy-3.4.1-headless-python3.10-x86_64-linux-gnu.tar.zst",
    )

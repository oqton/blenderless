""" Defines blenderless dependencies.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def blenderless_repositories():
    http_archive(
        name = "bpy",
        build_file = "@blenderless//build_tools:bpy.BUILD.bazel",
        sha256 = "2094a2dac279a393f6096ebad7c45ea6abf50b27e4ea869cf1a9cd242a70b483",
        strip_prefix = "install",
        url = "https://github.com/oqton/blenderless/releases/download/bpy-3.3.1-python3.10/bpy-3.3.1-headless-python3.10-x86_64-linux-gnu.tar.zst",
    )

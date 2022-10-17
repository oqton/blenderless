load("//build_tools:expand_template.bzl", "expand_template")
load("@pip_deps//:requirements.bzl", "requirement")
load("@rules_python//python:defs.bzl", "py_test")

def py_pytest_tests(name, **kwargs):
    """Adds a py_test with a pytest runner.

    Args:
        name: A unique target name.
        **kwargs: https://docs.bazel.build/versions/main/be/python.html#py_test
    """
    srcs = kwargs.pop("srcs", [])
    deps = kwargs.pop("deps", [])

    src_paths = ["$(rootpath {})".format(s) for s in srcs]

    runner = name + "_runner.py"
    expand_template(
        name = name + "_runner_generator",
        template = "//build_tools:pytest_runner.py.tpl",
        out = runner,
        substitutions = {"{args}": ", ".join(["'{}'".format(arg) for arg in src_paths])},
        data = srcs,
    )

    py_test(
        name = name,
        srcs = [runner] + srcs,
        main = runner,
        deps = [requirement("pytest")] + deps,
        **kwargs
    )

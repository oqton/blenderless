import logging

from IPython.display import Image, display

logger = logging.getLogger()


def notebook_preview(f):
    """Function decorator in order to preview an image in a IPython context."""

    def preview_wrapper(*args, **kwargs):
        path = f(*args, **kwargs)
        if in_ipynb():
            display(Image(str(path)))
        return path

    return preview_wrapper


def in_ipynb():
    """Determine if the code is run within an IPython context."""
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        return False

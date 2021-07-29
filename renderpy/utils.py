import logging

logger = logging.getLogger()


def notebook_preview(f):

    def preview_wrapper(*args, **kwargs):
        path = f(*args, **kwargs)
        if in_ipynb():
            import matplotlib.image as mpimg
            import matplotlib.pyplot as plt
            img = mpimg.imread(str(path))
            plt.imshow(img)
            plt.axis('off')
        return path

    return preview_wrapper


def in_ipynb():
    try:
        cfg = get_ipython().config
        return 'jupyter' in cfg['IPKernelApp']['connection_file'].lower()
    except NameError:
        return False

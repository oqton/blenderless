# Blenderless

Blenderless is the Python package for easy headless rendering using Blender.

## How to use this

### Python module

Create image from mesh:

```python
import blenderless
path_to_foo_png = blenderless.render('foo.stl')
```

### CLI

render geometry to image

```sh
blenderless image foo.stl
```

render geometry to gif

```sh
blenderless gif foo.stl
```

render config to image

```sh
blenderless config scene.yml
```

## Install

```buildoutcfg
sudo apt-get install xvfb
pipx install poetry==1.1.5
make .venv
```

### Testing

```sh
make test
```

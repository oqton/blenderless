# Blenderless

Blenderless is the Python package for easy headless rendering using Blender.


## Getting Started

Create image from mesh:

```python
import blenderless
path_to_foo_png = blenderless.render('foo.stl')
```

### Installing

Install blenderless
```buildoutcfg
sudo apt-get install xvfb pipx
pipx install poetry==1.1.5
make .venv
```

### Running the tests

```sh
make test
```

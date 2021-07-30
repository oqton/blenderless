import logging
import pathlib

import click
from tqdm import tqdm

import blenderless

l = logging.getLogger(__name__)


@click.group()
@click.option('--verbose/--no-verbose', '-v', default=False, help="Verbose output")
def cli(verbose):
    """rendering geometries from the cli using blender"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(processName)s %(message)s')
    logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))


@cli.command()
@click.argument("file_path", required=True, type=str)
@click.argument("root", default=".", required=False, type=str)
def image(file_path, root):
    """Render geometries to image"""
    geometry_files = list(pathlib.Path(root).glob(file_path))
    l.info(f'found {len(geometry_files)} geometry files')
    for geometry_file in tqdm(geometry_files):
        l.debug(f'render: {geometry_file}')
        blenderless.render(geometry_file, geometry_file.parent / f'{geometry_file.stem}.png')
        l.debug(f'render successful')


@cli.command()
@click.argument("file_path", required=True, type=str)
@click.argument("root", default=".", required=False, type=str)
def gif(file_path, root):
    """Render geometries to gif"""
    geometry_files = list(pathlib.Path(root).glob(file_path))
    l.info(f'found {len(geometry_files)} geometry files')
    for geometry_file in tqdm(geometry_files):
        l.debug(f'render: {geometry_file}')
        blenderless.gif(geometry_file, geometry_file.parent / f'{geometry_file.stem}.gif')
        l.debug(f'render successful')


@cli.command()
@click.argument("config_path", required=True, type=click.Path(exists=True))
@click.argument("output_file", default="render.png", required=False, type=str)
def config(config_path, output_file):
    """Render scene from config file"""
    scene = blenderless.Scene.from_config(config_path)
    scene.render(output_file)
    l.debug(f'render successful')

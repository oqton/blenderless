import json
import logging
import pathlib

import click

from blenderless import Blenderless

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose/--no-verbose', '-v', default=False, help="Verbose output")
@click.option('--export-blend-path', '-b', default=None, help="Path to export the generated .blend file to")
def main(verbose, export_blend_path):
    """Rendering geometries from the cli using blender"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(processName)s %(message)s')
    logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName(logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

    Blenderless.export_blend_path = pathlib.Path(export_blend_path) if export_blend_path else None
    if export_blend_path:
        logging.info(f'Generated .blend file will be exported to: {export_blend_path}')


@main.command()
@click.argument("file_path", required=True, type=str)
@click.argument("root", default=".", required=False, type=str)
def image(file_path, root):
    """Render geometries to image"""
    geometry_files = list(pathlib.Path(root).glob(file_path))
    logger.info(f'found {len(geometry_files)} geometry files')
    for geometry_file in geometry_files:
        logger.debug(f'render: {geometry_file}')
        Blenderless.render(geometry_file, geometry_file.parent / f'{geometry_file.stem}.png')
        logger.info((geometry_file.parent / f'{geometry_file.stem}.png').absolute())
        logger.debug('render successful')


@main.command()
@click.argument("file_path", required=True, type=str)
@click.argument("root", default=".", required=False, type=str)
def gif(file_path, root):
    """Render geometries to gif"""
    geometry_files = list(pathlib.Path(root).glob(file_path))
    logger.info(f'found {len(geometry_files)} geometry files')
    for geometry_file in geometry_files:
        logger.debug(f'render: {geometry_file}')
        Blenderless.gif(geometry_file, geometry_file.parent / f'{geometry_file.stem}.gif')
        logger.debug('render successful')


@main.command()
@click.argument("config_path", required=True, type=click.Path(exists=True))
@click.argument("output_path", default=".", required=False, type=str)
def config(config_path, output_path):
    """Render scene from config file"""
    output_path = pathlib.Path(output_path)
    render_paths = Blenderless.render_from_config(pathlib.Path(config_path), output_path)
    metadata = {}
    metadata['render_paths'] = [str(path.absolute()) for path in render_paths]
    with (output_path / 'meta.json').open("w") as f:
        json.dump(metadata, f)
    logger.info(json.dumps(metadata, indent=1))
    logger.debug('render successful')


if __name__ == '__main__':
    main()

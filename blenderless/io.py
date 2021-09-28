import abc
from pathlib import Path

import trimesh


class FileHandler():

    @abc.abstractstaticmethod
    def load(path: Path) -> trimesh.Trimesh:
        pass


class DracoFileHandler(FileHandler):

    @staticmethod
    def load(path: Path) -> trimesh.Trimesh:
        return trimesh.load(path)


class TrimeshFileHandler(FileHandler):

    @staticmethod
    def load(path: Path) -> trimesh.Trimesh:
        return trimesh.load(path)


class FileHandlerFactory():

    _loaders = {'.drc': DracoFileHandler}

    @classmethod
    def get_loader(cls, path: Path):
        if isinstance(path, str):
            path = Path(path)

        suffix = path.suffix

        return cls._loaders.get(suffix, TrimeshFileHandler)

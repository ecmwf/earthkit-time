import enum
import os
import pathlib
from importlib import resources
from typing import Optional, TextIO, Tuple

import yaml

PACKAGE = "earthkit.time.data"


def _extract_package(path: str) -> Tuple[str, str]:
    res = pathlib.PurePosixPath(path)
    parts = list(res.parts)
    if len(parts) == 1:
        return PACKAGE, parts[0]
    return (PACKAGE + "." + ".".join(parts[:-1])), parts[-1]


def _is_resource(package: resources.Package, name: str) -> bool:
    if hasattr(resources, "files"):  # Python >= 3.9
        return resources.files(package).joinpath(name).is_file()
    else:
        return resources.is_resource(package, name)


def _open_text(
    package: resources.Package,
    resource: resources.Resource,
    encoding: str = "utf-8",
    errors: str = "strict",
) -> TextIO:
    if hasattr(resources, "files"):  # Python >= 3.9
        return (
            resources.files(package)
            .joinpath(resource)
            .open("r", encoding=encoding, errors=errors)
        )
    else:
        return resources.open_text(package, resource, encoding, errors)


class ResourceType(enum.Enum):
    NOTFOUND = enum.auto()
    FILE = enum.auto()
    PACKAGED = enum.auto()


def find_resource(
    name: str,
    path: Optional[str] = None,
    env_file: Optional[str] = None,
    env_path: Optional[str] = None,
) -> Tuple[ResourceType, str]:
    """Find a given resource file using various methods

    The search order is: ``path``, ``env_file``, `env_path``, packaged date.

    Parameters
    ----------
    name: str
        Resource file name
    path: str or None
        Candidate path to the resource
    env_file: str or None
        Environment variable to check for a path to the file
    env_path: str or None
        Environment variable to check for a set of directories

    Returns
    -------
    ResourceType
        Whether the resource has been found, and where
    str
        Path to the resource, if found
    """

    if path is not None:
        if pathlib.Path(path).is_file():
            return ResourceType.FILE, path
    if env_file is not None:
        candidate = os.getenv(env_file)
        if candidate is not None:
            if pathlib.Path(candidate).is_file():
                return ResourceType.FILE, candidate
    if env_path is not None:
        path = os.getenv(env_path)
        bname = pathlib.Path(name).name
        if path is not None:
            for dir in path.split(os.pathsep):
                candidate = pathlib.Path(dir) / bname
                if candidate.is_file():
                    return ResourceType.FILE, str(candidate)
    pkg, res = _extract_package(name)
    if _is_resource(pkg, res):
        return ResourceType.PACKAGED, name
    return ResourceType.NOTFOUND, ""


def load_yaml(
    name: str,
    path: Optional[str] = None,
    env_file: Optional[str] = None,
    env_path: Optional[str] = None,
) -> object:
    """Load a YAML resource

    See `find_resource` for the signification of the parameters

    Raises `FileNotFoundError` if no corresponding resource is found
    """
    tp, res_path = find_resource(name, path, env_file, env_path)
    if tp == ResourceType.NOTFOUND:
        raise FileNotFoundError(name)
    elif tp == ResourceType.FILE:
        f = open(res_path, "r")
    elif tp == ResourceType.PACKAGED:
        pkg, res = _extract_package(res_path)
        f = _open_text(pkg, res)
    else:
        raise ValueError("Unknown resource type")
    with f:
        return yaml.safe_load(f)

# ============ Import python packages ============
from pathlib import Path, PurePath
from qtpy import QtCore


# ============ Same as napari CODE ============
ICON_PATH = (Path(__file__).parent / 'icons').resolve()
ICONS = {x.stem: str(x) for x in ICON_PATH.iterdir() if x.suffix == '.svg'}

QtCore.QDir.addSearchPath('icons', str(ICON_PATH))

def get_icon_path(name):
    """Return path to an SVG in the theme icons."""
    if name not in ICONS:
        raise ValueError(
            trans._(
                "unrecognized icon name: {name!r}. Known names: {icons}",
                deferred=True,
                name=name,
                icons=set(ICONS),
            )
        )
    return ICONS[name]

def get_relative_icon_path(name):
    """Return path to an SVG in the theme icons."""
    if name not in ICONS:
        raise ValueError(
            trans._(
                "unrecognized icon name: {name!r}. Known names: {icons}",
                deferred=True,
                name=name,
                icons=set(ICONS),
            )
        )
    return PurePath(ICONS[name]).as_posix()
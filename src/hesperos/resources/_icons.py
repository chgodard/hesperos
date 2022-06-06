from pathlib import Path, PurePath

ICON_PATH = (Path(__file__).parent / 'icons').resolve()
ICONS = {x.stem: str(x) for x in ICON_PATH.iterdir() if x.suffix == '.svg'}

## FROM napari CODE

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
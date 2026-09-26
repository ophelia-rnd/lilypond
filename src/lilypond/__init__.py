from __future__ import annotations

from importlib.metadata import PackageNotFoundError, metadata
from lilypond.basin import Basin
from lilypond.legacy_pond import LegacyPond
from lilypond.pond import Pond
from lilypond.pond_base_style import PondBaseStyle

__version__ = "0.2.1"

try:
    _meta = metadata("som-lilypond")
    __description__ = _meta["Summary"]
except PackageNotFoundError:
    __description__ = ""

def describe():
    description = (
        "Lilypond (som-lilypond)\n"
        "Description: {}\n"
        "Version: {}\n"
    ).format(__description__, __version__)

    print(description)

__all__ = ["__version__", "Basin", "LegacyPond", "Pond", "PondBaseStyle"]

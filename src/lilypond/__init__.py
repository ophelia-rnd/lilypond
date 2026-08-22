from lilypond.basin import Basin
from lilypond.legacy_pond import LegacyPond
from lilypond.pond import Pond
from lilypond.pond_base_style import PondBaseStyle
from importlib.metadata import PackageNotFoundError, metadata

__version__ = "0.2.0"

try:
    _meta = metadata("lilypond")
    __description__ = _meta["Summary"]
except PackageNotFoundError:
    __description__ = ""

def describe():
    description = (
        "Lilypond (lilypond)\n"
        "Description: {}\n"
        "Version: {}\n"
    ).format(__description__, __version__)

    print(description)

__all__ = ["__version__", "Basin", "LegacyPond", "Pond", "PondBaseStyle"]

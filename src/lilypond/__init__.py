from lilypond.basin import Basin
from lilypond.legacy_pond import LegacyPond
from lilypond.pond import Pond
from lilypond.som_representation import SomRepresentation
from lilypond.pond_base_style import PondBaseStyle
from importlib.metadata import PackageNotFoundError, metadata

__version__ = "0.1.0"

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

__all__ = ["__version__", "SomRepresentation", "Basin", "LegacyPond", "Pond", "PondBaseStyle"]

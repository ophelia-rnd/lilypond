import pytest
from lilypond.pond_base_style import PondBaseStyle
from lilypond.utils.colorscale import get_truncated_colorscale


def test_pond_base_style_get():
    pond = PondBaseStyle.get("pond")
    assert isinstance(pond, PondBaseStyle)

    iceflock = PondBaseStyle.get("iceflock")
    assert isinstance(iceflock, PondBaseStyle)

    with pytest.raises(ValueError, match="Unknown style 'nonexistent'"):
        PondBaseStyle.get("nonexistent")

from dataclasses import dataclass
from lilypond.utils.colorscale import get_truncated_colorscale

@dataclass(frozen=True)
class PondBaseStyle:
    water_colorscale: str | list
    rhizome_colorscale: str | list
    pad_colorscale: str | list
    petal_colorscale: str | list
    petal_marker: dict
    petal_marker_line: dict
    petal_halo_marker: dict

    @classmethod
    def pond(cls) -> "PondBaseStyle":
        return cls(
            water_colorscale=get_truncated_colorscale(colorscale="Blues", clip_interval=(.6, .9)),
            rhizome_colorscale=get_truncated_colorscale(colorscale="Greys", clip_interval=(.9, 1.0)),
            pad_colorscale=get_truncated_colorscale(colorscale="speed_r", clip_interval=(.0, .9)),
            petal_colorscale=get_truncated_colorscale(colorscale="Burg", clip_interval=(.0, .5)),
            petal_marker_line=dict(width=2),
            petal_marker=dict(symbol="asterisk", opacity=1),
            petal_halo_marker=dict(symbol="asterisk", color="black", opacity=.6, line=dict(width=6, color="black"))
        )

    @classmethod
    def iceflock(cls) -> "PondBaseStyle":
        return cls(
            water_colorscale=get_truncated_colorscale(colorscale="Blues", clip_interval=(.6, .9)),
            rhizome_colorscale=get_truncated_colorscale(colorscale="Burg", clip_interval=(.9, 1.0)),
            pad_colorscale=get_truncated_colorscale(colorscale="gray_r", clip_interval=(.0, .1)),
            petal_colorscale=get_truncated_colorscale(colorscale="gray_r", clip_interval=(.8, 1.0)),
            petal_marker_line=dict(width=0),
            petal_marker=dict(symbol="triangle-se", opacity=1),
            petal_halo_marker=None
        )

    @classmethod
    def get(cls, name: str) -> "PondBaseStyle":
        if hasattr(cls, name) and callable(getattr(cls, name)):
            return getattr(cls, name)()
        raise ValueError(f"Unknown style '{name}'.")

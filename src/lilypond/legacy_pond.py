import numpy as np
import plotly.express as px
from lilypond.basin import Basin

class LegacyPond:
    def __init__(self, basin: Basin, verbose=False):
        self.basin = basin
        self.verbose = verbose

    def visualize_distance_map(
            self,
            colormap="Spectral_r",
            fig=None,
            figsize=(None, 400),
            show_fig=True,
            **imshow_kwargs,
    ):
        imshow_args = dict(
            origin="lower",
            labels=dict(color="Distance"),
            color_continuous_scale=colormap,
        )
        imshow_args.update(imshow_kwargs)

        imshow_fig = px.imshow(
            self.basin.distance_map_,
            **imshow_args,
        )

        if fig is None:
            fig = imshow_fig
            width, height = figsize
            fig.update_layout(
                autosize=(width is None),
                height=height,
                title="Distance map",
                xaxis=dict(scaleanchor="y", constrain="domain"),
            )
            if width is not None:
                fig.update_layout(width=width)
        else:
            for trace in imshow_fig.data:
                fig.add_trace(trace)

        if show_fig:
            fig.show()

        return fig

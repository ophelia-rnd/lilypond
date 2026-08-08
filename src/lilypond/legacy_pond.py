import plotly.express as px

from lilypond.basin import Basin

class LegacyPond:
    def __init__(self, basin: Basin, verbose=False):
        self.basin = basin
        self.verbose = verbose

    def visualize_distance_map(self, colorscale="Spectral_r", show_fig=True, **layout_kwargs):
        fig = px.imshow(
            self.basin.distance_map,
            origin="lower",
            labels=dict(color="Distance"),
            color_continuous_scale=colorscale,
        )
        args = dict(title="Distance map", autosize=True, showlegend=True)
        args.update(layout_kwargs)
        fig.update_layout(args)
        if show_fig: fig.show()
        return fig

    def visualize_activation_map(self, colorscale="gray_r", show_fig=True, **layout_kwargs):
        fig = px.imshow(
            self.basin.activation_map,
            origin="lower",
            labels=dict(color="Activation"),
            color_continuous_scale=colorscale,
        )
        args = dict(title="Activation map", autosize=True, showlegend=True)
        args.update(layout_kwargs)
        fig.update_layout(args)
        if show_fig: fig.show()
        return fig

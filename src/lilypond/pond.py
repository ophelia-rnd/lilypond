import numpy as np
import plotly.express as px

from plotly import graph_objects as go
from typing_extensions import Literal
from lilypond.basin import Basin

class Pond:
    def __init__(self, basin: Basin, style_name:Literal["pond", "iceflock"]="pond", verbose=False):
        self.basin = basin
        self.verbose = verbose
        self.style_name = style_name
        self._style_config = Basin.STYLES[self.style_name]
        self._layers = []
        self.__water_layer()

    def __new_layer(self, layer):
        self._layers.append(layer)

    def __water_layer(self):
        distance_map = self.basin.distance_map_
        row_indices, col_indices = np.indices(distance_map.shape)
        distance = distance_map.ravel()

        __colorscale = self._style_config["water_colorscale"]
        colors = px.colors.sample_colorscale(__colorscale, distance)

        shapes = []
        for x, y, c in zip(col_indices.ravel(), row_indices.ravel(), colors):
            half = 1.0 / 2.0
            shapes.append(dict(
                type="rect",
                x0=x - half, x1=x + half,
                y0=y - half, y1=y + half,
                xref="x", yref="y",
                fillcolor=c,
                line=dict(width=0),
                layer="between",
            ))

        layer = {
            "type": "water",
            "shapes": shapes,
        }
        self.__new_layer(layer)
        return self

    def _get_projection_coords(self, X):
        som = self.basin.som
        winner_coords = np.array([som.winner(x) for x in np.asarray(X)])
        x_coords = winner_coords[:, 1]
        y_coords = winner_coords[:, 0]
        return x_coords, y_coords

    def pad_layer(self,
                  gap:Literal["auto", "nogap"]="auto",
                  min_fraction=0.1, name="Node Layer",
                  colorscale_source_feature_idx:int=None,
                  colorscale=None):

        row_indices, col_indices = np.indices(self.basin.lattice_shape_)
        color_values = np.empty(self.basin.lattice_shape_).ravel()
        distance = self.basin.distance_map_.ravel()

        if gap == "nogap":
            sizes = np.clip(1.0 - (distance - min(distance)), min_fraction, 1.0)
        elif gap == "auto":
            sizes = np.clip(1.0 - distance, min_fraction, 1.0)
        else: raise ValueError("The argument `gap` must be either 'auto' or 'nogap'")

        if colorscale_source_feature_idx is None:
            color_values = distance
        elif type(colorscale_source_feature_idx) == int:
            component_idx = colorscale_source_feature_idx
            assert (component_idx >= 0) and (component_idx < self.basin.component_size_), f"The argument `colorscale_source_feature_idx` must be within [0, {self.basin.component_size_})."
            node_weights_by_component = self.basin.node_weights_[:, :, component_idx]
            node_weights_by_component_norm = np.interp(node_weights_by_component, (node_weights_by_component.min(), node_weights_by_component.max()), (0, 1))
            color_values = node_weights_by_component_norm.ravel()
        else: raise ValueError("The argument `colorscale_source_feature_idx` must be either None or a feature index.")

        __colorscale = colorscale if colorscale is not None else self._style_config["pad_colorscale"]
        colors = px.colors.sample_colorscale(__colorscale, color_values)

        shapes = []
        for x, y, s, c in zip(col_indices.ravel(), row_indices.ravel(), sizes, colors):
            half = s / 2.0
            shapes.append(dict(
                type="rect",
                x0=x - half, x1=x + half,
                y0=y - half, y1=y + half,
                xref="x", yref="y",
                fillcolor=c,
                line=dict(width=0),
                layer="between",
            ))

        layer = {
            "type": "pad",
            "name": name,
            "shapes": shapes,
        }
        self.__new_layer(layer)
        return self

    def petal_layer(self, min_size=8, max_size=30, name="Training Activation", marker=None, marker_line=None, marker_halo=None, hide_halo=False, **kwargs):
        activation_map = self.basin.activation_map_
        row_indices, col_indices = np.nonzero(activation_map)
        activation_strength = activation_map[row_indices, col_indices]

        a_min, a_max = activation_strength.min(), activation_strength.max()

        if max_size > min_size and a_max > a_min:
            sizes = np.interp(activation_strength, (a_min, a_max), (min_size, max_size))
        else:
            sizes = np.full(activation_strength.shape, min_size)

        __colorscale = self._style_config["petal_colorscale"]
        __marker_line = self._style_config["petal_marker_line"](activation_strength, __colorscale)
        if marker_line: __marker_line.update(marker_line)
        __marker = self._style_config["petal_marker"](activation_strength, __colorscale, sizes, __marker_line)
        if marker: __marker.update(marker)

        if not hide_halo:
            __marker_halo = self._style_config["petal_halo_marker"](sizes)
            if marker_halo: __marker_halo.update(marker_halo)

            if len(__marker_halo):
                halo_layer = {
                    "type": "petal",
                    "name": "Halo Layer",
                    "x_coords": col_indices,
                    "y_coords": row_indices,
                    "marker": __marker_halo,
                    "scatter_kwargs": kwargs
                }
                self.__new_layer(halo_layer)

        layer = {
            "type": "petal",
            "name": name,
            "x_coords": col_indices,
            "y_coords": row_indices,
            "marker": __marker,
            "scatter_kwargs": kwargs
        }
        self.__new_layer(layer)

        return self

    def attraction_layer(self, X, jitter_amount=0.2, name="Projection", marker=None, **kwargs):
        default_marker = dict(color="red", size=10, symbol="circle")
        if marker: default_marker.update(marker)
        x_coords, y_coords = self._get_projection_coords(X)
        layer = {
            "type": "projection",
            "name": name,
            "jitter_amount": jitter_amount,
            "x_coords": x_coords,
            "y_coords": y_coords,
            "marker": default_marker,
            "scatter_kwargs": kwargs
        }
        self.__new_layer(layer)
        return self

    def visualize(self, show_fig=True):
        fig = go.Figure()

        for layer in self._layers:
            if layer["type"] in ["water", "pad"]:
                for shape in layer["shapes"]:
                    fig.add_shape(shape)

            else:
                if layer["type"] == "petal":
                    x_coords, y_coords = layer["x_coords"], layer["y_coords"]

                elif layer["type"] == "projection":
                    x_coords, y_coords = layer["x_coords"], layer["y_coords"]
                    jitter_amount = layer["jitter_amount"]

                    if jitter_amount > 0:
                        rng = np.random.default_rng(self.basin.random_seed)
                        x_jitter = rng.uniform(-jitter_amount, jitter_amount, size=x_coords.shape)
                        y_jitter = rng.uniform(-jitter_amount, jitter_amount, size=y_coords.shape)
                        x_coords = x_coords + x_jitter
                        y_coords = y_coords + y_jitter

                else: raise ValueError("Unknown layer type")

                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode="markers",
                    name=layer["name"],
                    marker=layer["marker"],
                    **layer["scatter_kwargs"]
                ))

            rows, cols = self.basin.lattice_shape_
            fig.update_xaxes(range=[-0.5, cols - 0.5], zeroline=False, showgrid=False)
            fig.update_yaxes(range=[-0.5, rows - 0.5], zeroline=False, showgrid=False)

        fig.update_layout(
            autosize=True,
            title="Distance map",
            xaxis=dict(scaleanchor="y", constrain="domain"),
            showlegend=True,
        )

        if show_fig:
            fig.show()

        return fig

from __future__ import annotations

import numpy as np
import plotly.express as px

from plotly import graph_objects as go
from typing import Literal
from lilypond.basin import Basin
from lilypond.pond_base_style import PondBaseStyle

class Pond:
    def __init__(self, basin: Basin, base_style:Literal["pond", "iceflock"] | PondBaseStyle = "pond", verbose=False):
        self.basin = basin
        self.verbose = verbose
        self.base_style = base_style
        self._base_style_config = base_style if isinstance(base_style, PondBaseStyle) else PondBaseStyle.get(base_style)
        self._layers = []
        self.__water_layer()

    def __new_layer(self, layer):
        self._layers.append(layer)

    def __water_layer(self):
        distance_map = self.basin.som_representation.distance_map
        row_indices, col_indices = np.indices(distance_map.shape)
        distance = distance_map.ravel()

        colorscale = self._base_style_config.water_colorscale
        colors = px.colors.sample_colorscale(colorscale, distance)

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
            "object": "water",
            "type": "shape",
            "shapes": shapes,
        }
        self.__new_layer(layer)
        return self

    def _get_projection_coords(self, X):
        som = self.basin.som_representation.som
        winner_coords = np.array([som.winner(x) for x in np.asarray(X)])
        x_coords = winner_coords[:, 1]
        y_coords = winner_coords[:, 0]
        return x_coords, y_coords

    def rhizome_layer(self, X=None, violations_only=False, min_width=5, max_width=15, colorscale=None, neighborhood:Literal["moore", "von-neumann"]="moore", name="Dual BMU Connections", show_colorbar=True, colorbar_title=None):
        unique_b2mu_edges, unique_b2mu_counts, unique_b2mu_distances = (
            self.basin.som_representation.unique_b2mu_edges_counts_distances
            if X is None
            else self.basin.som_representation._calc_unique_b2mu_edges_counts_distances(X)
        )

        show_inds = np.ones_like(unique_b2mu_distances).astype(bool)

        if violations_only:
            t_neigh = 1.42 if neighborhood == "moore" else 1
            show_inds = unique_b2mu_distances > t_neigh

        if any(show_inds == True):
            unique_edges, counts = unique_b2mu_edges[show_inds], unique_b2mu_counts[show_inds]

            c_min = float(counts.min())
            c_max = float(counts.max())
            if c_max > c_min:
                counts_norm_1 = np.interp(counts, (c_min, c_max), (0, 1))
                color_values = counts_norm_1
                cb_cmin, cb_cmax = c_min, c_max
            else:
                color_values = np.full_like(counts, 0.5, dtype=float)
                delta = abs(c_min) * 0.01 if c_min != 0.0 else 0.01
                cb_cmin, cb_cmax = c_min - delta, c_max + delta

            counts_norm_2 = np.interp(counts, (c_min, c_max), (min_width, max_width)) if c_max > c_min else np.full_like(counts, min_width, dtype=float)
            width_values = counts_norm_2

            _colorscale = colorscale if colorscale is not None else self._base_style_config.rhizome_colorscale
            colors = px.colors.sample_colorscale(_colorscale, color_values)

            shapes = []
            for (y1, x1, y2, x2), c, w in zip(unique_edges, colors, width_values):
                shapes.append(dict(
                    type="line",
                    x0=x1, y0=y1,
                    x1=x2, y1=y2,
                    line=dict(color=c, width=w),
                    layer="between",
                ))

            colorbar_config = None
            if show_colorbar and _colorscale:
                cb_title = colorbar_title if colorbar_title is not None else "Connection Line<br>Severity (Frequency)"
                colorbar_config = {
                    "title": cb_title,
                    "colorscale": _colorscale,
                    "cmin": cb_cmin,
                    "cmax": cb_cmax,
                }

            layer = {
                "object": "rhizome",
                "type": "shape",
                "shapes": shapes,
                "name": name,
                "colorbar": colorbar_config,
            }
            self.__new_layer(layer)
        return self

    def pad_layer(self, gap:Literal["auto", "nogap"]="auto", min_fraction=0.1, colorscale=None, color_by:Literal["distance"] | dict="distance", name="Node Layer", show_colorbar=True, colorbar_title=None):
        distance_map = self.basin.som_representation.distance_map
        row_indices, col_indices = np.indices(distance_map.shape)
        distance = distance_map.ravel()

        if gap == "nogap":
            sizes = np.clip(1.0 - (distance - min(distance)), min_fraction, 1.0)
        elif gap == "auto":
            sizes = np.clip(1.0 - distance, min_fraction, 1.0)
        else: raise ValueError("The argument `gap` must be either 'auto' or 'nogap'")

        if color_by == "distance":
            default_title = "Normalized Average<br>Neighbor Distance"
            d_min, d_max = float(distance.min()), float(distance.max())
            if d_max > d_min:
                color_values = np.interp(distance, (d_min, d_max), (0, 1)).ravel()
                cb_cmin, cb_cmax = d_min, d_max
            else:
                color_values = np.full_like(distance, 0.5, dtype=float).ravel()
                delta = abs(d_min) * 0.01 if d_min != 0.0 else 0.01
                cb_cmin, cb_cmax = d_min - delta, d_max + delta
        elif (
            isinstance(color_by, dict)
            and "feature_idx" in color_by
            and isinstance(color_by["feature_idx"], int)
        ):
            component_idx = color_by["feature_idx"]
            if not (0 <= component_idx < self.basin.som_representation.component_size_):
                raise ValueError(
                    f"The feature index {component_idx} is out of bounds for matrix dimensions (expected 0 <= feature_idx < {self.basin.som_representation.component_size_})."
                )
            default_title = f"Feature {component_idx + 1}"
            weights = self.basin.som_representation.node_weights_[:, :, component_idx]
            w_min, w_max = float(weights.min()), float(weights.max())
            if w_max > w_min:
                color_values = np.interp(weights, (w_min, w_max), (0, 1)).ravel()
                cb_cmin, cb_cmax = w_min, w_max
            else:
                color_values = np.full_like(weights, 0.5, dtype=float).ravel()
                delta = abs(w_min) * 0.01 if w_min != 0.0 else 0.01
                cb_cmin, cb_cmax = w_min - delta, w_max + delta
        else:
            raise ValueError("The argument `color_by` must be 'distance' or a dict with a 'feature_idx' integer index (e.g. {'feature_idx': 0}).")

        _colorscale = colorscale if colorscale is not None else self._base_style_config.pad_colorscale
        colors = px.colors.sample_colorscale(_colorscale, color_values)

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

        colorbar_config = None
        if show_colorbar and _colorscale:
            colorbar_config = {
                "title": colorbar_title if colorbar_title is not None else default_title,
                "colorscale": _colorscale,
                "cmin": cb_cmin,
                "cmax": cb_cmax,
            }

        layer = {
            "object": "pad",
            "type": "shape",
            "shapes": shapes,
            "name": name,
            "colorbar": colorbar_config,
        }
        self.__new_layer(layer)
        return self

    def petal_layer(self, min_size=8, max_size=30, colorscale=None, marker=None, marker_line=None, marker_halo=None, hide_halo=False, name="Training Activation", show_colorbar=True, colorbar_title=None, **kwargs):
        activation_map = self.basin.som_representation.activation_map
        row_indices, col_indices = np.nonzero(activation_map)
        activation_strength = activation_map[row_indices, col_indices]

        a_min, a_max = activation_strength.min(), activation_strength.max()

        if max_size > min_size and a_max > a_min:
            sizes = np.interp(activation_strength, (a_min, a_max), (min_size, max_size))
        else:
            sizes = np.full(activation_strength.shape, min_size)

        _colorscale = colorscale if colorscale is not None else self._base_style_config.petal_colorscale
        _marker = self._base_style_config.petal_marker.copy()
        _marker_line = self._base_style_config.petal_marker_line.copy()

        _marker_line.update(dict(colorscale=_colorscale, color=activation_strength))
        if marker_line: _marker_line.update(marker_line)

        _marker.update(dict(colorscale=_colorscale, color=activation_strength, size=sizes))
        _marker.update(dict(line=_marker_line))
        if marker: _marker.update(marker)

        if not hide_halo and (self._base_style_config.petal_halo_marker is not None or marker_halo is not None):
            _marker_halo = self._base_style_config.petal_halo_marker.copy()
            _marker_halo.update(dict(size=sizes * 1.2))
            if marker_halo: _marker_halo.update(marker_halo)

            if len(_marker_halo):
                halo_layer = {
                    "object": "petal_halo",
                    "type": "scatter",
                    "x_coords": col_indices,
                    "y_coords": row_indices,
                    "marker": _marker_halo,
                    "name": "Halo Layer",
                    "scatter_kwargs": kwargs
                }
                self.__new_layer(halo_layer)

        colorbar_config = None
        if show_colorbar and _colorscale:
            cb_title = colorbar_title if colorbar_title is not None else "Training Activation"
            cb_cmin = float(a_min)
            cb_cmax = float(a_max)
            if cb_cmax == cb_cmin:
                delta = abs(cb_cmin) * 0.01 if cb_cmin != 0.0 else 0.01
                cb_cmin, cb_cmax = cb_cmin - delta, cb_cmax + delta
            colorbar_config = {
                "title": cb_title,
                "colorscale": _colorscale,
                "cmin": cb_cmin,
                "cmax": cb_cmax,
            }
        layer = {
            "object": "petal",
            "type": "scatter",
            "x_coords": col_indices,
            "y_coords": row_indices,
            "marker": _marker,
            "name": name,
            "scatter_kwargs": kwargs,
            "colorbar": colorbar_config,
        }
        self.__new_layer(layer)

        return self

    def attraction_layer(self, X, jitter_amount=0.2, name="Projection", marker=None, **kwargs):
        default_marker = dict(color="red", size=10, symbol="circle")
        if marker: default_marker.update(marker)
        x_coords, y_coords = self._get_projection_coords(X)
        layer = {
            "object": "attraction",
            "type": "scatter",
            "jitter_amount": jitter_amount,
            "x_coords": x_coords,
            "y_coords": y_coords,
            "marker": default_marker,
            "name": name,
            "scatter_kwargs": kwargs
        }
        self.__new_layer(layer)
        return self

    def visualize(self, show_fig=True, **layout_kwargs):
        fig = go.Figure()

        shapes = [
            s for layer in self._layers
            if layer["type"] == "shape"
            for s in layer["shapes"]
        ]
        fig.update_layout(shapes=shapes)

        order = {"rhizome": 1, "pad": 2, "petal": 3}
        colorbar_layers = sorted(
            [layer for layer in self._layers if layer.get("colorbar") is not None],
            key=lambda l: order.get(l.get("object"), 99)
        )
        num_cbs = len(colorbar_layers)

        y_positions = {
            1: [0.60],
            2: [0.80, 0.40],
            3: [0.92, 0.60, 0.28],
        }.get(num_cbs, [0.95 - i * (0.75 / max(num_cbs - 1, 1)) for i in range(num_cbs)])

        # Assign colorbar layout dict to each layer and add dummy traces for shape layers
        for layer, y_pos in zip(colorbar_layers, y_positions):
            cb_info = layer["colorbar"]
            cb_dict = dict(
                orientation="h",
                title=dict(text=cb_info["title"], side="top"),
                x=1.02,
                xanchor="left",
                y=y_pos,
                yanchor="middle",
                lenmode="pixels",
                len=200,
                thickness=12,
            )
            cb_info["layout"] = cb_dict

            if layer["type"] == "shape":
                fig.add_trace(go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    showlegend=False,
                    hoverinfo="none",
                    marker=dict(
                        colorscale=cb_info["colorscale"],
                        cmin=cb_info["cmin"],
                        cmax=cb_info["cmax"],
                        color=[cb_info["cmin"]],
                        showscale=True,
                        colorbar=cb_dict,
                    ),
                ))

        scatter_layers = [layer for layer in self._layers if layer["type"] == "scatter"]
        has_legend = any(layer.get("name") for layer in scatter_layers)

        for layer in scatter_layers:
            x_coords, y_coords = layer["x_coords"], layer["y_coords"]

            if layer["object"] == "attraction":
                jitter_amount = layer["jitter_amount"]
                if jitter_amount > 0:
                    rng = np.random.default_rng(self.basin.random_seed)
                    x_jitter = rng.uniform(-jitter_amount, jitter_amount, size=x_coords.shape)
                    y_jitter = rng.uniform(-jitter_amount, jitter_amount, size=y_coords.shape)
                    x_coords = x_coords + x_jitter
                    y_coords = y_coords + y_jitter

            marker = layer["marker"].copy() if isinstance(layer.get("marker"), dict) else layer.get("marker")
            if layer.get("colorbar") is not None:
                cb_info = layer["colorbar"]
                marker["showscale"] = True
                marker["cmin"] = cb_info["cmin"]
                marker["cmax"] = cb_info["cmax"]
                marker["colorbar"] = cb_info["layout"]

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode="markers",
                name=layer["name"],
                marker=marker,
                **layer["scatter_kwargs"]
            ))

        rows, cols = self.basin.som_representation.lattice_shape_
        args = dict(
            autosize=True,
            showlegend=True,
            xaxis=dict(range=[-0.5, cols - 0.5], scaleanchor="y", constrain="domain", zeroline=False, showgrid=False),
            yaxis=dict(range=[-0.5, rows - 0.5], zeroline=False, showgrid=False),
            legend=dict(
                x=1.02,
                xanchor="left",
                y=0.0,
                yanchor="bottom",
            ),
            margin=dict(r=260) if colorbar_layers or has_legend else dict(),
        )

        if num_cbs >= 3:
            args["height"] = max(580, int(rows * 50))
        if "legend" in layout_kwargs and isinstance(layout_kwargs.get("legend"), dict):
            args.setdefault("legend", {}).update(layout_kwargs["legend"])
            layout_kwargs = {k: v for k, v in layout_kwargs.items() if k != "legend"}
        if "margin" in layout_kwargs and isinstance(layout_kwargs.get("margin"), dict):
            args.setdefault("margin", {}).update(layout_kwargs["margin"])
            layout_kwargs = {k: v for k, v in layout_kwargs.items() if k != "margin"}

        args.update(layout_kwargs)
        fig.update_layout(args)

        if show_fig:
            fig.show()

        return fig

import numpy as np
import plotly.express as px
import pytest

from lilypond.basin import Basin
from unittest.mock import MagicMock


def test_pad_layer_uniform_weights_maps_to_center():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)), component_size_=1)
    som_rep.node_weights_ = np.full((3, 3, 1), 5.0)

    pond = Basin(som_rep).pond().pad_layer(color_by={"feature_idx": 0})
    layer = pond._layers[-1]
    shapes = layer["shapes"]

    expected_color_center = px.colors.sample_colorscale(pond._base_style_config.pad_colorscale, [0.5])[0]
    assert all(s["fillcolor"] == expected_color_center for s in shapes), "Uniform weights should map to center color 0.5"

    cb = layer["colorbar"]
    assert cb["cmin"] < 5.0 < cb["cmax"], "Colorbar should be symmetrically centered around original value 5.0"
    assert np.isclose((cb["cmin"] + cb["cmax"]) / 2.0, 5.0), "Midpoint of colorbar should equal original value 5.0"


def test_rhizome_layer_uniform_counts_maps_to_center():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)))
    som_rep.unique_b2mu_edges_counts_distances = (
        np.array([[0, 0, 0, 1], [0, 1, 0, 2]]),
        np.array([4, 4]),
        np.array([1.0, 1.0]),
    )
    pond = Basin(som_rep).pond().rhizome_layer()
    layer = pond._layers[-1]
    shapes = layer["shapes"]

    expected_color_center = px.colors.sample_colorscale(pond._base_style_config.rhizome_colorscale, [0.5])[0]
    assert all(s["line"]["color"] == expected_color_center for s in shapes), "Uniform counts should map to center color 0.5"

    cb = layer["colorbar"]
    assert cb["cmin"] < 4.0 < cb["cmax"], "Colorbar should be symmetrically centered around original value 4.0"
    assert np.isclose((cb["cmin"] + cb["cmax"]) / 2.0, 4.0), "Midpoint of colorbar should equal original value 4.0"


def test_petal_layer_uniform_activations_maps_to_center():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)))
    som_rep.activation_map = np.array([
        [0, 2, 0],
        [2, 0, 2],
        [0, 0, 0],
    ])
    pond = Basin(som_rep).pond().petal_layer()
    layer = pond._layers[-1]

    cb = layer["colorbar"]
    assert cb["cmin"] < 2.0 < cb["cmax"], "Colorbar should be symmetrically centered around original value 2.0"
    assert np.isclose((cb["cmin"] + cb["cmax"]) / 2.0, 2.0), "Midpoint of colorbar should equal original value 2.0"

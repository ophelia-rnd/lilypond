import numpy as np
import plotly.express as px
import pytest

from lilypond.basin import Basin
from unittest.mock import MagicMock


def test_rhizome_layer_uniform_counts_maps_to_base_size_and_zero():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)))
    edges = np.array([[0, 0, 0, 1], [0, 1, 0, 2]])
    counts = np.array([3, 3])
    distances = np.array([1.0, 1.0])
    som_rep.unique_b2mu_edges_counts_distances = (edges, counts, distances)

    pond = Basin(som_rep).pond().rhizome_layer(min_width=5, max_width=15)
    shapes = pond._layers[-1]["shapes"]

    expected_color_0 = px.colors.sample_colorscale(pond._base_style_config.rhizome_colorscale, [0.0])[0]
    assert all(s["line"]["width"] == 5 for s in shapes), "Uniform counts should map to min_width (5)"
    assert all(s["line"]["color"] == expected_color_0 for s in shapes), "Uniform counts should map to color 0.0"


def test_petal_layer_uniform_activation_maps_to_min_size():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)))
    som_rep.activation_map = np.full((3, 3), 5.0)

    pond = Basin(som_rep).pond().petal_layer(min_size=8, max_size=30)
    sizes = pond._layers[-1]["marker"]["size"]

    np.testing.assert_array_equal(sizes, 8)

def test_pad_layer_uniform_weights_maps_to_zero():
    som_rep = MagicMock(distance_map=np.zeros((3, 3)), component_size_=1)
    som_rep.node_weights_ = np.full((3, 3, 1), 5.0)

    pond = Basin(som_rep).pond().pad_layer(colorscale_source_feature_idx=0)
    shapes = pond._layers[-1]["shapes"]

    expected_color_0 = px.colors.sample_colorscale(pond._base_style_config.pad_colorscale, [0.0])[0]
    assert all(s["fillcolor"] == expected_color_0 for s in shapes), "Uniform weights should map to color 0.0"

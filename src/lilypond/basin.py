from minisom import MiniSom
from typing import Literal
from lilypond.utils.colorscale import get_truncated_colorscale

class Basin:

    STYLES = {
        "pond": {
            "water_colorscale": get_truncated_colorscale(colorscale="Blues", clip_interval=(.6, .9)),
            "rhizome_colorscale": get_truncated_colorscale(colorscale="Greys", clip_interval=(.9, 1.0)),
            "pad_colorscale": get_truncated_colorscale(colorscale="speed_r", clip_interval=(.0, .9)),
            "petal_colorscale": get_truncated_colorscale(colorscale="Burg", clip_interval=(.0, .5)),
            "petal_marker": lambda activation_strength, colorscale, sizes, marker_line: dict(
                color=activation_strength, colorscale=colorscale, size=sizes, symbol="asterisk", opacity=1,
                line=marker_line
            ),
            "petal_marker_line": lambda activation_strength, colorscale: dict(
                width=2, color=activation_strength, colorscale=colorscale
            ),
            "petal_halo_marker": lambda sizes: dict(
                color="black", size=sizes * 1.2, symbol="asterisk", opacity=.6,
                line=dict(width=6, color="black")
            ),
        },
        "iceflock": {
            "water_colorscale": get_truncated_colorscale(colorscale="Blues", clip_interval=(.6, .9)),
            "rhizome_colorscale": get_truncated_colorscale(colorscale="Greys", clip_interval=(.9, 1.0)),
            "pad_colorscale": get_truncated_colorscale(colorscale="gray_r", clip_interval=(.0, .1)),
            "petal_colorscale": get_truncated_colorscale(colorscale="gray_r", clip_interval=(.8, 1.0)),
            "petal_marker": lambda activation_strength, colorscale, sizes, marker_line: dict(
                color=activation_strength, colorscale=colorscale, size=sizes, symbol="triangle-se", opacity=1,
                line=marker_line
            ),
            "petal_marker_line": lambda activation_strength, colorscale: dict(width=0),
            "petal_halo_marker": lambda sizes: dict(),
        }
    }

    def __init__(self, som: MiniSom, random_seed=None, verbose=False):
        self.som = som
        self.random_seed = random_seed
        self.verbose = verbose

    @classmethod
    def from_data(cls, X, random_seed=None, verbose=False):
        from lilypond import SomRepresentation
        som = SomRepresentation.with_derived_params(X, random_seed=random_seed, verbose=verbose).fit(X).som
        basin = cls(som, random_seed=random_seed, verbose=verbose)
        basin.X_ = X.copy()
        return basin

    @classmethod
    def from_som(cls, som:MiniSom, random_seed=None, verbose=False):
        basin = cls(som, random_seed=random_seed, verbose=verbose)
        return basin

    @property
    def training_data(self):
        assert self.has_training_data, "The Basin does not have explicitly assigned training data."
        return self.X_

    @property
    def has_training_data(self):
        return hasattr(self, "X_") and self.X_ is not None

    def prepare(self, neighbor_distance_scaling: Literal["sum", "mean"] = "mean"):
        node_weights = self.som.get_weights().copy()
        self.node_weights_ = node_weights
        self.component_size_ = node_weights.shape[2]

        distance_map = self.som.distance_map(scaling=neighbor_distance_scaling).copy()
        self.distance_map_ = distance_map
        self.lattice_shape_ = distance_map.shape
        self.rows_, self.cols_ = distance_map.shape

        if self.has_training_data:
            activation_map = self.som.activation_response(self.X_).astype(int).copy()
            self.activation_map_ = activation_map

        self.prepared_ = True
        if self.verbose: print("Basin has been prepared.")

        return self

    def legacy_pond(self):
        self.__assert_prepared()
        from lilypond.legacy_pond import LegacyPond
        return LegacyPond(self, verbose=self.verbose)

    def pond(self, style_name:Literal["pond", "iceflock"]="pond"):
        self.__assert_prepared()
        from lilypond.pond import Pond
        return Pond(self, style_name=style_name, verbose=self.verbose)

    def __assert_prepared(self):
        assert hasattr(self, "prepared_") and self.prepared_ is True, "The Basin must be prepared."

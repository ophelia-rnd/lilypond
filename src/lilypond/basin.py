from minisom import MiniSom
from typing import Literal

class Basin:

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
    def has_training_data(self):
        return hasattr(self, "X_") and self.X_ is not None

    @property
    def legacy_pond(self):
        self.__assert_prepared()
        return self.legacy_pond_

    @property
    def pond(self):
        self.__assert_prepared()
        return self.pond_

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

        from lilypond.legacy_pond import LegacyPond
        self.legacy_pond_ = LegacyPond(self, verbose=self.verbose)

        self.pond_ = None # FIXME

        return self

    def __assert_prepared(self):
        assert hasattr(self, "prepared_") and self.prepared_ is True, "The Basin must be prepared."

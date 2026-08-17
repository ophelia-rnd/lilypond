from typing import Literal
from lilypond.pond_base_style import PondBaseStyle
from minisom_representation import SomRepresentation

class Basin:

    def __init__(self, som_representation: SomRepresentation, random_seed=None, verbose=False):
        self.som_representation = som_representation
        self.random_seed = random_seed
        self.verbose = verbose

    @classmethod
    def from_data(cls, X, **kwargs):
        som_representation = SomRepresentation.with_derived_params(X, **kwargs).fit(X)
        return cls(som_representation, **kwargs)

    @classmethod
    def from_som_representation(cls, som_representation: SomRepresentation, **kwargs):
        return cls(som_representation, **kwargs)

    def legacy_pond(self):
        from lilypond.legacy_pond import LegacyPond
        return LegacyPond(self, verbose=self.verbose)

    def pond(self, base_style:Literal["pond", "iceflock"] | PondBaseStyle="pond"):
        from lilypond.pond import Pond
        return Pond(self, base_style=base_style, verbose=self.verbose)

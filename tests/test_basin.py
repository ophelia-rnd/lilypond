import numpy as np
import pytest
from lilypond.basin import Basin
from lilypond.legacy_pond import LegacyPond
from lilypond.pond import Pond


@pytest.fixture
def sample_data():
    rng = np.random.default_rng(42)
    return rng.standard_normal((30, 4))


def test_basin_from_data_online(sample_data):
    basin = Basin.from_data_online(sample_data, random_seed=42, verbose=True)
    assert basin.som_representation is not None
    assert basin.random_seed == 42
    assert basin.verbose


def test_basin_from_data_offline(sample_data):
    basin = Basin.from_data_offline(sample_data, random_seed=42, verbose=True)
    assert basin.som_representation is not None
    assert basin.random_seed == 42
    assert basin.verbose


def test_basin_from_som_representation(sample_data):
    from minisom_representation import SomRepresentation
    som_rep = SomRepresentation.with_derived_params(sample_data, random_seed=42).fit_online(sample_data)
    basin = Basin.from_som_representation(
        som_rep,
        random_seed=42,
        verbose=True,
    )
    assert basin.som_representation is not None
    assert basin.random_seed == 42
    assert basin.verbose


def test_basin_hyperparameters(sample_data):
    basin = Basin.from_data_online(
        sample_data,
        learning_rate=0.2,
        sigma=1.2,
        random_seed=42,
        verbose=True,
    )
    assert basin.som_representation is not None
    assert basin.som_representation.learning_rate == 0.2
    assert basin.som_representation.sigma == 1.2


def test_basin_spawn_pond_and_legacy(sample_data):
    basin = Basin.from_data_online(sample_data)

    pond = basin.pond()
    assert isinstance(pond, Pond)

    legacy_pond = basin.legacy_pond()
    assert isinstance(legacy_pond, LegacyPond)

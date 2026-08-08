import numpy as np

from minisom import MiniSom
from lilypond.utils.som_hyperparameter import calc_som_hyparams

class SomRepresentation():

    def __init__(self, d1, d2, sigma, topology="rectangular", learning_rate=0.5, num_iteration=20,
                    decay_function="asymptotic_decay", sigma_decay_function="asymptotic_decay",
                    neighborhood_function='gaussian', activation_distance='euclidean',
                    use_epochs=True, random_order=True, random_seed=None, verbose=False):
        self.d1 = d1
        self.d2 = d2
        self.sigma = sigma
        self.topology = topology
        self.learning_rate = learning_rate
        self.num_iteration = num_iteration
        self.decay_function = decay_function
        self.sigma_decay_function = sigma_decay_function
        self.neighborhood_function = neighborhood_function
        self.activation_distance = activation_distance
        self.use_epochs = use_epochs
        self.random_order = random_order
        self.random_seed = random_seed
        self.verbose = verbose

    @classmethod
    def with_derived_params(cls, X, random_seed=None, verbose=False, **kwargs):
        """Derives d1, d2, sigma from X, forwarding any extra overrides to __init__."""
        derived_params = calc_som_hyparams(X, verbose=verbose)
        return cls(random_seed=random_seed, verbose=verbose, **{**derived_params, **kwargs})

    @property
    def som(self):
        return self.som_

    def fit(self, X):
        self.X_ = X

        som_hyperparams = {
            "input_len": X.shape[1],
            "x": self.d1,
            "y": self.d2,
            "sigma": self.sigma,
            "topology": self.topology,
            "learning_rate": self.learning_rate,
            "decay_function": self.decay_function,
            "sigma_decay_function": self.sigma_decay_function,
            "neighborhood_function": self.neighborhood_function,
            "activation_distance": self.activation_distance,
            "random_seed": self.random_seed
        }

        som_fit_hyperparams = {
            "num_iteration": self.num_iteration,
            "random_order": self.random_order,
            "use_epochs": self.use_epochs,
            "verbose": self.verbose
        }

        som = self.__train_som(X, som_hyperparams, som_fit_hyperparams)

        if self.verbose:
            print("\nFinal hyperparameters of SOM:")
            print({
                **som_hyperparams,
                **som_fit_hyperparams
            })

            QE, TE, QE_ROUNDED, TE_ROUNDED = self.__som_quality(som, X)
            print("\nQuality of SOM:")
            print(f"Quantization error:\t{QE}")
            print(f"Topographic error:\t{TE}")
            print(f"Quantization error (rounded):\t{QE_ROUNDED}")
            print(f"Topographic error (rounded):\t{TE_ROUNDED}")

        self.som_ = som

        return self

    def __train_som(self, X, hyperparams, fit_hyperparams):
        som = MiniSom(**hyperparams)
        som.random_weights_init(X)
        som.train(X, **fit_hyperparams)
        return som

    def __som_quality(self, som:MiniSom, X, digits=3):
        QE = som.quantization_error(X)
        TE = som.topographic_error(X)
        return QE, TE, np.round(QE, digits), np.round(TE, digits)

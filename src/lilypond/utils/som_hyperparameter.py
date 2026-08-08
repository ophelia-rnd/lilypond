import numpy as np

def calc_recommended_total_node_count(X):
    N = len(X)
    M = int(np.ceil(5 * np.sqrt(N)))
    return M

def calc_recommended_lattice_side_ratio(X):
    cov = np.cov(X, rowvar=False)
    eigvals = np.linalg.eigvalsh(cov)
    eigvals = np.sort(eigvals)[::-1]
    lambdas = eigvals[:2]
    lambdas = np.clip(lambdas, a_min=1, a_max=None)
    lambda1, lambda2 = lambdas
    ratio = np.sqrt(lambda1 / lambda2)
    return ratio

def calc_recommended_lattice_sides(X):
    M = calc_recommended_total_node_count(X)
    ratio = calc_recommended_lattice_side_ratio(X)
    height = int(np.ceil(np.sqrt(M / ratio)))
    width = int(np.ceil(ratio * height))
    return height, width

def calc_initial_sigma(d1, d2, factor=2.0):
    L = max(d1, d2)
    if L <= 1: return 1.0
    return np.round(L / factor, 2)

def calc_som_hyparams(X, verbose=False):
    total_node_count = calc_recommended_total_node_count(X)
    height, width = calc_recommended_lattice_sides(X)
    initial_sigma = calc_initial_sigma(height, width)

    hyperparams = {
        "d1": height,
        "d2": width,
        "sigma": initial_sigma,
    }

    if verbose:
        print("\n--------------")
        print(f"Based on {len(X)} instances, the recommended SOM hyperparameters are the following:")
        print("Total node count (M):\t", total_node_count)
        print("Recommended sides (d1 x d2):\t", f"{height} x {width}")
        print("Initial neighborhood radius (sigma):\t", initial_sigma)
        print("--------------\n")

    return hyperparams

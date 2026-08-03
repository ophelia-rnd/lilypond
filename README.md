<div align="left">
    <img width="80px" alt="Lilypond logo" src="_assets/lilypond_logo.png" />
    <img height="80px" alt="Ophelia R&D logo" src="_assets/ophelia_rnd_logo.png" />
</div>

---

# Lilypond

🪷 Lilypond is an intuitive visualization tool for high-dimensional data using Self-Organizing Maps (SOM).

Lilypond uses [MiniSom](https://github.com/JustGlowing/minisom) for fitting the data and [Plotly](https://plotly.com/) for rendering,
adding nature-inspired visual enhancements to standard Self-Organizing Map plots.

This repository is a successor of the [Matplotlib](https://matplotlib.org)-based prototype library developed at [matthew-balogh/lilypond](https://github.com/matthew-balogh/lilypond).

## Quick Start

```
pip install git+https://github.com/ophelia-rnd/lilypond
```

```python
from lilypond import Basin
# Given dataset X

# prepare for the pond with a `Basin`
basin = Basin.from_data(X, random_seed=42, verbose=True).prepare()

# display the legacy visualization
basin.legacy_pond.visualize_distance_map();

# display the enhanced visualization
basin.pond.visualize_distance_map();
```
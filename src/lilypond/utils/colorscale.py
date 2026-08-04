import plotly.express as px

def get_truncated_colorscale(colorscale:str, clip_interval):
    color_seq = getattr(px.colors.sequential, colorscale)

    low_frac, high_frac = clip_interval
    low_frac = max(0.0, min(1.0, low_frac))
    high_frac = max(0.0, min(1.0, high_frac))

    assert low_frac <= high_frac, "clip_interval[0] must be strictly less than clip_interval[1]"

    n_colors = len(color_seq)
    start_idx = int(round(low_frac * (n_colors - 1)))
    end_idx = int(round(high_frac * (n_colors - 1))) + 1

    sliced_colors = color_seq[start_idx:end_idx]
    if len(sliced_colors) < 2:
        sliced_colors = color_seq[start_idx : min(start_idx + 2, n_colors)]

    n_sliced = len(sliced_colors)
    truncated_colorscale = [
        [i / (n_sliced - 1), color] for i, color in enumerate(sliced_colors)
    ]

    return truncated_colorscale

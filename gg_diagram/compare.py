"""
Side-by-side and overlay comparison of GG diagrams.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from gg_diagram.plot import gg_heatmap


def gg_compare(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    ax_col: str = "ax_mps2",
    ay_col: str = "ay_mps2",
    speed_col: str | None = "speed_mps",
    ts_col: str | None = "ts",
    hz: float = 10.0,
    distance_weighted: bool = True,
    range_mg: float = 1000.0,
    bin_size_mg: float = 20.0,
    title_before: str = "Before",
    title_after: str = "After",
    colorscale: str = "Jet",
    width: int = 1200,
    height: int = 600,
    unit: str | None = None,
) -> go.Figure:
    """Create a side-by-side comparison of two GG heatmaps.

    Parameters
    ----------
    df_before, df_after : DataFrame
        Data for the two trips / conditions to compare.
    ax_col, ay_col : str
        Acceleration column names.
    speed_col : str or None
        Speed column name (m/s).
    ts_col : str or None
        Timestamp column name.
    hz : float
        Sampling frequency fallback.
    distance_weighted : bool
        Use distance weighting.
    range_mg : float
        Axis half-range in mG.
    bin_size_mg : float
        Bin width in mG.
    title_before, title_after : str
        Subplot titles.
    colorscale : str
        Plotly colorscale.
    width, height : int
        Figure dimensions.
    unit : str or None
        Acceleration unit (auto-detected if None).

    Returns
    -------
    plotly.graph_objects.Figure
        A figure with two subplots side by side.
    """
    fig_a = gg_heatmap(
        df_before,
        ax_col=ax_col, ay_col=ay_col,
        speed_col=speed_col, ts_col=ts_col, hz=hz,
        distance_weighted=distance_weighted,
        range_mg=range_mg, bin_size_mg=bin_size_mg,
        title=title_before, colorscale=colorscale,
        unit=unit,
    )
    fig_b = gg_heatmap(
        df_after,
        ax_col=ax_col, ay_col=ay_col,
        speed_col=speed_col, ts_col=ts_col, hz=hz,
        distance_weighted=distance_weighted,
        range_mg=range_mg, bin_size_mg=bin_size_mg,
        title=title_after, colorscale=colorscale,
        unit=unit,
    )

    combined = make_subplots(
        rows=1, cols=2,
        subplot_titles=[title_before, title_after],
        horizontal_spacing=0.08,
    )

    for trace in fig_a.data:
        combined.add_trace(trace, row=1, col=1)
    for trace in fig_b.data:
        combined.add_trace(trace, row=1, col=2)

    combined.update_xaxes(
        title_text="Lateral accel (mG)",
        range=[-range_mg, range_mg],
        row=1, col=1,
    )
    combined.update_xaxes(
        title_text="Lateral accel (mG)",
        range=[-range_mg, range_mg],
        row=1, col=2,
    )
    combined.update_yaxes(
        title_text="Longitudinal accel (mG)",
        range=[-range_mg, range_mg],
        row=1, col=1,
    )
    combined.update_yaxes(
        title_text="Longitudinal accel (mG)",
        range=[-range_mg, range_mg],
        row=1, col=2,
    )

    combined.update_layout(
        width=width,
        height=height,
        margin=dict(l=60, r=20, t=60, b=60),
    )

    # Attach metadata from both
    combined._gg_meta = {
        "before": getattr(fig_a, "_gg_meta", {}),
        "after": getattr(fig_b, "_gg_meta", {}),
    }

    return combined

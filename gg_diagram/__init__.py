"""
GG Diagram - Vehicle dynamics acceleration heatmap visualization.

Plot lateral vs longitudinal acceleration (Gx vs Gy) as heatmaps,
scatter plots, and comparison overlays. Based on the GG diagram concept
from Milliken & Milliken's *Race Car Vehicle Dynamics*.
"""

__version__ = "0.1.0"

from gg_diagram.plot import gg_heatmap, gg_scatter
from gg_diagram.compare import gg_compare
from gg_diagram.io import load_csv, load_parquet

__all__ = [
    "gg_heatmap",
    "gg_scatter",
    "gg_compare",
    "load_csv",
    "load_parquet",
]

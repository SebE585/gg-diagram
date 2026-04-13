"""
GG Diagram - Vehicle dynamics acceleration heatmap visualization.

Plot lateral vs longitudinal acceleration (Gx vs Gy) as heatmaps,
scatter plots, and comparison overlays. Based on the GG diagram concept
from Milliken & Milliken's *Race Car Vehicle Dynamics*.
"""

__version__ = "0.2.0"

# gg_compare est canoniquement défini dans plot.py (coloraxis partagé,
# contour, layout équilibré). compare.py contenait une variante plus
# ancienne avec un bug (les Heatmap traces copiées entre subplots
# perdaient leur xref/yref → rendu vide). Supprimé en 0.2.0.
from gg_diagram.plot import gg_heatmap, gg_scatter, gg_compare
from gg_diagram.io import load_csv, load_parquet

__all__ = [
    "gg_heatmap",
    "gg_scatter",
    "gg_compare",
    "load_csv",
    "load_parquet",
]

"""
Core computation for distance-weighted 2D histograms.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

G = 9.80665  # m/s^2


def detect_unit(series: pd.Series | np.ndarray, col_name: str = "") -> str:
    """Heuristic unit detection for acceleration columns.

    Returns
    -------
    str
        One of ``"mps2"`` (m/s^2), ``"g"`` (multiples of g), or ``"mg"`` (milli-g).
    """
    arr = np.asarray(series, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return "mps2"

    p99 = np.percentile(np.abs(arr), 99)

    # Typical ranges:
    # m/s^2 -> peak ~10-15
    # g -> peak ~1-1.5
    # mG -> peak ~1000-1500
    if p99 > 50:
        return "mg"
    elif p99 > 3:
        return "mps2"
    else:
        return "g"


def to_mg(values: np.ndarray, unit: str) -> np.ndarray:
    """Convert acceleration values to milli-g."""
    if unit == "mps2":
        return (values / G) * 1000.0
    elif unit == "g":
        return values * 1000.0
    elif unit == "mg":
        return values.copy()
    else:
        raise ValueError(f"Unknown unit: {unit!r}. Expected 'mps2', 'g', or 'mg'.")


def compute_dt(df: pd.DataFrame, ts_col: str | None, hz: float) -> np.ndarray:
    """Compute per-sample time delta from timestamps or fixed frequency.

    Parameters
    ----------
    df : DataFrame
        Input data.
    ts_col : str or None
        Timestamp column name. If *None* or absent, falls back to ``hz``.
    hz : float
        Assumed fixed frequency (used when no timestamp column is found).

    Returns
    -------
    np.ndarray
        Time deltas in seconds, one per row.
    """
    if ts_col and ts_col in df.columns:
        ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
        dt_array = ts.diff().dt.total_seconds().fillna(1.0 / hz).values
        return np.clip(dt_array, 0, 2.0)
    return np.full(len(df), 1.0 / hz)


def compute_distance_weights(
    speed: np.ndarray | None,
    dt: np.ndarray,
) -> np.ndarray:
    """Compute distance weights: ``|speed| * dt``.

    If *speed* is None, returns uniform weights (equal to *dt*).
    """
    if speed is None:
        return dt.copy()
    return np.abs(speed) * dt


def build_histogram(
    ax_mg: np.ndarray,
    ay_mg: np.ndarray,
    weights: np.ndarray,
    range_mg: float = 1000.0,
    bin_size_mg: float = 20.0,
    speed: np.ndarray | None = None,
    min_speed: float = 0.5,
) -> dict:
    """Build a 2D histogram of lateral vs longitudinal acceleration.

    Parameters
    ----------
    ax_mg, ay_mg : array
        Longitudinal and lateral acceleration in milli-g.
    weights : array
        Per-sample weights (typically distance in metres).
    range_mg : float
        Half-range of the axes in mG.
    bin_size_mg : float
        Bin width in mG.
    speed : array or None
        Speed in m/s, used for filtering stationary points.
    min_speed : float
        Minimum speed threshold (m/s).

    Returns
    -------
    dict
        ``hist`` (2D array), ``hist_log`` (log10), ``xcenters``, ``ycenters``,
        ``xedges``, ``yedges``, ``total_distance``, ``std_gx``, ``std_gy``.
    """
    # Validity mask
    finite = np.isfinite(ax_mg) & np.isfinite(ay_mg) & np.isfinite(weights)
    in_range = (np.abs(ax_mg) <= range_mg * 1.5) & (np.abs(ay_mg) <= range_mg * 1.5)
    mask = finite & in_range

    if speed is not None:
        mask &= np.abs(speed) > min_speed

    ax_v = ax_mg[mask]
    ay_v = ay_mg[mask]
    w = weights[mask]

    n_bins = int(2 * range_mg / bin_size_mg) + 1
    edges = np.linspace(-range_mg, range_mg, n_bins + 1)

    # Convention: X axis = lateral (ay), Y axis = longitudinal (ax)
    hist, xedges, yedges = np.histogram2d(
        ay_v, ax_v,
        bins=[edges, edges],
        weights=w,
    )

    hist_log = hist.copy()
    hist_log[hist_log == 0] = np.nan
    hist_log = np.log10(hist_log)

    xcenters = (xedges[:-1] + xedges[1:]) / 2
    ycenters = (yedges[:-1] + yedges[1:]) / 2

    # Severity metrics
    total_w = w.sum()
    if total_w > 0:
        ax_g = ax_v / 1000.0
        ay_g = ay_v / 1000.0
        mean_gx = np.sum(w * ax_g) / total_w
        mean_gy = np.sum(w * ay_g) / total_w
        std_gx = float(np.sqrt(np.sum(w * (ax_g - mean_gx) ** 2) / total_w))
        std_gy = float(np.sqrt(np.sum(w * (ay_g - mean_gy) ** 2) / total_w))
    else:
        std_gx = std_gy = 0.0

    return {
        "hist": hist,
        "hist_log": hist_log,
        "xcenters": xcenters,
        "ycenters": ycenters,
        "xedges": xedges,
        "yedges": yedges,
        "total_distance": float(w.sum()),
        "std_gx": std_gx,
        "std_gy": std_gy,
        "n_valid": int(mask.sum()),
    }

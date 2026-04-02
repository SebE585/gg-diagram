"""
Data loading utilities for common file formats.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def _resolve_columns(
    df: pd.DataFrame,
    ax_col: str | None,
    ay_col: str | None,
    speed_col: str | None,
    ts_col: str | None,
) -> dict[str, str | None]:
    """Try to auto-resolve common column names."""
    ax_candidates = [ax_col, "acc_x", "ax", "ax_mps2", "accel_x", "lon_accel", "gx"]
    ay_candidates = [ay_col, "acc_y", "ay", "ay_mps2", "accel_y", "lat_accel", "gy"]
    speed_candidates = [speed_col, "speed", "speed_mps", "v", "velocity"]
    ts_candidates = [ts_col, "ts", "timestamp", "time", "datetime", "t"]

    def _pick(candidates):
        for c in candidates:
            if c and c in df.columns:
                return c
        return None

    return {
        "ax_col": _pick(ax_candidates),
        "ay_col": _pick(ay_candidates),
        "speed_col": _pick(speed_candidates),
        "ts_col": _pick(ts_candidates),
    }


def load_csv(
    path: str | Path,
    ax_col: str | None = None,
    ay_col: str | None = None,
    speed_col: str | None = None,
    ts_col: str | None = None,
    **read_kwargs,
) -> tuple[pd.DataFrame, dict[str, str | None]]:
    """Load a CSV file and auto-detect acceleration / speed columns.

    Parameters
    ----------
    path : str or Path
        Path to the CSV file.
    ax_col, ay_col, speed_col, ts_col : str or None
        Explicit column names. If None, the loader tries common names.
    **read_kwargs
        Extra keyword arguments forwarded to ``pd.read_csv``.

    Returns
    -------
    tuple[DataFrame, dict]
        The loaded DataFrame and a dict of resolved column names
        (keys: ``ax_col``, ``ay_col``, ``speed_col``, ``ts_col``).
    """
    df = pd.read_csv(path, **read_kwargs)
    cols = _resolve_columns(df, ax_col, ay_col, speed_col, ts_col)
    return df, cols


def load_parquet(
    path: str | Path,
    ax_col: str | None = None,
    ay_col: str | None = None,
    speed_col: str | None = None,
    ts_col: str | None = None,
    **read_kwargs,
) -> tuple[pd.DataFrame, dict[str, str | None]]:
    """Load a Parquet file and auto-detect columns.

    Parameters
    ----------
    path : str or Path
        Path to the Parquet file.
    ax_col, ay_col, speed_col, ts_col : str or None
        Explicit column names. Auto-detected if None.
    **read_kwargs
        Extra keyword arguments forwarded to ``pd.read_parquet``.

    Returns
    -------
    tuple[DataFrame, dict]
        The loaded DataFrame and resolved column names.
    """
    df = pd.read_parquet(path, **read_kwargs)
    cols = _resolve_columns(df, ax_col, ay_col, speed_col, ts_col)
    return df, cols

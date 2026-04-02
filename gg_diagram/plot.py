"""
GG Diagram — Publication-quality heatmap visualization (V2).

Solo and side-by-side comparison modes.
Style inspired by SAE/automotive publications.

V2 changes:
  - Directional labels on axes (Right Turn / Left Turn / Braking / Acceleration)
  - External contour (envelope of occupied domain)
  - Softer low-end palette (white → very pale blue → cyan)
  - Clearer title/subtitle hierarchy
  - Compare: Y label left only, more spacing, finer colorbar
  - mode="paper" vs mode="interactive"
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


G = 9.80665

# ── Colorscale V2 ────────────────────────────────────────────────────────

def _soft_jet_v2():
    """Low-end très proche du blanc pour distinguer vide/très faible/présence."""
    return [
        [0.00, "#f7fbff"],   # quasi-blanc
        [0.05, "#eef5fc"],   # blanc bleuté
        [0.12, "#d4e6f8"],   # bleu très pâle
        [0.22, "#9dcae1"],   # bleu clair
        [0.35, "#4ea3ff"],   # bleu
        [0.50, "#56c271"],   # vert
        [0.64, "#d7df4a"],   # jaune-vert
        [0.78, "#f4b247"],   # orange
        [0.90, "#ea6b3c"],   # orange-rouge
        [1.00, "#b40426"],   # rouge foncé
    ]


# ── Axis labels ──────────────────────────────────────────────────────────

X_LABEL = "\u2190 Right Turn \u2502 gamma Y (g) \u2502 Left Turn \u2192"
Y_LABEL = "\u2190 Braking \u2502 gamma X (g) \u2502 Acceleration \u2192"


def _axis_style(title=None, is_paper=False):
    font_size = 11 if is_paper else 12
    return dict(
        title=dict(text=title, font=dict(size=13 if is_paper else 14, family="Arial")) if title else None,
        range=[-1.0, 1.0],
        tickmode="array",
        tickvals=[-1.0, -0.5, 0.0, 0.5, 1.0],
        ticktext=["-1.0", "-0.5", "0", "0.5", "1.0"],
        ticks="outside", ticklen=5, tickwidth=1, tickcolor="#333",
        tickfont=dict(size=font_size),
        showline=True, linewidth=1.2, linecolor="#333", mirror=False,
        showgrid=True, gridcolor="rgba(0,0,0,0.07)", gridwidth=0.8,
        zeroline=True, zerolinecolor="rgba(0,0,0,0.45)", zerolinewidth=1.3,
    )


def _add_guides(fig, row=1, col=1):
    """Faint dotted crosshairs at ±0.5g."""
    for v in (-0.5, 0.5):
        fig.add_vline(x=v, line_width=0.6, line_dash="dot",
                      line_color="rgba(0,0,0,0.12)", row=row, col=col)
        fig.add_hline(y=v, line_width=0.6, line_dash="dot",
                      line_color="rgba(0,0,0,0.12)", row=row, col=col)


def _add_contour(fig, h_log, xc, yc, row=None, col=None):
    """Add a thin external contour showing the envelope of the occupied domain."""
    mask = np.isfinite(h_log) & (h_log > 0)
    if not mask.any():
        return
    binary = np.where(mask, 1.0, 0.0)
    trace = go.Contour(
        z=binary, x=xc, y=yc,
        contours=dict(start=0.5, end=0.5, size=1, coloring="none"),
        line=dict(color="rgba(60,60,60,0.30)", width=1.0),
        showscale=False, hoverinfo="skip",
    )
    if row is not None and col is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)


# ── Heatmap trace ────────────────────────────────────────────────────────

def _heatmap_trace(h_log, xc, yc, zmin, zmax, coloraxis=None, showscale=True,
                   is_paper=False):
    hover = ("Lat: %{x:.3f} g<br>Long: %{y:.3f} g<br>"
             "log\u2081\u2080(dist): %{z:.2f}<extra></extra>")
    if is_paper:
        hover = None

    kw = dict(
        z=h_log, x=xc, y=yc, zmin=zmin, zmax=zmax,
        colorscale=_soft_jet_v2(), hoverongaps=False,
    )
    if hover:
        kw["hovertemplate"] = hover

    if coloraxis:
        kw["coloraxis"] = coloraxis
        kw["showscale"] = False
    else:
        kw["showscale"] = showscale
        kw["colorbar"] = dict(
            title=dict(text="Distance (m, log\u2081\u2080)", side="right",
                       font=dict(size=12, family="Arial")),
            tickfont=dict(size=10), thickness=14, len=0.82,
            outlinewidth=0.6, outlinecolor="rgba(0,0,0,0.25)",
        )
    return go.Heatmap(**kw)


# ── Data preparation ─────────────────────────────────────────────────────

def _prepare_data(df, ax_col, ay_col, speed_col, ts_col, hz, range_g=1.0, bin_g=0.02):
    ax_raw = df[ax_col].to_numpy(dtype=float)
    ay_raw = df[ay_col].to_numpy(dtype=float)

    speed = None
    for c in ([speed_col] if speed_col else []) + ["speed_mps", "speed"]:
        if c and c in df.columns:
            speed = df[c].to_numpy(dtype=float)
            break

    if ts_col and ts_col in df.columns:
        ts = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
        dt = np.clip(ts.diff().dt.total_seconds().fillna(1 / hz).values, 0, 2)
    else:
        dt = np.full(len(df), 1 / hz)

    dist = np.abs(speed) * dt if speed is not None else dt
    ax_g = ax_raw / G
    ay_g = ay_raw / G

    moving = np.abs(speed) > 0.5 if speed is not None else np.ones(len(df), dtype=bool)
    finite = np.isfinite(ax_g) & np.isfinite(ay_g) & np.isfinite(dist)
    in_range = (np.abs(ax_g) <= range_g * 1.5) & (np.abs(ay_g) <= range_g * 1.5)
    valid = moving & finite & in_range

    # Convention: X = lateral (ay), Y = longitudinal (ax)
    lat_v, lon_v, dist_v = ay_g[valid], ax_g[valid], dist[valid]
    edges = np.linspace(-range_g, range_g, int(2 * range_g / bin_g) + 2)
    h, xe, ye = np.histogram2d(lat_v, lon_v, bins=[edges, edges], weights=dist_v)
    h[h == 0] = np.nan
    h_log = np.log10(h)
    xc = (xe[:-1] + xe[1:]) / 2
    yc = (ye[:-1] + ye[1:]) / 2

    w = dist_v
    tw = w.sum()
    if tw > 0:
        std_gx = float(np.sqrt(np.sum(w * (lon_v - np.sum(w * lon_v) / tw) ** 2) / tw))
        std_gy = float(np.sqrt(np.sum(w * (lat_v - np.sum(w * lat_v) / tw) ** 2) / tw))
    else:
        std_gx = std_gy = 0.0

    return h_log.T, xc, yc, std_gx, std_gy, tw / 1000


# ── Public API ───────────────────────────────────────────────────────────

def gg_heatmap(
    df,
    ax_col: str = "ax_mps2",
    ay_col: str = "ay_mps2",
    speed_col: str | None = "speed_mps",
    ts_col: str | None = "ts",
    hz: float = 10.0,
    title: str = "g-g Diagram",
    mode: str = "interactive",
    width: int = 820,
    height: int = 820,
    output_html: str | None = None,
    **kwargs,
) -> go.Figure:
    """Single GG heatmap, publication quality.

    Parameters
    ----------
    mode : str
        ``"interactive"`` (rich hover, larger fonts) or
        ``"paper"`` (compact, thinner lines, optimized for export).
    """
    is_paper = mode == "paper"
    h_log, xc, yc, std_gx, std_gy, km = _prepare_data(
        df, ax_col, ay_col, speed_col, ts_col, hz)
    zmax = np.nanmax(h_log) if np.any(np.isfinite(h_log)) else 4

    fig = go.Figure()
    fig.add_trace(_heatmap_trace(h_log, xc, yc, 0, zmax, is_paper=is_paper))
    _add_contour(fig, h_log, xc, yc)

    sub = f"<span style='font-size:0.75em; color:#777;'>Std Gx = {std_gx:.5f} g  \u2502  Std Gy = {std_gy:.5f} g  \u2502  {km:.0f} km</span>"
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b><br>{sub}",
            x=0.5, xanchor="center", y=0.97, yanchor="top",
            font=dict(family="Arial", size=18 if is_paper else 20)),
        font=dict(family="Arial", size=12 if is_paper else 14),
        paper_bgcolor="white", plot_bgcolor="white",
        width=width, height=height,
        margin=dict(l=85, r=80, t=100, b=80),
    )
    fig.update_xaxes(**_axis_style(X_LABEL, is_paper))
    fig.update_yaxes(**_axis_style(Y_LABEL, is_paper), scaleanchor="x", scaleratio=1)
    _add_guides(fig)

    fig._gg_meta = {"std_gx": std_gx, "std_gy": std_gy, "total_distance_km": km}
    if output_html:
        fig.write_html(output_html, include_plotlyjs="cdn")
    return fig


def gg_compare(
    df_before,
    df_after,
    ax_col: str = "ax_mps2",
    ay_col: str = "ay_mps2",
    speed_col: str | None = "speed_mps",
    ts_col: str | None = "ts",
    hz: float = 10.0,
    title_before: str = "Before",
    title_after: str = "After",
    main_title: str = "g-g Diagram Comparison",
    mode: str = "interactive",
    width: int = 1350,
    height: int = 720,
    output_html: str | None = None,
    **kwargs,
) -> go.Figure:
    """Side-by-side GG comparison, shared color axis."""
    is_paper = mode == "paper"
    h_a, xc, yc, sx_a, sy_a, km_a = _prepare_data(
        df_before, ax_col, ay_col, speed_col, ts_col, hz)
    h_b, _, _, sx_b, sy_b, km_b = _prepare_data(
        df_after, ax_col, ay_col, speed_col, ts_col, hz)
    zmax = max(
        np.nanmax(h_a) if np.any(np.isfinite(h_a)) else 4,
        np.nanmax(h_b) if np.any(np.isfinite(h_b)) else 4)

    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.12,
        subplot_titles=[
            f"<b>{title_before}</b><br>"
            f"<span style='font-size:0.78em;color:#777'>Std Gx={sx_a:.5f}g | Std Gy={sy_a:.5f}g | {km_a:.0f}km</span>",
            f"<b>{title_after}</b><br>"
            f"<span style='font-size:0.78em;color:#777'>Std Gx={sx_b:.5f}g | Std Gy={sy_b:.5f}g | {km_b:.0f}km</span>",
        ])

    fig.add_trace(_heatmap_trace(h_a, xc, yc, 0, zmax, coloraxis="coloraxis", is_paper=is_paper), row=1, col=1)
    fig.add_trace(_heatmap_trace(h_b, xc, yc, 0, zmax, coloraxis="coloraxis", is_paper=is_paper), row=1, col=2)
    _add_contour(fig, h_a, xc, yc, row=1, col=1)
    _add_contour(fig, h_b, xc, yc, row=1, col=2)

    fig.update_layout(
        title=dict(
            text=f"<b>{main_title}</b>",
            x=0.5, xanchor="center", y=0.98, yanchor="top",
            font=dict(family="Arial", size=18 if is_paper else 20)),
        font=dict(family="Arial", size=12 if is_paper else 13),
        paper_bgcolor="white", plot_bgcolor="white",
        width=width, height=height,
        margin=dict(l=85, r=85, t=100, b=80),
        coloraxis=dict(
            cmin=0, cmax=zmax, colorscale=_soft_jet_v2(),
            colorbar=dict(
                title=dict(text="Distance (m, log\u2081\u2080)", side="right",
                           font=dict(size=12, family="Arial")),
                tickfont=dict(size=10), thickness=12, len=0.78,
                x=1.04, y=0.5,
                outlinewidth=0.5, outlinecolor="rgba(0,0,0,0.2)")),
    )

    # Left panel: full axes
    fig.update_xaxes(**_axis_style(X_LABEL, is_paper), row=1, col=1)
    fig.update_yaxes(**_axis_style(Y_LABEL, is_paper), row=1, col=1)
    # Right panel: X label, no Y label
    fig.update_xaxes(**_axis_style(X_LABEL, is_paper), row=1, col=2)
    fig.update_yaxes(**_axis_style(None, is_paper), row=1, col=2)

    for col in [1, 2]:
        _add_guides(fig, row=1, col=col)

    fig.update_yaxes(scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_yaxes(scaleanchor="x2", scaleratio=1, row=1, col=2)
    fig.update_annotations(font=dict(family="Arial", size=13))

    if output_html:
        fig.write_html(output_html, include_plotlyjs="cdn")
    return fig


def gg_scatter(
    df,
    ax_col: str = "ax_mps2",
    ay_col: str = "ay_mps2",
    color_col: str | None = None,
    speed_col: str | None = "speed_mps",
    title: str = "g-g Scatter",
    width: int = 700,
    height: int = 700,
    **kwargs,
) -> go.Figure:
    """GG scatter plot."""
    ax_g = df[ax_col].to_numpy(dtype=float) / G
    ay_g = df[ay_col].to_numpy(dtype=float) / G

    marker_kw = dict(size=3, opacity=0.4)
    if color_col and color_col in df.columns:
        marker_kw.update(color=df[color_col].to_numpy(dtype=float),
                         colorscale="Viridis", colorbar=dict(title=color_col))
    elif speed_col and speed_col in df.columns:
        marker_kw.update(color=df[speed_col].to_numpy(dtype=float),
                         colorscale="Viridis", colorbar=dict(title="Speed (m/s)"))

    fig = go.Figure(data=go.Scattergl(x=ay_g, y=ax_g, mode="markers", marker=marker_kw))
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(family="Arial", size=18)),
        font=dict(family="Arial", size=14),
        paper_bgcolor="white", plot_bgcolor="white",
        width=width, height=height, margin=dict(l=80, r=30, t=60, b=70))
    fig.update_xaxes(**_axis_style(X_LABEL))
    fig.update_yaxes(**_axis_style(Y_LABEL), scaleanchor="x", scaleratio=1)
    _add_guides(fig)
    return fig

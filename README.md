# GG Diagram

**Vehicle dynamics acceleration heatmap visualization** -- plot lateral vs longitudinal acceleration (Gx vs Gy) as distance-weighted heatmaps.

Based on the GG diagram concept from Milliken & Milliken's *Race Car Vehicle Dynamics* (1995). The GG diagram is the standard way to visualize a vehicle's acceleration envelope and driving severity.

Inspired by vehicle dynamics research at [RoadSimulator3](https://research.roadsimulator3.fr).

## Features

- **Distance-weighted heatmaps** -- bins weighted by distance travelled, not just sample count
- **Scatter plots** -- coloured by speed or any custom column
- **Side-by-side comparison** -- compare before/after calibration or two different trips
- **Auto unit detection** -- handles m/s^2, g, and milli-g inputs automatically
- **Variable frequency support** -- auto-detects dt from timestamps
- **Clean Plotly output** -- interactive, exportable figures

## Installation

```bash
pip install gg-diagram
```

Or install from source:

```bash
git clone https://github.com/roadsimulator3/gg-diagram.git
cd gg-diagram
pip install -e .
```

## Quick start

```python
import pandas as pd
from gg_diagram import gg_heatmap, gg_scatter

# Load your telemetry data
df = pd.read_csv("my_trip.csv")

# Distance-weighted heatmap
fig = gg_heatmap(df, ax_col="acc_x", ay_col="acc_y", speed_col="speed")
fig.show()

# Scatter plot coloured by speed
fig = gg_scatter(df, ax_col="acc_x", ay_col="acc_y")
fig.show()
```

### Compare two trips

```python
from gg_diagram import gg_compare

fig = gg_compare(
    df_before, df_after,
    ax_col="acc_x", ay_col="acc_y",
    title_before="Before calibration",
    title_after="After calibration",
)
fig.show()
```

### Load data with auto-detected columns

```python
from gg_diagram import load_csv

df, cols = load_csv("my_trip.csv")
print(cols)  # {'ax_col': 'acc_x', 'ay_col': 'acc_y', 'speed_col': 'speed', 'ts_col': 'ts'}

fig = gg_heatmap(df, **cols)
fig.show()
```

## What is a GG diagram?

A GG diagram plots longitudinal acceleration (braking/acceleration) against lateral acceleration (cornering). Each point represents an instantaneous acceleration state of the vehicle:

- **Center** = cruising at constant speed on a straight road
- **Left/Right** = cornering (lateral force)
- **Top** = accelerating
- **Bottom** = braking
- **Corners** = combined manoeuvres (e.g. braking into a turn)

Distance weighting ensures that high-speed sections (which cover more ground) are represented proportionally, giving a better picture of road severity than simple sample counts.

## API reference

### `gg_heatmap(df, ax_col, ay_col, speed_col=None, ...)`

Create a distance-weighted 2D heatmap. Returns a Plotly `Figure`.

Key parameters:
- `distance_weighted` (bool, default True) -- weight by speed x dt
- `range_mg` (float, default 1000) -- axis half-range in milli-g
- `bin_size_mg` (float, default 20) -- bin width in milli-g
- `unit` (str or None) -- force unit (`"mps2"`, `"g"`, `"mg"`), auto-detected if None

### `gg_scatter(df, ax_col, ay_col, color_col=None, ...)`

Create a scatter plot. Colour defaults to speed if available.

### `gg_compare(df_before, df_after, ...)`

Side-by-side heatmap comparison. Returns a single Plotly figure with two subplots.

### `load_csv(path, ...)` / `load_parquet(path, ...)`

Load data and auto-detect column names. Returns `(DataFrame, column_dict)`.

## RS3 and RoadSimulator3

This package is part of the open-source tooling around [RS3](https://roadsimulator3.fr), a road surface simulation platform for vehicle dynamics research. Learn more at [research.roadsimulator3.fr](https://research.roadsimulator3.fr).

## License

MIT -- see [LICENSE](LICENSE).

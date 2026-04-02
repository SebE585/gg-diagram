"""
Basic GG Diagram usage with synthetic data.
"""
import numpy as np
import pandas as pd

from gg_diagram import gg_heatmap, gg_scatter

# Generate synthetic driving data (accelerations in m/s^2)
np.random.seed(42)
n = 5000
speed = np.clip(np.random.normal(15, 5, n), 1, 40)  # m/s
acc_x = np.random.normal(0, 1.5, n)  # longitudinal, m/s^2
acc_y = np.random.normal(0, 1.0, n)  # lateral, m/s^2

df = pd.DataFrame({
    "acc_x": acc_x,
    "acc_y": acc_y,
    "speed": speed,
})

# Distance-weighted heatmap
fig_heatmap = gg_heatmap(df, ax_col="acc_x", ay_col="acc_y", speed_col="speed")
print(f"Heatmap metadata: {fig_heatmap._gg_meta}")
fig_heatmap.show()

# Scatter plot (coloured by speed)
fig_scatter = gg_scatter(df, ax_col="acc_x", ay_col="acc_y", speed_col="speed")
fig_scatter.show()

"""
Compare two trips side by side (e.g., before/after road resurfacing).
"""
import numpy as np
import pandas as pd

from gg_diagram import gg_compare

np.random.seed(42)
n = 5000

# Trip A: rougher road -> higher accelerations
df_before = pd.DataFrame({
    "acc_x": np.random.normal(0, 2.0, n),
    "acc_y": np.random.normal(0, 1.5, n),
    "speed": np.clip(np.random.normal(15, 5, n), 1, 40),
})

# Trip B: smoother road -> lower accelerations
df_after = pd.DataFrame({
    "acc_x": np.random.normal(0, 1.2, n),
    "acc_y": np.random.normal(0, 0.8, n),
    "speed": np.clip(np.random.normal(15, 5, n), 1, 40),
})

fig = gg_compare(
    df_before, df_after,
    ax_col="acc_x", ay_col="acc_y",
    title_before="Before resurfacing",
    title_after="After resurfacing",
)
fig.show()

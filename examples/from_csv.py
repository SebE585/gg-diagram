"""
Load data from a CSV file with auto-detected columns.

Usage:
    python from_csv.py path/to/your_data.csv
"""
import sys

from gg_diagram import gg_heatmap, load_csv


def main():
    if len(sys.argv) < 2:
        print("Usage: python from_csv.py <path_to_csv>")
        print()
        print("Expected CSV columns (any of these names):")
        print("  Longitudinal accel: acc_x, ax, ax_mps2, accel_x, gx")
        print("  Lateral accel:      acc_y, ay, ay_mps2, accel_y, gy")
        print("  Speed (optional):   speed, speed_mps, v, velocity")
        print("  Timestamp (opt.):   ts, timestamp, time, datetime")
        sys.exit(1)

    path = sys.argv[1]
    df, cols = load_csv(path)

    print(f"Loaded {len(df)} rows from {path}")
    print(f"Detected columns: {cols}")

    if cols["ax_col"] is None or cols["ay_col"] is None:
        print("ERROR: Could not find acceleration columns. "
              "Please specify ax_col and ay_col explicitly.")
        sys.exit(1)

    fig = gg_heatmap(df, **cols)
    fig.show()


if __name__ == "__main__":
    main()

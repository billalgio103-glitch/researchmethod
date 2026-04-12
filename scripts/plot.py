"""
plot.py  --  Generate DMA figures from SQLite database.

Produces 9 SVG figures (3 properties × 3 axes):
    build/storage_modulus_{x,y,z}.svg
    build/loss_modulus_{x,y,z}.svg
    build/tan_delta_{x,y,z}.svg

Usage:
    python scripts/plot.py build/dma.db build/
"""

import sys
import sqlite3
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SAMPLES = {
    "product_board": "Product Board",
    "solder_board":  "Solder Board",
}

AXES = ["x", "y", "z"]

PROPERTIES = {
    "storage_modulus": {
        "column": "storage_modulus",
        "ylabel": "Storage Modulus E' (Pa)",
        "title":  "Storage Modulus vs Temperature",
        "filename": "storage_modulus",
    },
    "loss_modulus": {
        "column": "loss_modulus",
        "ylabel": "Loss Modulus E'' (Pa)",
        "title":  "Loss Modulus vs Temperature",
        "filename": "loss_modulus",
    },
    "tan_delta": {
        "column": "tan_delta",
        "ylabel": "Tan Delta",
        "title":  "Tan Delta vs Temperature",
        "filename": "tan_delta",
    },
}

COLORS = {
    "product_board": "#1f77b4",  # blue
    "solder_board":  "#d62728",  # red
}

STYLE = {
    "figure.dpi": 150,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "lines.linewidth": 1.2,
}


def fetch_data(conn, sample, axis, column):
    cur = conn.execute(
        f"SELECT temperature, {column} FROM dma_measurements "
        "WHERE sample=? AND axis=? AND temperature IS NOT NULL "
        f"AND {column} IS NOT NULL "
        "ORDER BY temperature",
        (sample, axis),
    )
    rows = cur.fetchall()
    temps = [r[0] for r in rows]
    vals  = [r[1] for r in rows]
    return temps, vals


def make_figure(conn, prop, axis, out_dir):
    cfg = PROPERTIES[prop]
    col = cfg["column"]

    with plt.style.context(STYLE):
        fig, ax = plt.subplots(figsize=(7, 4))

        for sample, label in SAMPLES.items():
            temps, vals = fetch_data(conn, sample, axis, col)
            if not temps:
                print(f"  WARNING: no data for {sample}/{axis}/{col}")
                continue
            ax.plot(temps, vals, label=label, color=COLORS[sample], alpha=0.85)

        ax.set_xlabel("Temperature (°C)")
        ax.set_ylabel(cfg["ylabel"])
        ax.set_title(f"{cfg['title']}  —  {axis.upper()}-axis")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()

        out_path = os.path.join(out_dir, f"{cfg['filename']}_{axis}.svg")
        fig.savefig(out_path, format="svg")
        plt.close(fig)
        print(f"  Saved: {out_path}")


def main(db_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)

    for prop in PROPERTIES:
        for axis in AXES:
            make_figure(conn, prop, axis, out_dir)

    conn.close()
    print("\nAll figures generated.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/plot.py <db_path> <out_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

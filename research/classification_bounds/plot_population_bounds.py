#!/usr/bin/env python3
"""Plot an illustrative population cap region; optional Matplotlib/NumPy.

Original figure code, MIT under the repository terms. This is not data or power.
"""
from fractions import Fraction as F
from pathlib import Path
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir())/"tmd-classification-mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir())/"tmd-classification-fonts"))
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "tmd-classification-population-v1"
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
from classification_bounds import population_arm


def main():
    result = population_arm(
        {"W": "1/6", "A": "1/2", "M": "1/3", "U": 0},
        {"W": "1/2", "A": 1, "M": 1},
    )
    lower = F(result["lower"]["exact"])
    upper = F(result["upper"]["exact"])
    vertices = np.array([[1/6, 1/2], [1/3, 1/3], [1/3, 1/2]])
    fig, ax = plt.subplots(figsize=(7.2, 5.8), layout="constrained")
    ax.add_patch(Polygon(vertices, closed=True, facecolor="#dcefe9",
                         edgecolor="#246c5c", linewidth=2))
    w, a = np.meshgrid(np.linspace(.155, .345, 450),
                       np.linspace(.323, .51, 450))
    m = 1-w-a
    allowed = (w <= 1/3) & (a <= 1/2) & (m <= 1/3) & (m > 0)
    q = np.ma.masked_where(~allowed, a*a/(w*m))
    contours = ax.contour(w, a, q, levels=[1.5, 2, 3, 4], colors="#5c877c",
                          linewidths=.8)
    ax.clabel(contours, fmt=lambda value: f"Q={value:g}", fontsize=9)
    ax.scatter([1/3], [1/3], color="#a64b34", s=55, zorder=4)
    ax.scatter([1/6, 1/3], [1/2, 1/2], color="#315c9e", s=55, zorder=4)
    ax.annotate(f"minimum Q = {lower}", (1/3, 1/3), xytext=(.23, .315),
                arrowprops={"arrowstyle": "-", "color": "#a64b34"}, color="#853c29")
    ax.text(.25, .517, f"maximum Q = {upper} at both top vertices",
            ha="center", color="#24467c", fontsize=10)
    ax.set(xlim=(.15, .35), ylim=(.305, .533), xlabel="Latent W probability",
           ylabel="Latent A probability (M = 1 − W − A)")
    ax.set_title("Curvature allowed by correct-call lower bounds", pad=30)
    ax.text(.5, 1.025, "Illustrative population model · no sampling confidence claim",
            transform=ax.transAxes, ha="center", fontsize=9, color="#555555")
    ax.text(.154, .372,
            "Observed W/A/M/U:\n(1/6, 1/2, 1/3, 0)\n\nCorrect-call lower bounds:\n(1/2, 1, 1)",
            fontsize=9, va="top", bbox={"facecolor": "white", "alpha": .92,
                                         "edgecolor": "#cccccc", "pad": 6})
    ax.spines[["top", "right"]].set_visible(False)
    out = Path(__file__).resolve().parent
    fig.savefig(out/"population_region.png", dpi=180)
    svg_path = out/"population_region.svg"
    fig.savefig(svg_path, metadata={"Date": None})
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines())+"\n")
    plt.close(fig)


if __name__ == "__main__":
    main()

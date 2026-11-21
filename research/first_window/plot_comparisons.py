"""Render the two yeast forecast comparisons from their archived results."""
from fractions import Fraction
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
ROWS = [
    ("Kennedy_to_Kennedy", "Kennedy → Kennedy"),
    ("Dowsett_to_Dowsett", "Dowsett → Dowsett"),
    ("Dowsett_to_Kennedy", "Dowsett → Kennedy"),
    ("Kennedy_to_Dowsett", "Kennedy → Dowsett"),
]
results = json.loads((HERE / "results.json").read_text())
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.1), sharey=True)
fig.subplots_adjust(left=0.20, right=0.98, top=0.75, bottom=0.29, wspace=0.13)
for ax, coding, title in zip(axes, ["six", "binary"], ["Six substitution classes", "Transitions and transversions"]):
    for i, (key, _) in enumerate(ROWS):
        row = results[key + "_" + coding]
        bounds = row["paired_bounds"]["mean_brier_gain"]
        endpoints = [float(Fraction(bounds[k])) for k in ("lower", "upper")]
        dot = float(Fraction(row["random_recorded_snv"]["mean"]["brier_gain"]))
        y = 3 - i
        ax.plot(endpoints, [y] * 2, color="#315980", linewidth=2.5, marker="|", markersize=9)
        ax.scatter(dot, y, s=62, marker="D", color="#bc5019", edgecolor="white", zorder=3)
    ax.axvline(0, color="#354147", zorder=0, linewidth=1)
    ax.set_xlim(-0.77, 0.77)
    ax.set_xticks([-0.6, -0.3, 0, 0.3, 0.6])
    ax.set_ylim(-0.6, 3.6)
    ax.set_title(title, fontsize=12, loc="left", fontweight="bold")
    ax.grid(axis="x", alpha=0.17)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=9)
axes[0].set_yticks([3, 2, 1, 0], [label for _, label in ROWS])
fig.suptitle("How much can an unresolved first class change the score?", x=0.03,
             ha="left", fontsize=17, fontweight="bold")
fig.text(0.03, 0.84, "Training study → test study   •   Seven equally weighted held-out pedigrees per comparison", fontsize=10)
fig.text(0.59, 0.16, "Mean Brier gain over the reference (positive favors the trained spectrum)", ha="center", fontsize=10)
fig.legend(handles=[Line2D([0], [0], color="#315980", marker="|", label="Compatible first-class gains (bounds)"),
                    Line2D([0], [0], color="#bc5019", marker="D", linestyle="", label="Random recorded substitution in first window")],
           loc="lower center", ncol=2, frameon=False, fontsize=9)
fig.savefig(HERE / "first_window_gains.png", dpi=160, facecolor="white")

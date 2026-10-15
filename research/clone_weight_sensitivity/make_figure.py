"""Render the hypothetical conditional envelopes; no empirical data are read.

Requires matplotlib, independently of the standard-library-only bounds module.
Example: MPLCONFIGDIR=/tmp/tmd-r41-mpl python make_figure.py
"""

import argparse
from fractions import Fraction
from math import sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bounds import clone_cdf_envelope


def make_figure(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "svg.hashsalt": "tmd-r41-conditional-clone-cdf",
    })
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 4.8), sharex=True, sharey=True)
    colors = ("#4D4D4D", "#0072B2", "#D55E00")
    rational_p = [Fraction(i, 400) for i in range(401)]
    p = [float(value) for value in rational_p]
    for ax, cap, color in zip(axes, (1, 2, 3), colors):
        values = [clone_cdf_envelope(value, cap) for value in rational_p]
        low = [float(value.lower) for value in values]
        high = [float(value.upper) for value in values]
        if cap > 1:
            ax.fill_between(p, low, high, color=color, alpha=0.16)
            ax.plot(p, low, color=color, linewidth=1.9)
            ax.plot(p, high, color=color, linewidth=1.9)
        ax.plot(p, p, color="#333333", linestyle="--", linewidth=1.2, label="Equal CDFs")
        ax.set(xlim=(0, 1), ylim=(0, 1), xticks=(0, 0.25, 0.5, 0.75, 1),
               yticks=(0, 0.25, 0.5, 0.75, 1), xlabel=r"Row CDF, $p(x)$")
        ax.set_aspect("equal")
        ax.grid(color="#dddddd", linewidth=0.55, zorder=0)
        ax.set_title(f"K = {cap}" + ("  ·  source-based cap" if cap == 3 else ""),
                     fontsize=11, color=color, pad=10)
        gap = (sqrt(cap) - 1) / (sqrt(cap) + 1)
        ax.text(0.5, -0.30, f"Uniform gap supremum: {gap:.6f}",
                ha="center", va="top", transform=ax.transAxes, fontsize=9)
    axes[0].set_ylabel(r"Clone CDF, $q(x)$")
    fig.suptitle("Conditional row-to-clone CDF envelopes", fontsize=16, y=0.98)
    fig.text(0.5, 0.905, "HYPOTHETICAL · no empirical points or estimated distortion",
             ha="center", fontsize=10, color="#555555")
    fig.text(0.5, 0.055,
             "Each eligible clone has one common value repeated 1 to K times. "
             "Shading gives pointwise bounds; dashed line is p = q.",
             ha="center", fontsize=9)
    fig.text(0.5, 0.017,
             "K = 3 applies conditionally to the selected Lauer-derived portion only. "
             "Finite row counts can tighten these bounds.",
             ha="center", fontsize=9)
    fig.subplots_adjust(left=0.075, right=0.98, bottom=0.28, top=0.79, wspace=0.20)
    title = "Hypothetical conditional row-to-clone CDF envelopes"
    description = ("Original mathematical illustration, no empirical data. "
                   "Pointwise envelopes for multiplicity caps K=1,2,3. "
                   "The K=3 source application is conditional on the stated assumption contract.")
    fig.savefig(output_dir / "figure.png", dpi=220,
                metadata={"Title": title, "Description": description})
    fig.savefig(output_dir / "figure.svg",
                metadata={"Title": title, "Description": description, "Date": None})
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    make_figure(parser.parse_args().output_dir)

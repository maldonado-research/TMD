"""Render the archived Aws–Mws count ranges with optional Matplotlib."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_ranges(folder):
    previous = json.loads((folder.parent / "archived_route_ranks" / "rank_result.json").read_text())
    howells = json.loads((folder / "howells_completion.json").read_text())
    series = [
        ("Bantinaki–McDonald", 26, previous["historical_26"]),
        ("Matela", 50, previous["matela_50"]),
        ("Howells, monoculture", howells["monoculture"]["parents"], howells["monoculture"]),
        ("Howells, coculture", howells["coculture"]["parents"], howells["coculture"]),
        ("Howells, pooled", howells["pooled"]["parents"], howells["pooled"]),
    ]
    return [(label, n, data["differences"]["A-M"]) for label, n, data in series]


def signed(value):
    return f"{value:+d}".replace("-", "−") if value else "0"


def render(rows, destination):
    ink, muted, blue = "#172c38", "#475b64", "#146474"
    fig = plt.figure(figsize=(7.6, 3.6), facecolor="white")
    chart = fig.add_axes([0.38, 0.23, 0.595, 0.53])
    chart.set_xlim(-6.6, 9.6)
    chart.set_ylim(-0.48, len(rows) - 0.52)
    chart.set_yticks([])
    chart.set_xticks(range(-4, 9, 2))
    chart.tick_params(axis="x", length=0, pad=6, labelsize=9, colors=muted)
    for spine in chart.spines.values():
        spine.set_visible(False)
    chart.grid(axis="x", color="#e2e8e9", linewidth=0.7)
    chart.axvline(0, color="#84949a", linewidth=1.05)

    fig.text(0.025, 0.907, "Aws minus Mws among represented parents",
             fontsize=17, fontweight="bold", color=ink)
    fig.text(0.026, 0.837, "Endpoints show the smallest and largest attainable count differences.",
             fontsize=10.5, color=muted)
    for x, label, align in [(0.026, "Archive or setting", "left"), (0.337, "Parents", "right")]:
        fig.text(x, 0.767, label, ha=align, fontsize=9, fontweight="bold", color=ink)

    # Place labels in figure coordinates horizontally and align to the data rows vertically.
    for y, (label, n, (low, high)) in zip(reversed(range(len(rows))), rows):
        row_y = fig.transFigure.inverted().transform(chart.transData.transform((0, y)))[1]
        fig.text(0.026, row_y, label, va="center", fontsize=10.3, color=ink)
        fig.text(0.337, row_y, str(n), va="center", ha="right", fontsize=10.3, color=ink)
        chart.plot([low, high], [y, y], color=blue, linewidth=2.5, marker="o",
                   markerfacecolor="white", markeredgewidth=1.5, markersize=5, zorder=3)
        for value, offset, align in [(low, -6, "right"), (high, 6, "left")]:
            chart.annotate(signed(value), (value, y), xytext=(offset, 0),
                           textcoords="offset points", ha=align, va="center",
                           fontsize=9.3, fontweight="bold", color=ink,
                           bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.35})
    chart.set_xlabel("Aws count minus Mws count", fontsize=10.2, labelpad=6, color=ink)
    fig.text(0.026, 0.042, "The pooled Howells row combines the same four monoculture and five coculture parents.",
             fontsize=9.1, color=muted)
    fig.savefig(destination, dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    render(load_ranges(here), here / "rank_margins.png")

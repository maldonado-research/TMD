"""Draw a descriptive comparison of paired peach detections. Requires Matplotlib."""

import json
from fractions import Fraction
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def render(receipt, output):
    frame = receipt["frame"]
    counts = receipt["pair_by_site_calls"]
    agreement = receipt["agreement"]
    sites = receipt["across_sites"]
    neither = counts["neither_positive"]
    a_only = counts["a_only_positive"]
    b_only = counts["b_only_positive"]
    both = counts["both_positive"]
    total = counts["total"]
    either = a_only + b_only + both
    assert total == either + neither == frame["published_flower_sites"] * frame["split_tissue_pairs"]
    matching = Fraction(neither + both, total)
    overlap = Fraction(both, either)
    assert matching == Fraction(agreement["matching_calls_over_all"])
    assert overlap == Fraction(agreement["both_positive_over_either_positive"])
    site_mean = Fraction(sites["mean_intersection_over_union_weighting_each_nonempty_site_equally"])
    n_sites = sites["at_least_one_positive_in_split_tissues"]

    fig = plt.figure(figsize=(7.6, 3.8), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis("off")
    ink, muted, teal = "#172c38", "#475b64", "#146474"

    def label(x, y, text, size, *, color=ink, weight="normal", align="left"):
        ax.text(x, y, text, fontsize=size, color=color, fontweight=weight, ha=align,
                va="center", transform=ax.transAxes)

    label(0.025, 0.926, f"Paired detections in peach flower {frame['flower']}", 18, weight="bold")
    label(0.026, 0.837, f"{frame['published_flower_sites']} published sites × "
          f"{frame['split_tissue_pairs']} split-tissue pairs = {total} site-by-pair comparisons",
          10.7, color=muted)
    label(0.026, 0.726, "Calls in subsamples A and B", 11.8, weight="bold")

    cell_width, cell_height = 0.141, 0.175
    cells = [(0, 0, neither, "Neither", "#e8edef"), (1, 0, b_only, "B only", "#d9e9eb"),
             (0, 1, a_only, "A only", "#d9e9eb"), (1, 1, both, "Both", teal)]
    for column, row, value, name, fill in cells:
        x = 0.121 + column * (cell_width + 0.005)
        y = 0.421 - row * (cell_height + 0.009)
        ax.add_patch(Rectangle((x, y), cell_width, cell_height, facecolor=fill, linewidth=0))
        color = "white" if name == "Both" else ink
        label(x + cell_width / 2, y + 0.105, str(value), 17, color=color, weight="bold", align="center")
        label(x + cell_width / 2, y + 0.044, name, 9.1, color=color, align="center")
    for i, status in enumerate(["−", "+"]):
        label(0.121 + cell_width / 2 + i * (cell_width + 0.005), 0.634, f"B {status}", 10, align="center")
        label(0.092, 0.421 + cell_height / 2 - i * (cell_height + 0.009), f"A {status}", 10, align="right")
    label(0.026, 0.167, "+  detected     −  no detection recorded", 9, color=muted)

    summaries = [
        (f"All {total} comparisons", f"{neither + both} have matching A and B calls.", matching),
        (f"{either} comparisons with a positive call", f"{both} are positive in both subsamples.", overlap),
        (f"{n_sites} sites with a positive call", f"Equal-weight mean of site overlaps = {site_mean}.", site_mean),
    ]
    for index, (heading, explanation, fraction) in enumerate(summaries):
        y = 0.723 - index * 0.202
        label(0.470, y, heading, 10.7, weight="bold")
        label(0.976, y, f"{float(fraction):.1%}", 12.7, weight="bold", align="right", color=teal)
        label(0.470, y - 0.062, explanation, 9.3, color=muted)
        ax.add_patch(Rectangle((0.471, y - 0.113), 0.504, 0.014, facecolor="#e4eaeb", linewidth=0))
        ax.add_patch(Rectangle((0.471, y - 0.113), 0.504 * float(fraction), 0.014,
                               facecolor=teal, linewidth=0))

    label(0.026, 0.061, "Within a site, positive overlap counts pairs positive in both subsamples out of those positive in either.",
          9, color=muted)
    fig.savefig(output, dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    render(json.loads((folder / "peach_receipt.json").read_text()), folder / "peach_pairs.png")

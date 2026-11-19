"""Draw the counts of listed leaves for the two historical flower markers."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
MARKERS = {"M71": ("Pp01", "2130859"), "M101": ("Pp04", "21561355")}


def get_sets(carriers, roster):
    with roster.open(encoding="utf-8", newline="") as stream:
        samples = [r["sample_id"] for r in csv.DictReader(stream, delimiter="\t")]
    leaves = set(samples)
    if len(leaves) != len(samples):
        raise ValueError("Duplicate sample IDs in roster")
    with carriers.open(encoding="utf-8", newline="") as stream:
        calls = {(r["chromosome"], r["position"]): set(r["listed_leaves"].split(";"))
                 for r in csv.DictReader(stream, delimiter="\t")}
    if any(not value.issubset(leaves) for value in calls.values()):
        raise ValueError("Unrecognized sample identifier in carrier table")
    a, b = (calls[MARKERS[key]] for key in ("M71", "M101"))
    return leaves, ((a & b, a - b), (b - a, leaves - a - b))


def draw(carriers, roster, output):
    leaves, cells = get_sets(carriers, roster)
    if (not all(cells[r][c] for r, c in [(0, 0), (0, 1), (1, 0)])
            or sum(len(s) for row in cells for s in row) != len(leaves)):
        raise ValueError("The selected pair does not have the reported crossing pattern")

    ink, gray, teal = "#19313F", "#486070", "#006B68"
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(10, 5.3), facecolor="white")
    def text(x, y, s, **style):
        fig.text(x, y, s, va="center", color=style.pop("color", ink), **style)

    text(.045, .918, "Two peach markers cross in the recorded leaf lists",
         fontsize=19.3, weight="bold")
    text(.045, .842, f"{len(leaves)} sampled leaves from one tree  ·  Each cell counts leaves",
         fontsize=11.5, color=gray)
    x0, x1, width = .155, .354, .193
    y1, y0, height = .291, .474, .173
    text(x0 + width / 2, .693, "M101 listed", ha="center", fontsize=11.4, weight="bold")
    text(x1 + width / 2, .693, "M101 unlisted", ha="center", fontsize=11.4, weight="bold")
    text(.138, y0 + height / 2, "M71\nlisted", ha="right", fontsize=11.5, weight="bold")
    text(.138, y1 + height / 2, "M71\nunlisted", ha="right", fontsize=11.5, weight="bold")
    palettes = ((teal, "#D9ECEB"), ("#D9ECEB", "#F0F3F4"))
    labels = (("Both listed", "M71 only"), ("M101 only", "Neither listed"))
    for row, y in enumerate((y0, y1)):
        for column, x in enumerate((x0, x1)):
            fig.add_artist(Rectangle((x, y), width, height, transform=fig.transFigure,
                                     facecolor=palettes[row][column], edgecolor="none",
                                     zorder=0))
            fg = "white" if (row, column) == (0, 0) else ink
            text(x + width / 2, y + .111, str(len(cells[row][column])),
                 ha="center", fontsize=23, weight="bold", color=fg)
            text(x + width / 2, y + .047, labels[row][column], ha="center", fontsize=10.3, color=fg)

    text(.61, .693, "What the crossing means", fontsize=12, weight="bold")
    text(.61, .572, "If each marker arose once and was\nretained, descendant sets on one\nlineage tree must nest or be disjoint.",
         fontsize=10.6, linespacing=1.47)
    text(.61, .388, "These lists contain a shared leaf and\nleaves exclusive to each marker.\nNeither marker’s list contains the other.",
         fontsize=10.6, linespacing=1.47)
    fig.add_artist(plt.Line2D([.045, .955], [.212, .212], transform=fig.transFigure,
                              color="#CDDBDD", linewidth=.85))
    text(.045, .142, "A bulk leaf can contain several cellular lineages. The catalogue gives no per-site coverage for unlisted leaves.",
         fontsize=10, color=gray)
    text(.045, .073, "Source data from Wang et al. (2019), S1 and S2. Marker identifiers follow Ji et al. (2025), Table S2.",
         fontsize=8.6, color=gray)
    fig.savefig(output, dpi=180, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--carriers", type=Path, default=HERE / "carriers.tsv")
    parser.add_argument("--roster", type=Path, default=HERE / "sample_roster.tsv")
    parser.add_argument("--output", type=Path, default=HERE / "plot.png")
    args = parser.parse_args()
    draw(args.carriers, args.roster, args.output)

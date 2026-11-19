"""Render the double-reference depth distribution and an illustrative read-sampling benchmark."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent


def main():
    receipt = json.loads((HERE / "depth_receipt.json").read_bytes())
    obs = receipt["double_reference"]
    hist = {int(d): n for d, n in obs["pairs_by_combined_depth"].items()}
    total = sum(hist.values())
    assert total == obs["cells"]
    thresholds = []
    for fraction in (0.05, 0.02, 0.01):
        required = math.ceil(math.log(0.05) / math.log1p(-fraction))
        present = sum(n for d, n in hist.items() if d >= required)
        thresholds.append((fraction, required, present))

    ink, secondary, accent, grid = "#192c35", "#425b64", "#066575", "#d8e4e5"
    fig = plt.figure(figsize=(8.4, 4.4), facecolor="white")
    fig.text(0.037, 0.907, "Read depth in double-reference peach comparisons",
             weight="bold", fontsize=17, color=ink)
    fig.text(0.039, 0.841, f"Flower #2   ·   {total} site–tissue comparisons with reference calls in both splits",
             fontsize=10.1, color=secondary)
    ax = fig.add_axes([0.105, 0.25, 0.456, 0.45])
    max_depth = max(max(hist), max(d for _, d, _ in thresholds)) + 6
    depths = range(max_depth + 1)
    tails = [sum(n for k, n in hist.items() if k >= d) for d in depths]
    ax.step(depths, tails, where="post", linewidth=2.1, color=accent)
    ax.fill_between(depths, tails, step="post", alpha=0.1, color=accent)
    ax.set(xlim=(0, max_depth), ylim=(-14, total + 25),
           xticks=[0, 50, 100, 150, 200, 250, 300], yticks=[0, 150, 300, 450, 600])
    ax.grid(axis="y", color=grid, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Combined reference and alternate reads", fontsize=9.4, color=ink, labelpad=5)
    ax.set_ylabel("Comparisons at or above depth", fontsize=9.3, color=ink, labelpad=4)
    ax.tick_params(length=0, labelsize=8.5, pad=3, colors=secondary)
    for side, spine in ax.spines.items():
        spine.set_visible(side in ("left", "bottom"))
        spine.set_color("#91a5aa")
    for _, d, count in thresholds:
        ax.plot(d, count, "o", color=accent, markeredgecolor="white", markersize=6.8,
                markeredgewidth=1.1, clip_on=False)

    fig.text(0.615, 0.709, "Illustrative 95% detection threshold",
             weight="bold", fontsize=10.9, color=ink)
    columns = [(0.617, "Alternate\nfraction", "left"), (0.789, "Reads\nrequired", "right"),
               (0.958, "Comparisons at\nor above depth", "right")]
    for x, label, align in columns:
        fig.text(x, 0.602, label, ha=align, va="center", color=secondary, fontsize=9.2)
    for i, (frac, depth, count) in enumerate(thresholds):
        y = 0.496 - i * 0.103
        for value, (x, _, align) in zip((f"{frac:.0%}", str(depth), f"{count} / {total}"), columns):
            fig.text(x, y, value, ha=align, va="center", fontsize=11, weight="bold", color=ink)
    fig.text(0.039, 0.065, "Model assumes independent reads and the same alternate fraction in both splits.",
             fontsize=9.1, color=secondary)
    fig.text(0.039, 0.025, "Detection means observing at least one alternate read. The fractions are hypothetical.",
             fontsize=9.1, color=secondary)
    fig.savefig(HERE / "depth_figure.png", dpi=190, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()

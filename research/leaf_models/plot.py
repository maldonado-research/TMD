"""Rebuild the model comparison plot from the stored exact calculations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent


def draw(out):
    edit = json.loads((HERE / "edits/mixed_result.json").read_text())
    mix = json.loads((HERE / "mixtures/figure_result.json").read_text())["branches"]
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.8, 4.25), layout="constrained")
    ink, teal, blue, amber = "#203748", "#00786A", "#42688F", "#AD651A"
    for ax in (left, right):
        ax.spines[["right", "top"]].set_visible(False)
        ax.tick_params(axis="both", colors=ink)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#DEE3E6", linewidth=.7)
    points = edit["global_frontier"]
    left.plot([x["removed"] for x in points], [x["added"] for x in points],
              color=blue, linewidth=1.1, zorder=2)
    left.scatter([x["removed"] for x in points[1:]], [x["added"] for x in points[1:]],
                 color=blue, s=38, label="M101 unlisted in focal leaf", zorder=3)
    left.scatter([0], [12], color=amber, marker="D", s=48,
                 label="M101 listed in focal leaf", zorder=3)
    left.set(xlabel="Listed memberships removed", ylabel="Unlisted memberships added",
             xlim=(-.6,9.65), ylim=(-.7,13.3))
    left.set_title("Single lineage per leaf", loc="left", color=ink, weight="bold")
    left.legend(loc="upper right", frameon=False, fontsize=8.8)
    left.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
    labels = list(mix)
    bottom = [0]*len(labels)
    for qty, color, legend in ((1, "#CCDADD", "1 pattern"), (2, teal, "2 patterns"), (3, amber, "3 patterns")):
        vals = [mix[b]["leaf_counts_by_minimum_paths"].get(str(qty),0) for b in labels]
        right.bar(labels, vals, bottom=bottom, width=.63, color=color, label=legend)
        for idx,(v,base) in enumerate(zip(vals,bottom)):
            if v >= 2:
                right.text(idx,base+v/2,str(v),ha="center",va="center",
                           color= ink if qty==1 else "white",fontsize=9)
        bottom=[p+v for p,v in zip(bottom,vals)]
    right.set(xlabel="Main branch of the peach tree", ylabel="Sampled leaves", ylim=(0,36))
    right.set_title("Minimum patterns per leaf with exact bulk calls",loc="left",color=ink,weight="bold",fontsize=11.2)
    right.legend(loc="upper right",frameon=False,fontsize=8.8)
    fig.savefig(out, dpi=165, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=HERE / "comparison.png")
    draw(parser.parse_args().output)

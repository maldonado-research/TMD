"""Render the two mouse comparisons from the released scores."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT / "mouse/results.json").read_text())
early = r["offspring_ascertained"]["primary_table2"]["families"]
parents = r["parent_ascertained"]["confirmed"]["families"]
fig, (left, right) = plt.subplots(1, 2, figsize=(11.2, 4.9))
fig.subplots_adjust(left=.10, right=.97, bottom=.22, top=.72, wspace=.32)
fig.suptitle("Does a parent’s tissue allele fraction predict offspring carriage?",
             fontsize=16, fontweight="bold", x=.027, ha="left", y=.98)
fig.text(.028, .867, "Lindsay et al. mouse pedigrees  •  Each point or bar summarizes one family", size=10.5)
left.set_title("Markers discovered in offspring", loc="left", fontsize=13, fontweight="bold")
left.set_yticks([1, 0], list(early))
for i, v in enumerate(early.values()):
    for label, x, color, marker, offset in [
            ("Parent tissue", v["mean_forecast"]["parent"], "#4473a5", "s", .13),
            ("Discovery pups", v["mean_forecast"]["wgs"], "#ac542e", "^", 0),
            ("Other pups (observed)", v["mean_observed"], "#202c31", "o", -.13)]:
        left.scatter(x, 1-i+offset, color=color, marker=marker, s=65, label=label if i == 0 else None)
left.legend(loc="lower left", bbox_to_anchor=(-.02, -.39), ncol=2, fontsize=8.4, frameon=False)
left.set_xlim(0, .20)
left.set_xticks([0, .05, .10, .15, .20])
left.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
left.set_ylim(-.48, 1.48)
left.set_xlabel("Mean predicted or observed carrier frequency")
right.set_title("Markers discovered in parents", loc="left", fontsize=13, fontweight="bold")
for i, (name, v) in enumerate(parents.items()):
    gain = v["pairwise"]["parent_vs_other_families"]["gain"]
    right.barh(3-i, gain, height=.45, color="#457566" if gain > 0 else "#a76352")
    right.text(gain + (.0005 if gain > 0 else -.0005), 3-i, f"{gain:+.4f}", va="center",
               ha="left" if gain > 0 else "right", fontsize=9)
right.set_yticks([3,2,1,0],list(parents))
right.axvline(0, color="#30383a", linewidth=1)
right.set_xlim(-.011, .034)
right.set_xticks([-.01, 0, .01, .02, .03])
right.set_xlabel("Brier gain over rate estimated from other families")
for ax in (left, right):
    ax.set_axisbelow(True)
    ax.grid(axis="x",alpha=.18)
    ax.tick_params(axis="y",length=0,pad=7)
    ax.spines[["top","right","left"]].set_visible(False)
fig.savefig(ROOT / "transmission_forecasts.png", dpi=170, facecolor="white")

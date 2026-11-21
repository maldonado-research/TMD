"""Plot the sensitivity of strict ancestral precedence to a panel-wide call budget."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
data = json.loads((HERE/"shorea/panel_budget/aggregate.json").read_text())
budgets = data["all_within_tree_pairs_by_budget"]
counts = [budgets[f"joint_minimum_plus_{j}"]["strict_order"] for j in range(3)]
minimum = sum(tree["minimum_required_missed_genotypes"] for tree in data["trees"].values())
extra = data["exactly_one_extra_miss"]
low, high = (extra[k] for k in ("min_pairs_on_nested_edges_in_one_placement",
                                "max_pairs_on_nested_edges_in_one_placement"))
fig, ax = plt.subplots(figsize=(9.1,5.3), facecolor="white")
fig.subplots_adjust(left=.12,right=.94,top=.76,bottom=.22)
ink, teal, orange = "#213848","#046B6B","#994B14"
fig.text(.08,.93,"How many mutation pairs keep the same order?",weight="bold",color=ink,fontsize=18)
fig.text(.08,.865,"1,118 two-state sites in four tropical trees  ·  287,404 within-tree pairs",
         color=ink,fontsize=11)
ax.plot(range(3),counts,"o-",color=teal,lw=2.8,ms=8,clip_on=False)
for i,c in enumerate(counts):
    ax.annotate(f"{c:,}",(i,c),xytext=(0,-18),textcoords="offset points",ha="center",
                fontsize=10,weight="bold",color=teal)
ax.errorbar([1],[(low+high)/2], yerr=[(high-low)/2], fmt="s", color=orange,ms=6,capsize=5)
ax.annotate(f"{low:,}–{high:,} ordered pairs in each\nof {extra['distinct_complete_placements']} alternatives with eight misses",
            (1,high),xytext=(1.14,80000),fontsize=9.6,color=orange,va="center",
            arrowprops={"arrowstyle":"-","color":orange,"lw":1})
ax.set_xlim(-.24,2.25); ax.set_ylim(0,88000)
ax.set_xticks([0,1,2],[str(minimum)+" (minimum)",str(minimum+1),str(minimum+2)])
ax.set_yticks([0,20000,40000,60000,80000])
ax.yaxis.set_major_formatter(FuncFormatter(lambda n,pos:f"{int(n):,}"))
ax.set_xlabel("Maximum number of missed tip calls across the panel",labelpad=9,color=ink)
ax.set_ylabel("Ordered site pairs",color=ink)
ax.spines[["top","right","left"]].set_visible(False)
ax.spines["bottom"].set_color("#93A2AA")
ax.tick_params(colors=ink,length=0,pad=7)
ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
fig.text(.08,.07,"The line counts specific pairs whose direction agrees across every allowed placement.",
         fontsize=10,color=teal,weight="bold")
fig.text(.08,.024,"Branch ancestry assumes one inherited change per site and the sampled basal genotype as the starting state.",
         fontsize=9,color=ink)
fig.savefig(HERE/"pedigree_resolution.png",dpi=190)

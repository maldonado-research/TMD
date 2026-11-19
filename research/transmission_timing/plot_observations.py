"""Plot count-level peach and sampled yeast observations in the archived report."""
import argparse
from collections import Counter
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
INK = "#1d3042"
SLATE = "#526676"
GRID = "#dce3e6"
TEAL = "#087c78"
BLUE = "#39678e"
AMBER = "#aa5d1b"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def draw_peach(ax, source):
    records = source["2016_leaf_panel"]
    counts = {True: Counter(), False: Counter()}
    for record in records.values():
        ref, alt = record["counts"]["M101"]
        assert ref + alt > 0
        counts["M101" in record["listed"]][alt] += 1
    groups = [(False, BLUE, "Unlisted"), (True, TEAL, "Listed")]
    focal = {}
    for stem in ("L1", "L2"):
        record = records[f"DHQ1_B1-1-{stem}"]
        ref, alt = record["counts"]["M101"]
        focal[("M101" in record["listed"], alt)] = f"includes {stem}, {alt}/{ref+alt} reads"
    largest = max(max(c) for c in counts.values())
    for listed, color, label in groups:
        for alt, n in sorted(counts[listed].items()):
            ax.barh(alt, n, height=.6, color=color, zorder=3)
            detail = focal.get((listed, alt))
            text = str(n) if detail is None else f"{n}   ({detail})"
            ax.text(n+.8, alt, text, va="center", color=INK, fontsize=9)
    ax.set_yticks(range(largest+1))
    ax.set_ylim(largest+.55, -.55)
    ax.set_xlim(0,56)
    ax.set_xlabel("Number of leaves")
    ax.set_ylabel("Alternate reads at M101")
    ax.set_xticks([0,10,20,30,40,50])
    ax.grid(axis="x", color=GRID, linewidth=.75)
    ax.legend(handles=[Patch(color=c, label=f"{name} ({sum(counts[tag].values())})")
                       for tag,c,name in groups], loc="lower center",
              bbox_to_anchor=(.48,1.015), ncol=2, frameon=False,
              columnspacing=1.4, handlelength=1.3, borderaxespad=0)


def draw_yeast(ax, source):
    times = source["visit_generations"]
    examples = source["P1E11_group_example"]
    ax.axhline(90, color=SLATE, ls=(0,(4,3)), lw=1.25, zorder=1)
    ax.text(190, 87, "90% threshold", va="top", fontsize=9, color=SLATE)
    handles = []
    for identifier, color, marker, width in (("145", BLUE, "o", 6), ("55", AMBER, "D", 5.5)):
        record = examples[identifier]
        counts = record["alternate_and_total_reads"]
        rates = [100 * alt/total for alt,total in counts]
        ax.plot(times, rates, c=color, linewidth=1.65, zorder=3)
        ax.plot(times, rates, linestyle="None", marker=marker, markersize=width,
                markerfacecolor="white" if marker=="D" else color,
                markeredgecolor=color, markeredgewidth=1.5, zorder=4)
        handles.append(Line2D([0],[0],color=color,lw=1.55,marker=marker,markersize=width,
                              markerfacecolor="white" if marker=="D" else color,
                              label=f"Group {identifier} · {record['class']}"))
        if identifier=="145":
            at=times.index(5150)
            alt,total=counts[at]
            ax.annotate(f"{alt}/{total} reads", xy=(times[at],rates[at]), xytext=(times[at]+240,68),
                        arrowprops={"arrowstyle":"-", "color":SLATE,"lw":.9}, fontsize=9.5, color=INK)
    ax.set_ylim(-5,105)
    ax.set_xlim(-390,10750)
    ax.set_yticks([0,20,40,60,80,100])
    ax.set_xticks(times, [f"{g:,}" for g in times], rotation=28, ha="right", rotation_mode="anchor")
    ax.set_xlabel("Sampled generation")
    ax.set_ylabel("Alternate reads (%)")
    ax.grid(axis="y", color=GRID,linewidth=.75)
    ax.legend(handles=handles,loc="lower center", bbox_to_anchor=(.49,1.015),
              ncol=2, frameon=False, columnspacing=1.1, borderaxespad=0,
              handlelength=1.65,handletextpad=.48)


def make_figure(study, out):
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10.5,
                         "axes.labelcolor":INK, "xtick.color":SLATE,"ytick.color":SLATE,
                         "text.color":INK,"axes.edgecolor":SLATE,
                         "axes.spines.top":False,"axes.spines.right":False,
                         "legend.fontsize":9.5})
    fig,(left,right)=plt.subplots(1,2,figsize=(12.7,4.9))
    fig.subplots_adjust(left=.074,right=.985,top=.755,bottom=.21,wspace=.29)
    for ax, title in ((left,"M101 support in 75 peach leaves"),(right,"Two mutation groups in yeast well P1E11")):
        ax.text(0,1.23,title,transform=ax.transAxes,ha="left",va="center",
                fontsize=15.7,weight="bold",color=INK)
        ax.tick_params(length=3)
        ax.set_axisbelow(True)
    draw_peach(left,read_json(study/"peach"/"peach_inputs.json"))
    draw_yeast(right,read_json(study/"yeast"/"verify_result.json"))
    fig.text(.074,.035,"Peach groups follow the historical carrier list. Fractions give alternate / total reads.",
             fontsize=8.4,color=SLATE)
    fig.text(.589,.035,"Yeast symbols mark sampled visits. Lines connect consecutive observations.",
             fontsize=8.4,color=SLATE)
    fig.savefig(out,dpi=190,facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir",type=Path,default=HERE)
    parser.add_argument("--output",type=Path,default=HERE/"sampled_observations.png")
    args=parser.parse_args()
    make_figure(args.study_dir,args.output)

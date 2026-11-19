"""Render the yeast leadership figure from two bundled tables of counts."""
import argparse
import csv
from fractions import Fraction
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DAYS = (0, 10, 15, 20, 22, 24, 25)
INK, GRAY, TEAL, LIGHT = "#172d3b", "#52636b", "#007970", "#d5dee0"


def read_tables(primary, technical):
    with primary.open() as stream:
        histories = {}
        for row in csv.DictReader(stream, delimiter="\t"):
            histories.setdefault(row["population_id"], {})[int(row["day"])] = (
                int(row["reads_A"]), int(row["reads_B"]))
    original, rerun = {}, {}
    with technical.open() as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            well, day = row["population_id"], int(row["day"])
            for run, collection in (("original", original), ("rerun", rerun)):
                a, b = row[f"{run}_A"], row[f"{run}_B"]
                if a != "" and b != "" and int(a) + int(b) > 0:
                    collection.setdefault(well, {})[day] = (int(a), int(b))
            chosen = original if row["selected"] == "original" else rerun
            assert chosen[well][day] == histories[well][day]
    assert all(set(days) == set(DAYS) for days in histories.values())
    matched = [w for w in histories if all(d in original.get(w, {}) and d in rerun.get(w, {})
                                            for d in (0, 10, 25))]
    return histories, [{w: run[w] for w in matched} for run in (original, rerun)]


def summarize(panel):
    early_hits = change_hits = change_only = early_only = 0
    for records in panel.values():
        start, early, end = (Fraction(records[d][0], sum(records[d])) for d in (0, 10, 25))
        project = 2 * early - start
        half = Fraction(1, 2)
        assert all(x != half for x in (early, project, end))
        early_ok = (early > half) == (end > half)
        change_ok = (project > half) == (end > half)
        early_hits += early_ok
        change_hits += change_ok
        early_only += early_ok and not change_ok
        change_only += change_ok and not early_ok
    return (early_hits, change_hits), (early_only, change_only)


def leader_series(histories):
    counts, uninterrupted = [], []
    for t in DAYS:
        current = ongoing = 0
        for record in histories.values():
            assert all(a != b for a, b in record.values())
            start = record[0][0] > record[0][1]
            same = {d: (a > b) == start for d, (a, b) in record.items()}
            current += same[t]
            ongoing += all(same[d] for d in DAYS if d <= t)
        counts.append(current)
        uninterrupted.append(ongoing)
    return counts, uninterrupted


def render(primary, technical, output):
    histories, repeats = read_tables(primary, technical)
    current, uninterrupted = leader_series(histories)
    (main, (early_only, change_only)), (original, _), (rerun, _) = map(summarize, [histories, *repeats])
    n, matched = len(histories), len(repeats[0])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "text.color": INK, "axes.labelcolor": GRAY,
                         "xtick.color": GRAY, "ytick.color": GRAY,
                         "svg.fonttype": "none", "svg.hashsalt": "yeast-leadership-v1"})
    fig = plt.figure(figsize=(11.5, 5.65), facecolor="white")
    fig.text(.055, .925, "Early lineage abundance and the day-25 leader", fontsize=23, weight="bold")
    fig.text(.055, .857, "Two labelled baker’s yeast lineages per well   ·   Fasanello et al. (2020)",
             fontsize=12, color=GRAY)
    fig.text(.055, .755, "A   Persistence of the day-0 lead", fontsize=14, weight="bold")
    fig.text(.55, .755, "B   Correct day-25 forecasts", fontsize=14, weight="bold")

    ax = fig.add_axes([.088, .283, .387, .368])
    ax.set(xlim=(-.8, 27), ylim=(0, 82), xlabel="Day", ylabel="Wells",
           yticks=(0, 20, 40, 60, 80), xticks=(0, 5, 10, 15, 20, 25))
    ax.grid(axis="y", color=LIGHT, linewidth=.65)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(LIGHT)
    ax.tick_params(length=0, pad=4)
    ax.plot(DAYS, current, "-o", color=TEAL, label="Leading at that visit",
            lw=2.3, ms=4.5, zorder=3)
    ax.plot(DAYS, uninterrupted, "--s", color=GRAY, markerfacecolor="white",
            label="Led at every visit so far", lw=1.6, ms=5, zorder=2)
    for series, color, y in [(current, TEAL, 1), (uninterrupted, GRAY, -2)]:
        ax.annotate(str(series[-1]), (DAYS[-1], series[-1]), xytext=(7,y),
                    textcoords="offset points", va="center", weight="bold", color=color)
    ax.legend(loc="lower left", bbox_to_anchor=(-.1, 1.005), frameon=False,
              ncols=2, fontsize=9.5, handlelength=1.8, columnspacing=1.1)
    fig.text(.055, .146, f"Of {n} day-0 leaders, {current[-1]} also led on day 25.",
             fontsize=10)
    fig.text(.055, .104, f"{uninterrupted[-1]} led at all seven observations.", fontsize=10)

    table = fig.add_axes([.55, .238, .4, .45])
    table.set(xlim=(0, 1), ylim=(0, 1))
    table.axis("off")
    def label(x, y, txt, size=11, **kwargs):
        table.text(x, y, txt, va="center", fontsize=size, **kwargs)
    label(0, .94, "Measurement", 10, color=GRAY)
    label(.65, .94, "Day-10 leader", 10, ha="center", color=GRAY)
    label(.91, .94, "Early change", 10, ha="center", color=GRAY)
    table.hlines(.853, 0, 1, color=LIGHT, lw=1)
    label(0, .723, "Authors’ selected counts", 10.5, weight="bold")
    label(0, .574, f"Paired disagreements in {n} wells", 9.5, color=GRAY)
    label(0, .478, f"Only day-10 leader correct in {early_only}  ·  Only change correct in {change_only}", 9.5)
    table.hlines(.36, 0, 1, color=LIGHT, lw=1)
    label(0, .265, "Original run", 11)
    label(0, .085, "Repeat run", 11)
    for y, (first, second), denom, weight in [(.723, main, n, "bold"),
                                               (.265, original, matched, "normal"),
                                               (.085, rerun, matched, "normal")]:
        for x, value in [(.65, first), (.91, second)]:
            label(x, y, f"{value}/{denom}", 13, ha="center", weight=weight)
    fig.text(.55, .146, f"The two runs cover the same {matched} wells at days 0, 10 and 25.", fontsize=10)
    fig.text(.55, .104, "Samples with elevated barcode contamination were rerun.", fontsize=10)
    fig.text(.055, .025, "Early change ranks each lineage by its day-10 share plus the change in its share from day 0 to day 10.",
             fontsize=9.5, color=GRAY)
    output.mkdir(exist_ok=True, parents=True)
    vector = output / "lineage_forecasts.svg"
    fig.savefig(vector, metadata={"Date": None})
    # Keep generated path coordinates free of trailing whitespace in Git.
    vector.write_text("\n".join(line.rstrip() for line in vector.read_text().splitlines()) + "\n")
    fig.savefig(output / "lineage_forecasts.png", dpi=190)
    plt.close(fig)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--counts", type=Path, default=root / "fasanello/fasanello_counts.tsv")
    parser.add_argument("--technical", type=Path, default=root / "fasanello/technical_counts.tsv")
    parser.add_argument("--out", type=Path, default=root)
    args = parser.parse_args()
    render(args.counts, args.technical, args.out)

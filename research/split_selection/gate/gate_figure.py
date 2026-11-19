"""Draw the conditional read-allocation comparison from its saved JSON receipt."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent


def main():
    receipt = json.loads((HERE / "gate_result.json").read_bytes())
    by_status = receipt["by_site_status"]
    groups = [
        ("All eligible comparisons", receipt["totals"]),
        ("Another library reaches five", by_status["outside_library_passes"]),
        ("Split totals guarantee five", by_status["automatic_given_split_totals"]),
        ("Split allocation decides", by_status["sensitive_to_allocation"]),
    ]
    series = [
        ("observed_one_sided", "Observed", "#243A46"),
        ("expected_without_gate", "Expected from uniform allocation", "#ABC3CC"),
        ("expected_given_gate", "Expected given the five-read proxy", "#087E74"),
    ]
    fig = plt.figure(figsize=(9.5, 6.4), facecolor="white")
    fig.text(0.035, 0.965, "A five-read screen changes the expected one-sided count",
             ha="left", va="top", fontsize=18.1, fontweight="bold", color="#1B303C")
    fig.text(0.035, 0.905, "One peach flower  ·  20 split lysates  ·  At least two alternate reads per comparison",
             ha="left", va="top", fontsize=11, color="#455A64")
    handles = [Patch(facecolor=col, label=label) for _, label, col in series]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.035, 0.855),
               ncol=3, frameon=False, handlelength=1.1, handletextpad=0.45,
               columnspacing=1.75, fontsize=9.2, borderaxespad=0)
    ax = fig.add_axes((0.315, 0.205, 0.65, 0.595))
    ax.set_xlim(0, 15.2)
    ax.set_ylim(-0.5, 3.9)
    ax.set_xticks(range(0, 15, 2))
    ax.set_yticks([])
    ax.tick_params(axis="x", colors="#455A64", labelsize=9, length=0, pad=5)
    ax.grid(axis="x", color="#DCE3E6", linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axvline(0, color="#98A9AF", linewidth=0.8)
    ax.set_xlabel("Site–tissue comparisons with all alternate reads in one aliquot",
                  fontsize=10, color="#324752", labelpad=9)
    group_positions = (3.45, 2.14, 1.08, 0.02)
    for (label, group), center in zip(groups, group_positions):
        ax.text(-0.427, center + 0.09, label, transform=ax.get_yaxis_transform(),
                fontsize=11.1, ha="left", va="center", fontweight="bold", color="#243A46")
        caption = f"{group['eligible_pairs']} comparisons  ·  {group['sites']} candidate sites"
        ax.text(-0.427, center - 0.16, caption, transform=ax.get_yaxis_transform(),
                fontsize=9.6, ha="left", va="center", color="#526772")
        for (key, _, color), delta in zip(series, (0.23, 0, -0.23)):
            value = group[key]
            ax.barh(center + delta, value, height=0.175, color=color)
            text = str(value) if key == "observed_one_sided" else f"{value:.2f}"
            ax.text(value + 0.13, center + delta, text, ha="left", va="center", fontsize=9.5,
                    color="#243A46")
    ax.plot([-0.427, 1], [2.82, 2.82], transform=ax.get_yaxis_transform(),
            color="#B2C2C7", linewidth=0.8, clip_on=False)
    foot = ("The proxy requires at least five alternate reads in a single library at a site.\n"
            "The lower three groups partition the 37 discovered sites. The original study applied additional filters.")
    fig.text(0.035, 0.082, foot, ha="left", va="top", fontsize=9.5,
             linespacing=1.4, color="#455A64")
    fig.savefig(HERE / "gate_figure.png", dpi=175, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()

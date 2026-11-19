"""Sharp pairwise count and weighted-share differences for the archived Matela roster."""
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = tuple(combinations("WAM", 2))


def group_sizes(blocks, field):
    sizes = Counter()
    for block in blocks:
        sizes[block[field]] += sum(block["parent_support"].values())
    return sizes


def pair_gaps(blocks, weights):
    """Each parent's vote can independently attain either endpoint of a given contrast."""
    result = {}
    for left, right in PAIRS:
        low = high = 0
        for block, weight in zip(blocks, weights):
            for support, count in block["parent_support"].items():
                contributions = [(label == left) - (label == right) for label in support]
                low += count * weight * min(contributions)
                high += count * weight * max(contributions)
        result[f"{left}-{right}"] = [low, high]
    return result


def first_ties(blocks, field):
    """Start at a strictly positive count gap. Allow one multiplier in [1, gamma] per block."""
    grouped = {}
    for block in blocks:
        grouped.setdefault(block[field], []).append(block)
    bounds = [pair_gaps(rows, [1] * len(rows)) for rows in grouped.values()]
    result = {}
    for left, right in PAIRS:
        pair = f"{left}-{right}"
        lower = [gaps[pair][0] for gaps in bounds]
        positive = sum(max(0, value) for value in lower)
        negative = sum(max(0, -value) for value in lower)
        if positive <= negative:
            raise ValueError(f"{pair} lacks a strict positive baseline at equal parent weights.")
        # The sharp lower gap is positive - gamma * negative before normalization.
        result[pair] = {
            "positive_lower_sum": positive,
            "negative_lower_magnitude": negative,
            "first_tie_ratio": Fraction(positive, negative) if negative else None,
            "finite_tie": bool(negative),
        }
    return result


def joint_witness(blocks, weights):
    """Assign every ambiguous parent in this roster to its admissible M class."""
    totals = dict.fromkeys("WAM", 0)
    for block, weight in zip(blocks, weights):
        for support, count in block["parent_support"].items():
            label = support if len(support) == 1 else "M"
            if label not in support:
                raise ValueError("The all-M witness is unavailable for this support.")
            totals[label] += count * weight
    return totals


def analyze(receipt):
    blocks = receipt["blocks"]
    total = receipt["represented_parents"]
    if sum(group_sizes(blocks, "source").values()) != total:
        raise ValueError("Parent count differs from receipt total.")
    if sum(block["selected_rows"] for block in blocks) != receipt["selected_wrinkly_rows"]:
        raise ValueError("Selected row count differs from receipt total.")
    unit_votes = [1] * len(blocks)
    result = {
        "source_sha256": receipt["source_sha256"],
        "represented_parents": total,
        "pooled_count_gaps": pair_gaps(blocks, unit_votes),
        "first_tie": {
            "scope": "Every gap is positive at equal parent weights. Each represented block receives a multiplier in [1, gamma]."
        },
        "all_ambiguous_to_M_witness": {"pooled_counts": joint_witness(blocks, unit_votes)},
    }
    for field in ("source", "source_year"):
        sizes = group_sizes(blocks, field)
        weights = [Fraction(1, len(sizes) * sizes[block[field]]) for block in blocks]
        result[f"equal_{field}_share_gaps"] = pair_gaps(blocks, weights)
        result["first_tie"][field] = first_ties(blocks, field)
        result["all_ambiguous_to_M_witness"][f"equal_{field}_shares"] = joint_witness(blocks, weights)
        omissions = {}
        for group, size in sizes.items():
            included = [int(block[field] != group) for block in blocks]
            omissions[group] = {
                "remaining_parents": total - size,
                "count_gaps": pair_gaps(blocks, included),
            }
        result[f"omit_one_{field}"] = omissions
    source_sizes = group_sizes(blocks, "source")
    largest = max(source_sizes, key=source_sizes.get)
    remaining = [int(block["source"] != largest) for block in blocks]
    result["all_ambiguous_to_M_witness"]["omit_largest_source_counts"] = joint_witness(blocks, remaining)
    return result


if __name__ == "__main__":
    receipt = json.loads((HERE / "block_receipt.json").read_bytes())
    print(json.dumps(analyze(receipt), default=str, indent=2, sort_keys=True))

"""Summarize the double-reference depth histogram under an idealized read model."""
import argparse
import json
from pathlib import Path
from statistics import median


def summarize(receipt):
    group = receipt["double_reference"]
    hist = {int(depth): count for depth, count in group["pairs_by_combined_depth"].items()}
    if any(depth <= 0 or type(count) is not int or count <= 0 for depth, count in hist.items()):
        raise ValueError("Invalid depth histogram")
    depths = [depth for depth, count in hist.items() for _ in range(count)]
    if (len(depths), sum(depths), min(depths), median(depths), max(depths)) != (
            group["cells"], group["ref_plus_alt_reads"], group["pair_depth"]["min"],
            group["pair_depth"]["median"], group["pair_depth"]["max"]):
        raise ValueError("Histogram differs from the reported coverage")
    output = {}
    for percent in (1, 2, 5, 10):
        # Under independent unbiased Bernoulli reads sharing fixed p within a pair,
        # at least one alternate has probability >= 95% iff 20*(100-p)^d <= 100^d.
        depth = 0
        while 20 * (100 - percent) ** depth > 100 ** depth:
            depth += 1
        output[str(percent)] = {
            "minimum_depth_for_95_percent_chance_of_one_or_more_alternate_reads": depth,
            "cells_at_or_above_this_depth": sum(n for d, n in hist.items() if d >= depth),
        }
    return {"model": "Independent reads with one stipulated alternate-read fraction per pair. "
                     "Endpoint is at least one alternate read. Illustrative, conditional on depth.",
            "denominator": group["cells"], "hypothetical_alternate_read_percent": output}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", nargs="?", type=Path,
                        default=Path(__file__).with_name("depth_receipt.json"))
    result = summarize(json.loads(parser.parse_args().receipt.read_bytes()))
    print(json.dumps(result, indent=2))

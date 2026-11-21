"""Extract the individual allele strokes in Plomion et al. (2018), Figure 2b."""

import argparse
import csv
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pymupdf


ARTICLE_SHA = "5e3e5544fa3fda8c1050b88aa0bdd34a2c4748c828059ae855c3558f78335856"
FIGPAGE_SHA = "91f45db2eedfe6a591b578fb11d26f9853bf5b122774261a3ff1219c0753180d"
S6_SCORABLE = (96, 83, 89, 47, 59, 15, 93, 113, 85, 19, 108, 112, 36, 47, 43, 84, 94, 12, 113)
COLUMNS = ("figure_order", "reported_origin", "L1_alternate", "L1_reference", "L2_alternate", "L2_reference")
PALETTE = {(0.74, 0.74, 0.74): "reference", (0.18, 0.00, 0.55): "alternate",
           (0.00, 0.55, 0.12): "alternate", (0.83, 0.65, 0.11): "alternate"}


def extract(pdf):
    file_sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    pages = {ARTICLE_SHA: 2, FIGPAGE_SHA: 0}
    if file_sha not in pages:
        raise ValueError("Unexpected input. Supply the PMC version 2 article PDF.")
    tally = defaultdict(Counter)
    seen = set()
    with pymupdf.open(pdf) as doc:
        for drawing in doc[pages[file_sha]].get_drawings():
            if drawing["type"] != "s":
                continue
            for item in drawing["items"]:
                if item[0] != "l":
                    continue
                start, end = item[1:]
                if not (379 <= start.x < 452 and 2.5 < end.x - start.x < 2.54
                        and abs(start.y - end.y) < 0.005):
                    continue
                if 497.7 <= start.y <= 576.3:
                    branch = "L2"
                elif 590.3 <= start.y <= 610:
                    branch = "L1"
                else:
                    continue
                x = round(start.x, 1)
                key = (x, round(start.y, 2))
                if key in seen:
                    raise ValueError("Overlapping allele strokes.")
                seen.add(key)
                colour = tuple(round(component, 2) for component in drawing["color"])
                tally[x][branch, PALETTE[colour]] += 1

    if len(tally) != len(S6_SCORABLE):
        raise ValueError("Unexpected number of plotted markers.")
    for index, x in enumerate(sorted(tally)):
        # The nine purple, six green and four gold square columns give the native origin order.
        origin = "shared_trunk" if index < 9 else "L1" if index < 15 else "L2"
        values = [tally[x][branch, allele] for branch in ("L1", "L2") for allele in ("alternate", "reference")]
        l1, l2 = sum(values[:2]), sum(values[2:])
        if l1 % 2 or l2 % 2 or l1 > 46 or l2 > 186 or l1 + l2 != 2 * S6_SCORABLE[index]:
            raise ValueError("Figure alleles disagree with the sampling frame or Supplementary Table 6.")
        yield (index + 1, origin, *values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(COLUMNS)
    writer.writerows(extract(args.pdf))

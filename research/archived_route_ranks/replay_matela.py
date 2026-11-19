"""Recount published category and parent-group totals in Matela et al., Table S1."""

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook


SOURCE = "https://pmc-oa-opendata.s3.amazonaws.com/PMC13101516.1/aem.02499-25-s0002.xlsx"
SOURCE_SHA256 = "90d591f688302c603abbfafcde57ce6fb1011eb6043177d44e3f704f3e818b21"
PARENT_ID = re.compile(r"([A-Z]+)_(\d{4})_(\d+)_(\d+)")
FAMILIES = {"W": "(wsp", "A": "(aws", "M": "(mws"}


def source_blocks(parent_categories, clone_counts):
    source_sizes = Counter(parent[0] for parent in parent_categories)
    schools = sorted(source_sizes, key=lambda school: (-source_sizes[school], school))
    support = defaultdict(Counter)
    row_counts = Counter()
    for parent, labels in parent_categories.items():
        cohort = parent[:2]
        support[cohort]["".join(sorted(labels))] += 1
        row_counts[cohort] += clone_counts[parent]

    blocks = []
    for number, school in enumerate(schools, start=1):
        years = sorted(year for site, year in support if site == school)
        for slot, year in enumerate(years, start=1):
            cohort = school, year
            blocks.append({
                "source": f"S{number}",
                "source_year": f"S{number}.{slot}",
                "selected_rows": row_counts[cohort],
                "parent_support": dict(support[cohort]),
            })
    return blocks


def replay(path, *, include_source_blocks=False):
    source_bytes = path.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("Input differs from the archived Table S1.")

    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        rows = workbook["mutations by clone"].values
        header = next(rows)
        id_column = header.index("Name (School,Year,Pop,Clone)")
        school_column = header.index("School")
        phenotype_column = header.index("Phenotype")
        label_columns = [header.index(f"gene {i}") for i in (1, 2, 3)]
        phenotypes = Counter()
        clone_categories = Counter()
        parent_categories = defaultdict(set)
        clone_counts = Counter()
        identifiers = set()
        for row in rows:
            clone = row[id_column]
            if not clone or clone in identifiers:
                raise ValueError("Missing or duplicate clone identifier.")
            identifiers.add(clone)
            phenotype = row[phenotype_column]
            phenotypes[phenotype] += 1
            if phenotype != "wrinkly":
                continue
            match = PARENT_ID.fullmatch(clone)
            if not match or match[1] != row[school_column]:
                raise ValueError("A selected clone lacks the stated parent-key structure.")
            parent = match.groups()[:3]
            label_text = " ".join(str(row[i] or "").lower() for i in label_columns)
            observed = {c for c, prefix in FAMILIES.items() if prefix in label_text}
            if not observed:
                raise ValueError("A selected clone has no recognizable focal family.")
            clone_categories["".join(sorted(observed))] += 1
            parent_categories[parent].update(observed)
            clone_counts[parent] += 1
    finally:
        workbook.close()

    if include_source_blocks:
        return {
            "source": SOURCE,
            "source_sha256": digest,
            "all_workbook_rows": len(identifiers),
            "selected_wrinkly_rows": phenotypes["wrinkly"],
            "represented_parents": len(parent_categories),
            "blocks": source_blocks(parent_categories, clone_counts),
        }

    parent_support = Counter("".join(sorted(s)) for s in parent_categories.values())
    return {
        "source": SOURCE,
        "source_bytes": len(source_bytes),
        "source_sha256": digest,
        "all_selected_clone_rows": len(identifiers),
        "phenotype_rows": dict(phenotypes),
        "selected_wrinkly_clone_distinct_focal_classes": dict(clone_categories),
        "represented_wrinkly_parents": len(parent_categories),
        "wrinkly_clones_per_parent_histogram": dict(Counter(clone_counts.values())),
        "focal_class_union_across_archived_wrinkly_clones_in_each_parent": dict(parent_support),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--source-blocks", action="store_true",
                        help="emit parent support counts by anonymized school and school-year")
    args = parser.parse_args()
    print(json.dumps(replay(args.workbook, include_source_blocks=args.source_blocks),
                     indent=2, sort_keys=True))

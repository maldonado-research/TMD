"""Verify released weight bounds by enumerating whole-roster votes; optionally reread Table S1."""
import argparse
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
CLASSES = "WAM"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_workbook(path, receipt):
    """Read the pinned workbook directly as Office XML, separately from the openpyxl replay."""
    require(hashlib.sha256(path.read_bytes()).hexdigest() == receipt["source_sha256"],
            "Workbook SHA-256 differs.")
    with ZipFile(path) as archive:
        strings_xml = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(node.text or "" for node in entry.iterfind(".//{*}t"))
                   for entry in strings_xml.findall("{*}si")]
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.findall(".//{*}sheetData/{*}row"):
        values = {}
        for cell in row.findall("{*}c"):
            value = cell.findtext("{*}v", "")
            if value:
                column = re.match(r"[A-Z]+", cell.get("r")).group()
                values[column] = strings[int(value)] if cell.get("t") == "s" else value
        if values:
            rows.append(values)
    columns = {value: key for key, value in rows[0].items()}
    by_parent = defaultdict(set)
    row_counts = Counter()
    for row in rows[1:]:
        if row[columns["Phenotype"]] == "wrinkly":
            parent = tuple(row[columns["Name (School,Year,Pop,Clone)"]].split("_")[:-1])
            require(len(parent) == 3 and parent[0] == row[columns["School"]], "Invalid parent.")
            row_counts[parent[:2]] += 1
            for index in (1, 2, 3):
                text = row.get(columns[f"gene {index}"], "")
                for match in re.finditer(r"\((aws|mws|wsp)", text, re.I):
                    by_parent[parent].add(match[1][0].upper())
            require(by_parent[parent], "Missing focal label.")
    require(len(rows) - 1 == receipt["all_workbook_rows"], "Workbook row total differs.")
    require(len(by_parent) == receipt["represented_parents"], "Workbook parent total differs.")
    require(sum(row_counts.values()) == receipt["selected_wrinkly_rows"], "Selected row total differs.")
    source_sizes = Counter(p[0] for p in by_parent)
    schools = sorted(source_sizes, key=lambda name: (-source_sizes[name], name))
    recounted = []
    for number, school in enumerate(schools, start=1):
        for slot, year in enumerate(sorted(y for s, y in row_counts if s == school), start=1):
            support = Counter("".join(sorted(labels)) for key, labels in by_parent.items()
                              if key[:2] == (school, year))
            recounted.append({"source": f"S{number}", "source_year": f"S{number}.{slot}",
                              "selected_rows": row_counts[(school, year)], "parent_support": dict(support)})
    require(recounted == receipt["blocks"], "Workbook-derived block counts differ.")


def check_bounds(tables, reported):
    for left, right in itertools.combinations(CLASSES, 2):
        differences = [table[left] - table[right] for table in tables]
        expected = list(map(Fraction, reported[f"{left}-{right}"]))
        require([min(differences), max(differences)] == expected, "Pairwise endpoints differ.")


def check_thresholds(pooled, omitted, reported):
    """Enumerate completed rosters and every corner of the block multiplier box."""
    for left, right in itertools.combinations(CLASSES, 2):
        margins = []
        first_tie = None
        for index, table in enumerate(pooled):
            baseline = table[left] - table[right]
            require(baseline > 0, "An assignment fails the strict baseline assumption.")
            gaps = [baseline - (tables[index][left] - tables[index][right]) for tables in omitted]
            margins.append(gaps)
            # Raise just the chosen blocks from 1 to gamma. Their summed gap is the slope.
            for raised in itertools.product((False, True), repeat=len(gaps)):
                slope = sum(value for value, high in zip(gaps, raised) if high)
                if slope < 0:
                    ratio = 1 + Fraction(baseline, -slope)
                    if first_tie is None or ratio < first_tie:
                        first_tie = ratio
        lower = [min(values) for values in zip(*margins)]
        expected = reported[f"{left}-{right}"]
        require(expected["positive_lower_sum"] == sum(x for x in lower if x > 0),
                "Positive lower-margin sum differs.")
        require(expected["negative_lower_magnitude"] == -sum(x for x in lower if x < 0),
                "Negative lower-margin magnitude differs.")
        require(expected["finite_tie"] == (first_tie is not None), "Finite-tie decision differs.")
        encoded = None if first_tie is None else str(first_tie)
        require(encoded == expected["first_tie_ratio"], "First tie differs from corner enumeration.")


def verify(receipt, result):
    """Assign one vote to each actual support slot, then weight entire completed tables."""
    parents = [(row["source"], row["source_year"], support) for row in receipt["blocks"]
               for support, count in row["parent_support"].items() for _ in range(count)]
    require(len(parents) == result["represented_parents"] == receipt["represented_parents"],
            "Roster sizes differ.")
    require(receipt["source_sha256"] == result["source_sha256"], "Source hashes differ.")
    site_counts = Counter(site for site, _, _ in parents)
    year_counts = Counter(year for _, year, _ in parents)
    largest = max(site_counts, key=site_counts.get)
    outcomes = defaultdict(list)
    witnesses = {}
    for choices in itertools.product(*(p[2] for p in parents)):
        pooled = Counter(choices)
        sites = defaultdict(Counter)
        years = defaultdict(Counter)
        for (site, year, _), label in zip(parents, choices):
            sites[site][label] += 1
            years[year][label] += 1
        outcomes["pooled"].append(pooled)
        witness = {"pooled_counts": pooled, "omit_largest_source_counts": pooled - sites[largest]}
        for name, strata, counts in [("source", sites, site_counts), ("source_year", years, year_counts)]:
            share = {label: sum(Fraction(votes[label], counts[group]) for group, votes in strata.items())
                     / len(strata) for label in CLASSES}
            outcomes[name].append(share)
            witness[f"equal_{name}_shares"] = share
            for group, votes in strata.items():
                outcomes[(name, group)].append(pooled - votes)
        if all(label == "M" for label, (_, _, support) in zip(choices, parents) if len(support) > 1):
            witnesses = witness

    check_bounds(outcomes["pooled"], result["pooled_count_gaps"])
    for name, groups in [("source", site_counts), ("source_year", year_counts)]:
        check_bounds(outcomes[name], result[f"equal_{name}_share_gaps"])
        reported = result[f"omit_one_{name}"]
        require(reported.keys() == groups.keys(), "Omission list differs.")
        for group, size in groups.items():
            require(reported[group]["remaining_parents"] == len(parents) - size, "Omission size differs.")
            check_bounds(outcomes[(name, group)], reported[group]["count_gaps"])
        omitted = [outcomes[(name, group)] for group in groups]
        check_thresholds(outcomes["pooled"], omitted, result["first_tie"][name])
    for name, expected in result["all_ambiguous_to_M_witness"].items():
        require(all(Fraction(expected[k]) == witnesses[name][k] for k in CLASSES), "Witness differs.")
    ranks = {}
    for name in ("pooled", "source", "source_year"):
        ranks[name] = sorted({">".join(sorted(CLASSES, key=lambda k: -table[k])) for table in outcomes[name]
                              if len(set(table[k] for k in CLASSES)) == 3})
    return {"vote_completions": len(outcomes["pooled"]), "pairwise_intervals": 3 * len(outcomes),
            "first_tie_thresholds": 3 * 2,
            "attainable_strict_orders": ranks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, help="verify the block receipt from the original Table S1")
    args = parser.parse_args()
    receipt = json.loads((HERE / "block_receipt.json").read_bytes())
    if args.workbook:
        verify_workbook(args.workbook, receipt)
    report = verify(receipt, json.loads((HERE / "weights_result.json").read_bytes()))
    report["verified_workbook"] = bool(args.workbook)
    print(json.dumps(report, sort_keys=True))

"""Summarize callable embryo genotypes and bound branch contrasts with missing genotypes."""
import argparse
import csv
import json
import sys
from fractions import Fraction
from pathlib import Path

BRANCH_EMBRYOS = {"L1": 23, "L2": 93}


def rounded(value):
    return None if value is None else round(float(value), 10)


def branch_record(row):
    origin = row["origin"]
    other = "L2" if origin == "L1" else "L1"
    fractions = {}
    for branch, embryos in BRANCH_EMBRYOS.items():
        alt, ref = int(row[f"{branch}_alt"]), int(row[f"{branch}_ref"])
        total = 2 * embryos
        missing = total - alt - ref
        if min(alt, ref, missing) < 0 or missing % 2:
            raise ValueError("Invalid diploid branch allele counts")
        fractions[branch] = (Fraction(alt, alt + ref) if alt + ref else None,
                             Fraction(alt, total), Fraction(alt + missing, total))
    p, lo, hi = fractions[origin]
    q, other_lo, other_hi = fractions[other]
    return {"figure_order": int(row["figure_order"]), "origin": origin,
            "called_difference": p - q if p is not None and q is not None else None,
            "all_embryos_lower": lo - other_hi, "all_embryos_upper": hi - other_lo}


def audit(rows):
    eligible = [r for r in rows if r["assay"] == "Y"]
    contrasts = [branch_record(r) for r in eligible if r["origin"] in BRANCH_EMBRYOS]
    if len(eligible) != 19 or len(contrasts) != 10:
        raise ValueError("Unexpected number of amplified or branch-assigned markers")
    grid = len(eligible) * sum(BRANCH_EMBRYOS.values())
    called = sum(int(r["genotyped"]) for r in eligible)
    het = sum(int(r["heterozygotes"]) for r in eligible)
    carriers = sum(int(r["carriers"]) for r in eligible)
    absent = grid - called
    branch_means = {}
    for key in ("called_difference", "all_embryos_lower", "all_embryos_upper"):
        margin = [v[key] for v in contrasts]
        branch_means[key] = (sum(margin) / len(margin) if None not in margin else None)
    marker11, = [r for r in eligible if r["figure_order"] == "11"]
    n11, k11, h11 = (int(marker11[key]) for key in ("genotyped", "carriers", "heterozygotes"))
    embryos = sum(BRANCH_EMBRYOS.values())
    groups = {}
    for origin in ("shared_trunk", "L1", "L2"):
        pool = [r for r in eligible if r["origin"] == origin]
        groups[origin] = {"amplified": len(pool), "carrier_positive": sum(int(r["carriers"]) > 0 for r in pool)}
    summary = {"trees": 1, "acorns": sum(BRANCH_EMBRYOS.values()), "acorns_by_branch": BRANCH_EMBRYOS,
               "loci_attempted": len(rows), "loci_amplified": len(eligible), "loci_per_origin": groups,
               "marker_embryo_pairs": grid, "genotyped": called, "missing": absent,
               "heterozygotes": het, "alternate_homozygotes": carriers - het, "carriers": carriers,
               "carrier_fraction_among_called": rounded(Fraction(carriers, called)),
               "carrier_fraction_all_embryos_bounds": [rounded(Fraction(k, grid)) for k in (carriers, carriers+absent)],
               "markers_with_parent_fraction_if_carrier_positive": sum(int(r["leaf_fraction_reported"])
                                   for r in eligible if int(r["carriers"]) > 0),
               "markers_with_parent_fraction_if_no_carrier": sum(int(r["leaf_fraction_reported"])
                                   for r in eligible if int(r["carriers"]) == 0),
               "maternal_alternate_under_mendelian_inheritance": {
                   "all_19_marker_embryo_pairs": {"denominator": grid, "lower": carriers - het,
                                                  "upper": carriers + absent},
                   "figure_marker_11": {"denominator": embryos, "lower": k11 - h11,
                                        "upper": k11 + embryos - n11}},
               "branch_specific_markers": len(contrasts), "mean_branch_contrast": {
                   k: rounded(v) for k,v in branch_means.items()},
               "strictly_positive_under_all_assignments": [r["figure_order"] for r in contrasts
                                                         if r["all_embryos_lower"] > 0],
               "strictly_negative_under_all_assignments": [r["figure_order"] for r in contrasts
                                                          if r["all_embryos_upper"] < 0]}
    return summary, contrasts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-tsv", action="store_true", help="Emit the ten marker-specific branch contrasts")
    args = parser.parse_args()
    with Path(__file__).with_name("marker_counts.tsv").open() as source:
        result, detailed = audit(list(csv.DictReader(source, delimiter="\t")))
    if args.branch_tsv:
        writer = csv.DictWriter(sys.stdout, detailed[0].keys(), delimiter="\t",lineterminator="\n")
        writer.writeheader()
        for record in detailed:
            writer.writerow({k: rounded(v) if isinstance(v, Fraction) else v for k,v in record.items()})
    else:
        print(json.dumps(result, indent=2))

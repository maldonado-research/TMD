"""Recalculate genotype and dwarf-phenotype concordance in Guner et al.'s Figure 7."""
import argparse
import csv
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDF_SHA256 = "ade8ac17497ac11a3b8cf6392099a732475fde846cca5659ccb226f152fddd79"
FAMILIES = ("WB-10", "WB-20", "Nana")
GENOTYPES = ("A/A", "A/G", "G/G")


def extract_pdf(path):
    """Read vector glyphs directly. Uses PyMuPDF only for the optional source replay."""
    import fitz

    if sha256(path.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError("Source PDF does not match the pinned author version.")
    with fitz.open(path) as document:
        assert len(document) == 1
        page = document[0]
        words = page.get_text("words")
        labels = [(w[4], (w[0] + w[2]) / 2) for w in words if w[4] in GENOTYPES]
        labels.sort(key=lambda t: t[1])
        assert [s for s, _ in labels] == list(GENOTYPES) * len(FAMILIES)
        headers = [w for w in words if w[4].replace("−", "-") in FAMILIES]
        assert [w[4].replace("−", "-") for w in sorted(headers, key=lambda w: w[0])] == list(FAMILIES)
        cores = Counter()
        drawings = page.get_drawings()
        panels = sorted((r["rect"] for r in drawings if r["type"] == "s"
                         and len(r["items"]) == 1 and r["items"][0][0] == "re"),key=lambda r:r.x0)
        assert len(panels) == 3
        for path_record in drawings:
            if tuple(part[0] for part in path_record["items"]) != ("c",) * 4:
                continue
            rect = path_record["rect"]
            assert abs(rect.width - 4.62) < .04 and abs(rect.height - 4.62) < .04
            assert path_record["type"] == "fs"
            center = (rect.x0 + rect.x1) / 2
            i = min(range(len(labels)), key=lambda j: abs(center - labels[j][1]))
            assert abs(center - labels[i][1]) < 5 and panels[i // 3].contains(rect)
            r, g, b = path_record["fill"]
            if (r, g, b) == (1, 0, 0):
                outcome = "dwarf"
            else:
                assert r == g == b and .54 < g < .56
                outcome = "normal"
            cores[FAMILIES[i // 3], labels[i][0], outcome] += 1
        return [{"family_panel": family, "genotype": geno, "dwarf": cores[family, geno, "dwarf"],
                 "normal": cores[family, geno, "normal"]}
                for family, geno in product(FAMILIES, GENOTYPES)]


def errors(rule, rows):
    return sum(r["normal"] if rule[GENOTYPES.index(r["genotype"])] else r["dwarf"] for r in rows)


def best_rule(rows):
    possibilities = list(product((False, True), repeat=3))
    costs = [errors(r, rows) for r in possibilities]
    minimum = min(costs)
    optimal = [dict(zip(GENOTYPES, ("dwarf" if x else "normal" for x in rule)))
               for rule, cost in zip(possibilities, costs) if cost == minimum]
    return {"minimum_errors": minimum, "optimal_rules": optimal}


def report(rows):
    assert [(r["family_panel"], r["genotype"]) for r in rows] == list(product(FAMILIES, GENOTYPES))
    totals = {}
    for genotype in GENOTYPES:
        selected = [r for r in rows if r["genotype"] == genotype]
        totals[genotype] = {k:sum(r[k] for r in selected) for k in ("dwarf", "normal")}
    per_family = {}
    for family in FAMILIES:
        selected = [r for r in rows if r["family_panel"] == family]
        per_family[family] = {k:sum(r[k] for r in selected) for k in ("dwarf", "normal")}
        per_family[family].update(best_rule(selected))
    rule = best_rule(rows)
    mistakes_family_specific = sum(v["minimum_errors"] for v in per_family.values())
    return {"point_counts": {k:sum(r[k] for r in rows) for k in ("dwarf", "normal")},
            "genotype_totals":totals, "panels":per_family, "common_rule":rule,
            "minimum_errors_if_rule_may_vary_by_panel":mistakes_family_specific,
            "finite_panel_formula_check":sum(min(v.values()) for v in totals.values()),
            "reported_results_for_comparison":{
                "Nana_GG_dwarf":55, "Nana_GG_total":64,
                "all_AA_dwarf":14, "all_AA_total":156}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract",type=Path,metavar="FIGURE7_PDF")
    args=parser.parse_args()
    if args.extract:
        import sys
        rows=extract_pdf(args.extract)
        writer=csv.DictWriter(sys.stdout, fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    else:
        with (HERE/"figure7_counts.tsv").open() as stream:
            rows=list(csv.DictReader(stream,delimiter="\t"))
        for r in rows:
            r["dwarf"], r["normal"] = int(r["dwarf"]), int(r["normal"])
        print(json.dumps(report(rows),indent=2))


if __name__=="__main__":
    main()

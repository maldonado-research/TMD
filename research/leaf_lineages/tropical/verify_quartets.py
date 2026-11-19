"""Check source pairs and quartet classifications without importing the production calculation."""
import argparse
from collections import Counter
from decimal import Decimal
from itertools import combinations, permutations
import json
from pathlib import Path
import re
from xml.etree import ElementTree
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent


def verify(rows, expected):
    physical = {}
    genetic = {}
    for a, b, cm, snvs in rows:
        edge = frozenset((a, b))
        assert edge not in physical
        physical[edge], genetic[edge] = cm, snvs
    assert len(physical) == 28
    nodes = sorted(frozenset().union(*physical))
    counts = Counter()
    for quartet in combinations(nodes, 4):
        kind = "basal_cambium_and_three_tips" if "0" in quartet else "four_tips"
        candidate = {}
        for a, b, c, d in permutations(quartet):
            parts = frozenset((frozenset((a,b)), frozenset((c,d))))
            candidate[parts] = tuple(sum(metric[edge] for edge in parts) for metric in (physical, genetic))
        assert len(candidate) == 3
        best = [set(), set()]
        exact = []
        for col in (0, 1):
            values = sorted(x[col] for x in candidate.values())
            best[col] = {split for split,vals in candidate.items() if vals[col] == values[0]}
            exact.append(values[1] == values[2])
        assert len(best[0]) == 1 and exact[0]
        if len(best[1]) == 3: status = "snv_tied_minimum"
        elif len(best[1]) == 1:
            status = "unique_agreement" if best[0] == best[1] else "unique_disagreement"
        else: raise AssertionError("Unexpected two-way tie for smallest")
        counts[kind,status] += 1
        counts[kind,"snv_exact_four_point"] += exact[1]
    for kind, result in expected.items():
        for name, n in result["comparison"].items():
            assert n == counts[kind, name]
        assert counts[kind, "snv_exact_four_point"] == result["snv_exact_four_point"]
        assert result["physical_exact_four_point"] == result["physical_unique_smallest"] == result["quartets"] == 35


def read_xml(workbook):
    # Parse sheet b via workbook relationships and address each lower-triangle block directly.
    with ZipFile(workbook) as z:
        book = ElementTree.fromstring(z.read("xl/workbook.xml"))
        sheet = next(s for s in book.findall(".//{*}sheet") if s.get("name") == "b")
        rid = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        rels = ElementTree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target = next(r.get("Target") for r in rels if r.get("Id") == rid)
        sheet_path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        strings = ["".join(si.itertext()) for si in ElementTree.fromstring(z.read("xl/sharedStrings.xml"))]
        tree = ElementTree.fromstring(z.read(sheet_path))
    cells = {}
    for cell in tree.findall(".//{*}c"):
        value = cell.findtext("{*}v")
        if value is not None:
            cells[cell.get("r")] = strings[int(value)] if cell.get("t") == "s" else value
    all_rows = {}
    for row in range(2,30):
        individual, sample = cells["B"+str(row)],cells["C"+str(row)]
        found = all_rows.setdefault(individual, {})
        for col in "DEFGHIJ":
            raw = cells.get(col+str(row))
            if raw is None:continue
            distance,count = re.fullmatch(r"([\d.]+)\s+\((\d+)\)",raw).groups()
            found[frozenset((cells[col+"1"],sample))]=(int(Decimal(distance)*100),int(count))
    return all_rows


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workbook",type=Path)
    args=p.parse_args()
    matrices=json.loads((HERE/"tip_distances.json").read_text())["trees"]
    results=json.loads((HERE/"quartet_result.json").read_text())
    native=read_xml(args.workbook) if args.workbook else None
    for individual, rows in matrices.items():
        if native is not None:
            assert {frozenset((a,b)):(d,n) for a,b,d,n in rows} == native[individual]
        verify(rows,results[individual])
    print("All 280 quartet comparisons agree with the independent enumeration.")
    if native is not None:print("All 112 pairs of physical and SNV distances agree with the workbook XML.")

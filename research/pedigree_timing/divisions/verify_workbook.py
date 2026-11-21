"""Extract anonymous totals for scored maternal divisions from Dowsett et al. Data 1."""
import argparse
import csv
import hashlib
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

EXPECTED = "cb2ebd86284731f8386f58ee67effbd1e6eeca0e3f73fbbe08897caf0c738fc7"


def extract(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED:
        raise ValueError("The input differs from the published workbook.")
    with ZipFile(path) as archive:
        strings = ["".join(s.itertext()) for s in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        sheets = {s.get("name"): "xl/" + rels[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
                  for s in ET.fromstring(archive.read("xl/workbook.xml")).findall(".//{*}sheet")}

        def rows(sheet, columns):
            with archive.open(sheets[sheet]) as stream:
                for _, row in ET.iterparse(stream, events=("end",)):
                    if not row.tag.endswith("}row"):
                        continue
                    values = {}
                    for cell in row.findall("{*}c"):
                        key = cell.get("r").rstrip("0123456789")
                        value = cell.findtext("{*}v")
                        if key in columns and value is not None:
                            values[key] = strings[int(value)] if cell.get("t") == "s" else value
                    row.clear()
                    yield values

        totals = {}
        for r in rows("MutInSegGroups", set("ABCDEFGHIJ")):
            if not r.get("A", "").isdigit():
                continue
            ident = int(r["A"])
            assert ident not in totals
            da, db, dm, ma, mb, mm, total = (int(r[k]) for k in "DEFGHIJ")
            assert da + db == dm and ma + mb == mm and dm + mm == total
            totals[ident] = (int(r["B"].removeprefix("AH")), int(r["C"]), total)

        raw = Counter()
        for r in rows("Full Mutation List", {"A", "B", "F"}):
            if r.get("F") == "Division ID":
                continue
            ident = int(r["F"])
            assert (int(r["A"]), int(r["B"])) == totals[ident][:2]
            raw[ident] += 1
        assert {i: v[2] for i, v in totals.items()} == raw

    lineages = sorted({v[0] for v in totals.values()})
    assert len(totals) == 50 and len(lineages) == 7
    result = sorted((f"Y{lineages.index(group)+1}", division, count) for group, division, count in totals.values())
    assert len(set((group, day) for group, day, _ in result)) == len(result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(("pedigree", "physical_division", "assigned_changes"))
    writer.writerows(extract(args.workbook))

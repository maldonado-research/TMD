#!/usr/bin/env python3
"""MIT. Offline R27 source identity, workbook units and public invariant checks.

No network access, spreadsheet execution, general formula evaluation or extraction.
Exact source files and provider wrappers remain outside the public repository.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def cache_path(cache, name):
    if Path(name).name != name:
        raise ValueError("Source name must be a basename")
    path = cache / name
    if path.is_symlink() or path.resolve().parent != cache.resolve():
        raise ValueError("Source must remain inside the declared cache")
    return path


def workbook(path, expected_sheet):
    if path.stat().st_size > 65536:
        raise ValueError("Workbook exceeds 64 KiB cap")
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        if len(entries) > 100 or sum(e.file_size for e in entries) > 1048576:
            raise ValueError("Workbook archive exceeds bounded inspection")
        if len({e.filename for e in entries}) != len(entries):
            raise ValueError("Duplicate archive entries")
        for e in entries:
            p = PurePosixPath(e.filename)
            if p.is_absolute() or ".." in p.parts or e.flag_bits & 1:
                raise ValueError("Unsafe or encrypted archive entry")
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        prop = wb.find("s:workbookPr", NS)
        if prop is not None and prop.attrib.get("date1904", "0") not in ("0", "false"):
            raise ValueError("Unexpected workbook date epoch")
        sheets = wb.findall("s:sheets/s:sheet", NS)
        if [s.attrib["name"] for s in sheets] != [expected_sheet]:
            raise ValueError("Unexpected worksheet names")
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        rid = sheets[0].attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rels[rid]
        if not re.fullmatch(r"worksheets/sheet[1-9][0-9]*\.xml", target):
            raise ValueError("Unexpected worksheet target")
        strings = ["".join(t.text or "" for t in x.findall(".//s:t", NS)) for x in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        styles = ET.fromstring(z.read("xl/styles.xml")).findall("s:cellXfs/s:xf", NS)
        cells = {}
        for c in ET.fromstring(z.read("xl/" + target)).findall(".//s:c", NS):
            v, f = c.find("s:v", NS), c.find("s:f", NS)
            value = None if v is None else v.text
            if c.attrib.get("t") == "s" and value is not None:
                value = strings[int(value)]
            cells[c.attrib["r"]] = {"value": value, "type": c.attrib.get("t"), "formula": None if f is None else {"text": f.text, "attributes": dict(f.attrib)}, "number_format": styles[int(c.attrib.get("s", "0"))].attrib.get("numFmtId")}
    return cells, target


def workbook_audit(cache):
    p, ptarget = workbook(cache_path(cache, "Pellicle_success.xlsx"), "Tabelle1")
    assert p["A1"]["value"] == "pellicle, total"
    strata = []
    for dilution_col, pair_col, row_end in [("A", "B", 7), ("D", "E", 7), ("G", "H", 5), ("J", "K", 4)]:
        assert p[dilution_col + "3"]["value"] == "dilution 10^x"
        date_cell = p[pair_col + "2"]
        assert date_cell["number_format"] == "14" and date_cell["formula"] is None
        serial = int(date_cell["value"])
        date = (dt.date(1899, 12, 30) + dt.timedelta(days=serial)).isoformat()
        for row in range(4, row_end + 1):
            cell = p[pair_col + str(row)]
            assert cell["formula"] is None and cell["type"] == "s"
            match = re.fullmatch(r"(\d+),\s*(\d+)", cell["value"])
            assert match
            successes, total = map(int, match.groups())
            assert 0 <= successes <= total
            strata.append({"date_serial_cell": pair_col + "2", "date_serial": serial, "date_iso_from_workbook_format": date, "dilution_exponent": p[dilution_col + str(row)]["value"], "pair_cell": pair_col + str(row), "pellicles": successes, "total_recorded": total, "individual_well_ids": None, "independent_preculture_ids": None})
    r, rtarget = workbook(cache_path(cache, "PcdrA-evo-count_2024_10_08.xlsx"), "Sheet1")
    categories = [r[c + "1"]["value"] for c in "BCDE"]
    assert categories == ["SM dark", "SM red", "WS dark", "WS red"]
    assert r["F1"]["value"] == "total"
    anchor = r["F3"]["formula"]
    assert anchor == {"text": "SUM(B3:E3)", "attributes": {"t": "shared", "ref": "F3:F7", "si": "0"}}
    rows, groups = [], []
    for row in range(2, 8):
        counts = []
        for col in "BCDE":
            cell = r[col + str(row)]
            assert cell["formula"] is None and cell["type"] != "s"
            value = int(cell["value"])
            assert value >= 0
            counts.append(value)
        f = r["F" + str(row)]["formula"]
        if row == 2:
            assert f == {"text": "SUM(B2:E2)", "attributes": {}}
        elif row > 3:
            assert f == {"text": None, "attributes": {"t": "shared", "si": "0"}}
        expected = sum(counts)
        assert expected == int(r["F" + str(row)]["value"])
        assert r["A" + str(row)]["value"] == f"plate {(row - 2)//2 + 1}-6-{(row - 2)%2 + 1}"
        rows.append({"source_row": row, "source_plate_label": r["A" + str(row)]["value"], "total_sampled_colonies": expected, "total_cell": "F" + str(row), "cached_total_agrees": True, "formula_status": "explicit" if row == 2 else "shared_anchor" if row == 3 else "shared_descendant_checked_by_relative_row_sum"})
    for i, (first, last) in enumerate([(2, 3), (4, 5), (6, 7)], 1):
        cell = "G" + str(last)
        assert r[cell]["formula"] == {"text": f"SUM(F{first}:F{last})", "attributes": {}}
        counts = {cat: sum(int(r[col + str(row)]["value"]) for row in (first, last)) for cat, col in zip(categories, "BCDE")}
        total = sum(counts.values())
        assert total == int(r[cell]["value"])
        groups.append({"numbered_plate_group": i, "source_rows": [first, last], "summary_cell": cell, "category_sums": counts, "sampled_colonies": total, "cached_summary_agrees": True, "independent_culture_id": None, "molecular_route_assignments": None})
    return {"schema_version": 1, "interpretation": "Derived unit audit, not independent origins or biological assay calibration.", "pellicle": {"source_filename": "Pellicle_success.xlsx", "sheet": "Tabelle1", "worksheet_member": ptarget, "date_epoch": "Excel 1900 system; serial >=61 converted with 1899-12-30 base; date style14 checked", "strata": strata, "date_block_count": 4, "aggregate_pair_count": 11, "recorded_well_outcomes_sum": sum(s["total_recorded"] for s in strata), "genotype_cell": None, "well_level_outcomes_available": False, "pooled_probability_admitted": False}, "reporter": {"source_filename": "PcdrA-evo-count_2024_10_08.xlsx", "sheet": "Sheet1", "worksheet_member": rtarget, "plate_rows": rows, "numbered_groups": groups, "category_totals": {cat: sum(g["category_sums"][cat] for g in groups) for cat in categories}, "sampled_colonies_total": sum(g["sampled_colonies"] for g in groups), "literal_category_count_cells": 24, "verified_cached_formula_cells": 9, "shared_formula_descendants": 4, "suffix_meanings_authenticated": False, "independence_of_numbered_groups_authenticated": False, "raw_plate_rows_pooled_as_origins": False}, "blank_cells_converted_to_zero": 0, "spreadsheets_executed": False, "raw_source_published": False}


def verify(cache=None):
    if sys.flags.optimize:
        raise RuntimeError("Run ordinary Python without -O or -OO; assertions are required")
    sources = read_json(ROOT / "SOURCES.json")
    strains = read_json(ROOT / "STRAIN_MAP.json")
    joins = read_json(ROOT / "UNIT_JOIN_MATRIX.json")
    audit = read_json(ROOT / "WORKBOOK_UNIT_AUDIT.json")
    assert sources["logical_scientific_calls"] == 7
    assert sources["exact_binary_bytes"] == 18289
    assert sources["one_evidence_family"] is True
    assert strains["strain_count"] == len(strains["strains"]) == 14
    assert len({s["internal_id"] for s in strains["strains"]}) == 14
    assert strains["coordinate_ambiguities"][0]["normalized_allele"] is None
    assert joins["decision"] == "NO_COMPLETE_MATCHED_ROUTE_ORIGIN_CONTROL_PANEL"
    assert joins["actual_study_fields_unchanged_null"] == 26
    assert joins["native_planning_fields_unchanged_null"] == 18
    assert audit["pellicle"]["aggregate_pair_count"] == 11
    assert audit["reporter"]["sampled_colonies_total"] == 3376
    assert sum(audit["reporter"]["category_totals"].values()) == 3376
    checked = []
    allow = read_json(ROOT / "PUBLIC_FILES.json")["files"]
    actual = sorted(p.name for p in ROOT.iterdir() if p.is_file())
    assert actual == sorted(allow)
    assert not any(p.is_symlink() or p.is_dir() for p in ROOT.iterdir())
    for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines():
        expected, name = line.split("  ", 1)
        assert name in allow and name not in ("SHA256SUMS.txt", "VERIFICATION_RECEIPT.json")
        assert digest((ROOT / name).read_bytes()) == expected
        checked.append(name)
    expected_hashed = set(allow) - {"SHA256SUMS.txt", "VERIFICATION_RECEIPT.json"}
    assert set(checked) == expected_hashed and len(checked) == len(expected_hashed)
    replay = "UNRUN_SOURCE_CACHE_NOT_PROVIDED"
    if cache is not None:
        for source in sources["acquisitions"]:
            payload = cache_path(cache, source["capture_filename"]).read_bytes()
            assert len(payload) == source["capture_bytes"] and digest(payload) == source["capture_sha256"]
            wrapper = json.loads(payload)
            assert wrapper["acquisition_id"] == source["acquisition_id"]
            assert wrapper["args"] == source["args"]
            canonical = json.dumps(wrapper["response"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            assert len(canonical) == source["response_canonical_json_bytes"] and digest(canonical) == source["response_canonical_json_sha256"]
        for binary in sources["exact_binaries"]:
            data = cache_path(cache, binary["filename"]).read_bytes()
            assert len(data) == binary["bytes"] and digest(data) == binary["sha256"] and hashlib.md5(data).hexdigest() == binary["md5"]
        assert workbook_audit(cache) == audit
        supplement = read_json(cache_path(cache, "04_supplement_pdf.json"))["response"]["structuredContent"]["markdown"]
        for strain in strains["strains"]:
            assert strain["internal_id"] in supplement
            for token in strain["representation_tokens"]:
                assert token in supplement
        for anchor in sources["anchors"]:
            source = read_json(cache_path(cache, anchor["capture_filename"]))["response"]["structuredContent"]
            assert anchor["excerpt"] in source[anchor.get("field", "markdown")]
        replay = "PASS_EXACT_R27_WRAPPERS_TWO_BINARIES_AND_DERIVED_AUDIT"
    return {"public_invariants": "PASS", "allowlist_and_hashes": "PASS", "source_replay": replay, "r26_source_replay": "UNRUN_PRIOR_CACHE_UNAVAILABLE", "supplement_exact_pdf_replay": "UNRUN_EXACT_PDF_NOT_ACQUIRED", "biological_or_causal_validation": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_cache), indent=2))

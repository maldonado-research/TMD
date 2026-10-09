#!/usr/bin/env python3
"""MIT. Offline R26 source-identity and declared workbook arithmetic checks.

No network, spreadsheet execution, expression evaluation, or archive extraction.
Raw source caches are optional and remain outside this public package.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET
import zipfile
import re
from fractions import Fraction

ROOT = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
WORKBOOK = "SM-mixevo_count_2024_10_02.xlsx"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_path(cache, name):
    if Path(name).name != name:
        raise ValueError("Source name must be a basename")
    path = cache / name
    if path.is_symlink() or path.resolve().parent != cache.resolve():
        raise ValueError("Source must remain inside the declared cache")
    return path


def workbook_audit(path):
    """Parse the pinned sheet and compute literal count sums, retaining anomalies."""
    if path.stat().st_size > 65536:
        raise ValueError("Workbook exceeds the declared 64 KiB cap")
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        if len(entries) > 100 or sum(x.file_size for x in entries) > 1048576:
            raise ValueError("Archive exceeds bounded inspection limits")
        if len({x.filename for x in entries}) != len(entries):
            raise ValueError("Duplicate archive members")
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or ".." in name.parts or entry.flag_bits & 1:
                raise ValueError("Unsafe or encrypted archive member")
        sheet_names = [x.attrib["name"] for x in ET.fromstring(z.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS)]
        if sheet_names != ["Tabelle1"]:
            raise ValueError("Unexpected sheets; mapping must be reviewed")
        strings = ["".join(t.text or "" for t in x.findall(".//s:t", NS)) for x in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        cells = {}
        for cell in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).findall(".//s:c", NS):
            value = cell.find("s:v", NS)
            formula = cell.find("s:f", NS)
            text = None if value is None else value.text
            if cell.attrib.get("t") == "s":
                text = strings[int(text)]
            elif text is not None:
                text = int(text)
            cells[cell.attrib["r"]] = {"value": text, "formula": None if formula is None else formula.text}
    if cells["B2"]["value"] != "red" or cells["D2"]["value"] != "green":
        raise ValueError("Unexpected colour columns")
    blocks = [("line_1", 3), ("line_1", 7), ("line_1", 11), ("line_2", 16), ("line_3", 21), ("line_4", 26), ("line_5", 32)]
    rows = []
    for line, start in blocks:
        for offset, morph in enumerate(["wheel", "large", "small", "SM"]):
            row = start + offset
            for colour, label_col, count_col in [("red", "B", "C"), ("green", "D", "E")]:
                if cells[label_col + str(row)]["value"] != morph:
                    raise ValueError("Unexpected morphology label")
                key = count_col + str(row)
                value = cells[key]["value"]
                if not isinstance(value, int) or value < 0 or cells[key]["formula"] is not None:
                    raise ValueError("Raw count must be a nonnegative literal integer")
                rows.append({"line_group": line, "source_block_label": cells["A" + str(start)]["value"], "colour_column": colour, "morphology": morph, "cell": key, "count": value, "status": "observed_zero" if value == 0 else "observed_positive"})
    if cells["B30"]["value"] != "Dark wheel" or cells["C30"]["value"] != 21:
        raise ValueError("The separate Dark wheel category changed")
    rows.append({"line_group": "line_4", "source_block_label": cells["A26"]["value"], "colour_column": "red_column_assignment_unadjudicated", "morphology": "Dark wheel", "cell": "C30", "count": 21, "status": "observed_positive"})
    summary = []
    for offset, morph in enumerate(["wheel", "large", "small", "SM"]):
        for colour, col in [("red", "I"), ("green", "K")]:
            key = col + str(3 + offset)
            expected = sum(x["count"] for x in rows if x["line_group"] == "line_1" and x["morphology"] == morph and x["colour_column"] == colour)
            summary.append({"cell": key, "colour": colour, "morphology": morph, "cached_value": cells[key]["value"], "formula_text": cells[key]["formula"], "independent_literal_sum": expected, "agrees": cells[key]["value"] == expected})
    lines = []
    for line in ["line_1", "line_2", "line_3", "line_4", "line_5"]:
        records = [x for x in rows if x["line_group"] == line]
        standard = [x for x in records if x["morphology"] != "Dark wheel"]
        colours = {colour: {morph: sum(x["count"] for x in standard if x["colour_column"] == colour and x["morphology"] == morph) for morph in ["wheel", "large", "small", "SM"]} for colour in ["red", "green"]}
        lines.append({"line_group": line, "literal_standard_count_sum": sum(x["count"] for x in standard), "separate_dark_wheel_count": sum(x["count"] for x in records if x["morphology"] == "Dark wheel"), "literal_sum_including_separate_category": sum(x["count"] for x in records), "standard_colour_morphology_sums": colours, "all_six_standard_WS_classes_positive": all(colours[c][m] > 0 for c in colours for m in ["wheel", "large", "small"]), "independent_mutation_origins": None, "Wsp_Aws_Mws_assignments": None})
    return {"schema_version": 1, "source_doi": "10.5281/zenodo.15735347", "article_doi": "10.1098/rspb.2025.2004", "source_license": "CC BY 4.0", "source_filename": WORKBOOK, "sheet": "Tabelle1", "worksheet_note_A1": cells["A1"]["value"], "line_1_summary_label_G3": cells["G3"]["value"], "summary_formula_cell_count": sum(x["formula_text"] is not None for x in summary), "unadjudicated_blank": {"cell": "E30", "source_cell_present": "E30" in cells, "value": None, "status": "absent_cell_not_zero", "meaning": "No paired green Dark wheel count is recorded; no negative biological conclusion."}, "interpretation": "Literal sampled-colony count arithmetic; source labels and article Fig 6 identify five line groups. Plate suffix meanings, unequal sampling weights, biological independence and origin counts are not authenticated by arithmetic.", "raw_count_cells": rows, "line_1_summary_cells_not_added_again": summary, "line_summaries": lines, "raw_count_cell_count": len(rows), "positive_count_cells": sum(x["count"] > 0 for x in rows), "zero_count_cells": sum(x["count"] == 0 for x in rows), "blank_cells_converted_to_zero": 0, "source_reported_FS_note_converted_to_numeric_zero": False, "sum_of_all_literal_count_cells": sum(x["count"] for x in rows), "sum_excluding_unadjudicated_Dark_wheel": sum(x["count"] for x in rows if x["morphology"] != "Dark wheel"), "independent_origin_count": None, "source_summary_formulas_executed": False, "raw_source_published": False}


def surface_audit(path):
    if path.stat().st_size > 65536:
        raise ValueError("Surface workbook exceeds 64 KiB")
    groups, formula_checks = [], []
    with zipfile.ZipFile(path) as z:
        entries = z.infolist()
        if len(entries) > 100 or sum(x.file_size for x in entries) > 1048576 or len({x.filename for x in entries}) != len(entries):
            raise ValueError("Unsafe archive size or duplicate members")
        for entry in entries:
            name = PurePosixPath(entry.filename)
            if name.is_absolute() or ".." in name.parts or entry.flag_bits & 1:
                raise ValueError("Unsafe or encrypted member")
        strings = ["".join(t.text or "" for t in x.findall(".//s:t", NS)) for x in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        rels = {x.attrib["Id"]: x.attrib["Target"] for x in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS):
            name = sheet.attrib["name"]
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rels[rid]
            if not re.fullmatch(r"worksheets/sheet[1-9][0-9]*\.xml", target):
                raise ValueError("Unexpected worksheet relationship")
            cells = {}
            for cell in ET.fromstring(z.read("xl/" + target)).findall(".//s:c", NS):
                value, formula = cell.find("s:v", NS), cell.find("s:f", NS)
                text = None if value is None else value.text
                if cell.attrib.get("t") == "s":
                    text = strings[int(text)]
                cells[cell.attrib["r"]] = {"value": text, "formula": None if formula is None else formula.text}
                if formula is not None:
                    if not re.fullmatch(r"[0-9]+(?:[*/][0-9]+)+", formula.text):
                        raise ValueError("Formula requires separate review; expressions are never executed")
                    tokens = re.split(r"([*/])", formula.text)
                    exact = Fraction(tokens[0])
                    for op, number in zip(tokens[1::2], tokens[2::2]):
                        exact = exact * Fraction(number) if op == "*" else exact / Fraction(number)
                    formula_checks.append({"sheet": name, "cell": cell.attrib["r"], "source_formula_text": formula.text, "cached_value": text, "independent_exact_rational": str(exact), "agrees": Fraction(text) == exact})
            if cells["A1"]["value"] != "Saturated cell density measured by plating [cells/mL]" or cells["B3"]["value"] != "ROI Area [um^2]":
                raise ValueError("Unexpected measurement units")
            rows = []
            for row in range(4, 8):
                dilution = cells.get("A" + str(row), {}).get("value")
                if dilution is None:
                    continue
                area = cells.get("B" + str(row), {}).get("value")
                counts = [{"cell": key, "count": int(item["value"]), "status": "observed_zero" if int(item["value"]) == 0 else "observed_positive"} for key, item in cells.items() if re.fullmatch(r"[C-Z]" + str(row), key) and item["value"] is not None]
                rows.append({"row": row, "dilution_factor": int(dilution), "ROI_area_um2": area, "count_cells": counts, "number_of_recorded_counts": len(counts), "literal_sum_of_recorded_counts": sum(x["count"] for x in counts) if counts else None, "status": "recorded_image_count_group" if area is not None and counts else "declared_dilution_missing_area_and_counts", "nominal_inoculum_cells_per_mL_exact": str(Fraction(cells["B1"]["value"]) / Fraction(dilution)), "independent_cultures": None, "known_introduced_lineages": None})
            groups.append({"sheet": name, "source_date_label_B2": cells["B2"]["value"], "saturated_density_cells_per_mL": cells["B1"]["value"], "rows": rows})
    count_cells = [x for g in groups for row in g["rows"] for x in row["count_cells"]]
    return {"schema_version": 1, "source_filename": "Surface_density_data.xlsx", "source_doi": "10.5281/zenodo.15735347", "source_license": "CC BY 4.0", "groups": groups, "formula_cache_checks": formula_checks, "sheet_count": len(groups), "declared_dilution_groups": sum(len(x["rows"]) for x in groups), "complete_count_groups": sum(row["status"] == "recorded_image_count_group" for x in groups for row in x["rows"]), "recorded_count_cells": len(count_cells), "observed_zero_count_cells": sum(x["count"] == 0 for x in count_cells), "missing_cells_imputed": 0, "normalization_contract": {"source_surface_density": "image count / ROI area [cells/um^2]", "nominal_inoculum_density": "source saturated plating-derived density / dilution factor [cells/mL]", "source_ratio_units": "mL/um^2; dimensional, not a probability", "required_join": "ROI/image/well/culture/date/strain/allele identity before biological replication or matched-context inference", "timepoint": "2 h from the primary Methods; not encoded independently in these sheets", "plate_count_to_actual_cell_number": "not independently calibrated in this workbook", "source_formulas_executed": False}, "independent_Wsp_Aws_Mws_panel": False}


def verify(cache=None):
    ledger = read_json(ROOT / "SOURCES.json")
    audit = read_json(ROOT / "DERIVED_WORKBOOK_AUDIT.json")
    checks = []
    def check(label, condition):
        if not condition:
            raise ValueError(label)
        checks.append(label)
    check("eleven bounded scientific acquisition attempts retained", len(ledger["acquisitions"]) == 11)
    check("study admission remains blocked", read_json(ROOT / "ADMISSION_MATRIX.json")["decision"] == "LICENSED_ECOLOGICAL_LEAD_AND_ENDPOINT_WORKBOOK_AUTHENTICATED_NO_MATCHED_PANEL_ADMITTED")
    check("five source line groups", len(audit["line_summaries"]) == 5)
    check("raw and aggregate cells kept separate", audit["raw_count_cell_count"] == 57 and len(audit["line_1_summary_cells_not_added_again"]) == 8)
    check("observed zeros retained", audit["positive_count_cells"] == 55 and audit["zero_count_cells"] == 2)
    check("all explicit line-1 summary values reproduced", all(x["agrees"] for x in audit["line_1_summary_cells_not_added_again"]))
    check("ambiguous Dark wheel retained separately", audit["sum_of_all_literal_count_cells"] == 1014 and audit["sum_excluding_unadjudicated_Dark_wheel"] == 993)
    check("no imputed missing counts or origins", audit["blank_cells_converted_to_zero"] == 0 and audit["independent_origin_count"] is None)
    surface = read_json(ROOT / "SURFACE_DENSITY_AUDIT.json")
    check("surface count groups and missing dilution preserved", surface["sheet_count"] == 7 and surface["declared_dilution_groups"] == 25 and surface["complete_count_groups"] == 24 and surface["recorded_count_cells"] == 200 and surface["missing_cells_imputed"] == 0)
    check("all restricted surface formula caches agree", len(surface["formula_cache_checks"]) == 21 and all(x["agrees"] for x in surface["formula_cache_checks"]))
    source_state = "UNRUN_EXTERNAL_CACHE_NOT_SUPPLIED"
    if cache is not None:
        for row in ledger["acquisitions"]:
            path = source_path(cache, row["capture_filename"])
            if path.stat().st_size > 2097152:
                raise ValueError("Source capture exceeds 2 MiB")
            raw = path.read_bytes()
            check(row["acquisition_id"] + " capture bytes/hash", len(raw) == row["capture_bytes"] and digest(raw) == row["capture_sha256"])
        api = read_json(source_path(cache, "08_context_deposit_api.json"))["response"]["structuredContent"]["rawHtml"]
        record = json.loads(api)
        check("official dataset identity and license", record["id"] == 15735347 and record["metadata"]["license"]["id"] == "cc-by-4.0")
        source_files = [{"filename": x["key"], "size_bytes": x["size"], "md5": x["checksum"], "url": x["links"]["self"]} for x in record["files"]]
        check("fourteen exact catalogue entries", source_files == read_json(ROOT / "ACQUISITION_PLAN.json")["official_deposit_files"] and len(source_files) == 14)
        filemeta = next(x for x in source_files if x["filename"] == WORKBOOK)
        path = source_path(cache, WORKBOOK)
        raw = path.read_bytes()
        check("workbook exact bytes and official MD5", len(raw) == filemeta["size_bytes"] == 9925 and "md5:" + hashlib.md5(raw).hexdigest() == filemeta["md5"])
        check("workbook SHA256", digest(raw) == ledger["workbook"]["sha256"])
        check("literal workbook replay matches full derived audit", workbook_audit(path) == audit)
        surface_path = source_path(cache, "Surface_density_data.xlsx")
        surface_bytes = surface_path.read_bytes()
        surfmeta = next(x for x in source_files if x["filename"] == "Surface_density_data.xlsx")
        check("surface workbook official bytes and MD5", len(surface_bytes) == surfmeta["size_bytes"] == 15773 and "md5:" + hashlib.md5(surface_bytes).hexdigest() == surfmeta["md5"])
        check("surface workbook SHA256", digest(surface_bytes) == ledger["surface_workbook"]["sha256"])
        check("surface workbook groups, missingness and formula-cache replay", surface_audit(surface_path) == read_json(ROOT / "SURFACE_DENSITY_AUDIT.json"))
        for anchor in ledger["primary_anchors"]:
            response = read_json(source_path(cache, anchor["capture_filename"]))["response"]["structuredContent"]
            text = response.get("markdown", response.get("rawHtml", ""))
            check(anchor["anchor_id"] + " exact primary text", anchor["excerpt"] in text)
        source_state = "PINNED_CACHE_AND_WORKBOOK_VERIFIED"
    return {"status": "PASS", "source_replay": source_state, "checks_passed": len(checks), "checks": checks, "scientific_boundary": "Artifact identity and declared literal arithmetic only; no full route/control panel, population frequency, independent-origin count, biological fit, forecast or causal validation."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_cache), indent=2) + "\n", end="")

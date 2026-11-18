#!/usr/bin/env python3
"""Recompute paired detection counts from Xian et al., Table S10 (Python 3 standard library)."""

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RECEIPT = Path(__file__).with_name("oak_receipt.json")


def load_workbook(path, source):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() == source["archive_sha256"]:
        with ZipFile(io.BytesIO(data)) as archive:
            data = archive.read(source["workbook_filename"])
    if hashlib.sha256(data).hexdigest() != source["workbook_sha256"]:
        raise ValueError("Input must match the journal workbook or its archived ZIP.")
    return data


def count_detections(data, selection):
    with ZipFile(io.BytesIO(data)) as book:
        sheet = ET.fromstring(book.read(selection["worksheet_member"]))
        styles = ET.fromstring(book.read("xl/styles.xml"))
        strings = ["".join(node.itertext()) for node in ET.fromstring(book.read("xl/sharedStrings.xml"))]
    cells = {cell.get("r"): cell for cell in sheet.iter(NS + "c")}
    fills = styles.find(NS + "fills")
    formats = styles.find(NS + "cellXfs")

    def value(address):
        cell = cells[address]
        raw = cell.findtext(NS + "v")
        return strings[int(raw)] if cell.get("t") == "s" else raw

    def detected(address):
        style = formats[int(cells[address].get("s", "0"))]
        fill = fills[int(style.get("fillId"))].find(NS + "patternFill")
        if fill.get("patternType") == "none":
            return False
        color = fill.find(NS + "fgColor")
        if fill.get("patternType") == "solid" and color is not None and color.get("rgb") == selection["detected_fill_argb"]:
            return True
        raise ValueError("Unexpected color in a detection field.")

    groups = {}
    for method, (first, last) in selection["method_rows"].items():
        records = {}
        for row in range(first, last + 1):
            key = (value(f"A{row}"), value(f"B{row}"))
            if not all(key) or key in records:
                raise ValueError("Missing or duplicate reference key in a method block.")
            records[key] = detected(f"B{row}")
        groups[method] = records

    combined, haploid, diploid = (groups[name] for name in selection["pattern_order"])
    if combined.keys() != haploid.keys() or combined.keys() != diploid.keys():
        raise ValueError("The method blocks have different sets of reference keys.")
    patterns = Counter(
        "".join("1" if calls[key] else "0" for calls in (combined, haploid, diploid))
        for key in combined
    )
    return {
        "paired_reference_positives": len(combined),
        "detected_by_method": {name: sum(calls.values()) for name, calls in groups.items()},
        "pattern_counts": {format(bits, "03b"): patterns[format(bits, "03b")] for bits in range(8)},
        "both_strelka2_references_detected": sum(haploid[k] and diploid[k] for k in combined),
        "neither_strelka2_reference_detected": sum(not (haploid[k] or diploid[k]) for k in combined),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_file", type=Path, help="Journal supplementary ZIP or original XLSX")
    args = parser.parse_args()
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    data = load_workbook(args.source_file, receipt["source"])
    counts = count_detections(data, receipt["selection"])
    if counts != receipt["counts"]:
        raise ValueError("Recomputed counts differ from the saved receipt.")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()

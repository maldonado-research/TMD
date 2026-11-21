"""Rebuild anonymous six-class division counts from Dowsett et al. Data 1 (2021)."""

import argparse
import csv
import hashlib
import io
import re
import sys
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile


WORKBOOK_SHA256 = "cb2ebd86284731f8386f58ee67effbd1e6eeca0e3f73fbbe08897caf0c738fc7"
PRIOR_DIVISIONS_SHA256 = "fa570d44673511a2b6f7f4e07cfe2e3726b5fda437bac6b87d4325537ce70a33"
REFERENCE_SHA256 = "dbf065ffc3f5bbaa7554ef53c6861399eecc597fe058df5f81ba557944e3f86b"
REFERENCE_FILE = "S288C_reference_genome_R64-2-1_20150113/S288C_reference_sequence_R64-2-1_20150113.fsa"
CLASSES = ("C>A", "C>G", "C>T", "T>A", "T>C", "T>G")
COMPLEMENT = str.maketrans("ACGT", "TGCA")
ID_COLUMNS = ("pedigree", "physical_division", "assigned_changes")
HEADER = (*ID_COLUMNS, *CLASSES, "transitions", "transversions", "unclassified")


def substitution(label):
    if not re.fullmatch("[ACGT]:[ACGT]", label or "") or label[0] == label[2]:
        return "unclassified"
    if label[0] in "AG":
        label = label.translate(COMPLEMENT)
    return label.replace(":", ">")


def read_rows(archive, member, columns, strings):
    with archive.open(member) as stream:
        for _, row in ET.iterparse(stream, events=("end",)):
            if not row.tag.endswith("}row"):
                continue
            values = {}
            for cell in row.findall("{*}c"):
                col = cell.get("r").rstrip("0123456789")
                value = cell.findtext("{*}v")
                if col in columns and value is not None:
                    values[col] = strings[int(value)] if cell.get("t") == "s" else value
            row.clear()
            yield values


def load_reference(path):
    with tarfile.open(path) as archive:
        data = archive.extractfile(REFERENCE_FILE).read()
    if hashlib.sha256(data).hexdigest() != REFERENCE_SHA256:
        raise ValueError("SGD reference FASTA differs from the 2015 file.")
    sequences = {}
    for line in data.splitlines():
        if line.startswith(b">"):
            accession = re.search(rb"NC_[0-9]+", line).group().decode()
            sequences[accession] = bytearray()
        else:
            sequences[accession].extend(line.strip().upper())
    return sequences


def write_tsv(out, header, rows):
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)


def extract(workbook, reference_path=None):
    if hashlib.sha256(workbook.read_bytes()).hexdigest() != WORKBOOK_SHA256:
        raise ValueError("Data 1 differs from the published workbook.")
    reference = load_reference(reference_path) if reference_path else None
    discrepancies = []
    with ZipFile(workbook) as archive:
        strings = ["".join(s.itertext()) for s in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        rels = {e.get("Id"): e.get("Target") for e in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        sheet_tag = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        sheets = {s.get("name"): "xl/" + rels[s.get(sheet_tag)]
                  for s in ET.fromstring(archive.read("xl/workbook.xml")).findall(".//{*}sheet")}

        totals = {}
        for row in read_rows(archive, sheets["MutInSegGroups"], set("ABCDEFGHIJ"), strings):
            if not row.get("A", "").isdigit():
                continue
            ident = int(row["A"])
            da, db, dm, ma, mb, mm, total = (int(row[k]) for k in "DEFGHIJ")
            if ident in totals or da + db != dm or ma + mb != mm or dm + mm != total:
                raise ValueError("Inconsistent native division summary.")
            totals[ident] = (int(row["B"].removeprefix("AH")), int(row["C"]), total)

        counts = {ident: Counter() for ident in totals}
        columns = set("ABFG") if reference is None else set("ABDFG")
        for row in read_rows(archive, sheets["Full Mutation List"], columns, strings):
            if row.get("F") == "Division ID":
                continue
            ident = int(row["F"])
            if (int(row["A"]), int(row["B"])) != totals[ident][:2]:
                raise ValueError("Native division and site assignment disagree.")
            label = row.get("G")
            cls = substitution(label)
            counts[ident][cls] += 1
            if reference is not None and cls != "unclassified":
                chrom, pos = row["D"].rsplit(":", 1)
                accession = re.search(r"NC_[0-9]+", chrom).group()
                ref = chr(reference[accession][int(pos) - 1])
                if ref != label[0]:
                    discrepancies.append((ident, label, ref))

    groups = sorted({group for group, _, _ in totals.values()})
    names = {group: f"Y{i}" for i, group in enumerate(groups, 1)}
    result = []
    for ident, (group, division, total) in totals.items():
        bins = counts[ident]
        if sum(bins.values()) != total:
            raise ValueError("Site count differs from the native division summary.")
        ts = bins["C>T"] + bins["T>C"]
        tv = sum(bins[c] for c in ("C>A", "C>G", "T>A", "T>G"))
        if ts + tv + bins["unclassified"] != total:
            raise ValueError("Substitution classes do not exhaust the division.")
        result.append((names[group], division, total, *(bins[c] for c in CLASSES),
                       ts, tv, bins["unclassified"]))
    result.sort()
    previous = io.StringIO()
    write_tsv(previous, ID_COLUMNS, (r[:3] for r in result))
    if hashlib.sha256(previous.getvalue().encode()).hexdigest() != PRIOR_DIVISIONS_SHA256:
        raise ValueError("Projected rows differ from the 50 v0.13.0 divisions.")
    if reference is not None:
        for ident, label, ref in discrepancies:
            group, division, _ = totals[ident]
            print(f"Reference discrepancy: {names[group]}, division {division}, "
                  f"native {label}, reference {ref}", file=sys.stderr)
        print(f"Classified rows with reference disagreement: {len(discrepancies)}", file=sys.stderr)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--reference-tgz", type=Path, help="SGD R64-2-1 archive for optional orientation audit")
    args = parser.parse_args()
    write_tsv(sys.stdout, HEADER, extract(args.workbook, args.reference_tgz))

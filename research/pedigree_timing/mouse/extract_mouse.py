"""Extract aggregate records of carrier litter order from Lindsay et al., Supplementary Data 1."""
import argparse
import csv
from collections import Counter
import hashlib
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

SHA256 = "a8b69ab1c059f9bc341e22ed78119af9583db489789b7c814eb0196c6a8e1519"
HEADER = ["chr", "pos", "type", "ref", "alt", "called in", "n_individuals shared", "shared",
          "Mosaic", "VEE/Zygotic", "Lineage", "RP_Phasing"]
FIELDS = ["family", "bases_in_event", "n_sample_tokens", "n_distinct_samples", "n_pups", "first_litter", "second_pup_litter",
          "last_litter", "parent_mosaic", "source_shared", "source_n_shared", "events"]
SAMPLE = re.compile(r"(CBGP[0-9]+|GPCB[0-9]+)_([1-9][0-9]*)([a-z])T?")


def native_rows(path):
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError("File differs from the pinned author workbook")
    with ZipFile(path) as z:
        strings = ["".join(t.text or "" for t in si.findall(".//{*}t"))
                   for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    result = []
    for row in sheet.findall(".//{*}sheetData/{*}row"):
        values = {}
        for cell in row.findall("{*}c"):
            value = cell.findtext("{*}v")
            if value is not None:
                col = re.fullmatch(r"([A-Z]+)[0-9]+", cell.get("r"))[1]
                values[col] = strings[int(value)] if cell.get("t") == "s" else value
        if values:
            if set(values) != set("ABCDEFGHIJKL"):
                raise ValueError("Incomplete native record")
            result.append([values[k].strip() for k in "ABCDEFGHIJKL"])
    assert result[0] == HEADER and len(result) == 761
    assert len({(r[0], r[1]) for r in result[1:]}) == 760
    return result[1:]


def event_rows(rows):
    grouped = {}
    for row in rows:
        if row[2] == "SNP":
            yield row, 1
        elif row[2] == "MNV":
            # Group only source-flagged MNVs with identical carriers and annotations.
            key = (row[0], *row[5:])
            grouped.setdefault(key, []).append(row)
        else:
            raise ValueError("Unexpected variant type")
    assert len(grouped) == 7
    for pair in grouped.values():
        assert len(pair) == 2 and 0 < abs(int(pair[0][1])-int(pair[1][1])) <= 5
        yield pair[0], 2


def extract(path):
    counts = Counter()
    for row, bases in event_rows(native_rows(path)):
        tokens = [v.strip() for v in row[5].split(",")]
        labels = [SAMPLE.fullmatch(t) for t in tokens]
        assert all(labels)
        families = {match[1] for match in labels}
        assert len(families) == 1
        pups = {(int(m[2]), m[3]) for m in labels}
        litters = sorted(litter for litter, pup in pups)
        assert row[8] in {"0", "Paternal", "Maternal"} and row[7] in {"0", "1"}
        key = (families.pop(), bases, len(tokens), len(set(tokens)), len(pups), litters[0],
               litters[1] if len(pups) >= 2 else 0, litters[-1], int(row[8] != "0"),
               int(row[7]), int(row[6]))
        counts[key] += 1
    assert sum(counts.values()) == 753
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(FIELDS)
    for key, n in sorted(counts.items()):
        writer.writerow((*key, n))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    extract(parser.parse_args().workbook)

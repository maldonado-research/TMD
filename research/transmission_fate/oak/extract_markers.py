"""Join Plomion Tables 5/6, figure-derived allele counts and Xian Table S8."""
import argparse
import csv
import hashlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from fractions import Fraction
from pathlib import Path

SUPP_SHA = "0c864f7b636641ab1ce44cc870d4448cfe53e5d484089e099bda4dbe2c6553ea"
XLSX_SHA = "b4d3b7993012cc350d2e7fb0fb5e87f359642ae2f996dec22a0475ee3e0a49f0"
ORIGINS = {"between XL1 and XL2": "shared_trunk", "L1 branch": "L1", "L2 branch": "L2"}
S6 = re.compile(r"^\s*SM\s+(Sc\d+_\d+)\s+3P\s+–\s+(.+?)\s+([YN])\s+"
                r"([\d.]+|NA)\s+(\d+)\s+([\d.]+|NA)\s+([\d.]+)\s*$", re.M)


def table8(path):
    with zipfile.ZipFile(path) as book:
        strings = ["".join(n.itertext()) for n in ET.fromstring(
            book.read("xl/sharedStrings.xml")).findall("{*}si")]
        sheet = ET.fromstring(book.read("xl/worksheets/sheet8.xml"))
    result = {}
    for row in sheet.findall(".//{*}row"):
        cells = {}
        for cell in row.findall("{*}c"):
            value = cell.findtext("{*}v")
            if value is not None:
                col = re.match(r"^[A-Z]+", cell.get("r"))[0]
                cells[col] = strings[int(value)] if cell.get("t") == "s" else value
        if cells.get("A", "").startswith("Sc"):
            key = cells["A"]
            if key in result:
                raise ValueError(f"Duplicate Xian marker {key}")
            has_fraction = any(cells[c] != "\\" for c in ("F", "G", "H"))
            group = {"XL1-XL2": "shared_trunk", "L1": "L1", "L2": "L2"}[cells["E"].strip()]
            result[key] = (group, int(cells["D"] == "Y"), int(has_fraction))
    return result


def extract(text, workbook, alleles):
    s5, s6 = text.split("Supplementary Table 5 List of control SNPs", 1)[1].split(
        "Supplementary Table 6 List of control SNPs")
    origins = dict(re.findall(r"^\s*SM\s+(Sc\d+_\d+)[^\n]+?3P\s+–\s+"
                              r"(between XL1 and XL2|L1 branch|L2 branch|between XL2 and L3)", s5, re.M))
    matches = S6.findall(s6)
    xian = table8(workbook)
    if len(origins) != 61 or len(matches) != 21 or len(xian) != 19 or len(alleles) != 19:
        raise ValueError("Unexpected source roster")
    figure_by_order = {int(row["figure_order"]): row for row in alleles}
    fig_order = 0
    used = set()
    for order, (key, raw_origin, success, miss, raw_n, raw_ho, _) in enumerate(matches, 1):
        if key in used or origins[key] != raw_origin:
            raise ValueError("Inconsistent origin or duplicate Table 6 marker")
        used.add(key)
        origin = ORIGINS[raw_origin]
        n = int(raw_n)
        row = {"s6_order": order, "figure_order": "NA", "origin": origin, "assay": success,
               "genotyped": n, "heterozygotes": "NA", "carriers": "NA", "missing": 116 - n,
               "leaf_fraction_reported": "NA", "L1_alt": "NA", "L1_ref": "NA", "L2_alt": "NA", "L2_ref": "NA"}
        if success == "N":
            if n or miss != "NA" or raw_ho != "NA" or key in xian:
                raise ValueError("Inconsistent failed assay")
            yield row
            continue
        fig_order += 1
        figure = figure_by_order[fig_order]
        other_origin, is_positive, has_fraction = xian[key]
        if figure["reported_origin"] != origin or other_origin != origin:
            raise ValueError("Branches disagree across sources")
        if abs(Fraction(miss) - Fraction(116-n,116)) > Fraction(1,2000):
            raise ValueError("Printed missing fraction disagrees with N")
        # H0 is given to three decimal places. Enumerate compatible diploid heterozygote counts.
        candidates = [h for h in range(n+1) if abs(Fraction(raw_ho) - Fraction(h,n)) <= Fraction(1,2000)]
        if len(candidates) != 1:
            raise ValueError("Heterozygote count not uniquely recovered")
        het, = candidates
        l1a, l1r, l2a, l2r = (int(figure[f"{b}_{allele}"]) for b in ("L1", "L2")
                               for allele in ("alternate", "reference"))
        alt = l1a + l2a
        carriers = (alt + het) // 2
        if (sum((l1a,l1r,l2a,l2r)) != 2*n or (alt-het) % 2 or not 0 <= het <= carriers <= n
                or is_positive != int(alt > 0)):
            raise ValueError("Allele counts, H0 or Xian outcome disagree")
        row.update(figure_order=fig_order, heterozygotes=het, carriers=carriers,
                   leaf_fraction_reported=has_fraction, L1_alt=l1a, L1_ref=l1r, L2_alt=l2a, L2_ref=l2r)
        yield row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plomion_supplement", type=Path)
    parser.add_argument("xian_workbook", type=Path)
    parser.add_argument("--alleles", type=Path, default=Path(__file__).with_name("oak_alleles.tsv"))
    args = parser.parse_args()
    for path, expected in ((args.plomion_supplement, SUPP_SHA), (args.xian_workbook, XLSX_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unexpected native SHA-256 for {path.name}")
    text = subprocess.check_output(["pdftotext", "-f", "86", "-l", "90", "-layout",
                                    str(args.plomion_supplement), "-"], text=True)
    with args.alleles.open() as source:
        alleles = list(csv.DictReader(source, delimiter="\t"))
    rows = list(extract(text, args.xian_workbook, alleles))
    writer = csv.DictWriter(sys.stdout, rows[0].keys(), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


if __name__ == "__main__":
    main()

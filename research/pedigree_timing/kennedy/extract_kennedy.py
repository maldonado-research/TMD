"""Extract the anonymized serial-daughter calls, division rosters and source crosschecks."""
import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path
from xml.etree.ElementTree import fromstring
from zipfile import ZipFile

SHEET = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DOC = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
HASHES = {
    "s010.xlsx": "e6005dbf96624706897b630bf36fcab64eeaf7c794266e16db08ae6461852ed3",
    "s011.xlsx": "45eba792cedbe93922934bb462a176658f3b835ab911521c891c053aba209922",
    "s001.docx": "bc1ecc3d3d11ee78be8343f99770089b87a0b4d4af300122a379780c0a5ce0b8",
}
PATHS = ("B", "C", "D", "E", "F", "G1", "G2", "H")
SITE = re.compile(r"NC_\d+[:|]\d+")


def check(path, expected):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Unexpected source bytes for {path}")


def sheets(path):
    with ZipFile(path) as z:
        xml = lambda entry: fromstring(z.read(entry))
        strings = ["".join(x.itertext()) for x in xml("xl/sharedStrings.xml")]
        tabs = xml("xl/workbook.xml").find("s:sheets", SHEET)
        styles = xml("xl/styles.xml").find("s:cellXfs", SHEET)
        for i, tab in enumerate(tabs, 1):
            root = xml(f"xl/worksheets/sheet{i}.xml")
            rows = {}
            for row in root.findall(".//s:row", SHEET):
                columns = {}
                for cell in row.findall("s:c", SHEET):
                    value = cell.find("s:v", SHEET)
                    text = value.text if value is not None else ""
                    if cell.get("t") == "s":
                        text = strings[int(text)]
                    col = re.match(r"[A-Z]+", cell.get("r"))[0]
                    columns[col] = (text.strip(), int(styles[int(cell.get("s", 0))].get("fillId")))
                rows[int(row.get("r"))] = columns
            yield tab.get("name"), rows


def write_tsv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("matrix", "model", "table", "out"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    for path, ext in ((args.matrix,"s010.xlsx"), (args.model,"s011.xlsx"), (args.table,"s001.docx")):
        check(path,HASHES[ext])

    _, model = next(sheets(args.model))
    assert "85 not 87" in model[19]["A"][0]
    model_counts = {}
    for col, (label, _) in model[2].items():
        path = label.rstrip("*")
        if path in PATHS:
            for row in range(4, 19):
                div = int(model[row]["A"][0])
                val = model[row].get(col, ("",))[0]
                if val:
                    model_counts[path,div] = int(val)

    with ZipFile(args.table) as z:
        document = fromstring(z.read("word/document.xml"))
    doc_counts, callable_bases = {}, {}
    path = ""
    for row in document.findall(".//w:tr", DOC):
        cells = ["".join(col.itertext()).strip() for col in row.findall("w:tc", DOC)]
        if len(cells) == 1 and cells[0].startswith("Lineage "):
            path = cells[0].split()[-1]
        elif path in PATHS and len(cells) >= 4 and cells[1].isdigit() and cells[2].isdigit():
            doc_counts[path,int(cells[1])] = int(cells[2])
            bases = int(cells[3])
            assert callable_bases.setdefault(path,bases) == bases
    assert doc_counts == {k:v for k,v in model_counts.items() if k != ("B",11)}

    slots, observations, global_ids = [], [], {}
    counts = Counter()
    for sheet, rows in sheets(args.matrix):
        path = sheet.split()[-1]
        if path == "A":
            continue
        assert path in PATHS
        a = lambda row: row.get("A", ("",))[0]
        head = next(n for n, row in rows.items() if a(row) == "Cell Division")
        summary = next(n for n,row in rows.items() if a(row) == "New Fixed Mutations")
        divisions = {k:int(v) for k,(v,_) in rows[head].items() if k != "A" and v}
        assert set(divisions.values()) == set(range(min(divisions.values()),max(divisions.values())+1))
        for col, div in sorted(divisions.items(), key=lambda c:c[1]):
            ref = rows[head-1][col][0]
            if path == "H" and div == 2:
                assert any(row.get(col, ("",))[0] == "DEAD" for row in rows.values())
                role = "dead"
            elif path == "F" and div == 8:
                assert rows[summary+1][col][0] == "Not sequenced"
                role = "unsequenced"
            elif path == "E" and div == 8:
                assert rows[summary+1][col][0] == "inferred"
                role = "inferred"
            elif "(d of " in ref:
                assert path == "D" and div in {11,15}
                role = "granddaughter"
            else:
                role = "daughter"
            val = rows[summary].get(col, ("",))[0]
            slots.append((path,div,role,val,model_counts.get((path,div),""),
                          doc_counts.get((path,div),""),callable_bases[path]))
        for n in range(head+1,summary):
            row = rows.get(n,{})
            cells = [(divisions[k],v.replace("|",":"),fill) for k,(v,fill) in row.items()
                     if k in divisions and SITE.fullmatch(v)]
            if not cells:
                continue
            locations = {v for _,v,_ in cells}
            assert len(locations) == 1
            loc = locations.pop()
            positives = sorted(d for d,_,_ in cells)
            assigned = [(d,f) for d,_,f in cells if f in (2,4)]
            # The only inherited rows on these sheets on G2 predate its branch.
            if not assigned:
                assert path == "G2" and ("G1",loc) in global_ids and positives == [5,6,7,8,9]
                ref = global_ids["G1", loc]
                status = "inherited"
            else:
                assert len(assigned) == 1 and assigned[0][0] == min(positives) and (path, loc) not in global_ids, (path, n, len(assigned), assigned, min(positives))
                ref = f"V{len(global_ids)+1:03}"
                global_ids[path, loc] = ref
                status = "interval" if assigned[0][1] == 4 else "assigned"
                if status == "interval":
                    assert path == "F" and min(positives) == 9
                counts[path,min(positives)] += 1
            observations.append((path, ref, status, ",".join(map(str,positives))))
    for path,div,_,matrix,model,doc,_ in slots:
        assert int(matrix or 0) == counts[path,div]
        if (path,div) in model_counts:
            assert model == int(matrix)
    assert len(global_ids)==237 and len(observations)==239
    args.out.mkdir(parents=True,exist_ok=True)
    write_tsv(args.out/"divisions.tsv", ("path","daughter_index","sample","s1_matrix_new","s2_model_new",
              "s1_docx_new","callable_bases_per_division"),slots)
    write_tsv(args.out/"observations.tsv", ("path","site_id","source_status","positive_daughter_indices"),observations)


if __name__ == "__main__":
    main()

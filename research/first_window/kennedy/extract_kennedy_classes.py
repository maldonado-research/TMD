"""Join Kennedy's S1 pedigree observations to the S3 directional substitutions."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

FILES = {
    "matrix": ("pgen.1005151.s010.xlsx", "e6005dbf96624706897b630bf36fcab64eeaf7c794266e16db08ae6461852ed3"),
    "changes": ("pgen.1005151.s012.xlsx", "471723155bbc46d1087c9ed1e1fc19c6a4039141f8568cc9d3e5046b89988fb1"),
    "spectrum": ("pgen.1005151.s002.docx", "94c19389a1c29b06e9ccf4d735103be27804008733203e571e00241daf43708e"),
}
OBSERVATION_SHA256 = "a61c6f21add3249c07431c86714b0bad3c0fce638644dfd5575d396fa6ad7752"
SITE = re.compile(r"NC_\d+[:|]\d+")
COMPLEMENT = str.maketrans("ACGT", "TGCA")


def sheets(path):
    """Read source-pinned worksheet values and fill indices with the standard library."""
    with ZipFile(path) as book:
        def xml(entry):
            return ElementTree.fromstring(book.read(entry))

        strings = ["".join(node.itertext()) for node in xml("xl/sharedStrings.xml")]
        styles = xml("xl/styles.xml").find("{*}cellXfs")
        tabs = xml("xl/workbook.xml").find("{*}sheets")
        for number, tab in enumerate(tabs, 1):
            cells = {}
            for row in xml(f"xl/worksheets/sheet{number}.xml").findall(".//{*}row"):
                values = {}
                for cell in row.findall("{*}c"):
                    value = cell.findtext("{*}v")
                    if value is None:
                        continue
                    if cell.get("t") == "s":
                        value = strings[int(value)]
                    col = re.match(r"[A-Z]+", cell.get("r")).group()
                    fill = int(styles[int(cell.get("s", 0))].get("fillId"))
                    values[col] = (value.strip(), fill)
                cells[int(row.get("r"))] = values
            yield tab.get("name"), cells


def normalized(arrow):
    if not re.fullmatch("[ACGT]→[ACGT]", arrow) or arrow[0] == arrow[2]:
        raise ValueError(f"Unexpected directional SNV label {arrow!r}")
    if arrow[0] in "AG":
        arrow = arrow.translate(COMPLEMENT)
    return arrow.replace("→", ">")


def write_tsv(out, rows):
    csv.writer(out, delimiter="\t", lineterminator="\n").writerows(rows)


def matrix_observations(path):
    events = {}
    inherited = []
    legacy_rows = [("path", "site_id", "source_status", "positive_daughter_indices")]
    for sheet, rows in sheets(path):
        arm = sheet.split()[-1]
        if arm == "A":
            continue
        def find_label(label):
            return next(n for n, row in rows.items() if row.get("A", ("",))[0] == label)

        head = find_label("Cell Division")
        summary = find_label("New Fixed Mutations")
        divisions = {col: int(v) for col, (v, _) in rows[head].items() if col != "A" and v}
        for n in range(head + 1, summary):
            calls = [(divisions[col], loc.replace("|", ":"), fill)
                     for col, (loc, fill) in rows.get(n, {}).items()
                     if col in divisions and SITE.fullmatch(loc)]
            if not calls:
                continue
            (loc,) = {loc for _, loc, _ in calls}
            indices = sorted(d for d, _, _ in calls)
            highlighted = [(d, fill) for d, _, fill in calls if fill in (2, 4)]
            if highlighted:
                ((upper, fill),) = highlighted
                assert upper == indices[0] and (arm, loc) not in events
                eid = f"V{len(events) + 1:03d}"
                status = "interval" if fill == 4 else "assigned"
                lower = upper - int(status == "interval")
                events[arm, loc] = (eid, lower, upper)
            else:
                assert arm == "G2" and indices == [5, 6, 7, 8, 9]
                eid = events["G1", loc][0]
                inherited.append(eid)
                status = "inherited"
            legacy_rows.append((arm, eid, status, ",".join(map(str, indices))))
    old = io.StringIO(newline="")
    write_tsv(old, legacy_rows)
    assert hashlib.sha256(old.getvalue().encode()).hexdigest() == OBSERVATION_SHA256
    return events, inherited


def directed_changes(path):
    changes = {}
    (_, rows), = sheets(path)
    assert [rows[3][c][0] for c in "ABDE"] == ["Lineage", "Division", "Mutation ID", "mutation"]
    for row in rows.values():
        loc = row.get("D", ("",))[0]
        if SITE.fullmatch(loc):
            arm, division, arrow = (row[c][0] for c in "ABE")
            normalized(arrow)
            key = (arm, loc.replace("|", ":"))
            assert key not in changes
            changes[key] = (int(division), arrow)
    return changes


def published_spectrum(path):
    with ZipFile(path) as doc:
        root = ElementTree.fromstring(doc.read("word/document.xml"))
    table = [["".join(col.itertext()).strip() for col in row.findall("{*}tc")]
             for row in root.findall(".//{*}tr")]
    arrows = table[0][1:]
    by_path = {row[0].split()[-1]: Counter(dict(zip(arrows, map(int, row[1:])))) for row in table[1:-1]}
    totals = Counter(dict(zip(arrows, map(int, table[-1][1:]))))
    assert table[-1][0] == "Total" and sum(by_path.values(), Counter()) == totals
    return by_path, totals


def sorted_counts(counts):
    return dict(sorted(counts.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    files = {}
    for name, (filename, digest) in FILES.items():
        files[name] = args.sources / filename
        if hashlib.sha256(files[name].read_bytes()).hexdigest() != digest:
            raise ValueError(f"Unexpected source bytes in {filename}")
    observations, inherited = matrix_observations(files["matrix"])
    changes = directed_changes(files["changes"])
    table, totals = published_spectrum(files["spectrum"])
    mutual = observations.keys() & changes.keys()
    assert len(observations) == len(changes) == 237 and len(mutual) == 236
    (s1_only,) = observations.keys() - changes.keys()
    (s3_only,) = changes.keys() - observations.keys()
    s1_chr, s1_pos = s1_only[1].split(":")
    s3_chr, s3_pos = s3_only[1].split(":")
    assert s1_only[0] == s3_only[0] == "F" and s1_chr == s3_chr
    assert abs(int(s1_pos) - int(s3_pos)) == 5
    assert observations[s1_only][1:] == (8, 9) and changes[s3_only][0] == 9

    records = [["pedigree", "path", "event_id", "time_lower", "time_upper",
                "substitution_class", "ts_tv", "linkage"]]
    date_mismatches = Counter()
    for key, (eid, lower, upper) in observations.items():
        arm, _ = key
        if key in changes:
            index, arrow = changes[key]
            change = normalized(arrow)
            broad = "Ts" if change in ("C>T", "T>C") else "Tv"
            linkage = "exact"
            if index != upper:
                date_mismatches[arm, upper, index] += 1
        else:
            change = broad = "unknown"
            linkage = "unmatched"
        pedigree = "G" if arm in ("G1", "G2") else arm
        records.append([pedigree, arm, eid, lower, upper, change, broad, linkage])

    by_class = Counter(dict.fromkeys(("C>A", "C>G", "C>T", "T>A", "T>C", "T>G", "unknown"), 0))
    by_class.update(row[5] for row in records[1:])
    s3_margins = Counter((p, arrow) for (p, _), (_, arrow) in changes.items())
    s3_totals = Counter(arrow for _, arrow in changes.values())
    repeated = Counter(loc for _, loc in observations)
    (recurrent,) = (loc for loc, count in repeated.items() if count > 1)
    recurring = [(arm, observations[arm, loc][0], normalized(changes[arm, loc][1]))
                 for arm, loc in observations if loc == recurrent]
    assert len(set(inherited)) == len(inherited) == 2
    assert len(recurring) == 2 and {p for p, _, _ in recurring} == {"E", "F"}
    assert sum(date_mismatches.values()) == 30
    qa = {
        "legacy_observations_sha256": OBSERVATION_SHA256,
        "s1_assigned_events": len(observations),
        "s3_directional_change_rows": len(changes),
        "same_path_exact_position_matches": len(mutual),
        "s1_unmatched_event": observations[s1_only][0],
        "s3_unmatched_path": s3_only[0],
        "s1_s3_unmatched_distance_bases": abs(int(s1_pos) - int(s3_pos)),
        "inherited_g1_event_ids_repeated_on_g2_excluded_from_table": sorted(inherited),
        "recurrent_position_events_in_distinct_paths": [
            dict(path=p, event_id=eid, substitution_class=change) for p, eid, change in recurring],
        "s1_s3_division_disagreements_on_exact_matches": [
            dict(path=p, s1_daughter_index=i, s3_division=j, count=count)
            for (p, i, j), count in sorted(date_mismatches.items())],
        "classified_source_events": sorted_counts(by_class),
        "s2_table_reported_directional_counts": sorted_counts(totals),
        "s3_dataset_directional_counts_all_rows": sorted_counts(s3_totals),
        "s2_table_and_s3_dataset_by_path": {
            arm: {"s2_table_count": sum(counts.values()),
                  "s3_dataset_count": sum(v for (p, _), v in s3_margins.items() if p == arm),
                  "directional_counts_differ": {
                      arrow: {"s2_table": counts[arrow], "s3_dataset": s3_margins[arm, arrow]}
                      for arrow in sorted(s3_totals | totals) if counts[arrow] != s3_margins[arm, arrow]}}
            for arm, counts in sorted(table.items())},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "kennedy_events.tsv").open("w", newline="", encoding="utf-8") as dest:
        write_tsv(dest, records)
    (args.output / "kennedy_linkage.json").write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

"""Reproduce aggregate counts from Goel et al., Additional file 2, using openpyxl."""

import argparse
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook


WORKBOOK_MD5 = "907e0155a2c9d0ed663c6cabb02eba91"
WORKBOOK_BYTES = 1_807_558
# The supplementary PDF, Figure S7 caption, enumerates 14 confirmed assay IDs.
CONFIRMED = {2, 17, 20, 25, 27, 28, 29, 30, 31, 32, 34, 35, 36, 38}
# Figure S8 labels three inconclusive assays despite their numerical readouts.
INCONCLUSIVE = {19, 21, 42}
STRATA = {"fruit": "fruit_only", "shared": "fruit_and_leaf", "leaf": "leaf_only"}


def records(book, sheet):
    rows = book[sheet].values
    next(rows)  # Worksheet title.
    headers = [str(name).strip() for name in next(rows)]
    return [dict(zip(headers, row)) for row in rows]


def replay(path):
    data = path.read_bytes()
    digest = hashlib.md5(data).hexdigest()
    if len(data) != WORKBOOK_BYTES or digest != WORKBOOK_MD5:
        raise ValueError("Workbook does not match the archived v1 size and MD5")
    book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    s3 = records(book, "table S3 somatic mutations")
    s4 = records(book, "table S4 Allele_frequency")
    s7 = records(book, "table S7 dPCR Primers")
    s8 = records(book, "table S8 dPCR Probes")
    s10 = records(book, "table S10 dPCR result")
    book.close()

    def event(row):
        return (row["Chromosome"], row["Position"], row["Alternate allele"])

    # S3 can list the same event in several samples. S4 has one row per event.
    event_organs = defaultdict(set)
    low_confidence = set()
    for row in s3:
        key = event(row)
        event_organs[key].add(row["Organ"])
        if row["Low confidence"] == "Y":
            low_confidence.add(key)
    source_organs = {event(row): row["Organ"] for row in s4}
    if len(source_organs) != len(s4) or event_organs != {
        key: {organ} for key, organ in source_organs.items()
    }:
        raise ValueError("S3/S4 event labels differ or S4 event keys repeat")
    at_location = defaultdict(list)
    for key in source_organs:
        chromosome, position, _ = key
        at_location[f"{chromosome}:{position}"].append(key)

    assays = [row for row in s10 if isinstance(row["Mut ID"], int)]
    id_to_location = {row["Mut ID"]: row["Genomic position"] for row in assays}
    s7_locations = {row["Mut ID"]: row["Genomic position"] for row in s7}
    s8_ids = {row["Mut ID"] for row in s8 if isinstance(row["Mut ID"], int)}
    if (len(id_to_location) != len(assays) or id_to_location != s7_locations
            or set(id_to_location) != s8_ids):
        raise ValueError("Assay identity or location differs across S7, S8 and S10")

    blank = {row["Mut ID"] for row in assays if row["AF found"] is None}
    if CONFIRMED & INCONCLUSIVE or blank & (CONFIRMED | INCONCLUSIVE):
        raise ValueError("Reference figures and missing-readout labels overlap")
    if set(id_to_location) != CONFIRMED | INCONCLUSIVE | blank:
        raise ValueError("Reference-status labels do not cover the assay roster")
    totals = Counter(source_organs.values())
    stats = {}
    for tag, label in STRATA.items():
        stats[label] = {"source_events": totals[tag], "assay_ids": 0,
                        "distinct_linked_events": 0, "confirmed_events": 0,
                        "inconclusive_numeric_events": 0, "blank_readout_events": 0}
    statuses = {}
    for row in assays:
        assay_id = row["Mut ID"]
        matching = at_location[id_to_location[assay_id]]
        if len(matching) != 1:
            raise ValueError("Printed assay location does not identify one source event")
        key = matching[0]
        group = stats[STRATA[source_organs[key]]]
        group["assay_ids"] += 1
        if assay_id in CONFIRMED:
            status = "confirmed_events"
        elif assay_id in INCONCLUSIVE:
            status = "inconclusive_numeric_events"
        else:
            status = "blank_readout_events"
        if key in statuses and statuses[key] != status:
            raise ValueError("Different statuses occur at one printed event key")
        if key not in statuses:
            statuses[key] = status
            group["distinct_linked_events"] += 1
            group[status] += 1
    return {
        "source": {"workbook": "10.6084/m9.figshare.26368540.v1",
                   "figures": "10.6084/m9.figshare.26367951.v1",
                   "article": "10.1186/s13059-024-03337-0",
                   "workbook_bytes": len(data), "workbook_md5": digest},
        "article_reported": {"targeted": 20, "confirmed": 14, "inconclusive": 6},
        "figure_transcription": {"confirmed_ids_figure_S7": len(CONFIRMED),
                                 "inconclusive_ids_figure_S8": len(INCONCLUSIVE)},
        "replayed": {"source_events_S4": len(s4),
                     "source_low_confidence_events_S3": len(low_confidence),
                     "assay_ids_S7_S8_S10": len(id_to_location),
                     "numeric_readouts_S10": len(assays) - len(blank),
                     "blank_readouts_S10": len(blank),
                     "distinct_printed_locations_S10": len(set(id_to_location.values())),
                     "distinct_linked_source_events": len(statuses),
                     "linked_low_confidence_events": len(low_confidence & statuses.keys()),
                     "by_source_organ": stats},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    print(json.dumps(replay(parser.parse_args().workbook), indent=2))

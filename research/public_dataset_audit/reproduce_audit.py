#!/usr/bin/env python3
"""Reproduce source-table inventory only; no workbook or TMD inference is claimed.

Python 3 standard library only. Raw publisher files remain outside public artifacts.
The input hash pins the PMC XML actually read during this audit. A refreshed XML
must match that snapshot, or be reviewed explicitly before this script is changed.
"""

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET


DOI = "10.1371/journal.pbio.3003282"
PMC_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=12273949"
INPUT_SHA256 = "a6477b003ba58cb2ab7249f96459e14a409fc6ed7c37ce450f9e2c8cfebdb0ea"
STRAINS = ["delta_mutS", "delta_mutL", "delta_mutH", "delta_nth_nei", "WT", "delta_mutY", "delta_mutT"]


def text(element):
    return "".join(element.itertext()).strip()


def build_audit(source):
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != INPUT_SHA256:
        raise ValueError("PMC XML differs from audited snapshot; explicit source review required")
    root = ET.fromstring(raw)
    article = root if root.tag == "article" else root.find("article")
    ids = {x.get("pub-id-type"): text(x) for x in article.findall("./front/article-meta/article-id")}
    if ids.get("doi") != DOI or ids.get("pmcid") != "PMC12273949":
        raise ValueError("Wrong article identity")
    # Deliberately exclude all reviewer sub-articles and template correspondence.
    table = article.find('./body//table-wrap[@id="pbio.3003282.t001"]')
    rows = [[text(cell) for cell in row] for row in table.findall(".//tr")]
    if len(rows[0]) != 8:
        raise ValueError("Unexpected Table 1 column structure")
    labels = {
        "ma_lines_evolved_author_reported": "MA lines evolved",
        "ma_lines_successfully_sequenced_author_reported": "MA lines successfully sequenced",
        "mutations_in_sequenced_lines_author_reported": "Total mutations in sequenced lines",
        "single_step_fitness_comparisons_author_reported": "MA lines with single mutations",
    }
    counts = {}
    for field, prefix in labels.items():
        matching = [r for r in rows if r[0].startswith(prefix)]
        if len(matching) != 1 or len(matching[0]) != 8:
            raise ValueError("Missing or ambiguous row: " + prefix)
        # '94c' is Table 1's explicit WT footnote, not a new numeric value.
        values = [int(v.removesuffix("c")) for v in matching[0][1:]]
        counts[field] = values
    footnote = next(text(fn) for fn in table.findall(".//fn") if text(fn).startswith("cAll of these"))
    for phrase in ("80 of the 94", "only 38 lines", "46 of them", "immediate ancestor"):
        if phrase not in footnote:
            raise ValueError("WT lineage qualification changed: " + phrase)
    license_text = ET.tostring(article.find("./front/article-meta/permissions"), encoding="unicode")
    if "https://creativecommons.org/licenses/by/4.0/" not in license_text:
        raise ValueError("Expected source license absent")
    supplements = {}
    for s in article.findall("./body//supplementary-material"):
        label = s.findtext("label", "")
        if label in ("S2 Data", "S3 Data"):
            media = s.find("media")
            supplements[label] = media.get("{http://www.w3.org/1999/xlink}href")
    if supplements != {"S2 Data": "pbio.3003282.s023.xlsx", "S3 Data": "pbio.3003282.s024.xlsx"}:
        raise ValueError("Supplement identities differ")
    by_strain = []
    for i, strain in enumerate(STRAINS):
        record = {"strain": strain, **{field: values[i] for field, values in counts.items()}}
        record["sequencing_exclusions_table_difference"] = (
            record["ma_lines_evolved_author_reported"] - record["ma_lines_successfully_sequenced_author_reported"]
        )
        by_strain.append(record)
    totals = {field: sum(values) for field, values in counts.items()}
    totals["sequencing_exclusions_table_difference"] = sum(r["sequencing_exclusions_table_difference"] for r in by_strain)
    if totals["single_step_fitness_comparisons_author_reported"] != 694:
        raise ValueError("Source-table fitness count does not sum to 694")
    return {
        "audit_scope": "authenticated_primary_article_table_inventory_only",
        "dataset_status": "supplement_workbook_bytes_not_acquired_or_audited",
        "provenance": {
            "citation": "Sane, Parveen and Agashe (2025), Mutation bias alters the distribution of fitness effects of mutations",
            "doi": DOI,
            "pmcid": ids["pmcid"],
            "pmcid_version": ids["pmcid-ver"],
            "source_url": PMC_URL,
            "source_sha256": digest,
            "source_bytes": len(raw),
            "source_location": "main article Table 1, footnote c, Methods, and supporting information labels",
            "article_license": "CC BY 4.0",
            "supplement_filenames_from_article": supplements,
        },
        "table1_by_strain": by_strain,
        "table1_totals": totals,
        "units_and_dependence": {
            "fitness_units": "author-reported single-step mutation fitness comparisons; not independent founding-line trials",
            "WT_block1_comparisons": 80,
            "WT_block1_founding_lines": 38,
            "WT_comparisons_at_second_third_or_fourth_step": 46,
            "WT_later_step_comparator": "immediate ancestor",
            "WT_block2_comparisons": 14,
            "fitness_media_author_reported": ["LB", "M9 minimal salts + 5 mM glucose"],
            "technical_replicates_per_fitness_estimate_author_reported": 3,
            "media_are_paired_on_same_isolates": True,
            "actual_workbook_rows_columns_missingness": None,
            "actual_well_plate_lineage_join_reconstruction": None,
        },
        "eligibility": {
            "eligible_for_Wsp_Aws_Mws_contrast": False,
            "independent_recovery_binomial_denominators_verified": False,
            "eligible_for_first_successful_arrival_likelihood": False,
            "biological_hypothesis_test_performed": False,
            "reason": "Selected MA mutation fitness panel, paired media, shared ancestry; no competing triad first arrivals or matched recovery controls in the audited source inventory.",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).parent / "raw/sane_pmc.xml")
    parser.add_argument("--fetch-source", action="store_true", help="Fetch public PMC XML only; hash must match audited snapshot")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "derived_aggregate.json")
    args = parser.parse_args()
    if args.fetch_source:
        args.source.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(PMC_URL, timeout=45) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != INPUT_SHA256:
            raise ValueError("Fetched XML differs from audited snapshot; not saved or accepted")
        args.source.write_bytes(raw)
    result = build_audit(args.source)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Reproduced article-table inventory:", args.output)
    print("Supplement workbook rows and raw fitness values remain unaudited.")


if __name__ == "__main__":
    main()

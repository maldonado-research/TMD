#!/usr/bin/env python3
"""Read pinned public source bytes; reconstruct physical geometry, not a rate fit."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as E
import zipfile

ZIP_SHA = "9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6"
ARTICLE_SHA = "937c7eded441b32eea42777d703647965e6090ccb5850017f2b5b6cbd4ea53c2"
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def run(zip_path, article_path):
    assert Path(zip_path).stat().st_size == 7880751
    data = Path(zip_path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == ZIP_SHA
    source = Path(article_path).read_bytes()
    assert hashlib.sha256(source).hexdigest() == ARTICLE_SHA
    root = E.fromstring(source)
    main = root.find("article")
    assert main is not None
    ids = [x.text for x in main.findall("front/article-meta/article-id") if x.get("pub-id-type") == "doi"]
    assert ids == ["10.1371/journal.pgen.1011572"]
    body = main.find("body")
    methods = next(x for x in body.iter("sec") if x.get("id") == "sec016")
    text = " ".join("".join(methods.itertext()).split())
    assert "6 mL" in text or "6 mL" in text
    assert "22 h" in text or "22 h" in text
    assert "six individual transformants" in text.lower()
    # Primary article checks exclude the separate review-history subarticles.
    history = []
    for sub in main.findall("sub-article"):
        attached = [x.get("{http://www.w3.org/1999/xlink}href") for x in sub.iter("media")]
        history.append({"id": sub.get("id"), "article_type": sub.get("article-type"),
                        "specific_use": sub.get("specific-use"),
                        "linked_author_response_files": attached,
                        "linked_file_body_in_article_XML": False if attached else None,
                        "not_final_article_methods": True})
    assert len(history) == 7
    outer = zipfile.ZipFile(io.BytesIO(data))
    names = [x for x in outer.namelist() if x.endswith("Colony Counts Fluctuation assays_20_6_24 .xlsx")
             and not x.startswith("__MACOSX/")]
    assert len(names) == 1
    b = outer.read(names[0])
    book = zipfile.ZipFile(io.BytesIO(b))
    strings = ["".join(x.itertext()) for x in E.fromstring(book.read("xl/sharedStrings.xml")).findall("x:si", NS)]
    links = {x.get("Id"): x.get("Target") for x in E.fromstring(book.read("xl/_rels/workbook.xml.rels"))}
    target = None
    for sheet in E.fromstring(book.read("xl/workbook.xml")).findall("x:sheets/x:sheet", NS):
        if sheet.get("name") == "Calculation of C565T frequency":
            rid = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = links[rid]
    assert target
    member = target.lstrip("/") if target.startswith("/") else "xl/" + target
    cells = {}
    for cell in E.fromstring(book.read(member)).findall("x:sheetData/x:row/x:c", NS):
        value = cell.find("x:v", NS)
        if value is not None and value.text is not None:
            cells[cell.get("r")] = strings[int(value.text)] if cell.get("t") == "s" else Fraction(value.text)
    rows, grouping = [], Counter()
    for r in range(2, 26):
        val = lambda col: cells[col + str(r)]
        assert val("F") == val("D") * 20 and val("G") == val("E") * 20 * 1000000
        p = val("I") * val("J") / 120
        assert 0 < p < 1 and val("L") >= 2
        grouping[(val("B"), str(p))] += 1
        rows.append({"source_row": r, "occasion": int(val("A")), "background": val("B"),
                     "transformant_replicate_number": int(val("C")),
                     "initial_CFU_per_ml_estimate": str(val("F")),
                     "nominal_initial_CFU_in_6ml": str(val("F") * 6),
                     "terminal_CFU_per_ml_estimate": str(val("G")),
                     "selective_plate_count": int(val("I")), "culture_dilution_fraction": str(val("J")),
                     "nominal_summed_sampling_fraction": str(p),
                     "candidate_colonies": int(val("H")),
                     "confirmed_C565T": int(val("L")), "sequenced_denominator": int(val("M")),
                     "confirmed_zero_observed": False,
                     "effective_detection_probability_calibrated": False})
    return {"schema_version": 1, "project": "Mutation by Natural Dominance", "round_id": "R000007",
            "scope": "source_grounded_partial_plating_contract_not_biological_likelihood_fit",
            "article_doi": ids[0], "article_XML_sha256": hashlib.sha256(source).hexdigest(),
            "dataset_doi": "10.5281/zenodo.14335473", "dataset_ZIP_sha256": ZIP_SHA,
            "workbook_member": names[0], "workbook_sha256": hashlib.sha256(b).hexdigest(),
            "source_facts": {"culture_volume_ml_reported": 6,
               "pre_assay_shaking_growth_hours_reported": 24, "fluctuation_growth_hours_reported": 22,
               "selective_plate_incubation_hours_reported": 72,
               "plate_volume_ml_inferred_from_workbook_factor20": "1/20",
               "culture_volume_actual_at_plating_measured": False,
               "individual_transformants_per_background_reported": 6,
               "occasions_per_transformant_reported": 2,
               "selective_colony_gate": "3mm or4mm depending on more or fewer than100 visible colonies; threshold tie rule not specified",
               "founder_quantity_is_CFU_estimate_not_known_independent_single_cells": True},
            "resolved_component": {"status": "partially_resolved_nominal_geometry",
               "formula": "p_nominal=I*(1/20ml)*J/(6ml)=I*J/120",
               "does_not_calibrate": ["mixing and viable-cell sampling", "genotype/colony recovery",
                                      "post-plating mutation", "size-based detection", "confirmation error"],
               "geometry_strata": [{"background": bg, "nominal_fraction": p, "culture_occurrences": n}
                                   for (bg,p),n in sorted(grouping.items())]},
            "source_culture_geometry_rows": rows,
            "source_confirmation_status": {"culture_occurrences":24,
               "frame":"released Figure4A cultures only; does not describe all time-course confirmation attempts",
               "all_confirmed_counts_positive": True, "minimum_confirmed_count": min(x["confirmed_C565T"] for x in rows),
               "confirmed_absence_sampling_frame_admitted": False,
               "candidate_sampling_pool_and_read_missingness_gaps": "preserved in R6; not resolved here",
               "fractional_corrected_CFU_are_not_observed_mutation_births": True},
            "likelihood_contract": {"admissible_for_biological_fit":False,
               "author_reported_method":"FALCOR MSS maximum likelihood",
               "server_version_and_settings_verified":False,
               "per_culture_software_input_values_verified":False,
               "density_vs_whole_culture_conversion_verified":False,
               "partial_plating_software_option_verified":False,
               "fractional_confirmation_correction_input_and_rounding_verified":False,
               "shared_vs_culture_specific_population_denominators_verified":False,
               "mutant_clone_growth_equal_to_parent_verified":False,
               "constant_mutation_per_division_across_growth_phases_verified":False,
               "division_and_death_history_measured":False,
               "reporter_to_native_rate_transfer_calibrated":False,
               "rate_confidence_interval_recipe_verified":False},
            "source_version_separation":{"final_methods_anchor":"main article body sec016",
               "peer_review_history":history,"reviewer_claims_are_not_final_article_results":True,
               "author_response_docx_body_acquired_or_read":False},
            "matched_WAM_panels_admitted":0,"actual_study_fields_resolved":0,"biological_rate_fit_performed":False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip",required=True,type=Path)
    p.add_argument("--article",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--check-against",type=Path)
    a=p.parse_args()
    text=json.dumps(run(a.zip,a.article),indent=2,sort_keys=True)+"\n"
    if a.check_against:assert text==a.check_against.read_text(),"measurement contract replay differs"
    a.output.write_text(text)
    print(json.dumps({"status":"passed","source_rows":24,"nominal_geometry_only":True,"rate_fit":False}))

if __name__=="__main__":main()

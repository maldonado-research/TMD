#!/usr/bin/env python3
"""Reproduce the public eligibility audit from pinned, locally held primary XML.

No network requests, TMD hypothesis test, or inferred biological trials are made.
Only the main article is inspected; eLife reviewer correspondence is excluded.
"""
import csv
import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE
RAW_DIR = PACKAGE / "raw"
DATE = "2026-10-02"
PROJECT_COMMIT = "9d957e7aa05172129fe4cbca61a2fe637ad65e51"
PROJECT_DOCUMENT_PINS = [
    ("DATA_AND_PROVENANCE_AUDIT.md", "9e55ac977c2209975e9c2ce1f0b9a98897724a3f88c2e45def47df85507771b7"),
    ("EVIDENCE_AND_CLAIMS.md", "c90011ec70a37eeb697b53b662c52aefaa04844a735bfb2be371755c8eb43ff5"),
    ("MATHEMATICAL_EXTENSION.md", "6ff2174ee99a62659c4c90d8aac5f6f8b5a7f87ee9eaaa64c7cd5142c626fda5"),
    ("PROSPECTIVE_TEST_PLAN.md", "8f00109661becb1251be6c9685846b3942ac4efb8b308c51c0f385acda07fade"),
    ("research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md", "d43cc0861d535389cf7650b3969c65b838e2222ae0215eef5359014367cc2a1d"),
]
GENERATED_FILES = ["sun_aws_table3_transcription.csv", "ELIGIBILITY_ROWS.json", "eligibility_rows.csv",
                   "MISSING_MEASUREMENTS.json", "missing_measurements.csv", "EVIDENCE_EXCERPTS.json",
                   "ACQUISITION_STATUS.json", "SOURCE_MANIFEST.json"]
PINS = {
    "lind2019": ("lind2019_pmc.xml", "38fd0408ef2b5e367aa1fe0307f160839bdc537e85fcd517a584d5177bcd6984", "10.7554/eLife.38822", "PMC6324874"),
    "sun2023": ("sun2023_pmc.xml", "6794652551e935e9f5b6ed53cd6b2d034b6b40a5acabeb4c614c39c75845192a", "10.1099/mic.0.001323", "PMC10268835"),
}


def norm(node):
    return " ".join("".join(node.itertext()).split()) if node is not None else ""


def write_json(name, obj):
    (ROOT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def write_csv(name, rows):
    with (ROOT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def load_source(key):
    filename, pin, doi, pmcid = PINS[key]
    data = (RAW_DIR / filename).read_bytes()
    assert hashlib.sha256(data).hexdigest() == pin, f"Source changed: {filename}"
    root = ET.fromstring(data)
    article = root.find("article") if root.tag != "article" else root
    assert article is not None
    ids = {x.get("pub-id-type"): norm(x) for x in article.findall("./front/article-meta/article-id")}
    assert ids["doi"] == doi and ids["pmcid"] == pmcid
    license_text = norm(article.find("./front/article-meta/permissions"))
    assert "creativecommons.org/licenses/by/4.0/" in license_text
    return article, ids


def sec(article, ident):
    x = article.find(f".//sec[@id='{ident}']")
    assert x is not None, ident
    return norm(x)


def make_row(identifier, study, unit, route, background, context, n, n_meaning, rate, locators, verdict, reason):
    return dict(row_id=identifier, study=study, doi=PINS[study][2], measurement_unit=unit,
                route=route, background=background, context=context, reported_n=n,
                reported_n_meaning=n_meaning, reported_mutation_rate=rate,
                matched_baseline_counts=None, matched_selected_route_counts=None,
                fixed_route_control_introduced=None, fixed_route_control_recovered=None,
                eligible_for_matched_tmd_panel=False, eligible_use=verdict,
                reason=reason, source_locators=locators,
                provenance="primary_article_derived_audit; not newly collected data")


def main():
    lind, lind_ids = load_source("lind2019")
    sun, sun_ids = load_source("sun2023")
    spectrum = sec(lind, "s2-4")
    assert "109 mutants" in spectrum and "105 harboured" in spectrum
    counts = {k: int(re.search(rf"{k} \((\d+) mutants\)", spectrum).group(1)) for k in ["wsp", "aws", "mws"]}
    assert counts == {"wsp": 46, "aws": 41, "mws": 18} and sum(counts.values()) == 105
    assert "remaining four" in spectrum and "PFLU0085, PFLU0183" in spectrum
    methods = sec(lind, "s4-2")
    assert "60 independent 110 μl cultures" in methods and "One randomly chosen colony per independent culture" in methods
    caption = norm(lind.find(".//fig[@id='fig8']/caption"))
    assert "Only within operon comparisons are valid" in caption and "double deletions" in caption
    fitness = sec(lind, "s4-4")
    assert "independently inoculated quadruplicates" in fitness and "24 hr" in fitness
    rates = sec(lind, "s2-1")
    for value in ["6.5 × 10−9", "3.7 × 10−9", "0.74 × 10−9", "11.2 × 10−9"]:
        assert value in rates
    assert "We only use experimental data published previously" in sec(sun, "s6")
    assert "not a statement about the true number" in sec(sun, "s8-2")
    assert sun.find(".//ref[@id='R21']//pub-id[@pub-id-type='doi']").text == PINS["lind2019"][2]

    rows = []
    designs = [("Wsp", "wsp", "PBR721 Δaws Δmws + pMSC", 3.7e-9, 200),
               ("Aws", "aws", "PBR713 Δwsp Δmws + pMSC", 6.5e-9, 200),
               ("Mws", "mws", "PBR712 Δwsp Δaws + pMSC", 0.74e-9, 400)]
    context = "SBW25 derivatives; KB, 28°C; shaken 200 rpm 16–19 h, kanamycin recovery"
    for route, gene, background, rate, rate_n in designs:
        rows.append(make_row(f"L2019_spectrum_{route}", "lind2019", "one sampled WS isolate per independent culture by protocol", route, background, context, counts[gene], "sequenced within-pathway mutant sample; not competing-route winners", None, ["s2-4", "fig6", "fig8", "s4-2", "s4-3"], "within-pathway mutation-spectrum analysis", "Other two focal pathways were deleted; do not normalize the 46/41/18 sample sizes into a common-background route distribution."))
        rows.append(make_row(f"L2019_rate_{route}", "lind2019", "fluctuation-test culture", route, background, context, rate_n, "Figure 2 reported fluctuation-test replicate count; distinct from sequenced-mutant sample size", rate, ["s2-1", "fig2", "s4-2"], "background-specific mutation-rate estimate", "Rate was measured in a pathway-isolated reporter background; not a matched route-multinomial baseline count or a fixed-route recovery-control denominator."))
    rows.append(make_row("L2019_rare_aggregate", "lind2019", "mutant aggregate", "Other: PFLU0085/PFLU0183", "Per-isolate and pathway-background allocation not specified in inspected aggregate", context, 4, "author-reported remaining rare-pathway mutants among 109; per-pathway allocation unavailable", None, ["s2-4"], "article-authenticated rare-mutant aggregate", "The primary article authenticates four rare mutants but does not make the mixed-background aggregate a common race or supply per-isolate allocation."))
    rows.append(make_row("L2019_preselection_aggregate", "lind2019", "mutants collected during fluctuation assays", "Wsp/Aws/Mws/rare", "mixed pathway-isolated assay backgrounds; do not infer rowwise allocation for rare mutants", context, 109, "105 focal mutants + 4 rare mutants; overlapping aggregate, not extra replication", None, ["s2-4", "fig8", "s4-2"], "sampling inventory only", "Aggregation combines different assay backgrounds; the count is not a selected competing-route denominator."))
    rows.append(make_row("L2019_WT_total_rate", "lind2019", "fluctuation-test culture", "all routes combined", "SBW25 ancestral genotype, all three focal pathways intact, + pMSC", context, 100, "Figure 2 reported WT fluctuation-test replicate count", 11.2e-9, ["s2-1", "fig2", "s4-2"], "total reporter-based mutation-rate estimate", "The common-background total rate is not route-resolved q or a selected-route distribution; only this assay context is documented."))
    rows.append(make_row("L2019_selected_historical_comparison", "lind2019", "previously published selected isolates", "Wsp fraction reported as 15/24", "earlier experiment; original selected data not acquired in this audit", "original static experimental evolution referenced to McDonald et al. 2009", 24, "denominator of Wsp 15/24 comparison in s2-7; do not reconstruct a complete triad", None, ["s2-7", "fig8"], "historical selected-comparison pointer", "The inspected text compares to prior selected results, rather than supplying a newly matched full selected panel with common-background supply and recovery controls."))
    rows.append(make_row("L2019_fitness_competitions", "lind2019", "independently inoculated pairwise competition microcosm", "representative Wsp/Aws/Mws mutants", "WS mutants and GFP WspF ΔT226-G275 reference; correction competitions for marker/deletion/reporter costs", "KB static growth, 28°C, 24 h; 1:1 initial mixture", 4, "quadruplicates per strain; total exported rows and successful replicates unverified", None, ["s2-8", "fig9", "s4-4", "fig9sdata1"], "competitive-performance measurement", "Before/after strain ratios, selection coefficients and marker/background controls do not supply one binary recovery per introduced fixed-route unit. Two >5% smooth-colony cases were excluded; workbook rows unavailable."))
    rows.append(make_row("S2023_aws_reuse", "sun2023", "prior experimental aws mutant occurrences", "Aws only", "inherits Lind 2019 pathway-isolated Aws reporter assay; no new common-background panel", "prior fluctuation experiment; context inherited from Lind 2019", 41, "Table 3 total; same empirical collection as Lind Aws, not 41 new trials", None, ["s2-2", "s6", "s8-3", "T3", "R21"], "mutation-rate-distribution calibration evidence", "Methods explicitly reuses published experiments; Table 3 cannot count as independent replication or new selected route outcomes."))
    rows.append(make_row("S2023_GPM_estimates", "sun2023", "estimated possible mutations", "16 genes grouped into pathways", "model of P. fluorescens SBW25 genotype-to-phenotype map", "illustrative incomplete empirical/molecular-function model", 500, "estimated possible mutation targets, not observed isolates or culture trials", None, ["s2-2", "s8-2", "T2"], "illustrative target-size model", "Authors explicitly say these estimates are not the true number of WS mutations per gene; do not turn 500 potential targets into observed counts."))
    rows.append(make_row("S2023_numerical_experiments", "sun2023", "simulated random draws and numerical replicates", "modelled mutation categories", "numerical model; no experimental common-background outcome panel", "Python completion, estimation, repeatability experiments", None, "numerical replication is not new biological replication", None, ["s6", "s7"], "simulation/model-method evidence", "Independent random mutation draws are a numerical assumption, not authenticated culture or binary-recovery observations."))

    needs = [
        ("common_background", ["strain_id", "ancestor_id", "genotype", "reporter", "route_availability", "context_id"], "All competing routes available in one documented background; contexts use the declared background.", "Fails for 46/41/18: double-deletion backgrounds differ by route. WT total-rate assay exists but has no route-resolved outcomes.", "No new common-background experiment; inherits Aws-only prior collection.", ["L:s2-1", "L:s4-1", "L:fig8", "S:s6", "S:R21"]),
        ("context_matched_supply", ["context_id", "baseline_culture_id", "baseline_counts_W_A_M", "mutation_assay_units", "division_or_opportunity_denominator", "uncertainty", "hotspot_repair_time_metadata"], "Independent validated route-probability calibration in every selected context; retain q uncertainty and measurement units.", "Background-specific rates exist in shaken KB; selected competition is static KB. No matched common-background route-multinomial baseline across contexts is authenticated.", "Uses assumed average rate and calibrated distribution plus reused Aws spectrum; these are not measured q for independent contexts.", ["L:s2-1", "L:s4-2", "L:s4-4", "S:s3-10", "S:s8-3"]),
        ("selected_route_counts", ["context_id", "culture_id", "outcome_rule", "route_W_A_M_Other", "selected_counts", "eligible_denominator", "missingness_exclusions", "ascertainment"], "Lock mutually exclusive route/outcome rules and exact common-background denominators; keep Other or declare conditional triad.", "46/41/18 are preselection spectra; the selected comparison refers to earlier work. No new matched full selected-route collection is authenticated here.", "No new selected biological collection reported; simulations and reused Table 3 do not provide selected counts.", ["L:s2-4", "L:s2-7", "L:fig8", "S:s6"]),
        ("independent_culture_lineage", ["founding_culture_id", "isolate_id", "lineage_id", "batch_id", "plate_well_id", "mutation_step", "immediate_ancestor_id", "replicate_type", "collection_reuse_id"], "Identify independent founding cultures, grouping and prior reuse; preserve dependent units during holdout.", "Methods supports one random isolate per independent culture and independent competition quadruplicates; culture/batch/well joins and exported completeness remain unverified because XLSX bytes were unavailable.", "Same 41 prior Aws occurrences are reused; numerical independence assumptions do not create biological IDs or extra cultures.", ["L:s4-2", "L:s4-4", "L:fig6sdata1", "L:fig9sdata1", "S:s6", "S:T3", "S:R21"]),
        ("fixed_route_recovery_controls", ["context_id", "branch_baseline_selected", "fixed_route_W_A_M", "introduced_L", "recovered_k", "exposed_unit_definition", "one_binary_outcome_per_unit", "binomial_marginal_justification", "control_relative_recovery_transport", "prespecified_mismatch_bounds"], "Six control cells per context: baseline/selected × W/A/M, each known L>0, integer 0≤k≤L and justified independent binary recovery; validate relative transfer or bounds.", "Existing GFP/deletion/reporter-cost competitions correct fitness ratios. Inspected Methods supplies no fixed-route binary introduced/recovered L,k panel; culture n, viable CFU, flow counts, 1:1 ratios and sequencing totals cannot substitute. Workbook fields remain unverified.", "No such new control panel in inspected article; reanalysed mutation occurrences and assumed numerical draws cannot substitute.", ["L:s4-2", "L:s4-4", "S:s6", "S:s8-3"]),
        ("whole_context_holdout", ["context_id", "context_protocol", "holdout_assignment", "freeze_timestamp", "training_blocks", "later_block_id", "theta_training_rule", "eta_holdout_prediction_rule", "loss_model_stopping_rules"], "Public prospective plan specifies ≥4 conditions and ≥1 whole-context holdout; fix theta and held-out eta before selected outcomes.", "Single KB-based assay setting with shaking/static branches; no prospectively frozen matched multiple-context training/holdout panel authenticated.", "Comparative simulated pathway cases are not independent biological contexts or held-out observations.", ["L:s4-1", "L:s4-2", "L:s4-4", "S:s6", "TMD:PROSPECTIVE_TEST_PLAN", "TMD:FORMULATION_AND_NEXT_EMPIRICAL_TEST"]),
    ]
    missing = []
    for component, fields, requirement, lind_status, sun_status, loc in needs:
        for study, status in [("lind2019", lind_status), ("sun2023", sun_status)]:
            missing.append(dict(study=study, component=component, required_fields=fields, admissibility_requirement=requirement,
                                authenticated_status=status, missing_measurement_status="not_authenticated_for_matched_TMD_panel",
                                absent_value_encoding="null; never substitute 0 or synthetic data",
                                inspected_scope="main primary article XML; Lind source XLSX contents unavailable; referenced studies/code not acquired",
                                evidence_locators=loc))

    table = sun.find(".//table-wrap[@id='T3']/table/tbody")
    assert table is not None
    aws_rows, current_gene = [], None
    for tr in table.findall("tr"):
        cells = [norm(x) for x in tr.findall("td")]
        if not cells or cells[0] == "Total":
            continue
        if cells[0].startswith("aws"):
            current_gene = cells.pop(0)
        assert current_gene and len(cells) >= 2, cells
        aws_rows.append(dict(gene=current_gene, mutation=cells[0], reported_occurrences=int(cells[1]),
                             source="Sun and Lind 2023 Appendix B Table 3; reused Lind et al. 2019",
                             independent_new_collection=False, eligible_competing_route_winner=False))
    assert len(aws_rows) == 12 and sum(x["reported_occurrences"] for x in aws_rows) == 41
    write_csv("sun_aws_table3_transcription.csv", aws_rows)
    write_json("ELIGIBILITY_ROWS.json", dict(schema_version="1.0", audit_date_utc=DATE, rows=rows,
               eligibility_scope="Inspected main-article material for the current matched common-background Wsp/Aws/Mws supply-selected-outcome-fixed-route-recovery estimand; not global absence or other scientific uses.",
               overall_verdict="no complete matched panel admitted from the inspected main-article material",
               panel_test_performed=False, source_workbooks_inspected=False,
               timing_eligibility="no exact first-successful-arrival/censoring records authenticated"))
    write_csv("eligibility_rows.csv", rows)
    write_json("MISSING_MEASUREMENTS.json", dict(schema_version="1.0", audit_date_utc=DATE, rows=missing))
    write_csv("missing_measurements.csv", missing)
    excerpts = [
        ("lind2019", "fig8/caption", caption, "Only within operon comparisons are valid for this figure as the mutants isolated without selection had double deletions of the other operons.", "Different background eligibility"),
        ("lind2019", "s4-2", methods, "One randomly chosen colony per independent culture with WS colony morphology was restreaked once on KB agar.", "Protocol-level sampling unit; exported joins unverified"),
        ("lind2019", "s2-4", spectrum, "Of the 109 mutants, 105 harboured a mutation in wsp (46 mutants), aws (41 mutants) or mws (18 mutants)", "Sequenced sample counts, not competing route probabilities"),
        ("lind2019", "s2-4", spectrum, "The remaining four had mutations in previously described rare pathways (PFLU0085, PFLU0183)", "Authenticate rare-four aggregate only"),
        ("lind2019", "s4-4", fitness, "Control competitions were also used to determine the cost of the double deletions and the reporter construct relative to a wild type genetic background", "Existing controls concern competition costs"),
        ("sun2023", "s6", sec(sun, "s6"), "We only use experimental data published previously, described in Appendix B.", "No new biological panel from numerical experiments"),
        ("sun2023", "s8-2", sec(sun, "s8-2"), "It is not a statement about the true number of WS mutations per gene", "500 target estimate is not an observed sample denominator"),
        ("sun2023", "s8-3", sec(sun, "s8-3"), "We used the experimental data for the aws pathway in Appendix B (Table 3) to calibrate the log-normal DMR model.", "Aws data is reused calibration evidence"),
    ]
    evidence = []
    for study, locator, source_text, quote, claim in excerpts:
        assert quote in source_text
        evidence.append(dict(study=study, doi=PINS[study][2], xml_locator=locator, evidence_excerpt=quote,
                             supported_claim=claim, source_sha256=PINS[study][1],
                             source_article_url=f"https://pmc.ncbi.nlm.nih.gov/articles/{PINS[study][3]}/",
                             source_license="CC BY 4.0", extraction_scope="short attributed excerpt from main article"))
    write_json("EVIDENCE_EXCERPTS.json", dict(audit_date_utc=DATE, rows=evidence))

    # The acquisition metadata is an immutable public audit record, not refreshed
    # from live URLs or the current state of the enclosing project checkout.
    acquisitions = json.loads((PACKAGE / "ACQUISITION_STATUS.json").read_text())["attempts"]
    assert len(acquisitions) == 6
    downloaded = sum(x.get("bytes", 0) for x in acquisitions)
    assert downloaded <= 10 * 1024 * 1024
    write_json("ACQUISITION_STATUS.json", dict(audit_date_utc=DATE, acquisitions_attempted=6,
               acquired_resources=3, source_acquisition_budget=6, downloaded_bytes=downloaded,
               download_budget_bytes=10 * 1024 * 1024, no_large_archive_downloaded=True,
               source_workbooks_acquired=False, attempts=acquisitions,
               limitations="API/CDN failures were proxy CONNECT 403; no publisher response or XLSX bytes. Candidate CDN v1 filenames were not version-authenticated. No access restriction was bypassed."))
    manifest = []
    for study, article, ids in [("lind2019", lind, lind_ids), ("sun2023", sun, sun_ids)]:
        fn, sha, doi, pmcid = PINS[study]
        rec = next(x for x in acquisitions if x.get("filename") == "raw/" + fn)
        manifest.append(dict(study=study, title=norm(article.find("./front/article-meta/title-group/article-title")), doi=doi,
                             pmcid=pmcid, pmcid_version=ids.get("pmcid-ver"), pmid=ids.get("pmid"),
                             local_raw_path="raw/" + fn, sha256=sha, bytes=rec["bytes"], url=rec["url"],
                             retrieved_utc=rec["retrieved_utc"], snapshot_not_experiment_certificate=True,
                             source_license="CC BY 4.0, verified in main article permissions", raw_publication_allowed_by_bundle=False,
                             inspected_scope="main article including Methods, figures, tables, data-availability statement and references; exclude subarticles/reviewer correspondence"))
    doc_hashes = [{"repository_relative_path": f, "sha256_as_inspected": sha, "source_commit": PROJECT_COMMIT,
                  "role": "frozen public project requirement snapshot; secondary claims not primary authentication; not refreshed during reproduction"}
                 for f, sha in PROJECT_DOCUMENT_PINS]
    write_json("SOURCE_MANIFEST.json", dict(audit_date_utc=DATE, primary_sources=manifest, public_project_documents=doc_hashes,
               declared_lind_source_files=[{"doi":"10.7554/eLife.38822.015", "xml_id":"fig6sdata1", "filename":"elife-38822-fig6-data1.xlsx", "description":"WS mutations in Wsp, Aws and Mws", "bytes_acquired":False},
                                           {"doi":"10.7554/eLife.38822.021", "xml_id":"fig9sdata1", "filename":"elife-38822-fig9-data1.xlsx", "description":"fitness assay data", "bytes_acquired":False}],
               sun_declared_code_url="https://github.com/anthony-sun/Mutationrates.git", code_acquired_or_run=False,
               prior_cached_lind_sun_primary_source_found=False))
    print(json.dumps(dict(eligibility_rows=len(rows), missing_measurement_rows=len(missing), aws_transcribed_rows=len(aws_rows), aws_occurrence_total=41, downloaded_bytes=downloaded, pinned_primary_identity_checks="passed", matched_panel_available=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Directory containing the two pinned primary XML files")
    parser.add_argument("--outdir", type=Path, default=PACKAGE, help="Output directory; expected artifact directory with --check")
    parser.add_argument("--check", action="store_true", help="Render in a temporary directory and compare generated files without overwriting artifacts")
    args = parser.parse_args()
    RAW_DIR = args.raw_dir.resolve()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="lind-sun-audit-check-", dir=PACKAGE) as temporary:
            ROOT = Path(temporary)
            main()
            for name in GENERATED_FILES:
                assert (ROOT / name).read_bytes() == (args.outdir / name).read_bytes(), f"Reproduction differs: {name}"
        print("All eight generated artifacts reproduce byte-for-byte; no published file overwritten.")
    else:
        ROOT = args.outdir.resolve()
        ROOT.mkdir(parents=True, exist_ok=True)
        main()

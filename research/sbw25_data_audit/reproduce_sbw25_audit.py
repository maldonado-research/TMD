#!/usr/bin/env python3
"""Original bounded audit of Farr's licensed figure data; standard library only.

The script reads the separately acquired, checksum-pinned public ZIP. It does
not execute workbook formulas, contact FALCOR, infer mutation births, or export
raw reads/workbooks, local-machine metadata, or article text.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import statistics
import xml.etree.ElementTree as ET
import zipfile

ZIP_BYTES = 7880751
ZIP_MD5 = "c07253f941ce89ceb594187255ba085a"
ZIP_SHA256 = "9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DATA_ROOT = "Zenodo data files 09 dec 2024/"
ARTICLE_DOI = "10.1371/journal.pgen.1011572"
DATA_DOI = "10.5281/zenodo.14335473"
WT = "SBW25 attTn7::nlpD-kan"
DEL = "SBW25 deltapsrA attTn7::nlpD-kan"
STRAINS = {WT: [38307, 38308, 38309, 38310, 38311, 38312],
           DEL: [38414, 38415, 38416, 38420, 38421, 38422]}


def close(actual, expected):
    return math.isclose(float(actual), float(expected), rel_tol=2e-12, abs_tol=1e-30)


def ratio(value):
    return Fraction(str(value))


def frac(value):
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def summary(values):
    values = list(map(float, values))
    return {"n": len(values), "arithmetic_mean": statistics.mean(values),
            "median": statistics.median(values), "minimum": min(values),
            "maximum": max(values)}


class Workbook:
    """Read strings, numeric cached values and formula text, without execution."""
    def __init__(self, content):
        self.z = zipfile.ZipFile(io.BytesIO(content))
        assert len(self.z.infolist()) <= 300
        assert sum(i.file_size for i in self.z.infolist()) <= 50 * 1024 * 1024
        strings = []
        if "xl/sharedStrings.xml" in self.z.namelist():
            tree = ET.fromstring(self.z.read("xl/sharedStrings.xml"))
            strings = ["".join(t.itertext()) for t in tree.findall("s:si", NS)]
        links = ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))
        targets = {x.attrib["Id"]: x.attrib["Target"] for x in links}
        self.sheets = {}
        self.formulas = {}
        tree = ET.fromstring(self.z.read("xl/workbook.xml"))
        for sheet in tree.findall("s:sheets/s:sheet", NS):
            rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = targets[rid]
            assert not target.startswith(("http:", "https:"))
            member = target.lstrip("/") if target.startswith("/") else "xl/" + target
            tree = ET.fromstring(self.z.read(member))
            cells, formulas, shared = {}, {}, {}
            for c in tree.findall("s:sheetData/s:row/s:c", NS):
                ref = c.attrib["r"]
                form, v = c.find("s:f", NS), c.find("s:v", NS)
                if form is not None:
                    if form.attrib.get("t") == "shared":
                        key = form.attrib["si"]
                        if form.text is not None:
                            shared[key] = (ref, form.text)
                            formulas[ref] = form.text
                        else:
                            master_ref, master_formula = shared[key]
                            formulas[ref] = translate_formula(master_formula, master_ref, ref)
                    else:
                        formulas[ref] = form.text
                typ = c.attrib.get("t", "n")
                if typ == "inlineStr":
                    el = c.find("s:is", NS)
                    val = "".join(el.itertext()) if el is not None else None
                elif v is None or v.text is None:
                    continue
                elif typ == "s":
                    val = strings[int(v.text)]
                elif typ in {"str", "e"}:
                    val = v.text
                elif typ == "b":
                    val = bool(int(v.text))
                else:
                    val = Fraction(v.text)
                cells[ref] = val
            self.sheets[sheet.attrib["name"]] = cells
            self.formulas[sheet.attrib["name"]] = formulas


def translate_formula(text, origin, target):
    """Expand ordinary shared A1 references; never evaluate a formula."""
    def column(name):
        n = 0
        for char in name:
            n = n * 26 + ord(char) - 64
        return n

    def col_name(n):
        chars = []
        while n:
            n, k = divmod(n - 1, 26)
            chars.append(chr(65 + k))
        return "".join(reversed(chars))

    a, b = [re.fullmatch(r"([A-Z]+)(\d+)", x) for x in (origin, target)]
    assert a and b
    dc, dr = column(b.group(1)) - column(a.group(1)), int(b.group(2)) - int(a.group(2))
    def replace(match):
        fixed_c, c, fixed_r, r = match.groups()
        cc = column(c) + (0 if fixed_c else dc)
        rr = int(r) + (0 if fixed_r else dr)
        assert cc > 0 and rr > 0
        return fixed_c + col_name(cc) + fixed_r + str(rr)
    return re.sub(r"(\$?)([A-Z]{1,3})(\$?)(\d+)", replace, text)


def read_fastq(content, compressed=False):
    if compressed:
        content = gzip.decompress(content)
    assert len(content) <= 2 * 1024 * 1024
    lines = content.decode("ascii").splitlines()
    assert len(lines) % 4 == 0
    records, seen = [], set()
    for h, s, sep, q in zip(lines[::4], lines[1::4], lines[2::4], lines[3::4]):
        assert h.startswith("@") and sep.startswith("+")
        assert len(s) == len(q) and 0 < len(s) < 5000
        assert set(s.upper()) <= set("ACGTRYKMSWBDHVN")
        assert all(33 <= ord(x) <= 126 for x in q)
        assert h not in seen
        seen.add(h)
        records.append((h, s.upper(), q))
    return records


def run(zip_path):
    assert Path(zip_path).stat().st_size == ZIP_BYTES
    data = Path(zip_path).read_bytes()
    assert len(data) == ZIP_BYTES
    assert hashlib.sha256(data).hexdigest() == ZIP_SHA256
    assert hashlib.md5(data).hexdigest() == ZIP_MD5
    z = zipfile.ZipFile(io.BytesIO(data))
    infos = z.infolist()
    assert len(infos) <= 250
    assert sum(x.file_size for x in infos) <= 100 * 1024 * 1024
    research, junk, dirs = {}, 0, 0
    for i in infos:
        p = PurePosixPath(i.filename)
        assert not p.is_absolute() and ".." not in p.parts and "\\" not in i.filename
        assert not stat.S_ISLNK(i.external_attr >> 16) and not i.flag_bits & 1
        if i.is_dir():
            dirs += 1
        elif i.filename.startswith("__MACOSX/") or p.name.startswith("."):
            junk += 1
        else:
            assert i.filename.startswith(DATA_ROOT)
            research[i.filename] = z.read(i)
    assert len(research) == 28
    inventory = [{"member": k, "bytes": len(v),
                  "sha256": hashlib.sha256(v).hexdigest()} for k, v in sorted(research.items())]

    def find(suffix):
        matches = [n for n in research if n.endswith(suffix)]
        assert len(matches) == 1, suffix
        return matches[0], research[matches[0]]

    workbook_name, content = find("Colony Counts Fluctuation assays_20_6_24 .xlsx")
    w = Workbook(content)
    c = w.sheets["Calculation of C565T frequency"]
    raw = w.sheets["Raw data of CFU"]
    plot = w.sheets["Data for plotting"]
    formulas = w.formulas["Calculation of C565T frequency"]
    rows, checks, formula_checks = [], 0, 0
    for r in range(2, 26):
        for col in "ABCDEFGHIJ":
            assert c[col + str(r)] == raw[col + str(r)]
            checks += 1
        val = lambda col: c[col + str(r)]
        trial, genotype, rep = int(val("A")), val("B"), int(val("C"))
        assert trial in (1, 2) and genotype in STRAINS and 1 <= rep <= 6
        h, plates, dilution = val("H"), val("I"), val("J")
        k, m = val("L"), val("M")
        assert all(v.denominator == 1 for v in (h, plates, k, m))
        assert 0 <= k <= m and h > 0 and plates > 0 and 0 < dilution <= 1
        expected = {"F": val("D") * 20, "G": val("E") * 20 * 1000000,
                    "K": h / (plates / 20) / dilution, "N": k / m}
        expected["O"] = expected["K"] * expected["N"]
        expected["P"] = expected["O"] / expected["G"]
        expected_forms = {"F": f"D{r}*20", "G": f"E{r}*20*1000000",
                          "K": f"H{r}/(I{r}/20)/J{r}", "N": f"L{r}/M{r}",
                          "O": f"K{r}*N{r}", "P": f"O{r}/G{r}"}
        for col, value in expected.items():
            assert close(val(col), value), (r, col)
            checks += 1
            assert formulas[col + str(r)] == expected_forms[col]
            formula_checks += 1
        assert plot["A" + str(r)] == trial and plot["B" + str(r)] == genotype
        assert plot["C" + str(r)] == rep and close(plot["D" + str(r)], expected["P"])
        assert close(plot["E" + str(r)], math.log10(float(expected["P"])))
        checks += 5
        rows.append({"workbook_row": r, "occasion": trial, "background": genotype,
                     "transformant_replicate_number": rep,
                     "transformant_label": "MPB" + str(STRAINS[genotype][rep - 1]),
                     "candidate_colonies_integer": int(h), "selective_plates_integer": int(plates),
                     "culture_fraction_dilution": frac(dilution), "plate_volume_ml": "1/20",
                     "confirmed_C565T_integer": int(k), "sequenced_denominator_integer": int(m),
                     "sequenced_exceeds_recorded_candidate_pool": m > h,
                     "confirmation_fraction": frac(expected["N"]),
                     "terminal_total_CFU_per_ml": frac(expected["G"]),
                     "corrected_C565T_CFU_per_ml": frac(expected["O"]),
                     "corrected_terminal_frequency": frac(expected["P"]),
                     "cached_frequency": float(val("P")),
                     "cached_minus_exact_frequency": float(val("P") - expected["P"])})
    strata = []
    for trial in (1, 2):
        for g in STRAINS:
            a = [x for x in rows if x["occasion"] == trial and x["background"] == g]
            vals = [Fraction(x["corrected_terminal_frequency"]) for x in a]
            strata.append({"occasion": trial, "background": g,
                           "culture_occurrences": len(a),
                           "candidate_colonies_total": sum(x["candidate_colonies_integer"] for x in a),
                           "confirmed_C565T_total": sum(x["confirmed_C565T_integer"] for x in a),
                           "sequenced_total": sum(x["sequenced_denominator_integer"] for x in a),
                           "terminal_frequency": summary(vals)})
    pooled = {g: summary(Fraction(x["corrected_terminal_frequency"]) for x in rows
                         if x["background"] == g) for g in STRAINS}
    contrasts = []
    for t in (1, 2):
        a, b = [next(s for s in strata if s["occasion"] == t and s["background"] == g)
                for g in (WT, DEL)]
        contrasts.append({"occasion": t,
                          "ratio_of_arithmetic_means": a["terminal_frequency"]["arithmetic_mean"] /
                                                       b["terminal_frequency"]["arithmetic_mean"],
                          "ratio_of_medians": a["terminal_frequency"]["median"] /
                                              b["terminal_frequency"]["median"]})
    # Diagnostic only: unique exact outer 15-base anchors and Phred+33 target Q>=20.
    # The 3-base window allows both the target substitution and adjacent A564G.
    ref_name, gb = find("Figure 4A sanger sequencing files/nlpD-kan reference sequence.gb")
    text = gb.decode("utf-8")
    assert 'promoter        2023..2025' in text and '/standard_name="codon 189"' in text
    ref = "".join(re.findall("[acgt]+", text.split("ORIGIN")[1].split("//")[0])).upper()
    assert len(ref) == 3294 and ref[2022:2025] == "CAG"
    target = 2022  # zero-based reference C, first nucleotide of codon 189.
    pattern = re.compile(re.escape(ref[target - 16:target - 1]) + "(...)" +
                         re.escape(ref[target + 2:target + 17]))
    seq = []
    for trial, suffix in [(1, "94 documents from 20_12_23 repeated fluctuation trial 1.fastq"),
                          (2, "96 documents from 10_1_24 fluctuation kan400 trial 2.fastq")]:
        name, content = find(suffix)
        records = read_fastq(content)
        groups = defaultdict(list)
        for head, bases, quals in records:
            match = re.match(r"@(MPB\d+)_c(\d+)_", head)
            assert match
            strain, colony = match.group(1), int(match.group(2))
            assert 1 <= colony <= 8
            windows = list(pattern.finditer(bases))
            call, quality = None, None
            if len(windows) == 1:
                pos = windows[0].start(1) + 1
                quality = ord(quals[pos]) - 33
                if quality >= 20 and bases[pos] in "ACGT":
                    call = bases[pos]
            groups[strain].append((colony, call, quality))
        for row in [x for x in rows if x["occasion"] == trial]:
            a = groups[row["transformant_label"]]
            colony_ids = [x[0] for x in a]
            assert len(set(colony_ids)) == len(colony_ids)
            counts = Counter(x[1] or "unresolved" for x in a)
            seq.append({"occasion": trial, "transformant_label": row["transformant_label"],
                        "background": row["background"], "available_read_records": len(a),
                        "missing_expected_colony_labels": sorted(set(range(1, 9)) - set(colony_ids)),
                        "diagnostic_target_calls": dict(sorted(counts.items())),
                        "workbook_confirmed_C565T": row["confirmed_C565T_integer"],
                        "workbook_sequenced_denominator": row["sequenced_denominator_integer"],
                        "exact_T_count_matches_workbook": counts["T"] == row["confirmed_C565T_integer"],
                        "available_records_equal_workbook_denominator": len(a) == row["sequenced_denominator_integer"]})
    assert all(x["exact_T_count_matches_workbook"] and
               x["available_records_equal_workbook_denominator"] for x in seq if x["occasion"] == 2)
    fastq_inventory = []
    for name, content in sorted(research.items()):
        if name.endswith((".fastq", ".fastq.gz")):
            fastq_inventory.append({"member": name,
                                    "records": len(read_fastq(content, name.endswith(".gz")))})

    # Time-course frequency arithmetic, destructive sampling: no mutation-rate fit.
    tc_name, content = find("26_11_24 time course calculations.xlsx")
    tcw = Workbook(content)
    time_rows, time_checks = [], 0
    for sn in ("data trial 1 feb 2024", "data trial 2 nov 2024"):
        s = tcw.sheets[sn]
        for r in range(2, 14):
            v = lambda col: s[col + str(r)]
            expected = {"D": v("C") * 20, "I": v("G") * v("H") * 20,
                        "N": v("K") * v("L") / v("M"), "Q": v("O") / v("P")}
            expected["R"] = expected["N"] * expected["Q"]
            expected["S"] = expected["R"] / expected["I"]
            for col, value in expected.items():
                assert close(v(col), value), (sn, r, col)
                time_checks += 1
            time_rows.append({"occasion": int(v("A")), "hours": float(v("F")),
                              "frequency": expected["S"], "confirmed": int(v("O")),
                              "sequenced": int(v("P")), "selected": int(v("K")),
                              "plates": str(v("J"))})
    times = []
    for key in sorted({(x["occasion"], x["hours"]) for x in time_rows}):
        a = [x for x in time_rows if (x["occasion"], x["hours"]) == key]
        times.append({"occasion": key[0], "hours": key[1], "culture_occurrences": len(a),
                      "confirmed_C565T_total": sum(x["confirmed"] for x in a),
                      "sequenced_total": sum(x["sequenced"] for x in a),
                      "terminal_frequency": summary(x["frequency"] for x in a)})
    assert len(time_rows) == 24 and sum(x["sequenced"] for x in time_rows) == 213

    # Recheck the supplied competition calculation, retaining marker strata.
    fit_name, content = find("Fitness assay data nlpDkan mutants 24_6_24 .xlsx")
    fw = Workbook(content)
    fs = fw.sheets["Selection coefficients"]
    fr = fw.sheets["Data for R"]
    fitness_values, fitness_checks = [], 0
    for r in range(2, 34):
        v = lambda col: fs[col + str(r)]
        generations = math.log2(float(v("V") / v("U")))
        sc = (math.log(float(v("O"))) - math.log(float(v("P")))) / generations
        assert close(v("W"), generations) and close(v("Y"), sc)
        fitness_checks += 2
        competition, trial = int(v("A")), int(v("B"))
        found = [i for i in range(2, 34) if fr["A" + str(i)] == competition and fr["B" + str(i)] == trial]
        assert len(found) == 1
        i = found[0]
        assert close(fr["E" + str(i)], sc)
        fitness_checks += 1
        fitness_values.append((fr["C" + str(i)], fr["D" + str(i)], trial, sc))
    fitness_strata = [{"background": bg, "mutant_fluorescent_marker": marker, "occasion": trial,
                       "selection_coefficient_per_generation": summary(x[3] for x in fitness_values
                          if x[:3] == (bg, marker, trial))}
                      for bg in ("WT", "Delta psrA") for marker in ("R", "G") for trial in (1, 2)]

    # Figure4B uses averaged technical Ct runs and a log2 transcript proxy.
    qp_name, content = find("2024_06_13_rtqpcrSBW25_Fig4B.xlsx")
    qw = Workbook(content)
    qc, qr = qw.sheets["Calculations"], qw.sheets["Rdata"]
    setup = qw.sheets["Sample set up round 1 +2"]
    amplicon_by_well = {int(setup["A" + str(r)]): setup["E" + str(r)]
                       for r in range(2, 98) if "A" + str(r) in setup and "E" + str(r) in setup}
    qvalues, qchecks = defaultdict(list), 0
    for r in range(2, 14):
        background, rep, value = qr["A" + str(r)], int(qr["B" + str(r)]), qr["C" + str(r)]
        genotype = "SBW25" if background == "SBW25" else "SBW25deltapsrA"
        matched = [i for i in range(4, 73, 4) if qc["K" + str(i)] == genotype and
                   qc["L" + str(i)] == "22hr" and qc["M" + str(i)] == rep]
        assert len(matched) == 1
        i = matched[0]
        assert amplicon_by_well[int(qc["A" + str(i - 1)])] == "nlpD5'"
        assert amplicon_by_well[int(qc["A" + str(i)])] == "nlpD3'"
        qchecks += 2
        for j in (i - 1, i):
            assert close(qc["H" + str(j)], (qc["C" + str(j)] + qc["D" + str(j)]) / 2)
            qchecks += 1
        delta = qc["H" + str(i)] - qc["H" + str(i - 1)]
        assert close(qc["N" + str(i)], delta)
        assert close(qc["O" + str(i)], 2 ** -float(delta))
        assert close(qc["P" + str(i)], math.log2(float(qc["O" + str(i)])))
        assert close(value, -delta)
        qchecks += 4
        qvalues[background].append(float(value))
    wt_log, del_log = statistics.mean(qvalues["SBW25"]), statistics.mean(qvalues["psrA"])
    assert close(qc["S8"], wt_log) and close(qc["T8"], del_log)
    qchecks += 2

    return {"schema_version": 1, "scope": "public_source_measurement_and_arithmetic_audit",
            "article_doi": ARTICLE_DOI, "dataset_doi": DATA_DOI,
            "zip_verification": {"bytes": ZIP_BYTES, "md5": ZIP_MD5, "sha256": ZIP_SHA256,
                                 "entries": len(infos), "expanded_bytes": sum(i.file_size for i in infos),
                                 "research_members": len(research), "excluded_junk_members": junk,
                                 "directory_entries": dirs, "safe_paths_no_symlinks_no_encryption": True},
            "research_member_inventory": inventory,
            "figure4A": {"workbook_member": workbook_name, "culture_occurrences": 24,
                          "distinct_transformants_per_background": 6, "occasions": 2,
                          "transformants_reused_across_occasions": True,
                          "integer_source_and_derived_measurement_ledger": rows,
                          "cached_numeric_and_plot_checks": checks,
                          "formula_text_checks": formula_checks,
                          "cached_difference_interpretation": "floating serialization residuals; no exact identity assertion",
                          "occasion_strata": strata, "pooled_descriptive_frequency": pooled,
                          "occasion_frequency_ratios": contrasts,
                          "pooled_mean_frequency_ratio": pooled[WT]["arithmetic_mean"] / pooled[DEL]["arithmetic_mean"],
                          "reported_MSS_mutation_rate_ratio_not_reproduced": float(Fraction(42, 10) * 100 / Fraction(72, 10)),
                          "reported_rate_fit_reproduced": False},
            "sequencing": {"reference_member": ref_name, "target_reference_position_1based": 2023,
                           "reference_annotation": "first base of annotated codon189; article nlpD C565",
                           "rule": "unique exact outer15-base anchors around564-566 window; Phred+33 targetQ>=20; no indel rescue or imputation",
                           "diagnostic_culture_groups": seq, "all_FASTQ_record_inventory": fastq_inventory,
                           "records_are_not_independent_founder_trials": True},
            "timecourse": {"workbook_member": tc_name, "culture_occurrences": 24,
                           "occasions": 2, "destructive_sampling": True,
                           "cached_arithmetic_checks": time_checks,
                           "sequenced_total": sum(x["sequenced"] for x in time_rows),
                           "occasion_time_strata": times,
                           "adaptive_extra_sequencing": "occasion2 approximately16h replicate2 has32 sequenced colonies, including24 follow-ups; preserve outcome-dependent sampling",
                           "excluded_contaminated_selective_plate": "occasion2 earliest time replicate1:7 plates instead of8; volume0.35mL"},
            "fitness": {"workbook_member": fit_name, "competition_occurrences": 32,
                        "cached_calculation_checks": fitness_checks,
                        "reproduced_from_supplied_ratio_and_population_columns": True,
                        "raw_cytometry_gating_reprocessed": False, "marker_occasion_strata": fitness_strata},
            "figure4B_transcript_proxy": {"workbook_member": qp_name, "cached_arithmetic_and_mapping_checks": qchecks,
                            "biological_replicate_labels_per_background": 6,
                            "technical_Ct_runs_averaged_per_sample": 2,
                            "reported_transform": "log2(2^(-Ct3prime+Ct5prime)); no efficiency refit",
                            "amplicon_mapping": "sample-setup wells B/F=nlpD5prime and C/G=nlpD3prime; all24 selected Ct-well labels checked",
                            "log2_transcript_proxy": {k: summary(v) for k, v in qvalues.items()},
                            "geometric_mean_proxy_ratio": 2 ** (wt_log - del_log),
                            "arithmetic_mean_linear_proxy_ratio": statistics.mean(2 ** x for x in qvalues["SBW25"]) /
                                                                  statistics.mean(2 ** x for x in qvalues["psrA"]),
                            "ratio_of_log2_means_is_not_a_fold_change": wt_log / del_log,
                            "article_text_reported_reduction": "approximately6-fold",
                            "article_Figure4B_caption_reported_reduction": "approximately4-fold",
                            "reason_for_article_text_caption_difference_verified": False,
                            "new_qPCR_fit_or_causal_promoter_measurement": False},
            "limits": {"native_selected_isolate_count_reconciled": False,
                       "native_per_division_rate_measured_by_this_audit": False,
                       "FALCOR_MSS_fit_reproduced": False,
                       "qPCR_raw_fluorescence_reprocessed": False,
                       "native_reporter_transport_parameter_identified": False,
                       "matched_WAM_panels_admitted": 0, "actual_registry_fields_resolved": 0,
                       "new_biological_TMD_confirmation": False}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--check-against", type=Path)
    args = p.parse_args()
    result = run(args.zip)
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check_against:
        assert encoded == args.check_against.read_text(), "derived replay differs"
    args.output.write_text(encoded)
    print(json.dumps({"status": "passed", "figure4A_culture_occurrences": 24,
                      "figure4A_cached_checks": result["figure4A"]["cached_numeric_and_plot_checks"],
                      "formula_checks": result["figure4A"]["formula_text_checks"],
                      "timecourse_checks": result["timecourse"]["cached_arithmetic_checks"],
                      "fitness_checks": result["fitness"]["cached_calculation_checks"],
                      "qPCR_arithmetic_checks": result["figure4B_transcript_proxy"]["cached_arithmetic_and_mapping_checks"],
                      "WAM_panels_admitted": 0, "FALCOR_fit_reproduced": False}))


if __name__ == "__main__":
    main()

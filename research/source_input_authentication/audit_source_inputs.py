#!/usr/bin/env python3
"""Offline original audit of published software declarations and workbook units.

Reads separately held, hash-pinned public source files. Does not execute Excel,
contact FALCOR, infer a historical submission, or fit biological mutation rates.
No full article text, relationship targets, reads or raw cell tables are exported.
Minimal formula masters and derived aggregate quantities are recorded.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import xml.etree.ElementTree as ET
import zipfile

ZIP_SHA = "9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6"
ARTICLE_SHA = "937c7eded441b32eea42777d703647965e6090ccb5850017f2b5b6cbd4ea53c2"
WORKBOOK_SHA = "93c1b8e0d341124723eb64ca2c28f058a46c38ea20b7f7cf6217451d84e4c6fb"
KEYWORDS = ("falcor", "mss", "maximum likelihood", "mutation rate")
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
XLINK = "{http://www.w3.org/1999/xlink}href"
WT = "SBW25 attTn7::nlpD-kan"
DEL = "SBW25 deltapsrA attTn7::nlpD-kan"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(obj):
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def rational(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def bounded_zip(data, max_entries, max_bytes):
    z = zipfile.ZipFile(io.BytesIO(data))
    assert len(z.infolist()) <= max_entries
    assert sum(i.file_size for i in z.infolist()) <= max_bytes
    for i in z.infolist():
        p = PurePosixPath(i.filename)
        assert not p.is_absolute() and ".." not in p.parts and "\\" not in i.filename
        assert not stat.S_ISLNK(i.external_attr >> 16) and not i.flag_bits & 1
    return z


def workbook_sheet(data, sheet_name):
    """Read cached values and formula masters without evaluating any formula."""
    z = bounded_zip(data, 300, 50 * 1024 * 1024)
    strings = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        strings = ["".join(s.itertext()) for s in ss.findall("s:si", NS)]
    rels = {r.attrib["Id"]: r.attrib["Target"]
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    w = ET.fromstring(z.read("xl/workbook.xml"))
    sheet = next(s for s in w.findall("s:sheets/s:sheet", NS)
                 if s.attrib["name"] == sheet_name)
    target = rels[sheet.attrib[RID]]
    assert not target.startswith(("http:", "https:", "file:"))
    part = target.lstrip("/") if target.startswith("/") else "xl/" + target
    values, masters = {}, {}
    for c in ET.fromstring(z.read(part)).findall("s:sheetData/s:row/s:c", NS):
        ref, typ = c.attrib["r"], c.attrib.get("t", "n")
        f, v = c.find("s:f", NS), c.find("s:v", NS)
        if f is not None and f.text is not None:
            masters[ref] = f.text
        if typ == "inlineStr":
            values[ref] = "".join(c.find("s:is", NS).itertext())
        elif v is not None and v.text is not None:
            if typ == "s": values[ref] = strings[int(v.text)]
            elif typ in {"str", "e"}: values[ref] = v.text
            elif typ == "b": values[ref] = bool(int(v.text))
            else: values[ref] = Fraction(v.text)
    return values, masters


def scan_workbook(name, data):
    z = bounded_zip(data, 300, 50 * 1024 * 1024)
    hits = []
    external_targets = Counter()
    for part in sorted(z.namelist()):
        if part.endswith((".xml", ".rels")):
            text = z.read(part).decode("utf-8").casefold()
            found = [k for k in KEYWORDS if k in text]
            if found: hits.append({"part": part, "keywords": found})
        if part.startswith("xl/externalLinks/_rels/") and part.endswith(".rels"):
            for r in ET.fromstring(z.read(part)):
                target = r.attrib.get("Target", "")
                # Deliberately do not copy original operator paths/targets.
                scheme = target.split(":", 1)[0].lower() if ":" in target else "relative"
                external_targets[scheme if scheme in {"file", "http", "https"} else "other"] += 1
    return {"member": name, "sha256": digest(data),
            "software_input_keyword_hits": hits,
            "external_link_part_count": sum("externalLink" in p for p in z.namelist()),
            "external_target_scheme_counts": dict(sorted(external_targets.items()))}


def audit(zip_path, article_path):
    archive, xml = Path(zip_path).read_bytes(), Path(article_path).read_bytes()
    assert len(archive) == 7880751 and digest(archive) == ZIP_SHA
    assert digest(xml) == ARTICLE_SHA
    z = bounded_zip(archive, 250, 100 * 1024 * 1024)
    research = {n: z.read(n) for n in z.namelist()
                if not n.endswith("/") and not n.startswith("__MACOSX/")
                and not PurePosixPath(n).name.startswith(".")}
    assert len(research) == 28
    workbooks = [scan_workbook(n, b) for n, b in sorted(research.items()) if n.endswith(".xlsx")]
    assert len(workbooks) == 6
    rtf_scan = [{"member": n, "sha256": digest(b),
                 "literal_decoded_keyword_hits": [k for k in KEYWORDS if k in b.decode("utf-8", errors="replace").casefold()]}
                for n, b in sorted(research.items()) if n.endswith(".rtf")]
    assert len(rtf_scan) == 5
    legacy = [{"member": n, "sha256": digest(b), "format": "OLE compound binary",
               "semantic_spreadsheet_parse": "UNRUN"}
              for n, b in sorted(research.items()) if n.endswith(".xls")]
    assert len(legacy) == 2
    for n, b in research.items():
        if n.endswith(".xls"): assert b.startswith(bytes.fromhex("d0cf11e0a1b11ae1"))

    article = ET.fromstring(xml).find("article")
    assert article is not None
    sec = next(s for s in article.find("body").iter("sec") if s.attrib.get("id") == "sec016")
    official = [e.attrib[XLINK] for e in sec.iter("ext-link")]
    assert official == ["https://lianglab.brocku.ca/FALCOR/"]
    method_text = " ".join("".join(sec.itertext()).split())
    assert "MSS maximum likelihood" in method_text and "6 mL" in method_text
    ref = next(r for r in article.find("back").iter("ref") if r.attrib.get("id") == "pgen.1011572.ref056")
    assert any(p.text == "10.1093/bioinformatics/btp253" for p in ref.iter("pub-id"))
    rates = [
        {"anchor": "sec006", "rate": "4.2e-7", "interval_endpoints_as_printed": ["4.5e-7", "3.9e-7"]},
        {"anchor": "sec007", "rate": "7.2e-9", "interval_endpoints_as_printed": ["9.2e-9", "5.4e-9"]},
    ]
    for item, expected_rate, expected_ci in zip(rates,
            ("4.2 × 10-7", "7.2 × 10-9"),
            ("95% CI = 4.5 – 3.9 × 10-7", "95% CI = 9.2 – 5.4 × 10-9")):
        section = next(s for s in article.find("body").iter("sec") if s.attrib.get("id") == item["anchor"])
        text = " ".join("".join(section.itertext()).split())
        assert expected_rate in text and expected_ci in text
    history = [{"id": s.attrib.get("id"), "article_type": s.attrib.get("article-type"),
                "not_final_methods": True} for s in article.findall("sub-article")]
    assert len(history) == 7

    n = next(n for n in research if n.endswith("Colony Counts Fluctuation assays_20_6_24 .xlsx"))
    assert digest(research[n]) == WORKBOOK_SHA
    cells, formulas = workbook_sheet(research[n], "Calculation of C565T frequency")
    expected = {"F2": "D2*20", "G2": "E2*20*1000000", "K2": "H2/(I2/20)/J2",
                "N2": "L2/M2", "O2": "K2*N2", "P2": "O2/G2"}
    assert {k: formulas[k] for k in expected} == expected
    rows, checks = [], 0
    for r in range(2, 26):
        c = {col: cells[f"{col}{r}"] for col in "ABCDEFGHIJLM"}
        for col in "ACHILM": assert c[col].denominator == 1
        assert c["B"] in {WT, DEL}
        H, I, J, L, M = (c[x] for x in "HIJLM")
        assert H > 0 and I > 0 and 0 < J <= 1 and 0 < L <= M
        corrected = H * L / M
        computed = {"F": c["D"]*20, "G": c["E"]*20*1000000,
                    "K": H*20/I/J, "N": L/M}
        computed["O"] = computed["K"] * computed["N"]
        computed["P"] = computed["O"] / computed["G"]
        for col, value in computed.items():
            assert math.isclose(float(cells[f"{col}{r}"]), float(value), rel_tol=2e-12, abs_tol=1e-30)
            checks += 1
        rows.append({"occasion": int(c["A"]), "background": c["B"], "transformant_number": int(c["C"]),
                     "candidate_H": H, "confirmed_L": L, "sequenced_M": M,
                     "candidate_pool_corrected_estimate": corrected,
                     "candidate_density_estimate_CFU_per_ml": computed["K"],
                     "C565T_corrected_density_estimate_CFU_per_ml": computed["O"],
                     "terminal_density_estimate_CFU_per_ml": computed["G"],
                     "nominal_terminal_population_estimate_CFU_in_6ml": computed["G"]*6,
                     "nominal_sampling_fraction": I*J/120})
    assert len({(x["occasion"],x["background"],x["transformant_number"]) for x in rows}) == 24
    quantities = []
    fields = [f for f in rows[0] if f not in {"occasion", "background", "transformant_number", "nominal_sampling_fraction"}]
    for background in (WT, DEL):
        group = [x for x in rows if x["background"] == background]
        assert len(group) == 12
        for field in fields:
            vector = [rational(x[field]) for x in group]
            quantities.append({"background": background, "quantity": field, "culture_occurrences": len(group),
                               "noninteger_estimates": sum(x[field].denominator != 1 for x in group),
                               "minimum": rational(min(x[field] for x in group)),
                               "maximum": rational(max(x[field] for x in group)),
                               "ordered_vector_sha256": digest(encode(vector)),
                               "historical_submission_authenticated": False})
    return {"schema_version": 1, "round_id": "R000009", "project": "Mutation by Natural Dominance",
            "article_doi": "10.1371/journal.pgen.1011572", "dataset_doi": "10.5281/zenodo.14335473",
            "article_sha256": ARTICLE_SHA, "dataset_zip_sha256": ZIP_SHA,
            "final_article_software_declaration": {"anchor": "main article body sec016",
                "official_url": official[0], "method": "MSS maximum likelihood", "software_paper_doi": "10.1093/bioinformatics/btp253",
                "historical_build_or_inputs_authenticated": False},
            "final_article_reported_rate_values_not_reproduced": rates,
            "research_file_extensions": dict(sorted(Counter(PurePosixPath(n).suffix.lower() for n in research).items())),
            "OOXML_scan_scope": {"files": len(workbooks), "mode": "case-insensitive literal XML/rels token scan, not execution",
                "keywords": list(KEYWORDS), "files_with_keyword_hits": sum(bool(x["software_input_keyword_hits"]) for x in workbooks)},
            "workbook_scan": workbooks, "RTF_scan": rtf_scan, "legacy_XLS_semantic_parse_UNRUN": legacy,
            "workbook_formula_masters": expected, "cached_arithmetic_comparisons": checks,
            "source_unit_quantity_fingerprints": quantities,
            "ordered_vector_scope": "per background: source rows ascending, occasion1 then occasion2, transformants1..6",
            "fingerprint_serialization": "SHA256 of UTF-8 JSON list, indent2 plus final newline; exact rational strings, integer strings omit /1; computed rational formulas, not Excel cached decimal bytes",
            "fingerprints_authenticate_or_disprove_a_historical_run": False,
            "Figure4A_confirmed_positive_culture_occurrences": 24,
            "candidate_pool_confirmed_estimate_noninteger_rows": sum(x["candidate_pool_corrected_estimate"].denominator != 1 for x in rows),
            "peer_history_not_final_methods": history,
            "absence_scope": "No literal software tokens in the six inspected OOXML and five decoded RTF files; no general historical-file absence inference.",
            "historical_FALCOR_input_vectors_identified": 0, "biological_rate_fit_performed": False,
            "actual_TMD_study_fields_resolved": 0, "hypothesis_confirmation": False,
            "raw_relationship_targets_exported": False}


def main():
    if not __debug__:
        raise SystemExit("Source verification requires assertions enabled; run without -O/-OO.")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", required=True)
    p.add_argument("--article-xml", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--check-against")
    a = p.parse_args()
    payload = encode(audit(a.zip, a.article_xml))
    if a.check_against: assert payload == Path(a.check_against).read_bytes(), "audit replay differs"
    Path(a.output).write_bytes(payload)
    print(json.dumps({"status": "PASS", "cached_arithmetic_comparisons": 144,
                      "historical_submissions_authenticated": 0, "output_sha256": digest(payload)}, sort_keys=True))


if __name__ == "__main__":
    main()

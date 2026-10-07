"""Replay synthetic mixtures; optionally authenticate cached inspected sources."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from translation_counterexample import benchmarks


def text(element):
    return " ".join("".join(element.itertext()).split()) if element is not None else ""


def source_replay(source_file, source_record):
    if source_file is None:
        return {"status": "unrun_source_cache_not_supplied", "checks": 0}
    if hashlib.sha256(source_file.read_bytes()).hexdigest() != source_record["sha256"]:
        raise ValueError("Source bytes differ from inspected immutable source")
    tree = ET.parse(source_file).getroot()
    article = tree if tree.tag == "article" else tree.find("article")
    if article is None:
        raise ValueError("Expected one article in source XML")
    checks = 1
    title = text(article.find("front/article-meta/title-group/article-title"))
    if title != source_record["title"]:
        raise ValueError("Source title differs")
    checks += 1
    paragraphs = [text(element) for element in article.findall("body//p")]
    if len(paragraphs) != source_record["body_paragraphs_inspected"]:
        raise ValueError("Source body paragraph inventory differs")
    checks += 1
    for anchor in source_record["anchors"]:
        encoded = paragraphs[anchor["body_paragraph_index"]].encode()
        if hashlib.sha256(encoded).hexdigest() != anchor["normalized_paragraph_sha256"]:
            raise ValueError("Source anchor hash differs")
        checks += 1
    return {"status": "passed_cached_source_byte_and_anchor_replay", "checks": checks,
            "raw_measurements_or_supplements_replayed": False}


def main():
    if not __debug__:
        raise SystemExit("Verification requires ordinary Python without -O/-OO.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    parser.add_argument("--human-xml", type=Path)
    parser.add_argument("--mouse-xml", type=Path)
    args = parser.parse_args()
    benchmark = benchmarks()
    encoded = (json.dumps(benchmark, indent=2)+"\n").encode()
    if args.check_against and encoded != args.check_against.read_bytes():
        raise SystemExit("Stored cancer-translation synthetic benchmark differs")
    sources = json.loads((Path(__file__).parent/"SOURCE_LEDGER.json").read_text())["primary_sources"]
    replay = {"human_esophagus": source_replay(args.human_xml, sources[0]),
              "mouse_competition": source_replay(args.mouse_xml, sources[1])}
    receipt = {"status": "passed_conditional_synthetic_methods", "synthetic_checks": benchmark["checks"],
               "synthetic_check_total": sum(benchmark["checks"].values()), "source_replay": replay,
               "source_hashes_do_not_authenticate_biological_interpretation": True,
               "biological_fit": False, "cancer_prevention_or_treatment_result": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()

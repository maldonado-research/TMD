"""Independent narrow check of root's original recent-method source summary.

Reads cached files only. Twelve anchored MitoTracer paragraphs and two abstracts
were inspected by R19; full-paper inspection in the summary belongs to root.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
REVIEW_SHA256 = "87c449917c9b2da5488e6eafc3cee4a591731ec5b717ba53a873df97d95d0bd6"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def text(element):
    return " ".join("".join(element.itertext()).split()) if element is not None else ""


def verify(cache):
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")
    review_bytes = (BASE/"RECENT_METHODS_REVIEW.json").read_bytes()
    require(hashlib.sha256(review_bytes).hexdigest() == REVIEW_SHA256,
            "Original recent-method review bytes changed")
    review = json.loads(review_bytes)
    files = ("PMC12184895.xml", "pubmed_search.json", "pubmed_candidates.xml",
             "horvitz_thompson_metadata.json")
    if cache is None or not all((cache/name).is_file() for name in files):
        return {"status": "UNRUN_recent_cached_sources_not_supplied",
                "R19_source_requests": 0}
    source = review["selected_primary"]
    data = (cache/files[0]).read_bytes()
    require(len(data) == source["bytes"] and
            hashlib.sha256(data).hexdigest() == source["sha256"], "Mito primary bytes changed")
    root = ET.fromstring(data)
    article = root if root.tag == "article" else root.find("article")
    require(article is not None, "Primary article missing")
    require(text(article.find("front/article-meta/title-group/article-title")).rstrip(".")
            == source["title"].rstrip("."), "Mito title metadata mismatch")
    for kind, value in source["front_identifiers_verified"].items():
        require(text(article.find('front/article-meta/article-id[@pub-id-type="'+kind+'"]'))
                == value, "Mito front identifier mismatch")
    permission = text(article.find("front/article-meta/permissions"))
    require("creativecommons.org/licenses/by/4.0/" in permission and
            "Creative Commons" in permission, "Mito article license missing")
    paragraphs = [text(x) for x in article.findall("body//p")]
    require(len(paragraphs) == 50 and source["paragraph_indices_are_one_based"] is True,
            "Mito paragraph count/indexing convention missing")
    for anchor in source["anchors"]:
        index = anchor["body_paragraph_index"] - 1
        require(hashlib.sha256(paragraphs[index].encode()).hexdigest() ==
                anchor["normalized_sha256"], "Mito normalized anchor mismatch")
    search = json.loads((cache/files[1]).read_bytes())["esearchresult"]
    require(search["count"] == "2" and
            set(search["idlist"]) == {"40549685", "38669515"},
            "Narrow two-hit search mismatch")
    candidates = ET.parse(cache/files[2]).getroot().findall("PubmedArticle")
    require(len(candidates) == 2, "Two candidate records required")
    expected = {source["pmid"]: source, review["secondary_abstract_only"]["pmid"]:
                review["secondary_abstract_only"]}
    for item in candidates:
        identifier = text(item.find("MedlineCitation/PMID"))
        require(identifier in expected, "Unexpected PubMed candidate")
        record = expected[identifier]
        require(text(item.find("MedlineCitation/Article/ArticleTitle")).rstrip(".")
                == record["title"].rstrip("."), "Candidate title mismatch")
        doi = text(item.find('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]'))
        require(doi == record["doi"] and
                bool(text(item.find("MedlineCitation/Article/Abstract"))),
                "Candidate DOI or abstract missing")
    ht = review["classical_sampling_reference"]
    ht_bytes = (cache/files[3]).read_bytes()
    require(len(ht_bytes) == ht["metadata_bytes"] and
            hashlib.sha256(ht_bytes).hexdigest() == ht["metadata_sha256"],
            "HT bibliography bytes mismatch")
    meta = json.loads(ht_bytes)["message"]
    require(meta["DOI"] == ht["doi"] and meta["title"][0] == ht["title"] and
            meta["issued"]["date-parts"][0][0] == ht["year"] and
            meta["container-title"][0] == ht["journal"] and
            meta["volume"] == ht["volume"] and meta["issue"] == ht["issue"] and
            meta["page"] == ht["pages"] and
            [x["family"] for x in meta["author"]] == ["Horvitz", "Thompson"],
            "HT bibliography metadata mismatch")
    total = sum((cache/name).stat().st_size for name in files)
    require(total == review["source_response_bytes"], "Root source-byte total mismatch")
    return {
        "status": "passed_independent_narrow_cached_recent_source_review",
        "R19_source_requests": 0, "root_source_requests": review["new_source_requests"],
        "root_response_bytes": total,
        "root_recent_review_sha256": REVIEW_SHA256,
        "Mito_primary_sha256": source["sha256"],
        "Mito_paragraph_anchors_verified_and_read": len(source["anchors"]),
        "Mito_paragraph_indices_one_based_subtract_one": True,
        "Brody_paragraph_indices_zero_based_separate_ledger": True,
        "two_PubMed_candidate_abstracts_read_and_metadata_checked": True,
        "HT_inspection": "Crossref bibliography only; primary text not read",
        "Mito_full_50_paragraph_inspection_claim_belongs_to_root_not_R19": True,
        "equations_code_simulations_or_raw_data_replayed": False,
        "actual_event_inclusion_parameter_or_TMD_panel_supplied": False,
        "raw_source_bodies_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--output", type=Path,
                        default=BASE/"SOURCE_REVIEW_RECEIPT.json")
    args = parser.parse_args()
    receipt = verify(args.cache_dir)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

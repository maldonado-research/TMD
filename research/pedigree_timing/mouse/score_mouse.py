"""Summarize evidence for sharing across distinct mouse offspring and litters."""
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LARGE = {"CBGP8", "GPCB2"}


def histogram(counter):
    return dict(sorted(counter.items()))


def summarize(rows):
    def count(predicate, weight="events"):
        return sum(r[weight] for r in rows if predicate(r))

    cross = Counter()
    lag = Counter()
    lag_no_tissue = Counter()
    spans = Counter()
    for r in rows:
        n = r["events"]
        shared = r["n_pups"] >= 2
        cross[("multiple_pups" if shared else "one_pup") +
              ("_parent_positive" if r["parent_mosaic"] else "_parent_no_signal")] += n
        if shared:
            wait = r["second_pup_litter"] - r["first_litter"]
            lag[wait] += n
            if not r["parent_mosaic"]:
                lag_no_tissue[wait] += n
            spans[r["last_litter"] - r["first_litter"]] += n
    always = lambda r: True
    return {
        "nucleotide_rows": count(always, "nucleotide_rows"),
        "events": count(always),
        "shared_nucleotide_rows": count(lambda r: r["n_pups"] >= 2, "nucleotide_rows"),
        "shared_nucleotide_rows_no_parental_signal": count(lambda r: r["n_pups"] >= 2 and not r["parent_mosaic"], "nucleotide_rows"),
        "shared_events_by_individuals": count(lambda r: r["n_pups"] >= 2),
        "shared_events_by_author_flag": count(lambda r: r["source_shared"]),
        "shared_events_by_author_numeric_column_at_least_two": count(lambda r: r["source_n_shared"] >= 2),
        "author_flag_disagrees_with_distinct_individuals": count(lambda r: bool(r["source_shared"]) != (r["n_pups"] >= 2)),
        "author_numeric_threshold_disagrees_with_distinct_individuals": count(lambda r: (r["source_n_shared"] >= 2) != (r["n_pups"] >= 2)),
        "events_with_two_distinct_sample_labels": count(lambda r: r["n_distinct_samples"] >= 2),
        "duplicate_sample_token_in_one_row_or_event": count(lambda r: r["n_sample_tokens"] != r["n_distinct_samples"]),
        "intersection_of_parental_tissue_and_sibling_evidence": dict(sorted(cross.items())),
        "second_distinct_pup_minus_first_litter": histogram(lag),
        "second_distinct_pup_minus_first_litter_no_parental_signal": histogram(lag_no_tissue),
        "last_minus_first_carrier_litter": histogram(spans),
    }


def score(path):
    with path.open(newline="") as f:
        rows = [dict(family=r["family"], **{k:int(v) for k,v in r.items() if k != "family"})
                for r in csv.DictReader(f, delimiter="\t")]
    for r in rows:
        r["nucleotide_rows"] = r["events"] * r["bases_in_event"]
        assert r["n_sample_tokens"] >= r["n_distinct_samples"] >= r["n_pups"] >= 1
        assert (r["n_pups"] == 1) == (r["second_pup_litter"] == 0)
        if r["n_pups"] >= 2:
            assert r["first_litter"] <= r["second_pup_litter"] <= r["last_litter"]
    main = [r for r in rows if r["family"] in LARGE]
    return {"native_sha256": "a8b69ab1c059f9bc341e22ed78119af9583db489789b7c814eb0196c6a8e1519",
            "table_sha256": sha256(path.read_bytes()).hexdigest(),
            "two_large_pedigrees": summarize(main),
            "two_large_pedigrees_single_nucleotide_events_only": summarize([r for r in main if r["bases_in_event"] == 1]),
            "large_pedigrees_individually": {fam:summarize([r for r in main if r["family"] == fam]) for fam in sorted(LARGE)},
            "other_four_pedigrees": summarize([r for r in rows if r["family"] not in LARGE]),
            "all_six_pedigrees": summarize(rows)}


if __name__ == "__main__":
    print(json.dumps(score(HERE/"litter_counts.tsv"), indent=2))

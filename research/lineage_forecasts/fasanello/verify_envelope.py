"""Score fixed anonymous forecasts against the observed day-25 libraries."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


LIBRARIES = ("original", "rerun")
VISITS = (0, 10, 25)


def read_counts(path):
    wells = defaultdict(dict)
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            well = row["population_id"]
            day = int(row["day"])
            if not well or day not in VISITS or day in wells[well]:
                raise ValueError(f"Invalid or duplicate well/visit: {well!r}, day {day}")
            counts = {}
            for library in LIBRARIES:
                a, b = (row[f"{library}_{label}"] for label in "AB")
                if a == b == "":
                    continue
                if not a or not b or min(int(a), int(b)) < 0:
                    raise ValueError(f"Invalid counts for {well}, day {day}, {library}")
                if int(a) + int(b) > 0:
                    counts[library] = (int(a), int(b))
            selected = row["selected"]
            if selected not in counts:
                raise ValueError(f"No usable selected counts for {well}, day {day}")
            wells[well][day] = (counts, selected)
    if not wells or any(set(visits) != set(VISITS) for visits in wells.values()):
        raise ValueError("Expected a nonempty table with days 0, 10 and 25 for each well")
    return wells


def unique_leader(scores, roster):
    maximum = max(scores[j] for j in roster)
    winners = [j for j in roster if scores[j] == maximum]
    return winners[0] if len(winners) == 1 else None


def score_well(well, visits):
    before = []
    for day in (0, 10):
        counts, selected = visits[day]
        before.append(counts[selected])
    p0, p10 = ([Fraction(n, sum(pair)) for n in pair] for pair in before)
    roster = [i for i in range(2) if before[0][i] + before[1][i] > 0]
    early = unique_leader(p10, roster)
    change = unique_leader([2 * y - x for x, y in zip(p0, p10)], roster)
    end_counts, selected = visits[25]
    if "original" not in end_counts:
        raise ValueError(f"The day-25 original is required for {well}")
    repeat = all("rerun" in visits[t][0] for t in VISITS)
    calls = {k: unique_leader(pair, (0, 1)) for k, pair in end_counts.items()}
    scores = {k: (int(t is not None and early == t), int(t is not None and change == t))
              for k, t in calls.items()}
    delta = {k: c - e for k, (e, c) in scores.items()}
    limits = {}
    for group, allow_rerun in (("complete", repeat), ("available", "rerun" in end_counts)):
        choices = list(delta.values()) if allow_rerun else [delta["original"]]
        limits[group] = (min(choices), max(choices))
    details = dict(population_id=well,
                   complete_repeat=int(repeat),
                   positive_rerun_endpoint=int("rerun" in end_counts),
                   predictions_disagree=int(early != change),
                   endpoints_disagree=int(calls["original"] != calls["rerun"]) if "rerun" in calls else "",
                   original_tie=int(calls["original"] is None),
                   rerun_tie=int(calls["rerun"] is None) if "rerun" in calls else "",
                   selected_endpoint_library=selected,
                   original_delta=delta["original"], rerun_delta=delta.get("rerun", ""),
                   selected_delta=delta[selected],
                   complete_repeat_choices_min=limits["complete"][0],
                   complete_repeat_choices_max=limits["complete"][1],
                   available_endpoint_choices_min=limits["available"][0],
                   available_endpoint_choices_max=limits["available"][1])
    return details, scores


def summarize(wells, rule):
    totals = {0}
    contributions = Counter()
    hits = {tag: [0, 0] for tag in ("original", "rerun_where_allowed", "archived")}
    for row, scores in wells:
        allow = row["complete_repeat"] if rule == "complete" else row["positive_rerun_endpoint"]
        libraries = ("original", "rerun") if allow else ("original",)
        options = sorted({scores[k][1] - scores[k][0] for k in libraries})
        contributions[tuple(options)] += 1
        totals = {a + b for a in totals for b in options}
        for tag, lib in (("original", "original"), ("rerun_where_allowed", libraries[-1]),
                         ("archived", row["selected_endpoint_library"])):
            e, c = scores[lib]
            hits[tag][0] += e
            hits[tag][1] += c
    return dict(wells=len(wells), attainable_delta=sorted(totals),
                well_contributions=[dict(options=list(op), wells=n)
                                    for op, n in sorted(contributions.items())],
                endpoint_choices={tag: dict(early=e, change=c, delta=c-e)
                                  for tag, (e, c) in hits.items()})


def note(summaries):
    lines = [
        "# Endpoint library sensitivity",
        "",
        "Each forecast uses the archived choices at days 0 and 10. The early forecast takes the day-10 leader. The change forecast ranks twice the day-10 fraction minus the day-0 fraction. Each uses the two anonymous labels detected by either forecast visit, or the single detected label if only one was observed. A forecast or endpoint tie earns zero strict hits. Zero-depth or absent rerun endpoints supply no alternate reading.",
        "",
        "Delta counts strict hits for change minus strict hits for early. Each well can contribute its delta from either allowed endpoint. The attainable totals are all sums obtained by choosing one allowed reading in each well. This allows arbitrary mixtures across wells. The original and rerun columns choose one library consistently in the eligible group. They retain original endpoints in other wells.",
        "When wells share a sequencing pool, assigning different libraries to those wells can produce a mixture that cannot result from a single pool-level choice.",
        "",
        "| Scope | Wells | Original delta | Rerun where allowed | Archive-selected delta | Attainable deltas |",
        "|---|---:|---:|---:|---:|---|",
    ]
    scopes = [
        ("complete_repeat_only", "Wells with complete repeat"),
        ("all_complete_repeat_choices", "All wells, vary complete repeats"),
        ("all_available_endpoint_choices", "All wells, vary usable endpoints"),
    ]
    for key, label in scopes:
        s = summaries[key]
        h = s["endpoint_choices"]
        deltas = ", ".join(str(x) for x in s["attainable_delta"])
        lines.append(f"| {label} | {s['wells']} | {h['original']['delta']} | "
                     f"{h['rerun_where_allowed']['delta']} | {h['archived']['delta']} | {deltas} |")
    total = summaries["all_available_endpoint_choices"]["wells"]
    complete = summaries["complete_repeat_only"]["wells"]
    lines += ["", f"{total - complete} wells lack a complete repeat at the three visits. "
              "The second row keeps their original endpoints. The third row also allows their positive-depth rerun endpoints. "
              "These results describe sensitivity to observed measurements. They assign no probability or ground-truth status to either library.", "",
              "Run from the directory containing this script and the normalized technical count table with "
              "`python3 verify_envelope.py technical_counts.tsv --out-dir results`. "
              "The JSON gives aggregate scores and all attainable deltas. The per-well TSV gives each library's delta and the minimum and maximum under each choice rule. An empty rerun field means that endpoint had no usable counts.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("counts", type=Path, help="Normalized technical_counts.tsv")
    parser.add_argument("--out-dir", type=Path, default=Path("."), help="Output directory (default: current directory)")
    args = parser.parse_args()
    raw = read_counts(args.counts)
    wells = [score_well(well, visits) for well, visits in sorted(raw.items())]
    complete = [pair for pair in wells if pair[0]["complete_repeat"]]
    summary = {
        "complete_repeat_only": summarize(complete, "complete"),
        "all_complete_repeat_choices": summarize(wells, "complete"),
        "all_available_endpoint_choices": summarize(wells, "available"),
    }
    data = {"input_sha256": hashlib.sha256(args.counts.read_bytes()).hexdigest(),
            "delta_definition": "change strict hits minus early strict hits", "scopes": summary}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with (args.out_dir / "endpoint_envelope_wells.tsv").open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(wells[0][0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(details for details, _ in wells)
    (args.out_dir / "endpoint_envelope.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "endpoint_envelope.md").write_text(note(summary), encoding="utf-8")


if __name__ == "__main__":
    main()

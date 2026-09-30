"""TMD 0.1: context-stratified route/time diagnostic (standard library only).

Copyright (c) 2026 Ricardo Maldonado. MIT License.
This is a statistical diagnostic, not a biological validation certificate.
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED = {"replicate_id", "context", "time", "event", "route", "provenance"}


def validate_rows(rows, routes):
    if (not isinstance(routes, (list, tuple)) or not routes
            or any(not isinstance(r, str) or not r or r != r.strip() for r in routes)
            or len(routes) != len(set(routes))):
        raise ValueError("Routes must be a nonempty unique list of predefined labels")
    seen, clean = set(), []
    for line, row in enumerate(rows, 2):
        if not isinstance(row, dict) or None in row:
            raise ValueError("Line %d: malformed record or surplus CSV cells" % line)
        if not REQUIRED.issubset(row):
            raise ValueError("Required columns: " + ", ".join(sorted(REQUIRED)))
        if any(value is None for value in row.values()):
            raise ValueError("Line %d: missing CSV cell" % line)
        for key in ("replicate_id", "context", "route", "provenance"):
            if not isinstance(row[key], str):
                raise ValueError("Line %d: %s must be a text cell" % (line, key))
        rid, context = row["replicate_id"].strip(), row["context"].strip()
        if not rid or not context or rid in seen:
            raise ValueError("Line %d: missing context or nonunique global replicate identifier" % line)
        seen.add(rid)
        try:
            t = float(row["time"])
        except (TypeError, ValueError, OverflowError):
            raise ValueError("Line %d: time must be a numeric cell" % line) from None
        if not math.isfinite(t) or t <= 0:
            raise ValueError("Line %d: time must be finite and > 0" % line)
        if "entry_time" in row:
            try:
                entry = float(row["entry_time"])
            except (TypeError, ValueError, OverflowError):
                raise ValueError("Line %d: entry_time must be numeric zero" % line) from None
            if not math.isfinite(entry) or entry != 0:
                raise ValueError("Line %d: delayed entry is unsupported; entry_time must be zero" % line)
        if "observation_type" in row and row["observation_type"] != "first_successful_arrival":
            raise ValueError("Line %d: unsupported observation_type; use first_successful_arrival" % line)
        if "cluster_id" in row:
            if not isinstance(row["cluster_id"], str) or row["cluster_id"].strip():
                raise ValueError("Line %d: clustered records are unsupported; cluster_id must be blank" % line)
        if str(row["event"]) not in {"0", "1"}:
            raise ValueError("Line %d: event must be 0 (right censored) or 1" % line)
        event, route = int(row["event"]), row["route"].strip()
        if event and route not in routes:
            raise ValueError("Line %d: event route is not predefined" % line)
        if not event and route:
            raise ValueError("Line %d: censored records must have an empty route" % line)
        provenance = row["provenance"].strip()
        if provenance not in {"synthetic", "observed", "literature_transcription"}:
            raise ValueError("Line %d: explicit provenance category required" % line)
        clean.append(dict(replicate_id=rid, context=context, time=t,
                          event=event, route=route, provenance=provenance))
    if not clean:
        raise ValueError("No replicate records")
    return clean


def validate_cuts(cuts):
    if any(not math.isfinite(t) or t <= 0 for t in cuts):
        raise ValueError("Bin cuts must be finite and positive")
    if list(cuts) != sorted(set(cuts)):
        raise ValueError("Bin cuts must be strictly increasing")


def contingency_deviance(table):
    """2*n*I(bin; route), natural logarithms, zero cells contribute zero."""
    if not table or any(len(r) != len(table[0]) for r in table):
        raise ValueError("Expected a rectangular table")
    if any(v < 0 or not isinstance(v, int) for row in table for v in row):
        raise ValueError("Expected nonnegative integer event counts")
    margins_b = [sum(r) for r in table]
    margins_i = [sum(r[i] for r in table) for i in range(len(table[0]))]
    n = sum(margins_b)
    if not n:
        return 0.0
    d = 2 * sum(v * math.log(v * n / (margins_b[b] * margins_i[i]))
                for b, row in enumerate(table) for i, v in enumerate(row) if v)
    return max(0.0, d)


def make_tables(rows, routes, cuts):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["context"]].append(row)
    tables, exposures, event_bins, event_routes = {}, {}, {}, {}
    ri = {r: i for i, r in enumerate(routes)}
    for context in sorted(grouped):
        table = [[0] * len(routes) for _ in range(len(cuts) + 1)]
        exposure = [0.0] * len(table)
        bins, labels = [], []
        for row in grouped[context]:
            t = row["time"]
            for b in range(len(table)):
                left = 0 if b == 0 else cuts[b - 1]
                right = cuts[b] if b < len(cuts) else t
                exposure[b] += max(0.0, min(t, right) - left)
            if row["event"]:
                b, i = bisect.bisect_left(cuts, t), ri[row["route"]]
                table[b][i] += 1
                bins.append(b)
                labels.append(i)
        tables[context], exposures[context] = table, exposure
        event_bins[context], event_routes[context] = bins, labels
    return tables, exposures, event_bins, event_routes


def aalen_johansen(rows, routes):
    """Descriptive cumulative incidence, events precede censoring at tied times."""
    risk, survival = len(rows), 1.0
    incidence = {r: 0.0 for r in routes}
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["time"]].append(row)
    result = []
    for t, batch in sorted(grouped.items()):
        deaths = Counter(r["route"] for r in batch if r["event"])
        censored = sum(1 - r["event"] for r in batch)
        for route in routes:
            incidence[route] += survival * deaths[route] / risk
        survival *= 1 - sum(deaths.values()) / risk
        result.append(dict(time=t, at_risk=risk, events=dict(deaths),
                           censored=censored, survival=survival,
                           cumulative_incidence=incidence.copy()))
        risk -= len(batch)
    return result


def analyze(rows, routes, cuts, permutations=1999, seed=20260930):
    rows = validate_rows(rows, routes)
    validate_cuts(cuts)
    if not isinstance(permutations, int) or permutations < 1:
        raise ValueError("At least one Monte Carlo permutation required")
    tables, exposures, bins, labels = make_tables(rows, routes, cuts)
    contexts, stat, informative = {}, 0.0, 0
    for c in tables:
        tab, exp = tables[c], exposures[c]
        n = sum(map(sum, tab))
        route_counts = [sum(r[i] for r in tab) for i in range(len(routes))]
        d = contingency_deviance(tab)
        info = sum(sum(r) > 0 for r in tab) >= 2 and sum(v > 0 for v in route_counts) >= 2
        informative += int(info)
        stat += d
        p = [v / n for v in route_counts] if n else [None] * len(routes)
        hazards = []
        for b, counts in enumerate(tab):
            a = sum(counts) / exp[b] if exp[b] else None
            hazards.append(dict(bin=b, exposure=exp[b], event_counts=dict(zip(routes, counts)),
                                free_hazards={r: counts[i] / exp[b] if exp[b] else None
                                              for i, r in enumerate(routes)},
                                common_clock_hazards={r: a * p[i] if a is not None and p[i] is not None else None
                                                      for i, r in enumerate(routes)}))
        contexts[c] = dict(replicates=sum(r["context"] == c for r in rows), events=n,
                           informative=info, deviance=d,
                           observed_event_proportions=dict(zip(routes, p)),
                           common_clock_route_estimates=dict(zip(routes, p)),
                           route_time_mi_nats=d / (2 * n) if n else None,
                           hazards=hazards,
                           cumulative_incidence=aalen_johansen([r for r in rows if r["context"] == c], routes))
    tail, pvalue = None, None
    if informative:
        rng, tail = random.Random(seed), 0
        for _ in range(permutations):
            perm_stat = 0.0
            for c in tables:
                permuted = labels[c].copy()
                rng.shuffle(permuted)
                table = [[0] * len(routes) for _ in range(len(cuts) + 1)]
                for b, i in zip(bins[c], permuted):
                    table[b][i] += 1
                perm_stat += contingency_deviance(table)
            tail += perm_stat >= stat - 1e-12
        pvalue = (tail + 1) / (permutations + 1)
    origins = sorted({r["provenance"] for r in rows})
    mixed_provenance = len(origins) > 1
    evidence_kind = ("mixed_provenance_requires_separate_evidence_review" if mixed_provenance
                     else "synthetic" if origins == ["synthetic"]
                     else "literature_transcription_not_authenticated" if origins == ["literature_transcription"]
                     else "user_declared_observations_not_authenticated")
    return dict(schema_version="0.1", analysis="common_clock_route_time_diagnostic",
                evidence_kind=evidence_kind, mixed_provenance=mixed_provenance,
                provenance_warning=("Mixed provenance is not a homogeneous empirical evidence sample; "
                                    "review and analyze evidence categories separately before interpretation."
                                    if mixed_provenance else None),
                input_provenance=origins, route_order=routes, bin_cuts=cuts,
                bin_convention="(left,right]; last bin extends to observed follow-up",
                contexts=contexts, informative_contexts=informative,
                statistic_deviance=stat, conditional_permutation_p=pvalue,
                monte_carlo_permutations=permutations if informative else 0,
                permutations_at_least_observed=tail, seed=seed,
                approximate_monte_carlo_se=math.sqrt(pvalue * (1 - pvalue) / (permutations + 1)) if pvalue is not None else None,
                interpretation="Tests route fractions constant across prespecified time bins within context; does not identify mutation, accessibility, establishment or frailty mechanism.",
                route_estimates_interpretation="Observed event proportions describe recorded events during follow-up; the same values estimate route shares only under the common-clock model and its censoring assumptions.",
                assumptions=["Exact first successful-arrival times, not endpoint dominance or detection times",
                             "Independent replicate units across all records, including different contexts; no unmodeled shared culture or batch",
                             "Censoring independent of both time and route given context",
                             "Route labels exhaustive, ascertainment route independent, no delayed entry",
                             "Cuts and tested contexts/routes fixed before outcome inspection",
                             "Nonrejection is not proof; binning can miss within-bin changes"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--routes", required=True, help="Comma-separated predefined route labels")
    parser.add_argument("--cuts", required=True, help="Comma-separated positive time cuts")
    parser.add_argument("--time-unit", required=True)
    parser.add_argument("--cuts-plan", required=True, help="Prespecified rationale or registration; synthetic design for simulations")
    parser.add_argument("--event-definition", choices=["first_successful_arrival"], required=True)
    parser.add_argument("--independent-replicates", action="store_true", required=True)
    parser.add_argument("--independent-censoring", action="store_true", required=True)
    parser.add_argument("--permutations", type=int, default=1999)
    parser.add_argument("--seed", type=int, default=20260930)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        raw = Path(args.csv).read_bytes()
        with Path(args.csv).open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, strict=True)
            names = reader.fieldnames
            if (not names or any(not name for name in names)
                    or len(names) != len(set(names))):
                raise ValueError("CSV header names must be nonempty and unique")
            rows = list(reader)
        result = analyze(rows, args.routes.split(","), [float(x) for x in args.cuts.split(",")], args.permutations, args.seed)
    except (ValueError, TypeError, KeyError, OSError, UnicodeError, csv.Error) as exc:
        parser.error(str(exc))
    result.update(input_sha256=hashlib.sha256(raw).hexdigest(), time_unit=args.time_unit,
                  cuts_plan=args.cuts_plan, event_definition=args.event_definition,
                  declared_assumptions_are_not_independently_verified=True)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["statistic_deviance", "conditional_permutation_p", "evidence_kind"]}))


if __name__ == "__main__":
    main()

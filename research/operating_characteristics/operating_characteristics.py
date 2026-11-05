#!/usr/bin/env python3
"""Synthetic finite operating characteristics of unchanged TMD implementations.

All artifacts are exploratory design diagnostics, not biological power, a
registered study, or guaranteed detection. Standard library only. Reads frozen
repository files; writes only the specified output directory outside the repo.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import random
import runpy
import time

NAMES = ("supply_observation", "supply_establishment_observation", "flexible")
EXCLUDED = ("Other", "no_qualified_outcome", "unresolved_classification", "missing")
SCENARIOS = {
    "conventional_equal": {"family": "conventional", "training_A": [F(1,4)]*4, "target_A": [F(1,4)]*2},
    "conventional_weak": {"family": "conventional", "training_A": [F(9,40),F(11,40),F(11,40),F(9,40)], "target_A": [F(9,40),F(11,40)]},
    "conventional_strong": {"family": "conventional", "training_A": [F(1,10),F(3,10),F(1,2),F(4,5)], "target_A": [F(1,10),F(4,5)]},
    "common_weak": {"family": "common", "exp_theta": F(3,2), "training_A": [F(1,10),F(3,10),F(1,2),F(4,5)], "target_A": [F(1,10),F(4,5)]},
    "common_strong": {"family": "common", "exp_theta": F(3), "training_A": [F(1,10),F(3,10),F(1,2),F(4,5)], "target_A": [F(1,10),F(4,5)]},
}


def normalize(values):
    return tuple(v / sum(values) for v in values)


def stream(*parts):
    raw = json.dumps(parts, separators=(",", ":")).encode()
    return random.Random(int.from_bytes(hashlib.sha256(raw).digest(), "big"))


def categorical(rng, n, probabilities):
    """Integer-threshold rational sampler (no floating law approximation)."""
    denominator = math.lcm(*(p.denominator for p in probabilities))
    weights = [int(p*denominator) for p in probabilities]
    assert sum(weights) == denominator
    cumulative, running = [], 0
    for w in weights:
        running += w
        cumulative.append(running)
    counts = [0]*len(weights)
    for _ in range(n):
        draw = rng.randrange(denominator)
        for j, threshold in enumerate(cumulative):
            if draw < threshold:
                counts[j] += 1
                break
    return counts


def control(rng, n, p):
    return [categorical(rng, n, (p,1-p))[0], n]


def assays(rng, n, establishment):
    return {
        "baseline_counts": categorical(rng,n,(F(1,3),)*3),
        "recovery_baseline": [control(rng,n,F(3,4)) for _ in range(3)],
        "recovery_selected": [control(rng,n,F(3,4)) for _ in range(3)],
        "establishment": [control(rng,n,p) for p in establishment],
    }


def endpoint_law(scenario, r, a):
    establishment = (r/4,a,F(1,4)/r)
    if scenario["family"] == "conventional":
        return establishment, normalize(establishment)
    return establishment, normalize((r, scenario["exp_theta"], 1/r))


def endpoint_frame(rng, n, p):
    outcomes = categorical(rng,n,tuple(F(4,5)*v for v in p)+(F(1,10),F(1,20),F(1,40),F(1,40)))
    return {"counts":outcomes[:3],"excluded_ledger":dict(zip(EXCLUDED,outcomes[3:]))}


def rational_forecast(p):
    """Define actual frozen dyadic vectors; no claim of ideal-real certification.

    Normalize the exact rational representations of the supplied floats, then
    use largest remainder on denominator 2**40. The rounding changes each
    normalized coordinate by less than 2**-40. No clipping. Nonpositive
    rounding blocks the repeat.
    """
    denominator = 1 << 40
    exact = [F.from_float(v) for v in p]
    exact = normalize(exact)
    scaled = [v*denominator for v in exact]
    numerators = [v.numerator//v.denominator for v in scaled]
    residual = denominator-sum(numerators)
    for j in sorted(range(3),key=lambda j:(scaled[j]-numerators[j],-j),reverse=True)[:residual]:
        numerators[j] += 1
    assert all(v > 0 for v in numerators)
    return [str(F(v,denominator)) for v in numerators]


def assumptions(n):
    return {
        "independent_founder_units":True,
        "iid_conditional_multinomial_marginals_justified":True,
        "independent_training_and_calibration":True,
        "forecasts_weights_gates_precision_frozen":True,
        "fixed_stopping_no_interim_looks":True,
        "other_exclusion_and_missingness_rule_frozen":True,
        "complete_endpoint_ledger":True,
        "clusters_not_counted_as_independent_descendants":True,
        "count_law_justification":"Synthetic IID rational categorical full-frame law; conditional W/A/M law is multinomial given its total. Stage-specific deterministic pseudorandom streams represent independent sampling.",
        "founder_unit_definition":"One independently simulated categorical unit; no biological data.",
        "sampling_and_conditioning_rule":"Fixed full frame; retain all seven categories, condition scores on qualifying W/A/M. Zero qualifying contexts are unevaluable and retained in simulation denominators.",
        "freeze_reference":"Synthetic plan constructed and hashed after independent training/calibration and before endpoint draws. Contexts fixed in advance; no context screening or selection is performed.",
        "fixed_stopping_rule":f"Exactly {n} full-frame units per heldout context; one analysis; no interim looks.",
    }


def one_repeat(design, engine, seed, scenario_name, calibration_n, full_n, repeat):
    scenario = SCENARIOS[scenario_name]
    key=(seed,scenario_name,calibration_n,full_n,repeat)
    training=[]
    training_ledgers=[]
    for j,r in enumerate((F(1,2),F(4,5),F(5,4),F(2))):
        establishment,truth=endpoint_law(scenario,r,scenario["training_A"][j])
        row=assays(stream(*key,"training_controls",j),calibration_n,establishment)
        frame=endpoint_frame(stream(*key,"training_outcomes",j),320,truth)
        if sum(frame["counts"]) == 0:
            return {"decision":"unevaluable_training_zero_qualifying"}
        row["selected_counts"]=frame["counts"]
        training.append(row)
        training_ledgers.append(frame)
    contexts,truths,predictions,targets=[],[],[],[]
    for j in range(2):
        establishment,truth=endpoint_law(scenario,F(1),scenario["target_A"][j])
        target=assays(stream(*key,"target_controls",j),calibration_n,establishment)
        prediction=design["build_predictors"](training,target)
        probabilities=prediction["probabilities"]
        contexts.append({"id":f"c{j}","weight":"1/2","fixed_total_units":full_n,
            "tmd":rational_forecast(probabilities["restricted"]),
            "comparators":{name:rational_forecast(probabilities[name]) for name in NAMES}})
        predictions.append(prediction)
        targets.append(target)
        truths.append(truth)
    plan={"alpha":"1/20","cp_bisection_bits":24,"log_terms":24,"log_fraction_bits":56,
        "report_fraction_bits":48,"comparator_names":list(NAMES),"contexts":contexts,
        "gates":{"success_threshold":"0","failure_mode":"any_upper_lt_threshold","failure_threshold":"0"}}
    frozen_hash=engine["plan_sha256"](plan)
    # All choices above precede heldout endpoints. No outcome-dependent tuning.
    outcomes={f"c{j}":endpoint_frame(stream(*key,"heldout_outcomes",j),full_n,truths[j]) for j in range(2)}
    doc={"schema_version":1,"scope":engine["SCOPE"],"provenance":"synthetic",
        "route_order":["W","A","M"],"assumptions":assumptions(full_n),"plan":plan,
        "expected_plan_sha256":frozen_hash,"outcomes":outcomes}
    parsed=engine["validate_plan"](plan)
    coefficients=engine["coefficient_table"](parsed)
    truth_bounds={name:[sum(F(1,2)*truths[j][i]*coefficients[f"c{j}"][name][i][side]
        for j in range(2) for i in range(3)) for side in (0,1)] for name in NAMES}
    forecast_only_gain_ceilings={name:sum(F(1,2)*max(coefficients[f"c{j}"][name][i][1] for i in range(3))
        for j in range(2)) for name in NAMES}
    summary={"truth_gain_midpoints":{name:float((v[0]+v[1])/2) for name,v in truth_bounds.items()},
        "forecast_only_upper_gain_bounds":{name:float(v) for name,v in forecast_only_gain_ceilings.items()},
        "all_comparator_001_margin_impossible_before_outcomes":any(v <= F(1,100) for v in forecast_only_gain_ceilings.values()),
        "all_comparator_005_margin_impossible_before_outcomes":any(v <= F(1,20) for v in forecast_only_gain_ceilings.values()),
        "truth_all_positive":all(v[0] > 0 for v in truth_bounds.values()),
        "truth_any_negative":any(v[1] < 0 for v in truth_bounds.values()),
        "qualifying_totals":[sum(outcomes[f"c{j}"]["counts"]) for j in range(2)],
        "excluded_totals":{name:sum(outcomes[f"c{j}"]["excluded_ledger"][name] for j in range(2)) for name in EXCLUDED}}
    if any(n == 0 for n in summary["qualifying_totals"]):
        summary["decision"]="unevaluable_endpoint_zero_qualifying"
        return summary
    result=engine["analyze"](doc)
    assert frozen_hash == engine["plan_sha256"](plan)
    bounds={name:[F(v) for v in result["weighted_score_intervals_exact"][name]] for name in NAMES}
    summary.update({"decision":result["decision"],
        "individual_positive_certificate":{name:v[0] > 0 for name,v in bounds.items()},
        "individual_negative_certificate":{name:v[1] < 0 for name,v in bounds.items()},
        "false_certificate_proved":False,"certificate_truth_numerically_unresolved":False})
    if result["decision"].startswith("certified_success"):
        summary["false_certificate_proved"]=any(v[1] <= 0 for v in truth_bounds.values())
        summary["certificate_truth_numerically_unresolved"]=not summary["truth_all_positive"] and not summary["false_certificate_proved"]
    if result["decision"].startswith("certified_failure"):
        summary["false_certificate_proved"]=all(v[0] >= 0 for v in truth_bounds.values())
        summary["certificate_truth_numerically_unresolved"]=not summary["truth_any_negative"] and not summary["false_certificate_proved"]
    summary["simultaneous_region_covers_truth"]=all(F(context["probability_box_exact"][i][0]) <= truths[j][i] <= F(context["probability_box_exact"][i][1])
        for j,context in enumerate(result["contexts"]) for i in range(3))
    artifact={"training":training,"training_endpoint_ledgers":training_ledgers,"target_controls":targets,
        "builder_predictions":predictions,"truths_exact":[list(map(str,p)) for p in truths],
        "truth_gain_bounds_exact":{name:list(map(str,v)) for name,v in truth_bounds.items()},
        "forecast_only_gain_upper_bounds_exact":{name:str(v) for name,v in forecast_only_gain_ceilings.items()},
        "score_input":doc,"score_result":result}
    return summary,artifact


def summarize(engine, records):
    count=len(records)
    decisions=Counter(row["decision"] for row in records)
    def rate(k):
        lo,hi,*_=engine["cp_interval"](count,k,F(1,40),32)
        return {"count":k,"fraction":k/count,"monte_carlo_95pct_CP_interval":[float(lo),float(hi)]}
    fitted=[row for row in records if "truth_gain_midpoints" in row]
    means={name:(sum(row["truth_gain_midpoints"][name] for row in fitted)/len(fitted) if fitted else None) for name in NAMES}
    for name in ("certified_success_at_declared_score_gate","certified_failure_at_declared_score_gate",
                 "inconclusive_at_declared_score_gate","unevaluable_training_zero_qualifying",
                 "unevaluable_endpoint_zero_qualifying"):
        decisions.setdefault(name,0)
    return {"repetitions":count,"decisions":{name:rate(k) for name,k in sorted(decisions.items())},
        "repeats_with_fitted_forecasts":len(fitted),
        "truth_gain_mean_nats":means,
        "all_comparator_001_margin_impossible_before_outcomes":rate(sum(row.get("all_comparator_001_margin_impossible_before_outcomes",False) for row in records)),
        "all_comparator_005_margin_impossible_before_outcomes":rate(sum(row.get("all_comparator_005_margin_impossible_before_outcomes",False) for row in records)),
        "truth_all_comparator_gains_positive":rate(sum(row.get("truth_all_positive",False) for row in records)),
        "individual_positive_certificates":{name:rate(sum(row.get("individual_positive_certificate",{}).get(name,False) for row in records)) for name in NAMES},
        "individual_negative_certificates":{name:rate(sum(row.get("individual_negative_certificate",{}).get(name,False) for row in records)) for name in NAMES},
        "false_certificates_proved":rate(sum(row.get("false_certificate_proved",False) for row in records)),
        "certificate_truth_numerically_unresolved":sum(row.get("certificate_truth_numerically_unresolved",False) for row in records),
        "simultaneous_outcome_region_misses_truth":rate(sum(row.get("simultaneous_region_covers_truth",True) is False for row in records)),
        "mean_qualifying_totals":[sum(row.get("qualifying_totals",[0,0])[j] for row in records)/count for j in range(2)],
        "excluded_totals":{name:sum(row.get("excluded_totals",{}).get(name,0) for row in records) for name in EXCLUDED}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,required=True,help="Existing TMD repository; read only")
    parser.add_argument("--output",type=Path,required=True,help="Result JSON in an existing directory outside the repository")
    parser.add_argument("--replicates",type=int,default=32)
    parser.add_argument("--seed",type=int,default=20261105)
    parser.add_argument("--scenarios",nargs="*",choices=list(SCENARIOS),default=list(SCENARIOS))
    parser.add_argument("--calibration-counts",nargs="*",type=int,default=[30,300])
    parser.add_argument("--endpoint-counts",nargs="*",type=int,default=[80,400])
    args=parser.parse_args()
    assert 1 <= args.replicates <= 500
    assert all(n>0 for n in args.calibration_counts)
    assert all(1<=n<=500 for n in args.endpoint_counts)
    assert not args.output.resolve().is_relative_to(args.repo.resolve())
    protected=[args.repo/"research/prospective_design/verify_design.py",
        args.repo/"research/prospective_design/REGISTRY_CANDIDATE.json",
        args.repo/"research/certified_score/certified_score.py"]
    hashes={str(p.relative_to(args.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    design=runpy.run_path(str(protected[0]),run_name="frozen_builder")
    engine=runpy.run_path(str(protected[2]),run_name="frozen_score")
    cells=[]
    start=time.monotonic()
    for scenario in args.scenarios:
        for calibration in args.calibration_counts:
            for endpoint in args.endpoint_counts:
                records=[]
                for repeat in range(args.replicates):
                    result=one_repeat(design,engine,args.seed,scenario,calibration,endpoint,repeat)
                    if isinstance(result,tuple):
                        summary,artifact=result
                        if repeat==0:
                            sample=args.output.parent/f"example_{scenario}_cal{calibration}_N{endpoint}.json"
                            sample.write_text(json.dumps(artifact,indent=2,sort_keys=True)+"\n")
                    else:
                        summary=result
                    records.append(summary)
                cell={"scenario":scenario,"calibration_trials_per_arm":calibration,
                    "baseline_trials_per_context":calibration,"training_full_frame_per_context":320,
                    "heldout_full_frame_per_context":endpoint,"summary":summarize(engine,records),"records":records}
                cells.append(cell)
                print(json.dumps({"completed":len(cells),"scenario":scenario,"calibration":calibration,"endpoint":endpoint,
                    "decisions":cell["summary"]["decisions"],"seconds":round(time.monotonic()-start,2)}),flush=True)
    after={str(p.relative_to(args.repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert hashes==after
    report={"status":"finite_synthetic_operating_characteristic_diagnostic","seed":args.seed,
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "frozen_source_hashes_before_and_after":hashes,"source_files_unchanged":True,
        "configuration":{"replicates_per_cell":args.replicates,"calibration_counts":args.calibration_counts,
            "endpoint_counts":args.endpoint_counts,"training_contexts":4,"heldout_contexts":2,
            "training_full_frame_per_context":320,"exp_x_training_exact":["1/2","4/5","5/4","2"],
            "exp_x_heldout_exact":["1","1"],"baseline_law_exact":["1/3"]*3,
            "binary_recovery_control_probability_exact":"3/4","qualifying_probability_exact":"4/5",
            "excluded_probabilities_exact":dict(zip(EXCLUDED,["1/10","1/20","1/40","1/40"])),
            "score_alpha_exact":"1/20","success_threshold_exact":"0","failure_threshold_exact":"0",
            "context_weights_exact":["1/2","1/2"],"cp_bisection_bits":24,"log_terms":24,
            "log_fraction_bits":56,"report_fraction_bits":48,"forecast_denominator":2**40,
            "candidate_screening":"none; fixed contexts", "score_calls_per_complete_study":1},
        "scenario_specs":{name:{k:([str(x) for x in v] if isinstance(v,list) else str(v)) for k,v in SCENARIOS[name].items()} for name in args.scenarios},
        "scope":"No biology, registry values, screening, algorithm modification, publication, or guaranteed power. Actual frozen builder + actual certified score on independently simulated stages. Monte Carlo intervals are marginal 95% each, not simultaneous across reported cells. Recovery controls and full endpoint laws are separately stipulated operational laws, not an absolute biological recovery map.",
        "cells":cells}
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    main()

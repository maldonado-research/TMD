"""Replay exact SYNTHETIC caller-capture fixtures to an external output path."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
from caller_capture import caller_summary, independent_law, marginal_bounds


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encoded(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [encoded(item) for item in value]
    return value


def benchmarks():
    if not __debug__:
        raise RuntimeError("Verification requires ordinary Python without -O/-OO")
    checks = {}
    def check(condition, category):
        if not condition:
            raise ValueError("Synthetic caller-capture check failed: "+category)
        checks[category] = checks.get(category, 0)+1
    fixtures = [
        ("empty_known_frame", (), (), (), 1, 0, F(0), F(0)),
        ("singleton", (F(1,3),), (0,), (), 1, 0, F(1,3), F(1,3)),
        ("OR_two_half", (F(1,2),)*2, (0,1), (), 1, 0, F(1,2), F(1)),
        ("both_half", (F(1,2),)*2, (0,1), (), 2, 0, F(0), F(1,2)),
        ("two_plus_reference", (F(1,2),)*3, (0,1), (2,), 2, 1, F(0), F(1,2)),
        ("OR_plus_reference", (F(1,2),)*3, (0,1), (2,), 1, 1, F(0), F(1,2)),
        ("two_of_three", (F(1,2),)*3, (0,1,2), (), 2, 0, F(1,4), F(3,4)),
        ("unequal_conjunction", (F(1,4),F(1,2),F(3,4)), (0,1), (2,), 2, 1, F(0), F(1,4)),
        ("two_groups_OR", (F(1,2),)*4, (0,1), (2,3), 1, 1, F(0), F(1)),
        ("two_carrier_any_reference", (F(1,2),)*4, (0,1), (2,3), 2, 1, F(0), F(1,2)),
        ("all_four", (F(1,2),)*4, (0,1), (2,3), 2, 2, F(0), F(1,2)),
        ("unused_descendants", (F(1,4),F(0),F(1),F(2,3)), (0,), (), 1, 0, F(1,4), F(1,4)),
        ("impossible_carrier_threshold", (F(1),)*3, (0,1), (2,), 3, 1, F(0), F(0)),
        ("impossible_reference_threshold", (F(1),)*3, (0,1), (2,), 1, 2, F(0), F(0)),
    ]
    outputs = []
    for name, marginals, carriers, references, k, r, lower, upper in fixtures:
        out = marginal_bounds(marginals, carriers, references, k, r)
        check(out["lower"] == lower and out["upper"] == upper, "closed_form_or_explicit_fixture_endpoints")
        check(out["lower"] <= out["value_if_independent"] <= out["upper"], "independence_within_sharp_bounds")
        for endpoint in ("lower", "upper"):
            law = out[endpoint+"_law"]
            check(sum(law.values(), F()) == 1 and all(value > 0 for value in law.values()), "witness_normalization")
            actual_marginals = tuple(sum((weight for mask, weight in law.items() if (mask >> j) & 1), F()) for j in range(len(marginals)))
            check(actual_marginals == marginals, "direct_witness_marginals")
            probability = sum((weight for mask, weight in law.items() if
                               sum((mask >> j) & 1 for j in carriers) >= k and
                               sum((mask >> j) & 1 for j in references) >= r), F())
            check(probability == out[endpoint], "direct_witness_predicate_endpoints")
            summary = caller_summary(len(marginals), law, carriers, references, k, r)
            check(summary["inclusion_probability"] == probability, "full_law_summary_vs_direct_witness")
        outputs.append({"name": name, "marginals": marginals, "carriers": carriers,
                        "references": references, "k": k, "r": r, "bounds": out})
    witnesses = {}
    for frame, law in {"common": {0:F(1,2),3:F(1,2)}, "independent": {mask:F(1,4) for mask in range(4)},
                       "exclusive": {1:F(1,2),2:F(1,2)}}.items():
        both = caller_summary(2, law, (0,1), (), 2, 0)
        probability = {"common":F(1,2),"independent":F(1,4),"exclusive":F(0)}[frame]
        check(both["descendant_call_marginals"] == (F(1,2),)*2 and both["inclusion_probability"] == probability,
              "same_marginal_two_support_counterexamples")
        expanded = {mask | (reference << 2): weight*F(1,2) for mask, weight in law.items() for reference in (0,1)}
        with_reference = caller_summary(3, expanded, (0,1), (2,), 2, 1)
        check(with_reference["inclusion_probability"] == probability/2, "explicit_independent_reference_special_case")
        witnesses[frame] = {"carrier_law":law,"both_support":both,"independent_reference_law":expanded,
                            "both_support_and_reference":with_reference}
    reference_dependence = {}
    for frame, law, probability in [
        ("reference_matches_carrier_pair", {0:F(1,2),7:F(1,2)}, F(1,2)),
        ("reference_opposes_carrier_pair", {3:F(1,2),4:F(1,2)}, F(0))]:
        summary = caller_summary(3, law, (0,1), (2,), 2, 1)
        projected = {mask: sum((value for full, value in law.items() if full & 3 == mask), F()) for mask in (0,3)}
        check(projected == {0:F(1,2),3:F(1,2)}, "fixed_full_carrier_law_reference_dependence")
        check(summary["descendant_call_marginals"] == (F(1,2),)*3, "fixed_reference_marginal_dependence")
        check(summary["inclusion_probability"] == probability, "reference_joint_law_changes_inclusion")
        reference_dependence[frame] = {"law":law,"summary":summary}
    eight = caller_summary(8, {255:1}, (0,1,2,3), (4,5,6,7), 4, 4)
    check(eight["inclusion_probability"] == 1 and eight["expected_carrier_call_copies"] == 4 and
          eight["expected_reference_calls"] == 4, "maximum_full_law_dimension")
    impossible = caller_summary(3, {7:1}, (0,1), (2,), 3, 1)
    check(impossible["structural_zero"] and impossible["inclusion_probability"] == 0 and
          impossible["expected_carrier_call_copies"] == 2, "structural_zero_despite_true_calls")
    boundary = marginal_bounds((F(1,2**31),F(2**31-1,2**31)), (0,1), (), 2, 0)
    check(boundary["lower"] == 0 and boundary["upper"] == F(1,2**31), "valid_32bit_rational_boundary")
    invalid = [
        lambda: caller_summary(True,{0:1},(),(),1,0), lambda: caller_summary(9,{0:1},(),(),1,0),
        lambda: caller_summary(1,{},(0,),(),1,0), lambda: caller_summary(1,{0:F(1,2)},(0,),(),1,0),
        lambda: caller_summary(1,{0:2,1:-1},(0,),(),1,0), lambda: caller_summary(1,{2:1},(0,),(),1,0),
        lambda: caller_summary(1,{True:1},(0,),(),1,0), lambda: caller_summary(1,{0:True},(0,),(),1,0),
        lambda: caller_summary(1,{0:1.0},(0,),(),1,0), lambda: caller_summary(1,{0:1},None,(),1,0),
        lambda: caller_summary(1,{0:1},(None,),(),1,0), lambda: caller_summary(1,{0:1},(True,),(),1,0),
        lambda: caller_summary(1,{0:1},(0,0),(),1,0), lambda: caller_summary(1,{0:1},(0,),(0,),1,0),
        lambda: caller_summary(1,{0:1},(0,),None,1,0), lambda: caller_summary(1,{0:1},(0,),(),0,0),
        lambda: caller_summary(1,{0:1},(0,),(),True,0), lambda: caller_summary(1,{0:1},(0,),(),10,0),
        lambda: caller_summary(1,{0:1},(0,),(),1,-1), lambda: caller_summary(1,{0:1},(0,),(),1,True),
        lambda: caller_summary(1,{0:1},(0,),(),1,0,False), lambda: caller_summary(1,{0:1},(0,),(),1,0,None),
        lambda: marginal_bounds((F(1,2),)*5,(0,),(),1,0), lambda: marginal_bounds((0.5,),(0,),(),1,0),
        lambda: marginal_bounds((F(1,2**40),),(0,),(),1,0), lambda: marginal_bounds((2,),(0,),(),1,0),
        lambda: marginal_bounds((True,),(0,),(),1,0), lambda: independent_law((F(1,2),)*9),
        lambda: independent_law("unknown"), lambda: marginal_bounds((F(1,2),),(0,),(0,),1,0),
    ]
    for action in invalid:
        try:
            action()
        except (ValueError,TypeError):
            checks["invalid_input_guards"] = checks.get("invalid_input_guards",0)+1
        else:
            raise ValueError("Invalid input admitted")
    return encoded({"candidate":"R000022","status":"passed","checks":checks,"check_total":sum(checks.values()),
                    "fixtures":outputs,"same_marginals_different_two_support_laws":witnesses,
                    "fixed_full_carrier_law_reference_dependence":reference_dependence,
                    "maximum_full_law_dimension":eight,"structural_zero_despite_calls":impossible,
                    "valid_32bit_boundary":boundary,"all_fixtures_synthetic":True,"source_acquisitions":0,
                    "actual_study_fields_resolved":0,"biological_fit_or_empirical_CI":False,
                    "native_caller_or_origin_authenticated":False,"new_theorem_claim":False})


def main():
    if not __debug__:
        raise SystemExit("Verification requires ordinary Python without -O/-OO")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-against", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == Path(__file__).resolve().parent or Path(__file__).resolve().parent in output.parents:
        raise SystemExit("Replay output must be external to the packaged candidate")
    content = (json.dumps(benchmarks(),indent=2)+"\n").encode()
    if args.check_against and content != args.check_against.read_bytes():
        raise SystemExit("Stored caller-capture benchmark differs")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(content)
    out = json.loads(content)
    print(json.dumps({"status":out["status"],"check_total":out["check_total"],"checks":out["checks"]}))


if __name__ == "__main__":
    main()

"""Construct joint laws attaining both published endpoints and verify their marginals exactly."""
import argparse
import json
from fractions import Fraction
from itertools import accumulate, pairwise
from math import comb, floor
from pathlib import Path


def fixed_size_atoms(probabilities):
    """Sample a shifted unit grid through adjacent intervals of the requested lengths."""
    ends = list(accumulate(probabilities, initial=Fraction(0)))
    breaks = sorted({Fraction(0), Fraction(1)} | {x % 1 for x in ends})
    for left, right in pairwise(breaks):
        shift = (left + right) / 2
        pattern = tuple(floor(b - shift) > floor(a - shift) for a, b in pairwise(ends))
        yield right - left, pattern


def upper_witness(probabilities, target):
    if target in (0, 1):
        yield from fixed_size_atoms(probabilities)
        return
    for weight, conditional in [
        (target, [min(p, target) / target for p in probabilities]),
        (1 - target, [max(p - target, 0) / (1 - target) for p in probabilities]),
    ]:
        for mass, pattern in fixed_size_atoms(conditional):
            yield weight * mass, pattern


def verify_law(probabilities, r, target):
    atoms = list(upper_witness(probabilities, target))
    assert sum(mass for mass, _ in atoms) == 1
    assert all(mass > 0 for mass, _ in atoms)
    assert [sum(mass for mass, pat in atoms if pat[i]) for i in range(len(probabilities))] == probabilities
    achieved = sum(mass for mass, pat in atoms if sum(pat) >= r)
    assert achieved == target
    # Dual inequalities independent of the witness: in a tail event at least r-j
    # of the indicators outside the j largest margins have value one.
    ordered = sorted(probabilities)
    cuts = [sum(ordered[:len(ordered)-j], Fraction(0)) / (r-j) for j in range(r)]
    assert target == min([Fraction(1), *cuts])
    return len(atoms)


def verify(profiles_path, result_path):
    data = json.loads(profiles_path.read_bytes())
    rows = data["eligible"]
    saved = json.loads(result_path.read_bytes())
    uniform = []
    gated = []
    updated_sites = set()
    for row in rows:
        tissue, site, a, b, k, flag = row
        # Sum every feasible placement, separately for both possible gate definitions.
        law = [(x, comb(a,x)*comb(b,k-x)) for x in range(max(0,k-b), min(a,k)+1)]
        other_max = data["other_library_evidence_by_site"][site][0]
        peer_rows = [r for r in rows if r[1] == site and r[0] != tissue]
        peer_guarantees_gate = any(all(max(x, alt-x) >= 5
                                       for x in range(max(0,alt-bb), min(aa,alt)+1))
                                   for _, _, aa, bb, alt, _ in peer_rows)
        any_local = any(max(x,k-x) >= 5 for x, _ in law)
        keep = law if other_max >= 5 or peer_guarantees_gate or not any_local else [
            (x, mass) for x,mass in law if max(x,k-x) >= 5]
        if len(keep) != len(law):
            # Confirm no other row at this site could have passed instead.
            assert not any(max(min(aa,alt),min(bb,alt)) >= 5
                           for _, _, aa, bb, alt, _ in peer_rows)
            updated_sites.add(site)
        for target, atoms in ((uniform,law), (gated,keep)):
            target.append(Fraction(sum(m for x,m in atoms if x in (0,k)), sum(m for x,m in atoms)))
    observed = sum(row[-1] for row in rows)
    n = len(uniform)
    assert (n, observed) == (saved["comparisons"], saved["observed_one_sided"])
    assert sorted(updated_sites) == saved["single_gate_witness_sites"]
    results = {}
    for name, probabilities in (("uniform",uniform), ("five_read_gate",gated)):
        item = saved[name]
        assert sum(probabilities) == Fraction(item["expected_one_sided"]["exact"])
        atoms_upper = verify_law(probabilities, observed, Fraction(item["sharp_upper"]["exact"]))
        atoms_lower = verify_law([1-p for p in probabilities], n-observed+1,
                                 1-Fraction(item["sharp_lower"]["exact"]))
        for scale, row in item["upper_if_marginals_multiplied_then_capped_at_one"].items():
            scaled = [min(Fraction(1), Fraction(scale)*p) for p in probabilities]
            verify_law(scaled, observed, Fraction(row["exact"]))
        results[name] = {"marginals_verified_per_endpoint": n,
                         "support_intervals_for_lower_endpoint": atoms_lower,
                         "support_intervals_for_upper_endpoint": atoms_upper,
                         "scaled_upper_witnesses_verified": len(item["upper_if_marginals_multiplied_then_capped_at_one"])}
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profiles", type=Path)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.profiles, args.result), indent=2))

"""Independent fixed-population design enumeration, frozen before producer inspection."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone
from itertools import combinations
import hashlib
import json
import random

BASE = Path(__file__).resolve().parent

def encode(v):
    if isinstance(v, F):
        return str(v)
    if isinstance(v, dict):
        return {str(k): encode(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [encode(x) for x in v]
    return v

def independently_enumerate(n, law, events):
    # Events are expressed as explicit sets of terminal indices; bit operations
    # never define the event predicates in this independent enumeration.
    realised = {}
    for code, weight in law.items():
        called = {index for index in range(n) if code // (2 ** index) % 2}
        realised[code] = {name for name, carriers in events.items() if set(carriers).intersection(called)}
    marginal = {i: sum((weight for code, weight in law.items() if code // (2 ** i) % 2), F()) for i in range(n)}
    inclusion = {name: sum((weight for code, weight in law.items() if name in realised[code]), F()) for name in events}
    joint = {a: {b: sum((weight for code, weight in law.items() if a in realised[code] and b in realised[code]), F()) for b in events} for a in events}
    expected_copies = sum((weight * sum(sum(code // (2 ** i) % 2 for i in carriers) for carriers in events.values()) for code, weight in law.items()), F())
    expected_detected = sum((weight * len(realised[code]) for code, weight in law.items()), F())
    ht = None
    if all(inclusion.values()):
        values = {code: sum((1 / inclusion[name] for name in realised[code]), F()) for code in law if law[code] > 0}
        mean = sum((law[code] * value for code, value in values.items()), F())
        variance = sum((law[code] * (value - len(events)) ** 2 for code, value in values.items()), F())
        if mean != len(events):
            raise AssertionError('Independent fixed-event expectation identity failed')
        ht = {'catalogue_size': len(events), 'expectation': mean, 'variance': variance, 'values': values}
    bounds = {}
    for name, carriers in events.items():
        ps = [marginal[i] for i in carriers]
        product = F(1)
        for p in ps:
            product *= 1 - p
        bounds[name] = {'lower': max(ps, default=F()), 'upper': min(F(1), sum(ps, F())), 'independent': 1 - product}
    return {'descendant_marginals': marginal, 'event_inclusion': inclusion, 'joint_inclusion': joint, 'expected_inherited_copies': expected_copies, 'expected_detected_events': expected_detected, 'ht': ht, 'frechet': bounds}

def main():
    rng = random.Random(19620)
    cases = []
    def add(name, n, weights, events):
        total = sum(weights.values())
        law = {code: F(weight, total) for code, weight in weights.items()}
        cases.append({'name': name, 'n': n, 'law': law, 'events': events, 'expected': independently_enumerate(n, law, events)})
    add('empty_catalogue', 0, {0: 1}, {})
    add('independent_siblings', 2, {0:1,1:1,2:1,3:1}, {'birth':[0,1]})
    add('coincident_siblings', 2, {0:1,3:1}, {'birth':[0,1]})
    add('exclusive_siblings', 2, {1:1,2:1}, {'birth':[0,1]})
    add('overlapping_event_carriers', 3, {i:1 for i in range(8)}, {'left':[0,1],'right':[1,2],'same_left':[0,1]})
    add('extinct_event', 2, {0:1,3:2}, {'observed':[0,1],'lost':[]})
    add('never_callable_descendant', 2, {0:1,1:2}, {'lost':[1],'retained':[0]})
    for index in range(48):
        n = 1 + index % 5
        weights = {code:rng.randrange(0,11) for code in range(2 ** n)}
        if not any(weights.values()):
            weights[0] = 1
        events = {}
        for event in range(1 + index % 5):
            size = rng.randrange(n + 1) if index % 7 == 0 else rng.randrange(1, n + 1)
            events['event_' + str(event)] = sorted(rng.sample(range(n), size))
        add('blind_' + str(index), n, weights, events)
    result = {'frozen_utc':datetime.now(timezone.utc).isoformat(), 'independence':'Generated and enumerated before any R20 producer code or fixtures were inspected', 'case_count':len(cases),'mask_rows':sum(len(c['law']) for c in cases),'cases':cases}
    body = json.dumps(encode(result), indent=2) + '\n'
    (BASE / 'R20_BLIND_ORACLE.json').write_text(body)
    print(json.dumps({'cases':len(cases),'mask_rows':result['mask_rows'],'sha256':hashlib.sha256(body.encode()).hexdigest(),'frozen_utc':result['frozen_utc']}))

if __name__ == '__main__':
    main()

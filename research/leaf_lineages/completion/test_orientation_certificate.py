"""Compare the orientation certificate with all binary tables on three leaves."""
from itertools import product

from orientation_certificate import certify


def exhaustive(original, requirements):
    best = None
    solutions = set()
    for table in product(*(tuple(v for v in range(1,8) if (s & v) == s) for s in original)):
        if any(table[a] & ~table[b] for a,b in requirements):
            continue
        # Write laminarity as an independent three-witness test on leaf labels.
        members = [{i for i in range(3) if mask & (1 << i)} for mask in table]
        if any(x.intersection(y) and x.difference(y) and y.difference(x)
               for i,x in enumerate(members) for y in members[:i]):
            continue
        count = sum(x.bit_count()-s.bit_count() for x,s in zip(table,original))
        if best is None or count < best:
            best, solutions = count, set()
        if count == best:
            solutions.add(table)
    return best, solutions


if __name__ == "__main__":
    checked = 0
    for original in product(range(1,8), repeat=3):
        for required in ((), ((0,1),), ((0,1),(1,0))):
            best, tables = exhaustive(original, required)
            certified, solutions, _, _ = certify(original, required)
            assert (certified, set(solutions)) == (best, tables), (original, required)
            checked += 1
    print(f"All costs and distinct optimum tables agree in {checked} exhaustive three-leaf cases.")

"""Check the conditional expectation with exhaustive enumeration of labeled read positions."""
from fractions import Fraction
from itertools import combinations, product

from gate_conditioning import site_score


def allocations(a, b, k):
    for selected in combinations(range(a + b), k):
        in_a = sum(i < a for i in selected)
        yield in_a, k - in_a


def enumerate_site(profiles, threshold, outside):
    draws = [list(allocations(*profile)) for profile in profiles]
    count = selected_count = all_ones = selected_ones = 0
    for outcome in product(*draws):
        count += 1
        score = sum(min(x, y) == 0 and x + y >= 2 for x, y in outcome)
        all_ones += score
        if outside or any(max(x, y) >= threshold for x, y in outcome):
            selected_count += 1
            selected_ones += score
    return (Fraction(all_ones, count), Fraction(selected_count, count),
            Fraction(selected_ones, selected_count) if selected_count else None)


def verify():
    margins = [(a, b, k) for a, b in [(1, 1), (1, 3), (2, 2)] for k in range(a + b + 1)]
    sites = [(), *((x,) for x in margins), *product(margins, repeat=2)]
    sites.append(((1, 3, 2), (2, 2, 2), (2, 1, 1)))
    checked = 0
    for profiles, threshold, outside in product(sites, range(1, 6), (False, True)):
        direct = enumerate_site(profiles, threshold, outside)
        calculated = site_score(profiles, outside, threshold)
        if direct != calculated:
            raise AssertionError((profiles, threshold, outside, direct, calculated))
        checked += 1
    print(f"{checked} small site configurations agree with direct subset enumeration.")


if __name__ == "__main__":
    verify()

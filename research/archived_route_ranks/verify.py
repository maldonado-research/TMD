"""Check count projections by enumerating concrete records and assignments."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from audit import project


LABELS = "WAMO"
PAIRS = ("WA", "WM", "AM")


def bounds(values):
    values = list(values)
    return [min(values), max(values)]


def check(groups, assignments, expected_differences=None):
    tables = [Counter(assignment) for assignment in assignments]
    assert all(sum(table.values()) == sum(groups.values()) for table in tables)
    totals = {label: bounds(t[label] for t in tables) for label in LABELS}
    differences = {
        f"{x}-{y}": bounds(t[x] - t[y] for t in tables) for x, y in PAIRS
    }
    if expected_differences is not None:
        assert list(differences.values()) == expected_differences, differences

    orders = set()
    ties_possible = False
    for table in tables:
        high, middle, low = sorted("WAM", key=table.__getitem__, reverse=True)
        if table[high] > table[middle] > table[low]:
            orders.add(">".join((high, middle, low)))
        else:
            ties_possible = True

    actual = project(dict(groups))
    assert actual["totals"] == totals, (groups, actual["totals"], totals)
    assert actual["differences"] == differences, (groups, actual["differences"], differences)
    assert sorted(actual["strict_orders"]) == sorted(orders), (groups, actual, orders)
    assert actual["ties_possible"] == ties_possible, (groups, actual, ties_possible)


def check_small_rosters():
    supports = [
        "".join(subset)
        for size in range(1, len(LABELS) + 1)
        for subset in combinations(LABELS, size)
    ]
    count = 0
    for size in (1, 2, 3):
        for slots in combinations_with_replacement(supports, size):
            check(Counter(slots), product(*slots))
            count += 1
    return count


def check_archive():
    slots = ["W"] * 16 + ["A"] * 6 + ["M"] * 3 + ["WAMO"]
    check(Counter(slots), product(*slots), [[9, 11], [12, 14], [2, 4]])


def parent_assignments(parents):
    # Choose a physical record from each parent before resolving its label.
    for records in product(*parents):
        yield from product(*records)


def check_published():
    parents = (
        [("W",)] * 36 + [("A",)] * 7 + [("M",)]
        + [("W", "W")] + [("W", "M")] * 2 + [("A", "M")] * 2
        + [("M", "WM", "WM")]
    )
    records = [record for parent in parents for record in parent]
    assert len(records) == 57 and len(parents) == 50
    check(Counter(records), product(*records), [[31, 33], [32, 36], [1, 3]])

    parent_groups = {"W": 37, "A": 7, "M": 1, "WM": 3, "AM": 2}
    check(parent_groups, parent_assignments(parents), [[28, 33], [31, 39], [1, 8]])
    check(
        {**parent_groups, "WAMO": 1},
        parent_assignments(parents + [("WAMO",)]),
        [[27, 34], [30, 40], [0, 9]],
    )


if __name__ == "__main__":
    check_archive()
    check_published()
    count = check_small_rosters()
    print(f"Verified 26 archived records, 57 published records, 50/51 parent slots,"
          f" and {count} exhaustive small rosters.")

"""Check mutation-tree and parent-path enumeration against all small binary tables."""
from itertools import combinations, product
from mutation_trees import backtrack, minimize_on_tree, trees


def rooted_compatible(table, k):
    for i,j in combinations(range(k),2):
        patterns={(bool(row & (1<<i)), bool(row & (1<<j))) for row in table}
        if {(True, True), (True, False), (False, True)} <= patterns:
            return False
    return True


def run():
    cases = 0
    for k in range(1,4):
        n = 3
        original = list(product(range(1<<k), repeat=n))
        feasible = {s for s in original if rooted_compatible(s,k)}
        possibilities = list(trees(k))
        assert len(possibilities) == (k+1)**(k-1)
        forest_tables = set().union(*(set(product(paths, repeat=n)) for paths in possibilities))
        assert feasible == forest_tables
        for old in original:
            exact = min(sum((new^y).bit_count() for new,y in zip(t,old)) for t in feasible)
            opt, tables = None, set()
            for paths in possibilities:
                c, trace, final = minimize_on_tree(paths, old, None, "unconstrained", None, None)
                if opt is None or c < opt:
                    opt, tables = c,set()
                if c == opt:
                    tables.update(backtrack(trace, final))
            wanted = {t for t in feasible if sum((x^y).bit_count() for x,y in zip(t,old))==exact}
            assert (opt, tables) == (exact, wanted)
            cases += 1
    print(f"All costs and distinct optima agree for {cases} exhaustive original tables.")


if __name__ == "__main__":
    run()

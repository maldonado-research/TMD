# Caller-aware event inclusion

Mutation by Natural Dominance · R000022 · 7 October 2026, America/Los_Angeles

A mutation-origin hypothesis may need more than one positive descendant and an informative reference branch. This conditional extension of R20 makes that extra observation requirement explicit. It computes exact probabilities from supplied joint call laws and sharp marginal-only bounds in a small finite domain. Every fixture is synthetic. No actual mutation rate, origin, native assay, clinical result or statistical confidence interval is inferred.

## The deliberately partial caller

Fix n eligible descendants, a **known** carrier set C and a **known** noncarrier/reference set R, with C and R disjoint. Other descendants can be outside both sets. A mask M records validated **correct target-specific genotype calls**: marked carriers supply correct alternate calls, and marked references supply correct reference calls. It describes more than isolation, survival, sequencing coverage or an ordinary positive variant-call flag.

The event-inclusion predicate is

    f(M) = 1{number of called C members >= k
              AND number of called R members >= r},
    k >= 1, r >= 0.

This is a synthetic support component, not the complete Brody branch caller or a biological mutation-origin authenticator. Ancestral/reference correctness, recurrence, allelic loss, copy state, call quality, locus errors, lineage concordance, and post-expansion origin ambiguity still need independent qualification. Additional observed data can challenge a real origin assignment; the partial predicate here is monotone only in correct-call membership under its supplied truth frame.

One true event inherited into multiple carriers still has one inclusion indicator. Known dead or unobservable descendants, too few eligible carriers, or too few reference descendants can make this component structurally zero. Unknown ancestry or genotype membership is refused, not encoded as a noncarrier or an empty known set. The `ancestry_known=True` flag is supplied scientific information, not authentication.

## Dependence changes the result

For two carriers, each with correct-call marginal 1/2, a requirement for both has these exact synthetic probabilities:

| Carrier joint call law | Both carriers called | Both plus an independently called reference with probability 1/2 |
| --- | ---: | ---: |
| Common success/failure | 1/2 | 1/4 |
| Independent carrier calls | 1/4 | 1/8 |
| Mutually exclusive carrier calls | 0 | 0 |

The last column additionally assumes the reference call is independent of the **entire carrier-call vector**. Equal reference marginals alone do not justify multiplication. Even fixing the full common carrier law, a reference with marginal 1/2 can coincide with the carrier pair and give inclusion 1/2, oppose it and give zero, or be independent and give 1/4. The benchmark supplies all these joint laws.

With three marginals (1/2,1/2,1/2), requiring two carrier calls and one reference call has sharp bounds [0,1/2] over all compatible joint laws. Requiring any one of those two carriers and the reference also has bounds [0,1/2], but its independence value is 3/8 rather than 1/8. R20's carrier-only OR bound [1/2,1] therefore cannot be reused for the reference-support predicate.

Requiring at least two of three carriers with marginal 1/2 and no references has sharp bounds [1/4,3/4]. Four-bit examples include separate carrier/reference groups, unused descendants and thresholds exceeding the known support. These are population/design constraints, not intervals calculated from an empirical sample.

## Exact finite API and bounds

`caller_capture.py` uses only the Python standard library and `Fraction`:

- `caller_summary(n, law, carriers, references, k, r, ancestry_known=True)` admits 0..8 descendants and a complete normalized rational joint mask law. It returns descendant marginals, event inclusion, positive-probability successful masks, all predicate-true masks, expected correct carrier-copy/reference-call counts and structural-zero status.
- `marginal_bounds(marginals, carriers, references, k, r, ancestry_known=True)` admits 0..4 descendants. It returns exact lower/upper probabilities, explicit rational witness laws, a separately labelled independence value and enumeration counts.
- `independent_law(marginals)` constructs the labelled independence special case through eight descendants. Independence is never inferred from supplied marginals or stage fractions.

Thresholds are exact integers k in 1..9 and r in 0..9, excluding booleans. Carrier/reference sets are explicit tuple/list indices, distinct within each set and disjoint across sets. External probabilities are integers or Fractions with numerator and denominator bit lengths at most 32; floats, booleans, invalid laws, unknown mappings and overlarge inputs are refused. Empty frames are allowed and have zero inclusion because carrier evidence is required.

The marginal solver enumerates every full-rank n+1-column basis of the binary mask moment matrix. At four bits this is 4,368 candidate bases and 3,008 nonsingular bases; integer arithmetic checks feasible weights and compares objectives after a cached structural rational inversion. It handles degenerate vertices using zero basis weights. Witness laws attain the reported endpoints. The proof in [CONDITIONAL_DERIVATION.md](CONDITIONAL_DERIVATION.md) uses standard finite linear programming, not a new theorem.

Exact intermediate and returned rationals can exceed the external 32-bit input cap. A derived witness or product law may then be refused by a separately called public function; unrestricted helper composition is not promised. The stored ordinary fixtures stay inside the accepted replay domain. Marginal bounds assert that all supplied probabilities are known population/design values; uncertainty in estimated marginals or dependence is not calibrated here.

Missing entries in a supplied **complete joint law** mean explicit zero probability. An empirical mask unobserved in finite data does not establish such a population zero. Positive marginal calls can coexist with zero event inclusion; good cell-stage recovery does not establish a usable event-denominator contract.

## Reproduce safely

Run from this directory:

```sh
python3 -B verify_benchmarks.py --output /tmp/tmd_r22_caller_replay.json --check-against BENCHMARKS.json
sha256sum -c SHA256SUMS.txt
```

The verifier requires an output path outside the packaged directory, rejects `-O`/`-OO`, and checks exact witnesses, explicit counterexamples, structural zeros and guard failures. Engine admission uses explicit checks and does not rely on assertions. File hashes establish byte integrity, not scientific truth.

R19's actual event-inclusion predicate, system, catalogs, axis, native controls, partner/protocol and inference design remain unchosen. All 26 actual bacterial registry inputs, prior likelihood admission, complete held-out forecast requirements, simultaneous error budgets and fixed stopping rules are preserved. No source was acquired, experiment registered, laboratory commissioned or qualified expert review received for this extension. No cancer-prevention result, new causal force, mathematical priority or novel theorem is claimed. Prepared by Ricardo Maldonado with AI assistance; original code MIT, original documentation and synthetic summaries CC BY 4.0.

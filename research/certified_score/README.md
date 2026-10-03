# Certified conditional-triad score decisions

Mutation by Natural Dominance (TMD) · R000005-NUMERIC method child of R000005 · 2 October 2026 (Pacific time)

This package addresses the explicit numerical gap in the R000003 prospective design: logarithms and confidence endpoints need certified outward enclosures before a near-threshold score decision. It implements that task with Python's standard library and exact rational arithmetic. It evaluates frozen forecasts of **observed qualifying W/A/M endpoints**. No biological observation, new causal mechanism, new theorem, registration, effect estimate or power result is provided. The R3 biological registry's unresolved fields stay unresolved.

The implementation remains a numerical method candidate. [Independent internal mathematical review](review/REVIEW_NOTES.md) accepted it within the documented rational conditional-triad domain after 30,887 exact assertions; the replay and receipt are in `review/`. This is not external peer review or approval of an actual biological study. An operational implementation cannot establish the required sampling law, independent founders, pre-outcome freezing or a meaningful scientific threshold merely by receiving declarations and hashes. Those require an authenticated measurement and study contract. The parent R000005 biological measurement task remains blocked, with the R3 registry's 26 actual-study fields unresolved.

## Target and statistical contract

For context c and frozen comparator m, the target is

    Delta_m = sum_c w_c sum_i t_ci log(pi_TMD,ci / pi_m,ci),  i in {W,A,M}.

Here t is the true **observed conditional-triad** distribution, w is a fixed nonnegative rational vector summing to one, and every forecast is a strictly positive rational probability vector summing to one exactly. A rational forecast produced by converting a floating exponential or ridge fit is the actual frozen forecast evaluated here. This does not certify that it equals an ideal real-number exponential/ridge model. Neither a contrast J nor differential-recovery bounds alone identify latent biological probabilities, Other outcomes or the complete observation map.

Before held-out endpoints, freeze the contexts, route registry, full sampling frames, trial/stopping rule, probabilities, context weights, alpha, numerical precision, comparator list and score gates. Independent training/calibration must precede and remain independent of the held-out outcomes. One endpoint from an independent founder/block is a trial; correlated descendants, paired arms or technical repeats are not extra trials. Within each context the conditional qualifying counts need justified IID multinomial marginals conditional on the frozen information and their qualifying total. Across-context or across-category independence is unnecessary for the union bound. The law cannot be silently replaced by a fluctuation-assay colony total or a selected-isolate spectrum.

The supported document has a fixed **full-frame total** per context. W/A/M counts plus Other, no-qualified-outcome, unresolved-classification and missing counts must equal it. The conditional count law must remain valid under the frozen conditioning/exclusion rule; a full ledger alone does not prove that. A random qualifying total under a fixed full frame is allowed if that conditional law is justified. Zero qualifying outcomes make the target unevaluable. This package performs one fixed analysis: repeated/interim looks need a separately calibrated procedure and do not receive a fresh alpha at every research round.

## Why the intervals are certified

Let C be the number of declared held-out contexts, including contexts assigned zero weight. Each of the 3C binomial marginals receives noncoverage alpha/(3C); each CP tail receives

    tau = alpha / (6C).

For positive qualifying n, the CP lower endpoint is zero when k=0; otherwise it is the root of P[Bin(n,p)>=k]=tau. The upper endpoint is one when k=n; otherwise it is the root of P[Bin(n,p)<=k]=tau. The tails are respectively continuous increasing and decreasing in p for these non-boundary cases. Bisection starts at [0,1], evaluates every tail and allocation comparison exactly, and preserves the root bracket. The lower root's lower bracket endpoint and upper root's upper endpoint form an **outward** interval. After B iterations each bracket has width at most 2^-B; exact equality can collapse it earlier. Binomial tail evaluation uses integer polynomial terms and a divisibility-checked recurrence, choosing the shorter tail or its exact complement. It never proposes or compares a floating root.

Each context's CP box is intersected with its probability simplex. On the one simultaneous coverage event, every true t_c lies in this product region. A union bound gives coverage at least 1-alpha without requiring independence between marginal intervals. Correct conditional marginal coverage given **that context's own** qualifying total gives unconditional marginal coverage after averaging over that total. The law must apply conditional on the independently frozen prediction information; it cannot be assumed from an outcome hash.

The stated coverage and false-certificate bound are **unconditional over the complete fixed-study sampling regime**, conditional only on the independent frozen prediction information. For this mathematical guarantee a context with zero qualifying outcomes can be assigned the whole simplex; the implementation instead issues no score certificate and returns unevaluable. Thus the probability of issuing an incorrect success or failure certificate is at most alpha across complete study repetitions. This is not a coverage claim conditional on all contexts having positive qualifying totals, their jointly observed total vector, issuance of a report, or a favorable decision. Such additional conditioning needs stronger jointly conditional marginal laws or a justified independence argument. Independently founding trials within each context alone does not justify conditioning on the full vector of totals across dependent contexts.

For a positive rational logarithm argument x, exact powers of two give x=2^e r with 1<=r<2. Put z=(r-1)/(r+1), so 0<=z<=1/3. For K positive terms,

    S_K(r) = 2 sum_{j=0}^{K-1} z^(2j+1)/(2j+1),
    0 <= log(r)-S_K(r)
      <= 2 z^(2K+1) / ((2K+1)(1-z^2)).

The upper bound follows by replacing every subsequent denominator by 2K+1 and summing the geometric series of nonnegative powers. Use the same construction for log(2). Multiply its interval by integer e, reversing endpoints if e<0, then add the interval for log(r). Finally round each exact rational result outward onto the declared dyadic grid using integer floor/ceiling division. Signed values, reciprocal arguments, zero curvature and exact log(1)=0 are handled without floats or a transcendental library. The test suite independently brackets logarithms with Python Decimal's correctly rounded ln; Decimal is **verification only**, never the score decision engine.

For logarithm coefficient intervals [a_i,b_i] and nonnegative t_i,

    min_{t in box intersect simplex} sum_i t_i a_i
      <= sum_i t_i log(pi_TMD,i/pi_m,i)
      <= max_{t in box intersect simplex} sum_i t_i b_i.

Each linear extremum is exact: initialize t at the box lower endpoints, then place the remaining probability mass into coordinates in increasing coefficient order for the minimum, decreasing order for the maximum, respecting upper capacities. This solves a linear objective with one equality and coordinate bounds; the exchange argument moves mass from a less favorable coefficient to a more favorable one until saturated. Signed and overlapping coefficient intervals are valid. Interval dependence can make bounds conservative but cannot make them narrower than the true objective. Empty regions are unevaluable, never a biological rejection.

Add context extrema using the frozen nonnegative weights. The contexts have separate probability constraints, so these weighted extrema separate exactly. Round the final sum outward to the report grid and **use those same reported rational endpoints for the gate**. This final rounding can change a strict pass into an inconclusive result; it cannot create a false pass.

Every frozen comparator uses this **same** simultaneous region. On its coverage event, all comparator targets lie inside their projected intervals together. There is therefore no additional comparator Bonferroni division. This statement does not authorize selecting or fitting a favorable comparator after observing held-out outcomes, or interpreting a conditional prediction comparison as a mechanism test.

## Gates and unsupported cases

The only success rule is that every declared comparator's lower endpoint is **strictly greater** than its frozen success threshold. The optional failure rule is that any declared comparator's upper endpoint is **strictly less** than its separately frozen failure threshold. The failure threshold cannot exceed the success threshold. Equality, overlap, or mixed support is inconclusive. With the failure gate disabled, there is no automatic failure decision. These are explicit score gates, not acceptance/rejection of TMD as a biological theory. No p-value, equivalence claim or causal conclusion is generated.

Malformed probability vectors, zero forecast components, bool/float counts, nonstandard NaN/Infinity, duplicate JSON keys, changed plan bytes, incomplete ledgers, unsupported stopping or precision settings, and empty regions are rejected. Missing observations are not supplied as zero. Resource caps do not coarsen an unsupported analysis into a favorable decision: the CLI exits with code 2 and no result.

The bounded prototype supports at most 16 contexts, 32 comparators, 500 full-frame units per context, 64 exact CP bisections, 64 log-series terms, and 96 log/report dyadic bits. Probability input numerator and denominator are at most 64 bits; other rational inputs are at most 128 bits. Rational strings are at most 96 characters; scientific notation and binary JSON floats are unsupported. The CP pre-outcome work cap is 6 B sum_c N_c <= 600,000, using **full frozen totals**, not favorable realized sample sizes. Input JSON is capped at 1 MB. These are explicit prototype limits, not scientific sample-size recommendations. Larger confirmatory studies require a separately reviewed implementation and frozen numerical plan before unblinding.

## Independent pre-outcome precision planning

`precision_plan` uses only the frozen plan, not endpoint outcomes. It supplies a conservative deterministic guide for CP projected **interval half-width**, not a biological effect estimate or statistical power.

Set L=log(1/tau). Hoeffding's binomial tail bound implies that an ideal CP interval lies within empirical k/n plus or minus sqrt(L/(2n)), clipped to [0,1]. Its outward bisection endpoints add at most d_CP=2^-B. In a triad simplex, choosing the median of a three-coordinate coefficient vector as the centering constant gives sum_i |a_i-median(a)|=max(a)-min(a). Because probability differences sum to zero, any score over that CP region differs from its empirical score by at most this range times the coordinate radius.

For each context let R_c bound every comparator's coefficient range, and D_c bound the largest log coefficient interval width. Using interval midpoints, the projected interval half-width is at most

    sum_c w_c R_c sqrt(L/(2 n_c))
      + sum_c w_c (R_c d_CP + D_c/2) + d_report,

where d_report=2^-report_bits covers the final outward score rounding. R_c and D_c are computed conservatively from the certified log intervals; a certified upper bound L_up is used. For a target h, subtract the known finite-precision allowance. If the positive remainder is r and the independently selected positive shares s_c sum to one, the sufficient qualifying counts are

    n_c >= ceil[L_up (w_c R_c)^2 / (2 (r s_c)^2)],

with a minimum of one qualifying outcome even for zero-range or zero-weight contexts. This allocates a width budget; it does not find an optimal study or a distribution of treatment effects. The bound holds for every admissible count vector reaching those qualifying totals, rather than an optimistic expected case. It may be very conservative. Fixed full-frame totals may fail to produce the required qualifying counts. A sampling/stopping contract must address that issue independently of observed score gains.

The synthetic `precision_result.json` asks for a 0.05-nat half-width with shares 2/3 and 1/3. It requires at least **527 and 921 qualifying endpoints**, exceeding this engine's per-context prototype cap. This explicit incompatibility is the result of a conservative mathematical width calculation, not a recommended biological study, achieved power, a registry field or permission to override the caps. A coarser synthetic 0.5-nat target is checked by enumerating every small count vector. Neither target was chosen as a meaningful biological threshold.

## Reproduce the original synthetic package

From this directory, with Python 3.12 or later and no installation:

```sh
python -m unittest -v test_certified_score.py
python certified_score.py example_input.json --output /tmp/tmd-score-result.json
python certified_score.py example_input.json --precision-target 1/20 \
  --precision-shares precision_shares.json --output /tmp/tmd-precision-result.json
python verify_replay.py --check
sha256sum -c SHA256SUMS.txt
```

The stored illustrative analysis is **inconclusive**. Two fixed context weights, three positive frozen comparators, raw zero/support boundary tests, full exclusion ledgers and strict gates are all synthetic. `example_result.json` contains exact rational intervals and extrema, not biological data. The verification receipt records the actually executed test count, fixture replay, exact finite coverage examples and source hashes. Exact small-n enumeration checks finite examples only; the general guarantee depends on the CP/union-bound and projection argument above. The accepted [internal review](review/REVIEW_NOTES.md) establishes the stated numerical checks and limits; it provides no external peer review or biological validation.

Original documentation is CC BY 4.0; original code is MIT under `LICENSE`. Prepared with AI assistance. Established Clopper-Pearson intervals, Bonferroni union bounds, the atanh log series, linear programming and Hoeffding's inequality are used without a new-mathematics or priority claim.

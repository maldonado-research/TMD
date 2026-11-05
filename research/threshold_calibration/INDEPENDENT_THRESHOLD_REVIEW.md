# Independent threshold-selection review

The strict maximum bound is the standard nonparametric one-sided tolerance
calculation. Its numerical equality to a zero-success Clopper–Pearson (CP)
endpoint does not make same-sample threshold selection a fixed-gate binomial
experiment. The inclusive maximum also admits a valid, generally conservative
CP-shaped bound when its tie multiplicity is observed. Neither calculation
establishes biological truth, target-control transport, or calibration of an
adaptively learned score processor.

Let the calibration scores `S_1,...,S_n` be independent draws from one fixed
score distribution, with fixed positive `n`. Let an independent future score
have that distribution. A score processor fixed before calibration, including
one trained independently, is sufficient for this score assumption; raw i.i.d.
samples alone are insufficient when the processor is fitted on them. Conditional
claims after independent processor training must hold for each training result.
Let `F(s)=P(S<=s)`, `M=max(S_i)`, and `K=sum_i 1{S_i=M}`. The actual threshold
is the sample maximum, with a specified strict or inclusive comparator. Additional
score tuning, threshold search, batch search, or optional stopping is outside this
fixed-rule argument. Statements are unconditional over calibration draws, not
conditional confidence claims after observing particular scores or tie counts.

## Strict maximum and general order statistic

For the gate `S_new>M`, write `r_>(M)=1-F(M)`. For `0<epsilon<1`,

```
P(r_>(M)>epsilon) <= (1-epsilon)^n.
```

Indeed, the set `{s:F(s)<1-epsilon}` is a lower set whose probability is at
most `1-epsilon`; the failure event requires all `n` scores to belong to it.
For a continuous cdf, `F(S_i)` are independent uniforms, so equality holds.
Thus the ideal upper bound at error `gamma` is
`U_0=1-gamma^(1/n)`, numerically the same as the one-sided CP upper endpoint
for zero out of `n`. This remains valid for arbitrary atoms and ties.

For the ascending order statistic `S_(j)`, the same argument gives

```
P(1-F(S_(j))>epsilon)
  <= P(Binomial(n,1-epsilon)>=j)
  = sum_{l=j}^n C(n,l)*(1-epsilon)^l*epsilon^(n-l).
```

There must be at least `j` calibration draws in the lower set. This checks the
tail orientation; at `j=n` it reduces to the maximum formula. For continuous
scores equality again holds. General-rank threshold selection must itself be
fixed beforehand; scanning ranks introduces another selection operation.

## Inclusive maximum with observed multiplicity

Define the ideal CP upper limits `U(k)` at common `n,gamma` for `k=0,...,n`.
For `k<n`, `U(k)` is the unique root of
`P(Binomial(n,U(k))<=k)=gamma`; `U(n)=1`. The ideal sequence is strictly
increasing. For the gate `S_new>=M`, its false-gate probability is
`r_>=(M)=1-F(M-)`. Then

```
P(r_>=(M)>U(K)) <= gamma.
```

The justification is not that `K` has a binomial law with the random tail
`r_>=(M)`. For `n=1`, `K=1` and `U(K)=1`, so the assertion is trivial. For
`n>=2`, set `d=1-U(1)` in `(0,1)` and let
`q=inf{s:F(s)>=d}`. The quantile properties give
`F(q-)<=d<=F(q)`. Set `p=P(S>=q)=1-F(q-)`, so
`p>=U(1)>U(0)`, and define the deterministic integer

```
b=max{k in {0,...,n-1}: U(k)<p}.
```

It exists because `p>U(0)`. Let `N=sum_i 1{S_i>=q}`, which is genuinely
`Binomial(n,p)` at the deterministic population cutoff `q`.

* If `M>q`, then `r_>=(M)<=1-F(q)<=U(1)<=U(K)`, so no failure occurs.
* If `M<q`, then `N=0<=b`.
* If `M=q` and failure occurs, then `N=K` and `U(K)<p`, so `N<=b`.

The entire failure event is therefore a subset of `{N<=b}`. By the CP root
identity and monotonicity of the binomial cdf in `p`,
`P(N<=b)<gamma`. This proves the stated weak inequality for every cdf,
without continuity, random tie-breaking, or a binomial model for `K` at `M`.

A certified numerical endpoint `Uhat(K)>=U(K)` preserves coverage, because its
failure event is a subset of the ideal failure event. This argument does not
need monotonicity of the returned, possibly coarsened floating endpoints. The
quantile proof uses monotonicity only of the mathematical ideal CP limits.

If only the maximum and `n` are reported, `K` could be any integer from `1` to
`n`. Maximizing the valid bounds over this set gives `U(n)=1`. A constant score
distribution explicitly attains inclusive false-gate probability one. Absence
of observed ties does not establish that the distribution is continuous. If `K=1`
is actually observed, `U(1)` is valid without assuming continuity; substituting
`U(0)` requires an independent non-atomicity premise or changing to the strict
gate.

## Scope of transfer and confidence composition

The calibration result bounds the false-gate probability for a future control
from the score law in the premise. Native Other false-gate behavior is bounded
only with a justified one-sided transport premise. Workflow blanks and biological
known-Other units are distinct control populations.

If another valid event of error at most `eta` supplies `g>=g_L`, and the
calibration event of error at most `gamma` supplies `f<=F_U`, their intersection
has error at most `eta+gamma` by the union bound, regardless of dependence.
On that event the earlier eligibility algebra gives
`T>=max(0,(g_L-F_U)/(1-F_U))` when `F_U<1`, or the uninformative lower bound
zero when `F_U=1`. Every additional confidence component needs its own allocation.
Random-threshold native counts require a valid conditional sampling argument,
for example endpoint samples collected independently after gate freezing; their
binomial validity does not follow from the threshold certificate alone.

Do not encode selected-threshold training observations as zero observed false
gates in the older fixed-gate count API. The numerical strict limit agrees with
CP zero successes, but the statistical contract and proof differ. Existing study
error budgets must not be overwritten automatically. A separately justified
population bound can be used with the population algebra while retaining its
selection argument and uncertainty allocation.

## Executed checks and limitations

`independent_threshold_oracle.py` uses only the Python standard library. It
imports neither the producer nor its preserved scalar CP engine. Integer
binomial tails decide ideal CP noncoverage without evaluating numerical roots.
For each ordered finite distribution it sums the exact joint law

```
P(M=s_j,K=k)=C(n,k)*p_j^k*F(s_j-)^(n-k).
```

The joint probabilities are checked to sum to one. The script audits inclusive
CP coverage, strict maximum coverage, and general ascending-order coverage on
the grid specified in `INDEPENDENT_THRESHOLD_RECEIPT.json`. These exact finite
checks corroborate the proofs; they do not establish arbitrary-distribution
coverage by enumeration.

The script also verifies two synthetic counterexamples to omitted assumptions.
With raw observations i.i.d. uniform on 100 symbols and `n=2`, a fitted score
`S_D(x)=1{x not seen in D}` makes every calibration score zero but future strict
passage at least `98/100`, violating the ordinary 95% strict-maximum bound on
every calibration draw. This is a generic construction, not a claim about an
article's implementation. Separately, searching thirty disjoint blocks of 59
Bernoulli(0.1) controls for an all-zero block creates false certification of
`r<=0.05` with probability above 0.05. A fixed 59-control block does not do so.

The calculation `n=59` for `epsilon=gamma=0.05` is a standard tolerance design
under the premises. It is not a native biological calibration, a power study,
or a recommended scientific sample size.

Replay from any directory:

```sh
python -B /path/to/independent_threshold_oracle.py --output /tmp/threshold-receipt.json
```

The separate `compare_frozen_threshold.py` pins the reviewed producer bytes and
calls its public calibration API. It checks the returned upper endpoints by
direct exact binomial sums, independently of the producer's scalar recurrence,
and checks the comparator, threshold preservation, marginal coverage wording,
absent native bound, and rejection of malformed inputs. Its receipt records the
executed cases and pinned hash. This is an implementation comparison, distinct
from the producer-independent finite-law oracle above.

```sh
python -B /path/to/compare_frozen_threshold.py \
  --producer-dir /path/to/threshold_calibration \
  --repository /path/to/TMD --output /tmp/threshold-comparison.json
```

This review is an independent computational and mathematical check, not a
qualified external biological review. No new priority claim is made for the
strict bound or elementary probability arguments here.

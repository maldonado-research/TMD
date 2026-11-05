# Selection-aware calibration of a maximum score threshold

Controls used to choose a threshold can still support inference when the
selection rule is included in the probability calculation. This utility bounds
future control false-gate probability after selecting the maximum of a fixed
number of iid scalar control scores. It covers a strict gate and an inclusive
gate with a recorded maximum tie count. It supplies a certificate `F` and its
error allocation `gamma`; it does not modify the earlier fixed-gate count API.
All supplied examples and numerical verification laws are synthetic. No native
control panel, numerical native false-entry rate, biological result or new
mathematical-priority claim is supplied.

## Design and target

Let `S_1,...,S_n` be iid scores from one independently known-Other control
population, with fixed positive `n`. The entire scalar score pipeline, including
preprocessing, must be fixed independently of these calibration observations.
Conditioning on an independently trained pipeline is allowed when the stated
assumptions hold for each training result. Raw iid input units alone do not
establish this premise if their scores are fitted using those same units.

Before observing calibration outcomes, fix the pipeline, `n`, the rule to use
the sample maximum, the strict/inclusive comparator and `gamma`. Let

```
M = max(S_1,...,S_n),   K = number of calibration scores equal to M.
```

Freeze this realized threshold and the same pipeline for future independent
units. With `H(s)=P(S<=s)` for the control score law, the targets are

```
r_>(M)  = P(S_new > M  | calibration sample) = 1-H(M),
r_>=(M) = P(S_new >= M | calibration sample) = 1-H(M-).
```

These are random population tail probabilities because `M` is random. The
confidence statement is marginal over repeated calibration samples. It is not
conditional confidence given a particular observed maximum or tie count, and
is not a posterior probability assigned to the realized population tail.
Choosing among score pipelines, maxima from several batches, thresholds, or
comparators after favorable outcomes, or stopping at a favorable sample size,
requires another argument or error allocation. Those operations are unsupported.

## Strict gate: `S > M`

For every real score distribution, including atoms and ties,

```
P_calibration{r_>(M) > epsilon} <= (1-epsilon)^n.
U_0 = 1-gamma^(1/n)
P_calibration{r_>(M) <= U_0} >= 1-gamma.
```

To see this, the lower set `{s:H(s)<1-epsilon}` has probability at most
`1-epsilon`. The failure event requires all `n` independent scores to lie in
that set. When `H` is continuous, the variables `H(S_i)` are independent
uniforms and equality holds. No continuous-score assumption is needed for the
inequality.

This is the classical one-sided order-statistic tolerance calculation. The
directly inspected [Tong, Feng and Li (2018), Proposition 1 and Equation (1)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5804623/)
give the strict score rule
and, for the ascending `j`th order statistic, the bound

```
P{1-H(S_(j)) > epsilon}
  <= sum_{l=j}^n C(n,l)*(1-epsilon)^l*epsilon^(n-l).
```

Setting `j=n` gives the maximum result above. The general-rank formula is
background only; this utility implements the maximum. See [SOURCES.md](SOURCES.md)
for provenance and the distinction between inspected full text and metadata.

Numerically, `U_0` is the one-sided Clopper–Pearson (CP) upper endpoint for
`0/n`. The tool reuses that certified scalar endpoint. Zero calibration passes
under `S>M` are a consequence of selection, so their validity here comes from
the order-statistic argument, not a binomial model for those passes under a
gate fixed beforehand. Reusing the numerical endpoint does not license entering
these observations as independent fixed-gate zero-success controls in the older
eligibility count interface.

The rank calculation also gives the different statement
`P(S_new>M) <= 1/(n+1)`, marginal over both calibration and the next score, with
equality for continuous scores. For `n=12`, this is `1/13`; the 95% population
tail upper bound is about `0.220922`. A marginal next-observation probability
must not be substituted for the high-confidence population bound `F` in the
eligibility calculation.

## Inclusive gate: `S >= M`, with observed `K`

Let `U_k` be the **ideal mathematical** one-sided CP upper endpoint at common
`n,gamma`. For `0<=k<n`, it is the unique root of

```
P{Binomial(n,U_k) <= k} = gamma;       U_n = 1.
```

The ideal sequence is strictly increasing. For an inclusive maximum gate,

```
P_calibration{r_>=(M) > U_K} <= gamma.
```

The justification uses a deterministic population quantile; it does not claim
that the data-dependent maximum multiplicity `K` is binomial at the random
threshold `M`. For `n=1`, `K=1` and `U_K=1`. For `n>=2`, set

```
d = 1-U_1,   q = inf{s:H(s)>=d},   p = P(S>=q) = 1-H(q-).
```

Quantile properties give `H(q-)<=d<=H(q)`, hence `p>=U_1>U_0`. Define
`b=max{k in {0,...,n-1}:U_k<p}`, which exists. The count
`N=sum_i 1{S_i>=q}` is genuinely `Binomial(n,p)` because `q` is deterministic
under the population law.

- If `M>q`, then `r_>=(M)<=1-H(q)<=U_1<=U_K`; failure is impossible.
- If `M<q`, then `N=0<=b`.
- If `M=q` and failure occurs, then `N=K` and `U_K<p`, so `N<=b`.

Thus every failure lies in `{N<=b}`. Since `p>U_b`, monotonicity of the
binomial lower tail gives `P(N<=b)<gamma`. This proves the asserted weak
inequality for arbitrary score laws, including discrete laws.

The implementation returns a certified rational upper enclosure
`Uhat_K>=U_K`. Enlarging the ideal endpoint preserves the guarantee.
Monotonicity is used only for the ideal sequence in the proof; it is not assumed
for the returned numerical endpoints, which can be conservatively coarsened.

An observed `K=1` permits a nontrivial inclusive bound without assuming
continuity. Absence of observed ties does not establish a non-atomic population.
If only `n` and `M` are available, `K` may be `n`, so the worst-case inclusive
bound is `U_n=1`. Indeed, constant scores have inclusive false-gate probability
one. Unknown multiplicity is refused by inclusive mode; it must not be filled
in as one or zero. Independently established continuity would make the two
population tails coincide, but this tool does not assume or test continuity.

## Numerical examples and conditional planning

At `gamma=1/20`, the supplied synthetic fixtures give:

| Rule and calibration summary | Certified upper bound, rounded for display |
| --- | ---: |
| Strict maximum, `n=12,M=50` | 0.2209222 |
| Strict maximum, `n=59,M=3/2` | 0.0495076 |
| Inclusive maximum, `n=12,M=50,K=1` | 0.3386807 |
| Inclusive maximum, `n=12,M=50,K=12` | 1 |

These maxima are declared synthetic observations; they are not source-derived
native certificates. The endpoint depends on `n,gamma` and, for an inclusive
rule, `K`; the realized `M` identifies which future gate it describes. Knowing
only a planned `n` gives a prospective operating guarantee, not an observed
threshold value or evidence that calibration has occurred.

For the strict rule, a prospective goal `r_>(M)<=epsilon` at confidence
`1-gamma` requires `(1-epsilon)^n<=gamma`. At `epsilon=gamma=1/20`, the smallest
integer is 59, because `(19/20)^59<=1/20<(19/20)^58`. Twelve controls yield
about 22.1%, not a 5% population-tail certificate at 95% confidence. This is
conditional mathematical planning, not a native assay sample-size
recommendation or a power calculation. More controls generally raise the
maximum threshold and can reduce passage of true eligible units; these
certificates do not assess that tradeoff.

## Relation to the SLST source audit

The [earlier audit](../eligibility_gate_bounds/source_audit/SLST_ELIGIBILITY_CONTROLS.md)
correctly says that threshold-selection observations do not justify an ordinary
fixed-gate population interval. This does not make selection data useless:
the specified maximum procedure above has its own selection-aware guarantee.

The source reports twelve workflow water blanks with a maximum of 50
reconstructed full-length sequences and excludes clinical samples with fewer
than 50 sequences. Its literal complementary count rule is `N>=50`. On the
same blank values, it has between 1 and 12 passes; all such passes equal the
maximum, so their number is the unknown `K`. No nontrivial inclusive bound
follows from the reported aggregate alone. The hypothetical strict rule `N>50`
would be a different gate (`N>=51` for integer counts). No correction or
alternative author implementation is inferred.

Even the approximately 22.1% strict bound is only a counterfactual illustration
under the stated design assumptions. The source does not establish an iid
blank-score law or a prospectively fixed calibration size. It also says that
the separate upstream filter of at least 50 **reads per UMI family** was based
on negative-control background. Independence of the entire score pipeline
from the twelve calibration blanks is therefore not established. This is a
boundary of available evidence, not an allegation of improper author behavior.
The sample-level sequence threshold and the UMI-family read filter are distinct.
The [source qualification](SOURCE_BOUNDARY_NOTE.md) and
[source evidence record](SOURCE_BOUNDARY_EVIDENCE.json) distinguish this
specific selection-aware extension from the earlier fixed-gate audit and
record the inspected attribution and source limits.

Finally, water blanks measure workflow background and are not independently
known-Other biological units sampled from a native cohort. Obtaining the
missing individual blank values or their tie count would not resolve these
design and transport assumptions. The source continues to supply no numerical
native `F`, eligible fraction `T` or `beta`. The negative-control supplement
remains unacquired; no access challenge was bypassed or source-author code run.

## Transport and composition with eligibility

This certificate concerns the declared control score population. To use its
bound for native Other units, separately justify

```
native_Other_false_gate_probability(M) <= control_false_gate_probability(M)
```

for the realized learned gate. Pointwise one-sided tail dominance at every
possible threshold is sufficient. A transport statement at some unrelated
fixed threshold is insufficient. Truth, score freezing, iid sampling and
transport are external premises; contract strings do not authenticate them.

Suppose the calibration event has error at most `gamma`, transport is justified,
and another valid event has error at most `eta` and supplies `g(M)>=gL` for the
same gate on the full native cohort. Then, with error at most `gamma+eta`, the
earlier gate mixture algebra gives

```
T >= beta = max(0,(gL-F)/(1-F)) if F<1; otherwise beta=0.
```

No independence between those valid events is required for the union bound.
Their individual sampling statements must still hold. For a random learned
gate, an independent endpoint sample assessed after gate freezing can justify
the needed conditional binomial law for `g(M)`; the threshold certificate alone
does not establish it. Include every additional confidence component in the
joint error budget. Possible estimation error in transport also requires an
allocation or a separate deterministic justification.

The [eligibility population gate mode](../eligibility_gate_bounds/README.md)
can evaluate the algebra from supplied `gL,F`; that mode does not itself carry
this confidence statement. Preserve the certificate and the full error budget
outside that arithmetic call. The existing fixed-gate count mode is unchanged
and must not be given adaptive threshold-training observations under its
fixed-gate binomial contract. No new `Q/J` model is introduced here.

## Bounded implementation and verification

`threshold_calibration.py` accepts a control summary containing `tested` and
`maximum`; inclusive mode also requires `maximum_multiplicity`. The summary is
an explicit assertion about all calibration units, not a reconstruction from
raw scores. The input must state the actual unit, control population and score
definition and agree to the declared design contract. Missing/extra keys,
floats, booleans used as counts, nonfinite tokens and duplicate JSON keys are
refused. Exact integer, rational and finite-decimal strings are accepted for
scores and `gamma`. Prototype limits are `1<=n<=5000`,
`1e-12<=gamma<1`, one MiB input, 200-character and 256-bit rational tokens.

The utility imports the unchanged, hash-pinned classification parser and
certified scalar CP implementation with bytecode writes disabled. Floating
roots only propose endpoints; exact binomial tails certify outward enclosures,
which are returned as exact rational strings. [SOURCES.md](SOURCES.md) records
the pins. No source-study analysis code is imported or executed.

When installed at `research/threshold_calibration/`, the default repository is
the containing TMD checkout. From that checkout run:

```sh
python -B research/threshold_calibration/threshold_calibration.py \
  research/threshold_calibration/example_strict_twelve.json
python -B research/threshold_calibration/threshold_calibration.py \
  research/threshold_calibration/example_inclusive_unique_maximum.json
python -B research/threshold_calibration/verify_threshold_calibration.py --repository .
```

The verifier writes fixtures and `VERIFICATION.json` beside itself. To preserve
a checkout, copy the directory to scratch and pass `--repository /path/to/TMD`.
It checks independent exact binomial-tail inequalities, exact joint
maximum/multiplicity probabilities on finite iid laws, dependency pins, input
refusals and the 59-control planning inequality. Finite enumeration corroborates
the stated proofs; it is not a proof over all distributions.

Two checked counterexamples expose omitted premises. Constant scores make the
inclusive tail one despite zero strict-gate calibration passes. Separately,
take raw observations uniform on 100 categories and `n=2`, and fit
`S_D(x)=0` for categories seen during calibration and `1` otherwise. Every
calibration score is zero, but future strict passage is at least 98%, above
the nominal 95% strict-maximum upper bound of about 77.6%, on every sample.
Thus freezing a fitted pipeline only after calibration does not suffice.
This artificial construction describes no source study.

The [independent review](INDEPENDENT_THRESHOLD_REVIEW.md) supplies the separate
finite-law checks, ideal-versus-certified endpoint distinction, and repeated
threshold-search counterexample. Its receipts and source hashes accompany it.

Original code is MIT and original prose is CC BY 4.0 under repository terms.
Prepared with AI assistance. Computational and mathematical checking does not
constitute external biological validation.

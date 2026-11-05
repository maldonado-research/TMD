# One error budget from learned thresholds to common curvature

This bounded integration carries a maximum-threshold calibration certificate
through a full-cohort eligibility lower bound, route-classification caps, and
conservative common-curvature inference. It uses one prespecified total error
budget across every context and arm. It imports the unchanged
[threshold calibration](../threshold_calibration/README.md),
[eligibility](../eligibility_gate_bounds/README.md), and
[classification](../classification_bounds/README.md) modules and their preserved
certified scalar confidence code. Their existing APIs and contracts remain intact.

All bundled observations are synthetic chosen count tables. The contribution is
an explicit composition and auditable interface for established probability and
mixture calculations, without a novelty claim. No native control panel, measured
native error rate, native eligible fraction, biological result, power estimate,
registry overwrite or study recommendation is supplied.

## Fixed plan, learned gate, then future observations

The input is a predeclared plan and a separate later observation record. Before
any calibration outcomes, fix the context family, the two arms `baseline` and
`selected`, endpoint units, truth definitions, entire score pipelines, maximum
rules and comparators, all sample sizes, total error `alpha`, and calibration
budget share `0<w<1`. A trained score pipeline is allowed only with independent
training and valid iid calibration score laws for each training result.
The fixed-sample prototype supports no outcome-driven stopping, search among
pipelines, exclusion of unfavorable contexts or reallocation of the budget.

For every arm and context, collect `n` independently known-Other calibration
scores from the declared iid population, then record their maximum `M`. The
strict rule is `score > M`. Inclusive mode is `score >= M` and additionally
requires the observed maximum multiplicity `K`. Freeze the learned threshold
and the entire gate-and-label pipeline before future evaluation.

The future native cohort must be the entire cohort before gate selection. Every
unit contributes one W/A/M/U label and a gate outcome. U retains every gate
failure and all unresolved units, and the gate and label denominators are the
same fixed `N`. The interface checks `W+A+M+U=N`, `gate.tested=N`, and
`W+A+M<=gate.positive`. Those arithmetic checks do not establish that the records
actually concern the same physical units. U is an observed outcome, not a true
Other control. No called-label renormalization is performed.

Future true-route controls measure a correct W, A or M call through the **whole
frozen learned gate-and-label pipeline**, with every introduced known-route unit
in the denominator. A control conditional on passing the gate, a callable-only
denominator, or a labeler-only control would measure a different probability.
Each control and cohort denominator is fixed in the plan and checked against
the observations. An explicit zero future denominator is permitted and yields
an uninformative endpoint; a calibration maximum requires `n>=1`.

Let `D` include **all** training and calibration data across every arm/context.
The future label, gate and true-route correct-call counts must each have the
declared fixed-denominator binomial marginal law conditional on `D`. Future raw
units independent of all training/calibration, evaluated using the frozen
pipeline, are a sufficient design under the stated within-cell iid sampling
premises. Processed outcomes generally depend on calibration through `M`;
their binomial parameters may depend on `D`. Unconditional binomial statements
alone do not justify substituting a learned random gate. Neither multinomial
label dependence, dependence between gate and labels on the same units, nor
dependence between otherwise valid component confidence events is prohibited.

Two pointwise transport premises are external:

```
native_Other_tail_D(M) <= calibration_control_tail_D(M),
native_correct_call_i(D) >= true_route_control_correct_call_i(D).
```

The first must hold at every possible learned threshold for each training
result and corresponding frozen score pipeline. A control-tail comparison at
an unrelated fixed threshold, or a comparison merely averaged across training
results, is insufficient. The second applies to the complete gate-and-label
pipeline. This prototype assumes those inequalities deterministically; it
allocates no error to estimating transport. Truth, iid sampling, freezing,
chronology and transport are not validated by contract strings or file hashes.

## One simultaneous guarantee

For `C` planned contexts allocate

```
gamma = alpha*w/(2*C)             per learned gate calibration,
eta   = alpha*(1-w)/(14*C)        per future-count endpoint.
```

There are two calibrations per context and, in each arm, seven future-count
components: three observed-label upper limits, three correct-call lower limits,
and one gate-positive lower limit. The software derives both allocations
centrally. Observations cannot supply an overriding gamma or eta.

For arm/context `j`, the pinned threshold routine gives `F_j(D)`, a control-tail
upper bound with marginal calibration failure probability at most gamma. Its
strict-maximum proof is the classical order-statistic tolerance argument;
inclusive mode uses the recorded `K` and the existing quantile-containment
argument. Numerically it reuses the CP upper endpoint at `0/n` or `K/n`.
These are numerical equivalences: the selected calibration passes are not
fixed-gate binomial counts. The wrapper passes the actual maximum summary to
`threshold.calibrate`; it never fabricates a `known_Other_controls: 0/n` record
for the older eligibility count mode.

Let `A` be the event that every calibration certificate covers. Conditional on
independent training, the calibration union bound gives error at most
`2*C*gamma=alpha*w`; average over training if necessary. Calibration certificates
are marginal over repeated calibration samples, **not** conditional confidence
given an observed maximum or tie count.

Let `B` be the event that every future-count endpoint covers its population
parameter for the realized frozen pipeline. By the conditional count premises,
for every admissible `D`,

```
P(B^c | D) <= 14*C*eta = alpha*(1-w).
P(B^c)     <= alpha*(1-w).
P(A^c or B^c) <= alpha*w + alpha*(1-w) = alpha.
```

The second line follows by averaging the conditional bound; the last is a union
bound. No independence between `A` and `B`, between contexts, or between arms
is needed. The conditioning requirement is essential and cannot be replaced
by the assertion that union bounds never need independence.

On `A` intersect `B`, write `gL` for the gate-positive lower limit, `U_i` for
the observed-label upper limits, and `L_i` for correct-call lower limits. The
pinned eligibility and classification functions give

```
beta = max(0,(gL-F)/(1-F)) if F<1; otherwise beta=0,
T >= beta,
o_i >= T*d_i*p_i >= beta*L_i*p_i,
u_i = min(1,U_i/(beta*L_i)) if beta*L_i>0; otherwise u_i=1.
```

Here `T` is the true W/A/M fraction of the full cohort; `p` is the strictly
positive W/A/M composition conditional on true eligibility, and `d_i` is the
unconditional full-pipeline native correct-call probability within true route
`i`. The Other label column remains unrestricted. The target requires `T>0`;
`beta=0` supplies no positive lower bound and does not establish `T=0`.

Project the caps through the unchanged formulas for `Q=pA^2/(pW*pM)` and
`J=Q(selected)/Q(baseline)`. On the simultaneous event each true J is in its
reported interval. Therefore separating context intervals gives a level-alpha
test of a common finite positive J under all declared premises. One context is
descriptive. An incompatible cap set is unevaluable and does not reject
curvature. Overlap is `not_rejected`, not proof of equal curvature or feasibility
under the full joint count/gate/classifier constraints. Cap witnesses concern
only the outer cap set; joint sharpness is not claimed.

## Why separate 95% statements do not compose to 95%

A calibration certificate with `gamma=.05` followed by a separate count family
with `alpha=.05` has an available union error bound `.10`, not `.05`. A simple
counterexample uses a strict maximum of one Uniform[0,1] calibration score;
the ideal 95% certificate fails with probability `.05`. An independent future
correct-call observation with true success probability `.049` has a 95% lower
confidence endpoint near `.05` when it succeeds, so its failure probability
is `.049`. Their union failure probability is

```
.05 + .049 - .05*.049 = .09655 > .05.
```

The verifier also checks the actual outward certified endpoint version. This
refutes the unsupported simultaneous-coverage claim; it is not a simulated
false-rejection rate for a particular common-J design.

The optional split `w=1/8` makes gamma and eta both `alpha/(16*C)`. This has
the same number of error allocations as the earlier fixed-gate eligibility
wrapper but uses a distinct valid selection-aware calibration argument for
one component per arm. At `C=2,alpha=1/20,w=1/8`, each component has error
`1/640`. The strict maximum bound for 59 controls is approximately
`0.10373254`, rather than 5%. For an ideal strict-tail certificate at most
`epsilon=1/20`, the exact smallest fixed calibration size is 126:

```
(19/20)^125 > 1/640 >= (19/20)^126.
```

The certified outward endpoints also straddle 5% at 125 and 126, with the
126-control value approximately `0.04998879`. These are conditional arithmetic
examples. Increasing calibration size may increase the learned maximum and
reduce true-route gate passage; future gate-positive and full-pipeline controls
must measure that behavior. The calculation is neither a native sample-size
recommendation nor a power calculation. The budget share must be fixed before
calibration, not selected to improve these observed bounds.

## Interface and reproducibility

`integrated_inference.py` accepts separate plan and observation JSON files.
The supplied examples show the complete schema. Each plan lists per-arm
pipeline identifiers, threshold calibration rule and fixed `n`, a threshold
contract, future cohort `N`, and three true-route control denominators. The
observation record supplies maximum summaries, all W/A/M/U counts, gate counts,
correct-call counts, and nonempty provenance descriptions. Inclusive mode
requires K; missing K cannot be filled in as one. Extra fields, including any
attempt to supply old fixed-gate Other counts, are refused.

The canonical plan digest is SHA-256 of UTF-8 JSON with sorted object keys,
compact separators and ASCII escaping; array order is retained. Observation
records bind to that digest. The CLI also reports hashes of the actual input
file bytes. These checks detect content differences. They are not registration,
proof that the plan existed first, identity authentication or validation of the
scientific premises. `--plan-only` validates a declared fixed design and reports
its budget/digest without observed calibration. It performs no registry write.

When installed at `research/integrated_inference/`, run from the TMD checkout:

```sh
python -B research/integrated_inference/integrated_inference.py \
  --plan research/integrated_inference/example_strict_separation_plan.json \
  --plan-only
python -B research/integrated_inference/integrated_inference.py \
  --plan research/integrated_inference/example_strict_separation_plan.json \
  research/integrated_inference/example_strict_separation_observations.json
python -B research/integrated_inference/verify_integrated_inference.py \
  --repository .
```

Outside that layout, pass `--repository /path/to/TMD`. The verifier regenerates
fixture/results and `VERIFICATION.json` beside itself; use a scratch copy to
preserve an installed checkout. The importer checks four source pins and
suppresses dependency bytecode writes. It creates no new CP implementation.
Python 3.10+ and the standard library suffice. Input limits reuse the pinned
parser: one MiB per file, up to 64 contexts, at most 5,000 trials per cell,
exact integer/rational/finite-decimal strings, 200-character and 256-bit rational
tokens. Duplicate JSON keys, booleans as counts, float probabilities and
nonfinite values are refused. Each derived gamma and eta must be at least
`1e-12`. Before inference, the planned work guard requires

```
sum_arm,context(n_calibration + 4*N_future + sum_route(n_control)) <= 60000.
```

This is an operational prototype bound, not a wall-clock guarantee. Exact
rational arithmetic is used after outward scalar certification, including every
cap division, interval comparison and common-J decision.

The three fixtures illustrate strict-calibration separation, inclusive
all-tied calibration giving `F=1,beta=0`, and one descriptive context with zero
true-route control observations giving uninformative caps. They are chosen
synthetic summaries, not random replicates. For the strict fixture a compatible
illustration has `T=19/20`, native gate sensitivity one and native Other gate
probability zero; native eligible correct-call probability `18/19` and control
correct-call probability `.9`. Calibration Other scores can be iid Bernoulli
with positive but small probability of score one and all 1,000 observed scores
zero. Native Other score zero and eligible score one pass the strict gate as
specified. Baseline p is uniform; selected p is `(1/10,4/5,1/10)` or
`(9/20,1/10,9/20)`. The stated joint gate/label counts have positive probability
under this construction. These illustrative laws are not inferred from counts.

The verifier checks the allocation identities, independent exact scalar-tail
inequalities, wrapper-to-pinned projection agreement, denominator/provenance
refusals, dependency changes and the 126-control inequality. It checks both
missing-control and incompatible-cap behavior. The general coverage result
comes from the conditional proof above, not finite tests. Independent review
artifacts supplied with this extension give separate finite-law checks.

The source limitations documented in the threshold and eligibility modules
persist: workflow blanks do not establish a native Other population, and the
published SLST summary does not supply independent training, prospective iid
calibration or native transport. A hash-verified transcription cannot establish
those preconditions. No source-author code, new biological experiment, external
message or archival publication is run by this tool.

Original code is MIT and original prose is CC BY 4.0 under repository terms.
Prepared with AI assistance. Computational review is not external biological
validation. See [SOURCES.md](SOURCES.md) for dependency provenance and attribution.

## Independent review and source checkpoint

The [independent integration review](INDEPENDENT_INTEGRATION_REVIEW.md) checks the conditional composition, boundary cases and exact finite examples. The [producer comparison receipt](PRODUCER_COMPARISON_RECEIPT.json) and [independent exact receipt](INDEPENDENT_EXACT_RECEIPT.json) record their bounded computational scope. Run `compare_frozen_integration.py --help` and `independent_integrated_oracle.py --help` for replay options; use a scratch output directory to preserve the committed receipts.

The [bounded literature assessment](literature_check/ASSESSMENT.md) records a failed PubMed backend query and a twenty-record Crossref fallback. It supplies no new native calibration or biological validation. Raw registered abstracts are excluded from these public materials.

# Calibrated eligibility before classification bounds

This extension turns the prior [true Other denominator boundary](../classification_bounds/README.md#true-other-and-the-denominator-boundary)
into an operational full-cohort eligibility lower bound. A calibrated binary gate
can bound the eligible fraction without assuming every cohort member is truly
W/A/M. The count tool carries that lower bound into conservative curvature
intervals. All supplied examples are synthetic. No native sample, truth panel,
power estimate, new theorem or biological mechanism is supplied or validated.
The earlier three-column classification implementation and its T=1 contract are
unchanged; this utility imports its pinned exact cap/projection and CP routines.

## Target and gate bound

Let `T=P(true W/A/M)` in the **entire cohort before gate selection**. Conditional
on true eligibility, let `p=(pW,pA,pM)` be strictly positive and sum to one. The
target is `Q=pA^2/(pW*pM)` and, within a context,
`J=Q(selected)/Q(baseline)`. The conditional target requires `T>0`; a zero lower
bound does not establish T=0 or an absence of eligible units.

For a binary gate define

```
g = P(G+) = a*T + f*(1-T),
a = P(G+ | true eligible),  f = P(G+ | true Other).
```

Given a justified `g>=gL` and `f<=F`, with `0<=a<=1`,

```
gL <= g <= T + F*(1-T),
beta = max(0,(gL-F)/(1-F))  if F<1, else beta=0,
T >= beta.
```

Screening positivity and prevalence have long been distinguished; see
[Rogan and Gladen (1978)](https://doi.org/10.1093/oxfordjournals.aje.a112510).
The [bibliographic record](BIBLIOGRAPHIC_RECORD.json) pins the official metadata
and abstract inspected here, without claiming a full-text review. If a and f
were exactly known and unequal, the mixture identity would give
`T=(g-f)/(a-f)`. This extension instead implements the one-sided bound above
under partial knowledge, using standard mixture algebra.

An empirical sensitivity lower bound is unnecessary for this conservative
direction: only the probability upper bound `a<=1` is used. A gate positivity
rate alone is insufficient. If `F=1`, or `gL<=F`, beta is zero.

This beta is sharp for these **gate marginal constraints alone**. When `gL>F`,
take `T=beta,a=1,f=F,g=gL`. When beta is zero, the closed model allows `T=0` and
`f=gL`; for the strict T>0 target, take `T=epsilon,a=f=gL` to approach zero. If
`gL=1` and `F<1`, T=1. Conditional probabilities for an absent class at T=0 or
T=1 are understood as arbitrary probability kernels; they do not identify that
class's empirical behavior. Gate mode outputs these marginal witnesses only.

Beta is neither `P(eligible|G+)` (gate-positive predictive value) nor the observed
W/A/M fraction. For example, `T=1/10,a=1,f=0` gives PPV=1 but beta=1/10. With
`o=(1/5,1/5,1/5,2/5)`, correct-call lower bounds `(3/5,3/5,3/5)` and unrestricted
Other labels, `p=(4/5,1/10,1/10)` is possible at T=1/10. Substituting PPV=1 as
beta would falsely force p to be uniform. A target defined only within G+
requires a separate derivation.

## From eligibility to conservative curvature intervals

The observation model has four true columns W,A,M,Other and four observed rows
W,A,M,U. Each full-cohort unit has one observed label, and U retains lost or
unresolved units. U is not a known-truth Other category. Define
`d_i=P(observed label i | true route i)`, without conditioning on gate passage.
This includes gate failures when the gate is part of the measurement pipeline.
The Other column is unrestricted. Therefore

```
o_i >= T*d_i*p_i >= beta*d_i*p_i,
u_i = min(1,o_i/(beta*d_i)) if beta*d_i>0, else 1.
```

For an independently known beta>0 and no additional gate restrictions, these
are the exact conditional-triad caps under an unrestricted Other column. To see
sufficiency, choose T=beta, reserve mass `beta*d_i*p_i` in the correct rows, and
distribute the residual observed vector using one common residual distribution
across each eligible column's remaining `1-d_i` mass and the entire Other
column. The residual mass is `1-beta*sum(d_i*p_i)`. At zero residual mass, any
residual distribution suffices. This is the earlier corollary, not a new theorem.

After deriving beta from gate constraints, the tool uses only this cap outer
set. It **does not claim joint gate/classifier sharpness or full feasibility**.
If the gate is a deterministic function of labels, the marginal witness and cap
witness need not jointly satisfy that relationship. For example, suppose
`G+` means observed W, `o=(1/2,1/4,1/4,0)`, `d=(1,1,1)` and `F=0`. The gate
bound is beta=1/2, and caps `(1,1/2,1/2)` admit `p=(1/10,9/20,9/20)`. But the
joint rule and perfect route calls require `T*pW=oW`, forcing T=5 at that p.
The outer point is not jointly feasible. Population gate mode supplies no Q
feasibility decision; count-mode witnesses certify only the cap outer set.

Without a positive beta and with positive observed W/A/M probabilities, an
unrestricted Other column leaves conditional Q unbounded. Exact population
zeros with positive correct-call lower bounds can instead contradict a strictly
positive target. Finite zero counts do not establish such population zeros.

## Count interface and confidence statement

Each arm/context must provide:

- `observed_counts`: W,A,M,U on the full cohort, with `N=sum(counts)`.
- `gate_counts`: `tested=N` and `positive` on those same cohort units. Dependence
  between gate and label outcomes is allowed.
- `known_truth_controls`: introduced/correct counts for each independently known
  true route. Correct calls must use every introduced unit in the denominator.
- `known_Other_controls`: tested/positive counts for independently known true
  Other units under the same gate rule.

If only G+ units receive route typing, retain every G− unit as U. Then true-route
controls must calibrate the **whole gate plus labeling pipeline**:
`P(correct route label | true route i)`, not `P(correct | G+,true route i)`.
The counts and truth definitions must refer to a fixed common endpoint unit;
read, cell, lineage and technical-replicate denominators are not interchangeable.

Required one-sided transport assumptions are

```
native eligible correct-call_i >= true-route control correct-call_i,
native Other false-gate probability <= known-Other control false-gate probability.
```

The Other controls must represent the native Other mixture or justify the latter
inequality for it. Water blanks, a convenient mixture average, and observed U
units do not automatically do so. Controls must cover the relevant routes,
states, matrices, arms, contexts and batches, or justify one-sided transfer.
A late spike-in does not calibrate earlier gate or labeling loss. The explicit
contract strings record these external premises; software does not authenticate
truth, design, transport or the binomial count laws.

For C fixed contexts, allocate `alpha/(16*C)` to each one-sided component:
two arms times `(3 observed-label upper + 3 correct-call lower + 1 gate-positive
lower + 1 Other false-gate upper)`. The pinned certified CP scalar code provides
outward binary-float endpoints certified using exact binomial tails. Those
endpoints are immediately converted to their exact rational values for beta,
caps and comparisons. No estimate is substituted for a confidence bound.

On the simultaneous event of probability at least 1-alpha,

```
o_i<=U_i, native_d_i>=L_i, g>=gL, native_f<=F,
T>=beta(gL,F), p_i<=min(1,U_i/(beta*L_i)).
```

The union bound does not require independence between these components. Each
component still requires its declared valid fixed-denominator binomial marginal.
The two transport assumptions are treated as deterministic external premises;
their own possible estimation error is not included in alpha. Plugging estimated
transport inequalities into the contract does not preserve the stated guarantee.

The unchanged capped-simplex Q formulas and arm-ratio projection give conservative
J intervals. At least two disjoint context intervals reject a common finite
positive J at level alpha under all premises. A cap incompatibility is
unevaluable, not a biological rejection. Overlap is `not_rejected`, not proof of
full confidence-region feasibility or equal biological curvatures. Count-mode
projection is not claimed sharp.

Missing required fields are refused. Explicit zero Other-control observations
give F=1, beta=0 and caps 1; Q and J have range closure `[0,infinity]`, with both
endpoints excluded from the finite positive target. The same convention applies
to zero gate observations. Zero route-control observations give that route cap 1.

## Bounded implementation and synthetic examples

The CLI accepts exact integer/rational/finite-decimal strings, rejects floats,
duplicate/unknown keys and nonfinite tokens, and caps input at one MiB. Inherited
limits are 64 contexts, 5,000 units per cohort/control, alpha at least `1e-12`
and below one, and bounded 200-character/256-bit rational input tokens. Before CP
work it limits `sum(3*N_labels + sum_i N_route_control_i + N_gate + N_Other)` to
60,000. With the same-cohort API, `N_gate=N_labels`. These are prototype work
guards, not a general runtime guarantee.

When installed at `research/eligibility_gate_bounds/`, the default repository
path resolves to the containing TMD checkout. From that checkout run:

```sh
python3 -B research/eligibility_gate_bounds/eligibility_gate_bounds.py \
  research/eligibility_gate_bounds/example_population_gate.json
python3 -B research/eligibility_gate_bounds/eligibility_gate_bounds.py \
  research/eligibility_gate_bounds/example_calibrated_counts.json
python3 -B research/eligibility_gate_bounds/verify_eligibility_gate.py --repository .
```

The verifier regenerates receipts and example files beside itself. Copy this
directory to scratch and pass `--repository /path/to/TMD` when preserving an
untouched checkout.

| Synthetic fixture | Outcome |
| --- | --- |
| Population gate `gL=19/20,F=1/20` | Sharp marginal beta=18/19. |
| Calibrated counts, two contexts | At alpha=1/20 and 32 allocations, beta is about 0.92575 in each arm; A-rich J lower is about 7.450 and A-poor J upper about 1.214, so the outer intervals separate. |
| Same counts, zero Other-control observations | beta=0, all caps 1, and common J is not rejected. |

The count fixture uses chosen possible outcomes: 950 gate positives per 1,000
full-cohort units, zero false gates per 1,000 true-Other controls, and 900 correct
calls per 1,000 true-route controls. A compatible illustrative law is T=19/20,
gate a=1,f=0, native eligible diagonal 18/19 with remaining outcomes U, and all
Other outcomes U. Native labels then have probabilities `0.9*p_i` with U=0.1;
true-route control correct probability 0.9 satisfies one-sided transport. Baseline
p is uniform; selected p is `(1/10,4/5,1/10)` or `(9/20,1/10,9/20)`. The supplied
count realizations have positive probability under these laws, including when
gate and labels share units. These are not random replicates or a power study.

The verifier checks exact gate necessity and endpoint witnesses, all reported CP
certificates, small-binomial one-sided coverage, missing-control behavior and
input refusals. `VERIFICATION.json` records executed checks and source hashes.
See [SOURCES.md](SOURCES.md) for original-project dependency provenance and
licenses. Original documentation is CC BY 4.0; original code is MIT under
repository terms. Prepared with AI assistance. Computational review does not
constitute qualified external biological review.

The [independent review](INDEPENDENT_REVIEW.md) distinguishes marginal gate
sharpness from conservative joint projection and documents the finite checks.
The [source audit](source_audit/SLST_ELIGIBILITY_CONTROLS.md) replays the published
threshold and cached retained-sample roster; the
[native control note](source_audit/native_controls/NATIVE_CONTROL_NOTE.md)
explains why selected non-focal WS examples are not a false-entry control
denominator. Neither audit supplies a numerical native beta.

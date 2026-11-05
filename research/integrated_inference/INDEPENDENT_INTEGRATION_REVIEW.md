# Independent integration review

The proposed composition is valid under its explicit sampling, truth and
transport premises. It does not validate those premises in the native system.
The strict-maximum tolerance calculation and the union-bound composition are
standard probability arguments; this review makes no priority claim.

Let `H0` contain the prespecified design and every independently trained score
pipeline, across all contexts and arms. Conditional on each `H0` realization,
each gate's positive, fixed-size calibration score sample must be iid from its
specified known-Other control population. The comparator and maximum rule are
fixed before calibration. Calibration samples can be dependent across gates.
Write `H` for `H0` together with ALL calibration observations. The learned gate,
its future probabilities, and any other frozen pipeline components are now
`H`-measurable. The score pipeline must not have been fitted or tuned on these
calibration observations.

For `C` contexts and two arms, fix `alpha` and `0<w<1` before outcomes, and set

```
gamma = alpha*w/(2*C)
eta   = alpha*(1-w)/(14*C).
```

There are `2C` maximum-threshold certificates. The threshold module proves
marginal-over-calibration coverage, conditionally on independent prior training:
`P(f_control(H)>F(H) | H0)<=gamma`. This is NOT a conditional-on-the-realized-
threshold confidence statement. By integration and union bound, any calibration
certificate fails with probability at most `2C*gamma`.

Each of the `14C` future count endpoints must have a valid binomial marginal
conditional on `H`, with its planned fixed denominator and its own possibly
`H`-dependent success probability. These endpoints are, per arm/context, three
native observed-label upper bounds, three true-route-control correct-call lower
bounds, and one native gate-positive lower bound. The gate and labels use the
same full-cohort W/A/M/U denominator. In particular, retained-only denominators
and calibration-derived adaptive zero counts do not satisfy this count API.
Future raw iid evaluation units independent of all training/calibration data,
processed through the now-frozen pipeline, are sufficient. The resulting
processed outcomes can depend on calibration through the frozen threshold.

A conditional union bound gives `P(any count endpoint fails | H)<=14C*eta`.
Averaging this inequality and combining with the calibration union bound gives

```
P(any calibration or count certificate fails)
 <= 2C*gamma + E[P(any count endpoint fails | H)]
 <= 2C*gamma + 14C*eta
  = alpha.
```

There is no assumption of independence between labels, gate counts, route
controls, arms, or contexts. Independence used in a particular exact synthetic
oracle is a property of that oracle's law, not a premise of this union bound.
Shared future units across arms or contexts are allowed when all required
conditional marginals remain valid. Using those future units in calibration,
or optional sample sizes, needs a new argument and is excluded by the stated
chronology and sampling contract.

For each frozen pipeline, require external transport inequalities
`f_native<=f_control` and `d_native,i>=d_control,i`. A uniform native-Other tail
domination at every possible learned threshold, for each trained pipeline, is
sufficient for the first inequality. An inequality only at some deterministic
threshold need not hold at the learned threshold. The route-control probability
is unconditional over the entire gate-plus-label pipeline for known true route
i; it cannot be accuracy among controls that passed the gate. Truth and sampling
units must be established independently of the score-based classifier.

On the simultaneous certificate event, write `g=P(gate+)`, `T=P(true W/A/M)`,
and `a=P(gate+ | true W/A/M)`. Then `g=T*a+(1-T)*f_native` implies
`g<=T+(1-T)*F`. Hence

```
beta = max(0,(g_L-F)/(1-F))  if F<1; otherwise beta=0
T >= beta.
```

For each observed route label, `o_i>=T*p_i*d_native,i`, where `p_i` is the
strictly positive route composition conditional on true eligibility. Thus
`p_i<=min(1,o_U,i/(beta*d_L,i))`, taking the cap as one if its denominator is
zero. An unrestricted true-Other classifier column only contributes
nonnegative observed-label mass, so it does not invalidate the inequality.

The capped-simplex Q interval contains the actual positive
`Q=p_A^2/(p_W*p_M)`. Each context's ratio interval contains its actual
`J=Q_selected/Q_baseline`. Under a common-J null, that common value belongs to
all reported context intervals on the simultaneous certificate event, so empty
intersection has probability at most alpha. Empty/no-positive-law cap sets
remain unevaluable rather than automatic common-J rejection. A one-context
calculation is descriptive. Outer projection does not prove joint feasibility
or joint gate/classifier sharpness; overlap does not establish equal curvature.

## Exact finite checks

`independent_integrated_oracle.py` imports only the standard library and performs
no simulation, producer calls, or numerical beta inversion. Ideal CP failures
are decided by exact integer binomial tails. A known-Other calibration law on
scores zero and one gives random learned thresholds. Native true-route scores
one and two make subsequent correct-call and gate parameters depend on that
threshold. Native observed-label and gate errors are enumerated jointly over
the same full-cohort multinomial units. Four context/arm cells deliberately
share the exact same samples, showing that complete cross-cell dependence is
consistent with the union-bound argument. Both strict and inclusive comparator
experiments have positive calibration and count error probabilities.

The receipt records nonzero error for the simultaneous sufficient certificate
event, not actual Q/J projection noncoverage. Projection may cover even when an
ingredient certificate fails. The finite audit checks the separately stated
proof; it is not a proof over all distributions or native biological evidence.

At `C=2`, `alpha=1/20`, `w=1/8`, both component errors are `1/640`.
Strict-maximum `n=59` gives upper tail approximately `0.10373254330022949`.
The exact inequalities `(19/20)^125>1/640` and
`(19/20)^126<=1/640` make 126 the minimum per-gate calibration count to bound
the population false tail by five percent under this allocation. This is
conditional planning arithmetic, not native calibration or a power calculation.

The oracle also gives two exact counterexamples to unauthorized searching:

- With iid Bernoulli(3/50) known-Other scores, an all-zero 126-unit block falsely
  certifies a tail below five percent. Searching four independent blocks makes
  this error approximately `0.0016439993>gamma`; searching 125 makes it
  approximately `0.050117755>alpha`. This is a false-tail certificate
  counterexample, not a computation of common-J rejection size.
- With iid Bernoulli(1/2) count outcomes, ten successes in ten trials give a
  one-sided lower endpoint above one half at `eta=1/640`. Searching two such
  blocks gives noncoverage `2047/1048576>1/640`.

A plan hash binds content. It cannot establish that the plan preceded outcomes,
that samples are independent, or that truth/transport assertions hold. A valid
registration/chronology claim needs external evidence. Separate plan and record
files improve auditability but do not supply that evidence by themselves.

## Frozen implementation comparison

The final reviewed producer SHA-256 is
`6bd25d526dc7a95338ab861eb426b36728fc997bf80c3bd45f4c19ce6494e45f`.
A final metadata-only rename to `native_parameter_authentication_performed`
was reviewed and the frozen comparison rerun. Numerical logic is unchanged.
The separate producer-independent mathematical oracle and its receipt were
left unchanged.

`compare_frozen_integration.py` matches the three supplied final fixtures and
two independently constructed boundary fixtures against the preserved threshold,
eligibility, classification and certified-CP sources. The receipt records
18 calibration matches, 126 count-endpoint matches, 64 independent direct
binomial-tail checks, 18 gate matches, 18 cap/Q matches and 14 J/common-interval
checks. It verifies an informative strict-separation example, inclusive all-tied
vacuity, a one-context case without truth controls, mixed comparators with unequal
control denominators, and a zero-future-cohort boundary case.

For a standalone archive preserving `research/` paths, both scripts are bounded
replay candidates. For example, from the extracted archive root:

```sh
python -B research/integrated_inference/compare_frozen_integration.py \
  --producer-dir research/integrated_inference --repository . \
  --output /tmp/integrated-comparison.json
python -B research/integrated_inference/independent_integrated_oracle.py \
  --output /tmp/integrated-exact-oracle.json
```

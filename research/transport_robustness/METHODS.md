# Conditional confidence projection under bounded recovery mismatch

## Observable and biological contrasts

Routes are Wsp, Aws, Mws, abbreviated `(W,A,M)`. Let `q_ci` and `p_ci` be the positive biological baseline and selected route probabilities in context `c`. Actual biological-sample recovery probabilities are `r_0ci,r_1ci`; matched fixed-route controls identify positive recovery probabilities `d_0ci,d_1ci`. Recovered categorical probabilities obey

```text
b_ci ∝ q_ci r_0ci          t_ci ∝ p_ci r_1ci.
```

Controls have known fixed introduced denominators and one binary recovery per introduced unit. Baseline and selected categorical samples must justify the marginal binomial laws used by the stored simultaneous Clopper–Pearson projection. Positive population components are required for the finite log contrasts; observed zero counts are permitted.

Define `v=(-1/2,1,-1/2)` and

```text
theta_bio,c = v · [log(p_c) - log(q_c)]
theta_corr,c = v · [log(t_c) - log(b_c) - log(d_1c) + log(d_0c)]
e_ci = (r_1ci/r_0ci)/(d_1ci/d_0ci)
theta_corr,c = theta_bio,c + v · log(e_c).
```

Normalizing constants disappear because the weights sum to zero. With `J=exp(2 theta)`,

```text
Jcorr,c = Jbio,c × e_cA²/(e_cW e_cM).
```

This is a relative contrast. Common route-independent recovery factors cancel. It does not identify absolute recovery or separate mutation supply, accessibility, establishment, selection, and drift.

## Exact interval correction

Suppose valid, prespecified, finite rational bounds satisfy `0<L_ci<=e_ci<=U_ci`. Over this rectangular residual set,

```text
mlo,c = L_cA²/(U_cW U_cM)
mhi,c = U_cA²/(L_cW L_cM).
```

These extrema are attained at the corresponding route corners. If the stored observable interval is `[Jlo,c,Jhi,c]`, project it to

```text
Jbio,c ∈ [Jlo,c/mhi,c, Jhi,c/mlo,c].
```

Zero lower endpoints and infinite upper endpoints are preserved. A general asymmetric residual box may exclude 1 and shift an interval; only nested admissible sets guarantee nesting of the corrected intervals. The term "widen" in the function name describes the common symmetric case.

The extrema are exact over the supplied scalar `J` interval crossed with the residual box. They are conservative relative to probability-simplex constraints, shared recovery mechanisms, or other known joint constraints not used by this calculation. Restored intersection means the procedure can no longer reject under this enlarged set; it need not imply a fully feasible biological model under additional constraints.

## Conditional confidence and the shared finite null

Let the original simultaneous probability intervals cover their true values on event `E`, with `P(E)>=1-alpha`. Provided the observation model and valid fixed residual bounds hold, every true biological `J_c` belongs to its corrected interval on `E`. Under a shared finite contrast, a common `0<J<infinity` therefore belongs to all corrected intervals. Reject only when the maximum lower endpoint is **strictly greater** than the minimum finite upper endpoint. The false-rejection probability is at most `alpha` under those conditions. No across-coordinate independence is required by the Bonferroni union bound; invalid within-sample count laws remain invalid.

Positive finite touching endpoints are compatible. One context is always `descriptive_only`: it cannot test across-context equality. `compatible_unbounded` means the nonempty intersection has lower endpoint zero or upper endpoint infinity, hence is unbounded in finite-log-contrast coordinates. Neither outcome establishes equivalence or confirms the mechanism.

The public interval API accepts finite rational numbers only (integer, `Fraction`, or integer/fraction string). It rejects floats, booleans, decimal strings, malformed infinity encodings, negative lower endpoints, zero upper endpoints, reversed bounds, duplicate/empty context names, and inconsistent metadata. A zero lower endpoint denotes an unattained `theta -> -infinity` limit; an infinite upper endpoint denotes `theta -> +infinity`. Structural-zero models whose contrast is undefined, `J=0` only intervals, and infinite lower endpoints are outside this finite-contrast contract and are declined.

The saved 0.5 marginal endpoints were binary floating-point numbers. A dedicated historical adapter converts those exact saved binary values to rational numbers and independently reconstructs the stored rational projection. Its acceptance of legacy JSON numbers does not extend to the new residual or `J` APIs. The adapter checks projection arithmetic and source allocation metadata; it does not newly certify every old binomial tail or scientifically verify the marginal laws.

## Symmetric sensitivity frontier

If each **differential residual** has the same bound `e_ci in [1/R,R]`, `R>=1`, then

```text
m_c ∈ [R^-4,R^4]
Jbio,c ∈ [Jlo,c/R^4, Jhi,c R^4].
```

The radius is common but route residual vectors can differ across contexts. For an initially rejecting collection, put

```text
L = max_c Jlo,c
U = min_c Jhi,c among finite upper endpoints
Q = L/U > 1.
```

The first compatible radius is the positive eighth root `R*=Q^(1/8)`. At equality the intervals touch and are compatible. Existing compatibility has minimum admissible radius 1; a single-context frontier is not applicable. Under the accepted finite-contrast interval contract, initial rejection guarantees positive finite `L,U`, so this threshold is finite.

`threshold_bracket` uses exact rational bisection and compares eighth powers. Its endpoints enclose `R*`; a nonzero-width lower bracket still rejects and the upper bracket is compatible. The absolute width is at most `2^-80` in the reported analysis. No floating logarithm or root controls any decision. Decimal displays are outward rounded and informational only.

Two distinctions matter. First, separately bounding each branch ratio `r_hci/d_hci` in `[1/R,R]` yields a differential interval `[R^-2,R²]`. The corresponding context expansion is `R^8` and pairwise frontier exponent is **16**, not 8. Second, if the identical residual vector is physically shared by every context, its contrast bias is common and equality is unchanged. Permitting independent context-specific vectors discards that coupling and can be conservative.

## Assumption contract and historical boundary

The new wrapper requires affirmative declarations that the source marginal laws and simultaneous coverage are justified; population components are positive; the observable corrected parameter is distinguished from the biological parameter; the observation model applies; and the differential mismatch bounds cover the actual residuals and are fixed independently of outcomes for any confidence claim.

These are conditional modeling declarations, not findings inferred by the program. The five grid bounds are hypothetical sensitivity scenarios. The reported frontier is exploratory. Data-dependent selection of a tolerable radius does not establish its scientific validity or retain a prespecified test interpretation.

The preserved 0.5 `validate_document` requires `control_relative_recovery_transports=true`. We do not feed a mismatch model to that validator or rewrite its metadata. We use the stored CP probability projection separately, where exact transport is not needed to define the observable corrected parameter. The illustrative mismatch generator calls only the preserved scalar CP and probability projection routines, and explicitly records that exact transport is false.

Extension 0.3.0 already develops the residual-bias identity and sensitivity boxes with approximate positive-cell intervals. This package integrates that established idea with the boundary-compatible rational interval outputs of 0.5.0. It does not claim a new mathematical principle.

## Stored-data and illustrative analyses

All four original scenarios contribute all 40 recorded results, with original seed and index labels retained. No replacements or newly sampled replicates occur. Scenario names containing `new_` are inherited historical labels from 0.5.0, not claims that these records are newly generated here.

The illustrative mismatch example uses uniform biological probabilities in both branches and both contexts. Controls have recovery 1/2 on every route and branch. Actual baseline recovery also equals 1/2. Actual selected recovery is `(1/4,1,1/4)` in one context and `(1,1/4,1)` in the other. Thus `Jbio=1` in both, residual vectors are `(1/2,2,1/2)` and `(2,1/2,2)`, and corrected observable contrasts are 16 and 1/16. Chosen categorical count vectors are baseline `(300,300,300)` and selected `(150,600,150)` / `(400,100,400)`; all controls recover 500 of 1000 introduced units. These are possible illustrative outcomes under the stated laws, not random replicates, typical-outcome claims, or biological evidence.

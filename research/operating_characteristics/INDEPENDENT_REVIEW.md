# Independent scientific operating-characteristic review

This note reviews the existing `prospective_design`, `certified_score`, and
`calibration_disagreement` packages. It changes no repository files, fitted
algorithm, registry entry, biological sampling contract, score gate or numerical
implementation. All proposed operating-characteristic work is a separate
synthetic design experiment, not achieved biological power or a study amendment.

## Pre-outcome feasibility ceiling

For comparator m, let a_cmi = log(T_ci / M_cmi), with frozen positive forecasts
and nonnegative weights summing to one. Over the product of the context truth
simplices,

    C_m = max_p sum_c w_c sum_i p_ci a_cmi
        = sum_c w_c max_i a_cmi.

Each context's linear objective is maximized at a maximizing coordinate, so the
second equality holds. If C_m <= s, no possible truth distribution has strict
gain greater than success threshold s against that comparator. Therefore
all-comparator success is unattainable. This is an arithmetic limitation of
frozen forecasts and their gate, not evidence that a comparator is better.

The accepted score engine supplies certified coefficient intervals [l_cmi,
u_cmi]. The exact rational sums

    C_lower = sum_c w_c max_i l_cmi,
    C_upper = sum_c w_c max_i u_cmi

enclose C_m. `C_upper <= s` certifies this necessary-condition failure without
any held-out outcome data. This also rules out a success certificate from the
unchanged engine on every evaluable count vector: its lower projected endpoint
cannot exceed this full-simplex ceiling, and final outward rounding only lowers
that endpoint. If the ceiling enclosure straddles s, no conclusion follows.

`feasibility_ceiling.py` independently implements these max/sum projections,
using the existing engine solely for validated plans and certified logarithm
coefficients. It never accesses document outcomes. Its status is deliberately
distinct from `unevaluable`, `certified_failure`, and `inconclusive`: an
unattainable positive improvement target can coexist with a candidate that
outpredicts every comparator, but by less than the target.

There is no new multiple-testing correction: this diagnostic is deterministic
arithmetic conditional on the already frozen forecasts. Each comparator passing
its necessary ceiling check does not establish joint all-comparator feasibility,
because its maximizing truth can differ from other comparators' maximizing
truths. It also establishes no sampling power at the fixed endpoint totals.

At s=0 every context's maximum log ratio is nonnegative because both forecasts
sum to one. It is zero only for identical forecasts. Thus this particular
ceiling can rule out a zero-margin gate only when forecasts agree in every
positively weighted context; near-identical forecasts alone do not prove
unattainability at s=0. Positive margins can be ruled out for merely similar
forecasts. Zero-weight contexts still obey the engine's input, count and
unevaluability rules; this diagnostic does not remove them.

## Exact restricted-versus-flexible identity

Let theta_j and eta_j be the training log contrasts already computed by the
frozen builder, xbar the equal-context training feature mean, and

    b_theta = sum_j (x_j-xbar)(theta_j-thetabar)
              / (sum_j (x_j-xbar)^2 + 0.01).

Linearity of the same intercept-plus-ridge operator applied to the two flexible
offsets gives, exactly in real arithmetic,

    eta_flexible(x) = eta_restricted(x),
    theta_restricted(x) = thetabar,
    theta_flexible(x) = thetabar + b_theta (x-xbar).

Consequently, a target feature equal to xbar, zero training feature variation,
one training context, or zero theta-feature covariance makes the predictions
identical. A deterministic common rationalization of identical computed
probability vectors preserves the tie. Independently evaluated floating algebra
can instead introduce negligible numerical differences; these should not be
interpreted as biological or statistical discrimination.

If the true training curvature is common and calibration/training sample sizes
increase at a fixed finite training context set, b_theta tends to zero. Both
predictors tend to the same forecast even when their common eta prediction is
slightly slope-shrunk by the fixed ridge penalty. Therefore the true gain against
flexible tends to zero. A fixed strictly positive required gain against every
comparator cannot be asymptotically guaranteed by increasing held-out endpoints.
Finite training may give the restricted predictor a variance-reduction advantage,
but the replicate-specific sign and size must be measured, not assumed from a
common-curvature DGP label.

The proposed symmetric training x values log(1/2), log(4/5), log(5/4), log(2)
have xbar=0. Targets with x=0 approach the exact center tie as calibration grows,
even with nonconstant training curvature. This is a relevant limitation to
report. Dropping the flexible comparator or adjusting the gate after seeing
simulation decisions would change the frozen test.

## End-to-end simulation requirements

Each replicate must regenerate independent training endpoint counts, baseline
triad counts, both phase recovery counts and establishment counts. It must call
the existing builder, apply a fixed documented positive rationalization rule,
freeze forecasts and a plan hash, and then generate a complete fixed-frame
held-out seven-category ledger. Evaluation must call the unchanged certified
score engine. Fixed hypothetical counts such as 20/100 are useful conditional
fixtures, but do not represent repeated calibration operating characteristics.

The engine supports at most 500 full-frame units per context and requires
6 * cp_bits * sum(full_frame_totals) <= 600000. Numerical settings and resource
failures must be predeclared, not chosen after favorable observed counts.
Generating zero qualifying counts must remain unevaluable and remain in the
denominator of every unconditional decision frequency. Never resample a failed
replicate until all contexts qualify. All exclusion categories remain explicit.

Report probabilities of all-comparator success, any-comparator failure,
inconclusive and unevaluable over all fixed repetitions, with Monte Carlo
uncertainty. Per-comparator score margins help explain the global gate, but are
not replacements for it. Expected JS, expected log-score gain and interval
half-width are not rejection probabilities. Monte Carlo uncertainty is separate
from the score engine's illustrative study alpha.

The true evaluated score varies by replicate because forecasts are trained and
calibrated afresh. False success means the algorithm issues success while at
least one realized true comparator gain is <= the success threshold. False
failure means it issues failure while every realized true gain is >= the failure
threshold. A broad scenario label such as 'null' cannot replace those conditions.
Known rational synthetic truths and certified log intervals can bound each
replicate's true score; an interval straddling a threshold must remain unresolved.

## Count laws, selection, missingness and confounding

Fixed IID seven-category units imply multinomial W/A/M counts conditional on
their own qualifying total, with true conditional probabilities obtained by
normalizing those three joint-category probabilities. This is a coherent way to
retain nonqualification. It does not justify calling those conditional truths
latent all-category biological probabilities.

With route-independent missingness, the qualifying truth remains the stipulated
route truth. Route-dependent recovery/missingness generally changes that truth;
it need not break the observed conditional multinomial law. Correct observed
score coverage can therefore coexist with wrong biological interpretation.
Shared biological cluster effects require a justified count law at the cluster
unit; repeated descendants are not extra independent founders. Six marginal CP
control guarantees need binomial cell laws, not mutual independence across arms.

Choosing contexts using independent pre-outcome screening does not by itself
invalidate score coverage conditional on the chosen frozen forecasts and target
frame. It does change the study target. A reproducible-selection simulation
must regenerate every screened context and the full selection/confirmation rule
on every repeat, reporting failures to select as well. Reusing selected
calibration intervals for claims about true contrast requires selection-aware
coverage or independent confirmation. A six-cell Bonferroni region cannot be
reused as if it had covered a larger screened family.

The proposed design has fixed contexts and explicitly no screening, so it can
validly quantify only that fixed-context procedure. It should not claim to
quantify discovery/selection of a useful context pair.

Product-rule endpoint scenarios must explicitly assume the observed winner law
proportional to the appropriate supply, establishment and selected-phase
recovery. Binomial establishment controls alone do not imply that rule. A
constant-curvature scenario and a product-rule scenario are competing assumed
generative models, not mechanistic discoveries. The quadratic loglinear TMD
forecast remains observationally identical to its standard statistical
representation. Native transfer errors, nonstationary residents, interference,
frequency dependence, sparse supply and unknown genotypes remain unmodeled unless
their generative assumptions are separately supplied.

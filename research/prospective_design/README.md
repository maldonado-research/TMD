# A prospective discriminating test of Mutation by Natural Dominance

Research round R000003 · Original design candidate · 2 October 2026 (Pacific time)

This candidate defines a testable forecast and the measurements needed to interpret it. It is not a registered experiment: actual genotypes, sampling frames, contexts, sample sizes, stopping rules and decision thresholds remain unresolved in [REGISTRY_CANDIDATE.json](REGISTRY_CANDIDATE.json). No biological observation or new external source was acquired in this round. The preceding eligibility audit admitted zero complete matched Wsp/Aws/Mws panels within its inspected scope.

## The precise hypothesis and its mathematical limit

Here “natural dominance” means a defined heritable route's relative propensity to produce a specified successful outcome in a specified context. It is not a Mendelian dominance coefficient, a new inheritance rule or a demonstrated cause of mutation. Independently measured mutation supply, establishment through selection and drift, and assay recovery can each explain a common route.

For a biological conditional-triad baseline q with positive components, the proposed restriction is

    p_ci = q_ci exp(theta 1[i=A] + eta_c s_i) / Z_c,
    s = (1, 0, -1),
    J_c = p_cA^2 q_cW q_cM / (p_cW p_cM q_cA^2) = exp(2 theta).

Since 1[i=A] = 1 - s_i^2, exactly the same probabilities have the standard quadratic loglinear representation q_ci exp(-theta s_i^2 + eta_c s_i) after normalization. This is a statistical curvature restriction, with no identified special causal mechanism. One positive triad is saturated; a common theta across C contexts supplies C-1 restrictions. Forecasting a new context also requires eta to be fixed before its outcomes.

Conditional on fixed N and D=n_W-n_M, a multinomial likelihood eliminates eta. That can test theta when q is independently known, but it is a weaker conditional test, not a forecast of the full triad. It can be uninformative when the conditional count support has only one point. Training or scoring data cannot silently substitute for independently measured q.

## Biological and observation contracts

Choose a single common ancestral genotype and an operational endpoint before collecting outcomes. Lock a molecular genotype-to-route registry: explicit eligible alleles, compound events, ambiguous assignments, and “Other.” Phenotype, fitness and winner prevalence cannot define route membership. If a route contains alleles with different recovery or establishment, measure those alleles or justify a frozen aggregation bound. Different pathway-isolated ancestors do not form a common race.

The primary observational unit is one independently founded run/block with one predefined endpoint outcome. A block with multiple correlated descendants or paired arms does not create additional independent trials. Preserve founder, run, immediate ancestor, batch and context identifiers. Keep every member of a biological cluster, paired arms and nested technical replicates on the same side of the training/held-out split. Common genotype does not itself prove independence of run outcomes.

Each context requires these independent measurement components:

| Component | Eligible measurement | What it cannot silently replace |
| --- | --- | --- |
| Supply | Mutation production in the common background, with a defined event/division denominator, opportunity exposure, sequence/repair context and a validated sampling frame; baseline recovered triad counts b are usable only under that frame. | Mutant endpoint CFU fraction, selected isolate spectrum or a hotspot fraction is not automatically mutation probability per division. |
| Establishment | A known introduced eligible lineage, one binary operational establishment outcome per independent trial, measured before the separate recovery step. Supply, accessibility, establishment and recovery definitions must avoid double counting. | Growth rate, endpoint abundance, survival of an unknown mixture or repeated descendants is not an establishment probability. |
| Recovery/classification | Known introduced totals with binary correct recovery outcomes, by route/allele, context and baseline/selected phase. Challenge controls in relevant biological states, with blinded route classification. | Sequence reads, an uncertain concentration or a multi-cell well is not a known independent trial denominator. |
| Selected endpoint | One adjudicated W, A, M, Other, or no-qualified-outcome result per independent unit, with all exclusions and missing outcomes recorded. | An endpoint winner is not an exact first mutation, first establishment time or fixation event. |

No laboratory genotypes, eligible denominator frame or biologically justified transport bound has yet been selected. These are required inputs, not minor implementation details. A supply assay may require a fluctuation or lineage model rather than independent binomial counts; descendant jackpots cannot enter the current count-confidence construction as independent mutations. Every arm used by that construction needs its own justified marginal count law.

## One candidate forecast algorithm, frozen before held-out endpoints

This algorithm makes a forecast of **observed conditional-triad outcomes**. Its predictor is constructed independently of held-out selected endpoints. An observed forecast can be assessed even if its biological interpretation remains blocked; calling it a biological forecast additionally requires the observation contract below.

1. Designate complete training contexts and complete held-out contexts, preferably including a later independent batch. Use calibration units separate from the selected endpoint units used for held-out scoring; complete the independent baseline, establishment and recovery assays before unblinding selected held-out endpoints. Freeze the admissibility decision, contexts, route registry, context weights and all predictor bytes.
2. Form positive point predictors using fixed smoothing for prediction only. For a triad count vector k with total n, use (k_i+1/2)/(n+3/2). For an independent binary control with k recovered among n introduced, use (k+1/2)/(n+1). Missing or invalid denominators block a predictor; smoothing does not repair them. Raw zero counts retain their proper uncertainty endpoints in inference.
3. Let b_c be the baseline point vector and d_hci the phase-specific recovery point vector. Define the operational selected-frame supply predictor

       qstar_ci proportional to b_ci d_1ci/d_0ci.

   It is a point prediction convention, not a claim that the controls identify biological supply. Under exact matched transfer, b proportional to q_bio r_0 and d_1/d_0 proportional to r_1/r_0, this is the supply-and-observation offset appropriate to observed selected outcomes. Without that transfer, it remains a declared operational predictor.
4. In each training context, compute l_ci=log(t_ci/qstar_ci) from its smoothed selected triad t. Set theta_c=l_cA-(l_cW+l_cM)/2 and eta_c=(l_cW-l_cM)/2. Use the equal-context mean of theta_c as theta_hat. Do not select contexts or weights because their curvature agrees.
5. Independently measure route-specific establishment F_ci, with the binary predictor above. Define the dimensionless calibration feature x_c=log(F_cW/F_cM)/2. Fit eta_c=beta_0+beta_1 x_c by least squares on training contexts only, minimizing sum(eta_c-beta_0-beta_1 x_c)^2 + 0.01 beta_1^2. The intercept is unpenalized and features are not rescaled. The closed form uses centered sums; zero training feature variation gives beta_1=0. Missing held-out x blocks the forecast. Laboratory range/extrapolation admissibility remains to be frozen in the registry.
6. Forecast eta_new=beta_0+beta_1 x_new and observed triad probabilities proportional to qstar_new exp(theta_hat 1_A+eta_new s). Store counts, smoothing rule, training identifiers, coefficients, feature value and forecast probabilities before unblinding. The penalty 0.01 is an operational candidate choice, not a population-genetic constant. A covariate fit and training theta estimate are prediction conventions, not causal identification.

The candidate choice may be revised using training-only design work before the study is frozen. Any later change creates a different candidate; it cannot be fitted to held-out outcomes and reported as the original forecast.

## Strong comparators with the same information

Freeze all comparator probabilities before held-out endpoints:

* **Supply and observation:** qstar alone.
* **Supply, establishment and observation:** normalize qstar_ci F_ci, with no winner-derived establishment estimate.
* **Flexible context response:** regress the two training offsets log(t_A/t_W)-log(qstar_A/qstar_W) and log(t_M/t_W)-log(qstar_M/qstar_W) separately on intercept and the same x, with the same slope penalty 0.01. Forecast normalize qstar times (1, exp(g_A), exp(g_M)). This permits feature-varying curvature. Because the ridge operator is linear, g_A=theta_c-eta_c and g_M=-2 eta_c imply the same forecast eta as the restricted predictor, while flexible theta is a ridge prediction of theta_c rather than its constant mean. This is a frozen flexible predictor; it cannot refit held-out winners. Its penalty geometry differs from the restricted parameterization, so penalized fits are not a likelihood-ratio nested-model test.

All models receive the same admitted training outcomes and independent target-context assays. Record hotspot/sequence and repair background, demographic drift, accessibility, allele aggregation, clonal interference and differential recovery as competing explanations. A successful restricted forecast does not distinguish these mechanisms. If measured supply and establishment forecast as well or better, retain that absence of incremental support.

## Error allocation, scores and a fixed study

The primary score is expected log-score gain in nats per **observed qualifying triad outcome**, with strictly positive frozen predictions. Report Other, no-qualified-outcome, unresolved classification and missingness counts beside their denominators. Excluding those categories changes the estimand; it cannot establish an all-category forecast or absence of competing routes. A fixed clipping rule, if needed, must precede testing and constitutes a changed forecast.

For held-out context c and frozen comparator m,

    Delta_cm = sum_i t_ci log(pi_TMD,ci / pi_m,ci).

Here t is the true observed conditional-triad probability, not an automatically recovered latent biological p. Predeclare nonnegative context weights w summing to one. The overall target is sum_c w_c Delta_cm; weights cannot follow favorable observed sample sizes or results.

Given independent trials with justified conditional multinomial marginals, use simultaneous Clopper-Pearson marginal intervals with Bonferroni allocation over every held-out context/category cell. Intersect each context's box with its probability simplex. Correct marginal laws suffice; independence between different marginal intervals is not required. Within-cell correlated biological descendants invalidate a simple binomial count model and require another justified procedure. A numeric empty box/simplex intersection is unevaluable rather than a biological rejection.

For fixed forecasts, score gain is linear in t. Project this **one simultaneous region** through every frozen comparison and the declared context weights. On the event that the region covers t, all projected comparisons cover their targets together, so adding frozen comparators does not require another Bonferroni division. Training uncertainty changes the forecast that was fitted; the outcome interval evaluates that realized frozen forecast conditional on its independent training/calibration information. It is not an uncertainty interval for latent regression parameters, all future contexts or a causal effect.

The verification script checks the simplex projection and CP definitions in floating arithmetic. It is not a certified score-decision engine: logarithms generally need directed enclosures for rigorously certified numeric decisions. Use the existing certified rational interval methods for their J target, and choose a declared appropriate implementation for prospective score decisions before inferential execution.

The study's total alpha, count/transfer allocations, meaningful effect threshold, primary success/failure gates, number of contexts, number of independent trials per arm and fixed stopping rule remain null. Thus no formal decision or sample-size claim can be made yet. Plan precision and power before collection with independent design simulation, realistic sparse supply, measured recovery and plausible weak effects. For example, with uniform q, eta=0 and theta=log(1.5), the ideal restricted model's gain over q is only 0.01962008079052644 nats: arbitrarily choosing a 0.02-nat improvement requirement would exceed that scenario's oracle gain. It is a synthetic warning about threshold selection, not an effect estimate or a power calculation.

Repeated research rounds do not renew a study's error budget. Fixed stopping must be chosen before outcomes; interim looks need a separately calibrated sequential rule.

## Biological contrast and control transfer are a separate branch

The simultaneous contrast analysis can test a common theta only under its measurement and transport assumptions. Write residual differential recovery

    e_ci = (r_1ci/r_0ci) / (d_1ci/d_0ci),
    J_corrected,c = J_biological,c e_cA^2/(e_cW e_cM).

Prespecified independently justified bounds L_ci <= e_ci <= U_ci give

    m_lo = L_A^2/(U_W U_M),  m_hi = U_A^2/(L_W L_M),
    J_biological in [J_corrected,lo/m_hi, J_corrected,hi/m_lo].

Retain zero/infinite endpoints. Reject the common-contrast restriction only for an empty cross-context intersection under the frozen valid region and admitted transfer bounds. Overlap is compatibility, not equality. Estimated transfer bounds consume their simultaneous noncoverage budget; a union bound with the count budget gives the combined guarantee without component independence. Unknown transfer is unbounded and can block biological interpretation.

Contrast-only recovery bounds do not identify a whole probability observation map, the Other category or eta. For example, uniform biological triad probabilities with selected recoveries (0.6,0.9,0.6) generate apparent theta=log(1.5) and J=2.25. Different recoveries (0.9,0.6,0.4) preserve J=1 while changing all triad probabilities. An all-category biological forecast needs independently measured route-specific observation/classification probabilities, their transfer bounds and a defined no-event/censoring model; the differential J bound alone cannot supply them. Paired baseline data and explicitly bounded routewise residuals can support a stronger observation model, but its assumptions must be separately frozen.

The primary transport challenge is a matched route-by-phase assay in every context. An optional maximum/conformal transfer envelope across contexts requires scientifically justified exchangeability of a declared scalar discrepancy. At target failure level a, a finite distribution-free maximum envelope needs at least 1/a-1 calibration contexts for one exchangeable target (integer-rounded upward); simultaneous H-target allocation requires at least H/a-1. Estimated calibration residuals also need a valid simultaneous measurement bound and error allocation before their maximum can bound true transfer. Deliberately chosen media are not automatically exchangeable. This optional design is not a substitute for presently missing bounds.

Pooling is also unsafe: equal-weight mixtures of the uniform-q contexts eta and -eta have apparent pooled theta=theta-log(cosh(eta)). At theta=0, eta=1 this becomes -0.4337808304830271 despite zero curvature in both contexts. The formula has these symmetry assumptions, not arbitrary contexts. Preserve within-context sampling and predeclared weighted scores.

## Completion boundary and reproducibility

[verify_design.py](verify_design.py) checks algebraic equivalence, single-context reconstruction, conditional eta cancellation, the qualified pooling example, recovery artifacts, CP probability-region coverage in a small finite example, score projection against explicit vertices and the frozen prediction implementation. Every input is synthetic. The receipt reports computations actually executed; it supplies no biological replication or general power guarantee.

Run without dependencies or edits to the public package:

```sh
python research/prospective_design/verify_design.py --check
```

The next substantive step is an authenticated laboratory/source measurement specification resolving the registry's null fields, followed by blinded design simulation and independent review before registration or collection. This round can finish as **design_only**, while the confirmatory experiment stays blocked. Standard quadratic loglinear models, binomial confidence intervals and linear score projection are established mathematics; this candidate claims no new theorem, breakthrough or biological discovery.

Original documentation is CC BY 4.0 and new code is MIT under the repository terms. Prepared with AI assistance; independent internal review is recorded separately and is not external peer review.

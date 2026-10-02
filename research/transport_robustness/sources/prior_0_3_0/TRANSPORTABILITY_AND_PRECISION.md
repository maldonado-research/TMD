# What if the controls do not fully transfer?

Methods extension 0.3.0, 30 September 2026. This is an application of standard log contrasts, interval arithmetic, the multinomial delta method and constrained allocation. No external mathematical priority is asserted.

## The exact residual bias

Use route order Wsp, Aws, Mws, abbreviated W, A, M in the data schema, and weights v = (−1/2, 1, −1/2). Let q and p be the biological baseline and selected route distributions. The four observed probability vectors are b, t, a0 and a1; r0 and r1 are independently known positive control input compositions. Recovery is route specific and all relevant probabilities are strictly positive.

For biological baseline and selected recovery d0b and d1b, and control recovery d0c and d1c:

```text
b  ∝ q  × d0b          a0 ∝ r0 × d0c
t  ∝ p  × d1b          a1 ∝ r1 × d1c
h0 = d0b / d0c         h1 = d1b / d1c
rho = log(h1) − log(h0)
theta_bio = v · (log(p) − log(q))
theta_corr = v · (log(t) − log(b) − log(a1) + log(r1) + log(a0) − log(r0))
theta_corr = theta_bio + v · rho
```

Products and division are routewise. Normalizing constants disappear because the weights sum to zero. Relative control recovery must transport to the biological samples for the corrected contrast to equal the biological contrast. A common recovery multiplier for every route in an assay branch cancels; a route-dependent mismatch need not cancel. Absolute recovery probabilities cannot be inferred from these conditional multinomial counts.

## Partial identification instead of assuming exact transport

Suppose independent knowledge justifies routewise bounds lower_i ≤ rho_i ≤ upper_i. For positive weights use the lower endpoint to minimize bias; for negative weights use the upper endpoint. This gives sharp lower and upper bias bounds L and U over the stated rectangular uncertainty set. Hence:

```text
theta_bio ∈ [theta_corr − U, theta_corr − L]
```

“Sharp” means the extrema occur at allowed corners of the supplied box. It does not authenticate the box, establish physical joint feasibility under additional constraints, or imply probability coverage. Add any known cross-route restrictions instead of silently discarding them. Unknown transport with no finite restrictions leaves biological theta unbounded. Equal route shifts cancel even if the shift itself is unknown.

For a symmetric log mismatch bound |rho_i| ≤ epsilon, the contrast bias lies in [−2 epsilon, 2 epsilon]. Two contexts' corrected contrasts can differ by up to 4 epsilon solely through allowed opposite biases. At epsilon=0.1 this permits a difference of 0.4. This value is an illustration, not a measured tolerance. A common biological contrast is structurally compatible with multiple contexts only if their biological-theta intervals intersect. Compatibility is not confirmation; a disjoint intersection rules out a common contrast only conditional on the observation model and justified bounds.

Bounds must apply to the **difference of two branch transport log ratios**. If each branch separately has |log(hj_i)| ≤ e, the conservative bound on |rho_i| is 2e, not e. Uncertain r0/r1 introduce additional log-composition error; the present implementation treats r as known and does not silently omit this uncertainty.

## Sampling uncertainty from all four arms

With independent multinomial samples and recovered totals M, N, H0 and H1, the positive-cell delta variance is:

```text
A(x) = sum_i v_i² / x_i
Var(theta_corr) ≈ A(b)/M + A(t)/N + A(a0)/H0 + A(a1)/H1
```

The off-diagonal multinomial terms reduce to −(sum_i v_i)²/total = 0. Controls are random observations, so their variance remains in the calculation. Shared batches or reused units require covariance terms and a different supported design; separate files do not establish independence.

An analytic example with all three routes equally frequent and 100 recovered independent observations in each arm gives variance 0.18 and standard error 0.4243. Treating the control outcomes as known constants would give standard error 0.3000: the proper value is 41.4% larger. This compares equal biological sample totals, not equal total sampling budgets. It is an uncertainty calculation, not a power measurement.

`simultaneous_sensitive_intervals` constructs positive-count, normal-approximation intervals with Bonferroni critical value z_(1−alpha/(2C)), then widens each by its assumed bias bounds. Bonferroni itself does not require independent contexts, but the within-context variance requires independent arms. Coverage is asymptotic under the stated model; small cells, unmodeled dependence and bounds that miss the true transport invalidate it. A shared-theta intersection is only a compatibility screen, not a substitute for the joint likelihood/bootstrap test. The helper declines zero cells and offers no pseudocount interval.

## Allocate the budget to informative observations

For planning probabilities and per-recovered-unit costs c_g, minimize sum_g A_g/n_g subject to sum_g c_g n_g = B. The continuous allocation and minimum variance are:

```text
n_g = B sqrt(A_g/c_g) / sum_h sqrt(A_h c_h)
minimum variance = [sum_h sqrt(A_h c_h)]² / B
```

Equal costs give n_g proportional to sqrt(A_g). Equal probabilities and equal costs give equal allocation to all four arms. This is a local regular-model forecast; actual recovery yield, per-context overhead, batch structure, power, integer rounding and uncertainty in planning probabilities need laboratory-specific treatment. Sample sizes here count **recovered independent categorical units**, not sequencing reads or exposed fixed-route inputs.

## Reproduce

From the extracted package root:

```sh
python3 design/transport_sensitivity.py
python3 -m unittest discover -s design -p 'test_transport_sensitivity.py' -v
```

The tests compare box bounds with all corners, verify signed subtraction and common-scale cancellation, recover a contrast under unequal input mixtures/recovery, check control variance, verify the allocation's budget and optimality conditions, and ensure unsupported zero/dependent inputs decline. The checked-in JSON contains analytic planning examples only.

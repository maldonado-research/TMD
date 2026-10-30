# Independent calibration oracle check

This check reads the hypothetical example in [the context-contrast note](../model_disagreement/README.md). It does not edit the repository or modify the frozen analysis. All six count records are synthetic. The 0.05 calibration allocation below is illustrative and does not replace an existing registered error allocation.

Run `python -B independent_check.py`. The standalone standard-library script uses 80-digit Decimal arithmetic and inverts binomial tail probabilities by bisection. The script prints its numerical output. An additional independent numerical check using SciPy beta quantiles and six-dimensional differential evolution returned the same corner minimum within floating-point precision. The proof below, not the numerical optimizer, establishes global sharpness.

## Confidence construction and distinction from point forecasts

Let the six latent establishment probabilities be f_ci. For each fixed route/context cell assume the marginal count law K_ci ~ Binomial(100, f_ci). At illustrative family error alpha = 0.05, assign alpha/6 to each two-sided Clopper–Pearson interval, or alpha/12 = 1/240 to each tail. For 0 < k < n the bounds are

L_k = BetaQuantile(1/240; k, n-k+1),
U_k = BetaQuantile(239/240; k+1, n-k).

Equivalently, P_(L_k)(K >= k) = 1/240 and P_(U_k)(K <= k) = 1/240. The six-dimensional rectangle has simultaneous coverage at least 0.95 by the union bound.

| k out of 100 | L_k | U_k |
|---|---:|---:|
| 10 | 0.037201814163155080 | 0.204653017048016235 |
| 20 | 0.106658304479594910 | 0.324256396188766449 |
| 80 | 0.675743603811233551 | 0.893341695520405090 |

Four cells have k=20, but their unknown probabilities remain separate coordinates. Equal observed counts do not justify pooling controls or imposing equality of true probabilities. The rectangular parameter set allows each coordinate to vary independently; this statement is distinct from assuming stochastic independence of all six counts.

These intervals concern latent Bernoulli probabilities f_ci. They are not confidence intervals for the already realized deterministic smoothed predictors Fhat_ci=(k_ci+1/2)/101. In particular, do not apply smoothing to the interval endpoints and then claim unchanged frequentist coverage for f_ci.

## Sharp full-vector minimum

Condition on fixed uniform q* and additionally posit the product law p_ci=f_ci/sum_i f_ci. This law is an assumption here, not a consequence of the binomial calibration model.

For equal context weights define JS(p1,p2)=[KL(p1||m)+KL(p2||m)]/2, with m=(p1+p2)/2 and natural logarithms. Coarsen the three routes to A versus {W,M}. The log-sum inequality gives

JS(p1,p2) >= JS_Bernoulli(p1A,p2A).

Throughout the rectangle,

p1A <= a = U_10/(U_10+2 L_20) = 0.489636098687438811,
p2A >= b = L_80/(L_80+2 U_20) = 0.510281548011424152.

Thus a < b. Writing H for binary entropy,

JS_Bernoulli(u,v)=H((u+v)/2)-[H(u)+H(v)]/2.

For u<v, its partial derivative in u is [H'((u+v)/2)-H'(u)]/2 < 0 and its partial derivative in v is [H'((u+v)/2)-H'(v)]/2 > 0, since H' is strictly decreasing. Hence the binary minimum is at u=a, v=b.

Both inequalities attain equality at the feasible controls

f1=(L_20,U_10,L_20),
f2=(U_20,L_80,U_20).

Their product-law vectors are

p1=(0.255181950656280595, 0.489636098687438811, 0.255181950656280595),
p2=(0.244859225994287924, 0.510281548011424152, 0.244859225994287924).

The W/M conditional distribution is (1/2,1/2) in both contexts, so coarsening loses no JS. The sharp minimum over the entire original six-dimensional rectangle is therefore

**0.0002131324325820320180102990593953074 nats per endpoint.**

The point-forecast JS is 0.1116667616609811957639717419868908101 nats. The rectangular minimum is 0.0019086470263111887 times that value, approximately 0.1909%, or about 524 times smaller. This is the sharp minimum for this chosen confidence rectangle; it is not a claim that this confidence construction is optimal.

The same box gives x_c in [-0.555952120277907312, 0.555952120277907312] independently for either context. It gives z1 in [-2.165177021187852794, 0.651685636758445828] and z2 in [0.734279170688979913, 2.125338836901375171], with minimum z2-z1 = 0.082593533930534085. Equal estimated x does not certify equal true x, although the minimizing controls above happen to satisfy x1=x2=0.

## Why this does not lower-bound the gain of fixed forecasts

Let r1=(41,21,41)/103 and r2=(41,161,41)/243 be the actual fixed point forecasts. For any candidate truth pair p1,p2, the expected log-score gain of these forecasts over the best common oracle forecast m=(p1+p2)/2 is

JS(p1,p2) - [KL(p1||r1)+KL(p2||r2)]/2.

At the attainable rectangle minimum above, the misspecification term is 0.1255926063732636059557312584626919145 nats. The fixed forecasts' gain over that best common predictor is **-0.1253794739406815739377209594032966071 nats**. Therefore a positive lower bound on oracle JS does not imply that the realized fixed supply–establishment forecasts have positive expected advantage. This example does not identify the score of the actual frozen fitted TMD candidate: its coefficients cannot be replaced with the oracle common mean after outcomes.

The original 0.111666761661 conditional oracle calculation remains mathematically correct when the point vectors themselves are stipulated to be the true endpoint laws. Calibration sensitivity changes what can be claimed about latent truths under uncertainty; it does not change the two stored forecast vectors or the exact calculation on them.

## Scope of the confidence and biological claims

- The individual CP guarantees require the declared binomial count law. Fixed known trial denominators, correct success/failure definitions, appropriate within-cell independence and stable trial probabilities are one sufficient route to it. Clustering, repeated subunits, overdispersion, heterogeneous latent probabilities or optional stopping need their own justified count-law treatment; marginal binomial calibration cannot be assumed from n=100 alone.
- Bonferroni simultaneous coverage does not require the six cell counts to be mutually independent, provided each cell's marginal interval guarantee holds. Independence between calibration/training and evaluated endpoint outcomes serves a separate role in freezing forecasts and avoiding outcome-dependent fitting.
- The six-interval allocation applies to the declared six-cell problem. Screening many context pairs and reporting a favorable pair requires accounting for that selection, enlarging the simultaneous family, or using independent confirmation. These synthetic counts have no selection history to validate.
- Fixed known uniform q* is an imposed simplification. Estimated offsets and recovery factors require their own uncertainty treatment. Control-to-target transport is also assumed exact; any defensible transport-error set must be propagated along with calibration uncertainty.
- The calibration binomial law alone does not imply endpoint route probabilities proportional to q*f. Origin competition, frequency dependence, resident changes, observation processes and other departures can invalidate that product interpretation.
- Under the count law, fixed context selection, fixed q*, exact transport and the product law, projecting the simultaneous box yields a conservative lower confidence bound on the oracle JS functional. With these synthetic records this is an illustration of a procedure, not empirical coverage evidence, an observed effect, a power calculation, a sample-size claim, or evidence for either biological mechanism.
- Evaluation of the realized independently frozen predictors can proceed under its own held-out sampling assumptions without equating the predictors with true establishment or endpoint probabilities. Its actual performance needs endpoint evidence and the registered scoring/uncertainty procedure.

An optional mathematical transport sensitivity illustrates the narrow residual separation: if each true target-control probability were allowed an additional independent additive error of magnitude epsilon, expanding every CP interval by epsilon, the two symmetric feasible product-law vectors first coincide at epsilon = (L_80 L_20-U_10 U_20)/(U_10+U_20+L_80+L_20) = 0.0043571783256117231. This value is a sensitivity boundary, not an estimated or justified biological transport tolerance.

## Review of the proposed companion implementation

The independently authored `calibration_sensitivity.py`, `README.md` and `results.json` were also inspected. A fresh run reproduced the saved JSON exactly. Each of the six independently computed 80-digit CP roots lies strictly inside that implementation's exact dyadic bracket. Its full-box sharpness argument and all score decomposition signs agree with this check.

Its strictly interior rational witness f1=(0.107,0.204,0.107), f2=(0.324,0.676,0.324) avoids any reliance on outward bracket corners being inside the exact CP interval. Independently recomputing expected log-score gain of the fixed point forecasts against the common vector (1/4,1/2,1/4) gives -0.1241925344787818735569799433345060632 nats, agreeing with the companion output. This common vector belongs to the parameterized common family but is not identified as the actual frozen TMD forecast.

Review outcome: no mathematical or implementation defect found. This is internal computational review, not external peer review or biological validation.

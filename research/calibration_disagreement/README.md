# Calibration uncertainty in the two-context forecast contrast

Ricardo Maldonado · 30 October 2026 · Original conditional design analysis with AI assistance

**The hypothetical contrast is much less robust to calibration uncertainty than its point calculation suggests.** Under the particular simultaneous control region below, the smallest oracle separation is approximately **0.00021313 nats per endpoint**, compared with **0.11166676** at the frozen point vectors. Moreover, the actual point forecasts can lose to a common forecast for control probabilities inside that region. This is a prospective sensitivity calculation, not biological evidence, a power result, or a change to the frozen study.

The starting point is the [27 October design note](https://github.com/maldonado-research/TMD/blob/c9ff3d68d640d6eb024024bec378743620a31748/research/model_disagreement/README.md). It gives hypothetical establishment successes `(20,10,20)` and `(20,80,20)` in route order W/A/M, each from 100 trials. Uniform fixed `q*`, equal context weights, and the existing smoothing rule produce the two conventional point forecasts

\[
f_1=(41,21,41)/103,\qquad f_2=(41,161,41)/243.
\]

The candidate TMD forecast has a common vector here because its independently frozen inputs `q*` and `x` coincide. Its actual fitted coefficients are not supplied. The existing note correctly labels its 0.11166676 calculation as an oracle calculation under hypothetical truths equal to these point forecasts; this follow-up quantifies the importance of that condition.

## An explicitly separate illustrative calibration budget

Assume each of the six control counts has its declared binomial marginal law. Give each Clopper–Pearson (CP) tail probability

\[
\tau=0.05/12=1/240.
\]

The six two-sided intervals have joint coverage at least 95% by a union bound. Dependence between the six arms does not invalidate that bound if their individual binomial laws hold. Correlated trials within an arm need not have that law. This is an **illustrative standalone allocation**, not the frozen study's unresolved allocation. Combining this region with outcome, selection or transport guarantees requires a separately specified budget and sampling contract.

| Successes / 100 | CP lower | CP upper |
|---|---:|---:|
| 10 | 0.03720181 | 0.20465302 |
| 20 | 0.10665830 | 0.32425640 |
| 80 | 0.67574360 | 0.89334170 |

The script brackets each CP root using exact binomial-tail comparisons on a dyadic grid. It uses the outward endpoints, each at most `2^-64` from its root. Decimal logarithms are calculated with 60-digit working precision; displayed transcendental results are numerical approximations, not certified logarithm intervals. The exact fractions and root brackets are retained in [results.json](results.json).

This region expresses sampling uncertainty about six hypothetical control probabilities. It is not a posterior distribution, a claim that its corners are likely, or an estimate of calibration errors in a real experiment. Native control transfer, supply uncertainty, unknown genotypes and endpoint observation effects are excluded from this calculation, rather than resolved by it.

## Sharp minimum over all six control probabilities

For this sensitivity analysis only, suppose the outcome laws satisfy the conventional product rule

\[
p_{ci}=F_{ci}/\sum_jF_{cj}.
\]

This uses uniform known `q*` and does not establish that biological winners follow the product rule. Let `L_k,U_k` be the CP bounds for a count of `k`. Monotonicity gives the attainable A-probability intervals

\[
a_1\in\left[\frac{L_{10}}{L_{10}+2U_{20}},
\frac{U_{10}}{U_{10}+2L_{20}}\right],\quad
a_2\in\left[\frac{L_{80}}{L_{80}+2U_{20}},
\frac{U_{80}}{U_{80}+2L_{20}}\right].
\]

Their closest endpoints are

\[
u_1=0.4896360987,\qquad l_2=0.5102815480.
\]

For any positive common probability vector `r`, with `m=(p1+p2)/2`,

\[
\tfrac12\sum_c D_{KL}(p_c\Vert r)
=JS(p_1,p_2)+D_{KL}(m\Vert r).
\]

Thus `JS` is the oracle's expected log-score advantage over the best common predictor. Pooling W and M cannot increase KL divergence, so

\[
JS(p_1,p_2)\ge JS(\operatorname{Bern}(a_1),\operatorname{Bern}(a_2)).
\]

For `a<b`, the derivative of Bernoulli JS with respect to `a` is
`[logit(a)-logit((a+b)/2)]/2 < 0`; its derivative with respect to `b` is positive. The minimum for these disjoint intervals is therefore at `(u1,l2)`. Equality in the pooling bound is attained by equal W/M shares in both contexts. The six values

\[
F_1=(L_{20},U_{10},L_{20}),\quad
F_2=(U_{20},L_{80},U_{20})
\]

attain exactly those shares and interval endpoints. This proves the minimum over the **full six-dimensional Cartesian box**, rather than just a symmetric subset. For overlapping A intervals the same reasoning gives zero if a common A probability with equal W/M shares is feasible; that is not the present case. Different route offsets or asymmetric bounds require a new minimization.

The result is

\[
\min JS=0.000213132432582\ \text{nats per endpoint},
\]

about 524 times smaller than the original point calculation. This is sharp for the script's very slightly enlarged outward CP box. The control curvature intervals are `z1=[-2.1651770,0.6516856]` and `z2=[0.7342792,2.1253388]`, leaving only `0.0825935` separation in `z=log(F_A/sqrt(F_W F_M))` under the same region.

## The frozen comparator is not the oracle

The preceding minimum grants the conventional comparator the true laws `p_c`. The actual frozen forecasts remain `f_c`. Their expected gain over the best common vector is instead

\[
G_f(p)=JS(p_1,p_2)-\tfrac12\sum_cD_{KL}(p_c\Vert f_c).
\]

At the minimizing corner, the second term is approximately `0.1255926064`, and the gain is **−0.1253794739 nats per endpoint**. This is an admissible witness for the enlarged box, not a claimed global minimum of `G_f`. It shows why positive oracle separation cannot be treated as guaranteed performance of the finite-calibration point predictor.

The conclusion does not depend on dyadic endpoints or a common predictor chosen after seeing hypothetical truths. The rational control vectors

\[
F_1=(0.107,0.204,0.107),\quad F_2=(0.324,0.676,0.324)
\]

are strictly inside the exact CP intervals, as verified using the inner root brackets. At these truths the point forecasts lose **0.1241925345 nats per endpoint** to the illustrative common vector `(1/4,1/2,1/4)`. That vector belongs to the common TMD family with `eta=0` and `theta=log(2)`, but it is not an actual fitted or frozen TMD forecast. This counterexample establishes no universal ordering of the project's realized algorithms.

## What this changes about the next analysis

The design should assess whether calibration precision leaves useful, reproducible predictive disagreement before selecting endpoint conditions. A complete operating-characteristic analysis must simulate or enumerate independent training, calibration, any context-screening/confirmation stage, and held-out endpoints; reconstruct the actual frozen predictors; and apply the declared outcome score procedure. It must include near-null and weak alternatives, qualify endpoint counts, and retain unresolved outcomes. That would address the currently unresolved power/design entry; this calculation does not fill it.

For perspective, at the minimizing laws 500 qualifying endpoints in each context give only `1000 * JS = 0.21313` total expected oracle advantage over the best common predictor. An expectation is not a rejection probability, achieved power, Bayes factor, or sample-size recommendation. No conclusion about the existing score engine's power follows from this number alone.

Valid comparison of independently frozen forecasts on observed endpoints does **not** require the control probabilities to be known truth. Its sampling and observation assumptions still matter. This sensitivity result concerns interpreting a point-calibrated context contrast as reliably discriminating biological laws. It does not create a new barrier to scoring already frozen predictions.

## Reproduce

Python 3.11 or later; standard library only:

```sh
python -B calibration_sensitivity.py --output /tmp/tmd-calibration-results.json
```

The script has no network operations. It preserves exact root-bracketing checks, probability normalization, full-box attaining values and the strict interior counterexample. The accompanying [independent check](INDEPENDENT_CHECK.md) and `independent_check.py` use a separate numerical implementation; internal computational review is not external peer review. No native data, registry value, forecast algorithm, success threshold or stopping rule is changed.

Original documentation and original code follow the TMD repository's documentation and software licensing respectively. Established CP intervals, Bonferroni coverage, KL identities and information monotonicity are used without a claim of new mathematics.

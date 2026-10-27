# A context contrast that can distinguish the frozen route predictors

Ricardo Maldonado · 27 October 2026 · Original design analysis with AI assistance

This note identifies a potentially informative context contrast. It supplies no biological observations, selected study conditions, fitted predictor, sample-size claim or new mathematical theorem. It does not change the frozen TMD candidate, comparators, study registry, error allocation or stopping rule.

An independent synthetic check runs this example through the existing forecast builder and compares it with the exact fractions below. From the repository root, run `python -B research/model_disagreement/verify_disagreement.py --repo .`. It also verifies the owner's stored receipt and checks that the inspected files are unchanged. This is an implementation check, not an empirical test.

The current TMD candidate uses independently measured establishment through only

\[
x_c=\tfrac12\log(F_{cW}/F_{cM}),\qquad
\widehat\eta_c=\widehat\beta_0+\widehat\beta_1x_c,
\]

and predicts

\[
\pi^T_{ci}\propto q^*_{ci}\exp(\widehat\theta\,1_{i=A}+\widehat\eta_cs_i),
\qquad s=(1,0,-1).
\]

Its existing flexible comparator also uses only x. Consequently, contexts with the same admitted q* and x receive identical predictions from each of those algorithms. Neither can respond to a change in F_A alone. The existing supply–establishment comparator, \(\pi^F_i\propto q^*_iF_i\), can respond. This is a concrete design distinction, not an undisclosed error in the existing specification. See [the candidate, steps 5–6 and comparators](../prospective_design/README.md).

## Exact identity and an informative contrast

For positive F, define

\[
z_c=\log\frac{F_{cA}}{\sqrt{F_{cW}F_{cM}}},\qquad
g_c=\tfrac12(\log F_{cW}+\log F_{cM}).
\]

Then \(\log F_{ci}=g_c+z_c1_{i=A}+x_cs_i\): substituting W, A and M verifies each component. The common \(e^{g_c}\) cancels in normalization, proving

\[
\pi^F_{ci}\propto q^*_{ci}\exp(z_c1_{i=A}+x_cs_i).
\]

Thus this conventional comparator has curvature \(\theta_c=z_c\) and tilt \(\eta_c=x_c\). Its \(q^*\)-adjusted contrast is

\[
J_c^F=\frac{(\pi^F_{cA})^2q^*_{cW}q^*_{cM}}
{\pi^F_{cW}\pi^F_{cM}(q^*_{cA})^2}=e^{2z_c}.
\]

The identity is established log-product algebra. Its experimental implication is useful: seek independently calibrated contexts where x is similar and z differs, before inspecting selected endpoint outcomes. Varying only x can leave the principal curvature restriction weakly challenged. Exact equality of q* is helpful for illustration but unnecessary for a real comparison, provided each context's admitted q* is included in its full forecast.

**Entirely hypothetical example implementing the frozen smoothing rule:** let q*=(1/3,1/3,1/3), with route order W/A/M. Assume each route has n=100 independently admitted establishment trials in each context. Take W=M=20 successes in both contexts and A=10 versus 80 successes. The frozen binary point rule \(F=(k+1/2)/(n+1)\) gives the vectors below. These are assumed control records and their point predictors, not actual observations or known biological establishment probabilities. Uniform q* is an assumed independently frozen offset; equal baseline route counts and equal recovery ratios are one compatible construction.

| Quantity | Context 1 | Context 2 |
|---|---:|---:|
| Hypothetical successes k, each n=100 | (20, 10, 20) | (20, 80, 20) |
| Smoothed establishment predictor F | (41, 21, 41)/202 | (41, 161, 41)/202 |
| x | 0 | 0 |
| z | log(21/41) | log(161/41) |
| Supply–establishment prediction | (41, 21, 41)/103 | (41, 161, 41)/243 |
| J under that prediction | 441/1681 | 25921/1681 |

Every fixed TMD candidate gives the same vector in both contexts:

\[
\pi^T=\frac{(e^{\widehat\beta_0},e^{\widehat\theta},e^{-\widehat\beta_0})}
{e^{\widehat\beta_0}+e^{\widehat\theta}+e^{-\widehat\beta_0}}.
\]

It therefore cannot equal both distinct conventional vectors. This conclusion requires no choice of its unknown fitted coefficients and does not fit them to hypothetical test outcomes.

For equal context weights, if the two conventional vectors were the true outcome laws, even the best common prediction would incur an average expected log-score loss of **0.111666761661 nats per qualifying endpoint** relative to them. To see this, their mean is m=(7093,10843,7093)/25029, and for any positive common prediction r,

\[
\tfrac12\sum_{c=1}^2D_{KL}(\pi_c^F\Vert r)
=\tfrac12\sum_{c=1}^2D_{KL}(\pi_c^F\Vert m)+D_{KL}(m\Vert r).
\]

The first term is the stated number; the second is nonnegative. This is an oracle design calculation under hypothetical truths, **not** an observed effect, power estimate, effect threshold or fitted TMD result.

## Feasibility, uncertainty and interpretation

1. Use independent calibration or training information to identify a plausible z contrast, and document every candidate context screened. Lock the selected contexts, weights, forecasts and success/failure thresholds before endpoint outcomes. Selection using calibration affects the target frame and calibration uncertainty; it cannot be justified using favorable endpoint results. If screening estimates are reused inferentially, account for their selection or obtain independent confirmation.
2. Establishment must retain the existing operational definition and known trial denominator. Record route/allele, resident composition, starting frequency, density, introduction time and growth phase. A 1:1 competition coefficient, endpoint abundance or successful recovery fraction is not automatically F. Propagate uncertainty and justified transport error into the possible z separation and full-vector disagreement. Approximate x matching has uncertainty; zero counts do not justify plugging zero into logarithms or claiming infinite contrasts. Existing smoothing defines positive forecasts, not exact biological probabilities.
3. The algebra proves what the declared q*F predictor says. It does not prove that observed winners follow q*F. Such an interpretation needs an admitted generative and observation model; competing mutation origins, clonal interference, frequency dependence, changing residents and route-dependent observation can break a simple product rule. A richer conventional model must use independent/training information and be separately frozen before outcomes. Failure of q*F alone would not establish failure of ordinary evolutionary models.
4. Evaluate complete positive route vectors on independent endpoint units with the existing conditional-triad estimand and uncertainty procedure; retain Other, no-qualified-outcome, ambiguous and missing counts. Do not refit eta or theta on held-out outcomes. Source, clustering and observation admission remain necessary. A retrospective exploratory comparison must be labelled as such.

Uncertainty in F and z matters when claiming a biological contrast or a reproducible separation between contexts. Evaluation of the realized independently frozen forecasts can still be valid under its stated sampling assumptions without treating those predictors as known biological truths.

The newest [frequency-dependence assessment](../ecological_context_2026/FREQUENCY_DEPENDENCE.md) makes the third condition substantive: phase-specific effects can cancel in a whole-cycle measurement, and reference-based fitness differences need not predict direct competition. It does not establish an appropriate native F or furnish the two example contexts. The [existing ecological-control contract](../establishment_controls/REPORT.md) already distinguishes these limitations.

A real win would demonstrate incremental prediction by the frozen restriction within the evaluated frame. Because TMD here is exactly a quadratic loglinear model, it would not distinguish TMD from that identical ordinary statistical model or identify a new evolutionary mechanism. The immediate useful deliverable is a feasible, independently calibrated context pair with quantitatively separated forecasts; without that evidence, this remains a design criterion rather than an empirical advance.

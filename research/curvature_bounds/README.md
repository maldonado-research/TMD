# R000018: exact bounded endpoint-curvature feasibility

**7 October 2026 · Methods candidate · Synthetic algebra only**

This standard-library certificate asks whether a common TMD curvature is algebraically possible under independently supplied, positive, finite population bounds on expected endpoint masses, relative supply weights, expected growth/retention yields, and recovery probabilities. It adds bounded uncertainty to the endpoint mimic discussed in R000015. It analyzes no biological dataset and supplies no empirical confidence interval, P value, power calculation, cancer outcome, or causal confirmation. R000017 remains a separate blocked work item.

An authenticated matched biological panel and the prospective design inputs in the public cancer translation contract remain missing. Admission flags are declarations, not experimental authentication. No source acquisition or network query was performed for this candidate.

## Observation model and target

For three fixed, ordered routes, the hypothetical residual endpoint model is

$$
m_{ci}=\kappa_c q_{ci}g_{ci}r_{ci}
\exp\{\theta\,1_{i=2}+\eta_c s_i\},
\qquad s=(1,0,-1).
$$

Here $m$ is positive population **expected recovered endpoint mass**, $q$ is a positive relative new-origin supply weight, $g$ is a positive expected terminal yield including growth and retention/loss, $r$ is a positive recovery probability at most one, and $\kappa_c$ is an unrestricted context-wide exposure scale. These are population quantities. Fractional expected yields are permitted; fractional realized cells are not asserted.

The factorization itself needs independent scientific admission. Normalizing masses gives $p_{ci}=m_{ci}/\sum_jm_{cj}$, the share of expected endpoint mass. It need not equal the expectation of a realized sample fraction, a founder's lineage-fate probability, a culture's selected categorical outcome, or a first-arrival route probability. A new count law and justified observation rule would be needed for any such transfer.

Define endpoint supply-adjusted curvature and its nuisance-corrected residual:

$$
J_c^{\rm endpoint}
=\frac{m_{c2}^2q_{c1}q_{c3}}{m_{c1}m_{c3}q_{c2}^2},
\qquad
K_c=\frac{m_{c2}^2q_{c1}q_{c3}g_{c1}g_{c3}r_{c1}r_{c3}}
{m_{c1}m_{c3}q_{c2}^2g_{c2}^2r_{c2}^2}=e^{2\theta}.
$$

Common normalization scales cancel. The engine uses $K$, not the raw endpoint $J$. Growth or recovery can produce raw common curvature while mutation supply stays unchanged, as R000015 demonstrates. Introducing a residual TMD weight after measured $q,g,r$ is a phenomenological model; it does not identify an additional mutation-generation mechanism. Controls fitted to the same selected outcomes cannot supply independent causal separation.

## Exact sharp interval over the admitted box

For every context and every route, specify closed intervals $[m^-,m^+]$, $[q^-,q^+]$, $[g^-,g^+]$, $[r^-,r^+]$ with strictly positive finite rational endpoints. The unknown population parameters vary over **positive real values** inside the box. The Cartesian assumption means the feasible parameter set permits all combinations:

- between route coordinates;
- between endpoint, supply, growth, and recovery factors;
- between contexts, apart from the tested shared curvature.

This is an assumption about a feasible set, not a statement that observations or random estimators are statistically independent. A shared uncertain calibration constant, linked lineage measurements, a known total mass, or biological coupling may prevent Cartesian combinations.

The sharp lower bound is

$$
L_c=
\frac{(m_{c2}^-)^2q_{c1}^-q_{c3}^-g_{c1}^-g_{c3}^-r_{c1}^-r_{c3}^-}
{m_{c1}^+m_{c3}^+(q_{c2}^+)^2(g_{c2}^+)^2(r_{c2}^+)^2}.
$$

The sharp upper bound $U_c$ reverses every lower/upper choice. Each signed exponent fixes the coordinate's monotonic direction. Consequently the supplied minimum and maximum corners attain $L_c,U_c$ exactly. The positive closed box is compact and connected; its continuous positive ratio has connected image in the real line. That image is exactly $[L_c,U_c]$, not just a pair of outer endpoints.

Independent context-specific parameter choices therefore permit a common curvature precisely when

$$
\max_c L_c\ \le\ \min_c U_c.
$$

Equality/contact is feasible. An empty intersection is **conditional algebraic incompatibility** with the model and the admitted population bounds. An overlap is inconclusive about predictive success or mechanism; it is not evidence supporting TMD. With one context the result is descriptive and cannot test cross-context sharing.

If the true feasible set is non-Cartesian but contained in these boxes, the ratio intervals can still be outer enclosures. An empty outer intersection would exclude a common value under that containment assumption. A nonempty outer intersection would no longer establish feasibility in the true joint set. The current engine refuses a declared non-Cartesian case rather than claim to solve its missing joint optimization.

## Normalization and real-valued witnesses

The bounds constrain unnormalized expected masses and unnormalized relative supply weights. Every corner can be normalized to positive simplex shares, and normalization preserves the ratio. Thus attaining mass-box corners is consistent with having normalized shares.

This does **not** justify entering independent per-coordinate share intervals while discarding their sum-to-one constraint. The normalized image of a mass box generally has dependent coordinates. The engine refuses the **simplex_coordinate_share_bounds** representation. A caller with uncertain normalized-share intervals must supply an admitted unnormalized mass/weight envelope or perform a separate joint simplex optimization. Exact singleton vectors can be represented as masses, but this is no permission to reinterpret a sample histogram as a population vector.

Rational endpoints do not imply rational interior witnesses. For $m_1=m_3=1$, $m_2\in[1,2]$, and unit nuisance factors, $K\in[1,4]$. Feasible $K=2$ requires $m_2=\sqrt2$, an irrational real. The certificate promises rational corner witnesses and real-valued interior existence, not an exact rational reconstruction of every interior point.

Conversely, for any positive parameter point define $z_i=m_i/(q_i g_i r_i)$. The residual form is reconstructed over the positive reals by

$$
\kappa=\sqrt{z_1z_3},\qquad
e^\eta=\sqrt{z_1/z_3},\qquad
e^\theta=z_2/\sqrt{z_1z_3}.
$$

Therefore $K=e^{2\theta}$ is the complete curvature restriction when the context scale and $\eta_c$ remain free. The code neither computes rounded logarithms nor uses them in decisions.

## Fixed curvature, free common curvature, and the conventional null

Free common curvature asks whether **some** positive common $K$ exists. A fixed-curvature forecast asks whether an independently locked value $K_0=e^{2\theta_0}$ lies in every interval. The prototype accepts an exact rational $K_0$; irrational forecast targets require another exact representation and are declined by this input contract. Fixing curvature while refitting $\eta_c$ is not a complete held-out probability forecast. The full forecast additionally needs a locked $\eta_c$ rule.

The conventional supply-growth-recovery model is $m_i=\kappa q_i g_i r_i$, without residual weighting. Its necessary curvature condition is $K=1$. But $K=1$ with free $\eta$ is insufficient: residual weights $(2,1,1/2)$ have $K=1$ and nonzero $\eta$.

The engine consequently supplies a **separate full conventional proportionality gate**. For route $i$, the attainable scale ratio is

$$
\frac{m_i}{q_i g_i r_i}\in
\left[\frac{m_i^-}{q_i^+g_i^+r_i^+},
      \frac{m_i^+}{q_i^-g_i^-r_i^-}\right].
$$

The conventional model is feasible in a context exactly when these three route intervals have a common positive scale. The same connected-image argument supplies all intermediate ratios, and Cartesian route bounds permit simultaneous choices. Context exposure scales are free; full conventional feasibility requires that gate in every context. This distinction avoids labeling a feasible necessary curvature condition as a fit of the complete conventional model.

## Synthetic cases

All cases are constructed population-bound inputs. They are not empirical measurements or assumed binomial confidence limits.

| Case | Exact result | Meaning |
| --- | --- | --- |
| Exact growth mimic | Corrected $K=[1,1]$ in both contexts; raw endpoint $J=4$ | The stipulated measured growth explains the synthetic endpoint curvature. |
| Growth known within 1% | $K=[9801/10201,10201/9801]$ | Conventional proportionality is feasible; residual forecast $K_0=4$ is incompatible. |
| Growth in $[1/4,4]$ by route | $K=[1/64,1024]$ | Both $K_0=1$ and $K_0=4$ remain possible; broad bounds do not distinguish them. |
| Different residual targets | $[4,4]$ versus $[9,9]$ | Free common curvature is incompatible under exact unit controls. |
| Contact | $[1,4]$ versus $[4,9]$ | The common point $4$ is feasible; equality is not rejection. |
| Free versus fixed | Same contact example, but $K_0=2$ | Free common curvature is feasible while the fixed forecast fails. |
| Irrational interior | $[1,4]$ versus $[2,2]$ | Common $2$ exists over reals; one context needs an irrational mass witness. |
| Gross finite recovery loss | $[1/250000000000,4000000000000]$ | Numerically exact but far too broad to resolve modest competing targets. |
| Nonzero axis, unit curvature | Residual $(2,1,1/2)$ | $K=1$ passes its necessary gate but fails full conventional proportionality. |
| Uncertainty in all four factors | $K=[5/864,16]$; conventional scale $[1,6/5]$ | All endpoint, supply, growth and recovery bounds vary simultaneously. |

These illustrations do not demonstrate that independent controls have been obtained in biology. Unknown loss, extinct unobserved lineages, route-dependent missingness, uncertain denominators, or unbounded nuisance factors cannot be replaced by convenient finite bounds. Structural zeros need another model. An arbitrary tiny positive floor is not a measurement.

## Input contract and reproduction

**fixtures/precise_growth_controls.json** is a complete example. The schema requires each context's three ordered route bounds for all four factors, provenance, and explicit admission declarations. Missing or unknown fields are refused. Declare whether bounds were fixed independently of selected outcomes; a positive declaration does not authenticate that history.

Use integers or rational strings such as **"99/100"**, never floating-point inputs or decimal strings. Reduced/canonical rational numerators and denominators are limited to 32 bits; rational input strings separately have a 24-character limit. At most 64 contexts and 1 MiB of input JSON are supported. Results use arbitrary-precision **Fraction** arithmetic, exact rational strings and integer cross-products. Recovery upper bounds must not exceed one. All other upper bounds must be positive and finite. Zero, negative, missing, unknown, infinite, inverted, or unsupported assumptions are declined; no pseudocounts are introduced.

~~~sh
python3 -B curvature_bounds.py fixtures/precise_growth_controls.json
python3 -B verify_producer.py
sha256sum -c SHA256SUMS.txt
~~~

Ordinary Python is required; both engine certification and producer verification refuse **-O/-OO**. Invalid requests return a declined message and do not overwrite an existing output file. Producer replays regenerate their named synthetic fixtures, results and receipt.

The producer checks explicit analytical scenarios, normalization and common-scale invariance, witness admission, the full conventional-null distinction, unknown/zero/dependent-input refusals, duplicate/nonfinite JSON, optimized-Python refusals, and preservation of existing output on decline. They are producer checks; root's independently constructed corner/cross-product oracle is the review gate. Hashes identify bytes and do not establish scientific truth or provenance. This candidate makes no claim of external peer review.

## Design applicability and unmet biological inputs

Before applying any endpoint-curvature claim, a qualified study must independently establish actual fixed route catalogs and their axis, common ancestry/background, new-origin supply, endpoint population meaning, growth/retention and recovery bounds, fixed observation/stopping rules, lineage and batch records, and joint dependence constraints. Controls and nuisance bounds must be chosen or measured independently before selected results. Mutually exclusive founder/culture outcomes, nested tissue samples, clone abundance, read counts and first arrivals require their own observation models.

A registered statistical claim would additionally require an authenticated joint uncertainty envelope, sampling laws, multiplicity/stopping design and justified error budget. Supplied finite deterministic bounds alone do not provide finite-sample coverage. This engine neither manufactures such an envelope from empirical histograms nor updates an existing study registry.

## In More Basic Terms

Endpoint counts can change because more mutations arise, descendants grow or disappear, or the experiment recovers some routes better. This calculation keeps independently justified ranges for each explanation. It asks whether one shared route-curvature value remains mathematically possible.

Precise synthetic controls can exclude a proposed residual value that broad controls leave unresolved. Overlap says that the assumptions and ranges have not settled the question. It does not show that a new biological force exists. The next empirical priority remains a matched, independently measured biological panel with a valid observation model.

## Public basis and reuse

Read [the public cancer translation design contract](https://github.com/maldonado-research/TMD/blob/main/research/cancer_translation/DESIGN_CONTRACT.md) and [R000015's endpoint counterexample](https://github.com/maldonado-research/TMD/blob/main/research/cancer_translation/translation_counterexample.py). The model follows the project's existing fixed-axis form; interval extremization, continuity and exact rational comparison are established mathematical methods. No source-literature novelty search was performed for this work.

Code: MIT. Original documentation and synthetic summaries: CC BY 4.0. AI assistance was used under Ricardo Maldonado's direction. No private archive, patient data, raw third-party measurements, credentials or article text is included.

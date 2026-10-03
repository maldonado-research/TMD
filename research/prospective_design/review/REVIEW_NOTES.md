# Independent mathematical review of the prospective design

Date: 2026-10-03. This is an internal review of a proposed analysis, not an external peer review, registration, experiment, publication, or claim of mathematical or biological novelty. Original reviewer notes are confined to this review directory. The repository has not been modified by this reviewer.

Primary input: `/workspace/TMD/research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md`. The existing prospective plan was also read. The candidate README and registry were subsequently reviewed; implementation review is recorded separately below.

## 1. Algebra and scope of the fixed-axis model

For positive triad probabilities, let

\[
p_i=\frac{q_i\exp\{\theta 1_{i=A}+\eta s_i\}}{Z},\qquad s=(1,0,-1).
\]

Since \(1_{i=A}=1-s_i^2\), this is exactly the same family as \(p_i\propto q_i\exp(-\theta s_i^2+\eta s_i)\). The common factor \(e^\theta\) cancels in normalization. Thus the second finite difference of the supply-adjusted log weights is \(-2\theta\); this is a quadratic curvature parameterization on three fixed axis points, not an additional identifiable mechanism.

The inverse parameterization is

\[
\theta=\log\frac{p_A/q_A}{\sqrt{(p_W/q_W)(p_M/q_M)}},\qquad
\eta=\tfrac12\log\frac{p_W/q_W}{p_M/q_M}.
\]

It verifies \(J=e^{2\theta}\) and saturation of every interior one-context triad. A common \(\theta\) across \(C\) contexts imposes \(C-1\) restrictions when the supplies are fixed/known. Estimating supply from selected winners, changing categories post hoc, or fitting a free held-out \(\eta\) weakens that test. A shared parameter or successful forecast does not separate mutation, establishment, selection, and recovery.

## 2. Conditional nuisance removal

For a fixed total \(N\), counts \((w,a,m)\), and \(D=w-m\), the multinomial likelihood is proportional to

\[
\frac{N!}{w!a!m!}q_W^wq_A^aq_M^m e^{\theta a+\eta D}Z^{-N}.
\]

Conditioning on \(D\) cancels both \(e^{\eta D}\) and \(Z^{-N}\). The conditional mass for \(a\) is proportional to

\[
\frac{N!}{[(N-a+D)/2]!a![(N-a-D)/2]!}
q_W^{(N-a+D)/2}q_A^aq_M^{(N-a-D)/2}e^{\theta a},
\]

over \(0\le a\le N-|D|\) with \(a\equiv N-D\pmod2\). This is valid for a known/fixed positive \(q\) and the stated multinomial law. The conditional information is \(\operatorname{Var}_\theta(a\mid D)\), which is zero when the support has only one point; in particular \(N-|D|<2\) is degenerate. Conditioning removes a nuisance for this contrast test; it does not estimate the held-out axis tilt or forecast a whole new probability vector. Independently estimated supply requires propagated nuisance uncertainty rather than treating an estimate as exact.

## 3. Pooling and recovery counterexamples

With identical uniform supply and equal-weight contexts having tilts \(+\eta\) and \(-\eta\), the normalizers coincide. The pooled probabilities obey

\[
\bar p_W=\bar p_M=\frac{\cosh\eta}{e^\theta+2\cosh\eta},\qquad
\bar p_A=\frac{e^\theta}{e^\theta+2\cosh\eta},
\]

so \(\theta_{\rm pool}=\theta-\log\cosh\eta\). This identity requires those weights, supplies, and symmetric tilts; it is not a general formula for unequal context mixtures. It demonstrates why a pooled contrast can depart from a shared within-context contrast.

Uniform biological supply and selected probabilities with selected recovery \((0.6,0.9,0.6)\) yield observed probabilities \((2/7,3/7,2/7)\). Against a uniform or equally recovered baseline, the apparent contrast is \(\theta=\log1.5\) and \(J=2.25\), despite biological \(\theta=0\). If baseline and selected recovery have the same route ratios, that artifact cancels; the example must state the baseline observation model.

## 4. Frozen expected log-score bounds

For frozen normalized positive target probabilities \(a_{ci}\) and comparator probabilities \(b^{(k)}_{ci}\), define \(h^{(k)}_{ci}=\log(a_{ci}/b^{(k)}_{ci})\). The expected per-founder score advantage in the actually scored outcome law is

\[
\Delta_{ck}(t_c)=\sum_i t_{ci}h^{(k)}_{ci}.
\]

This is linear in \(t\). Intersect simultaneous categorical marginal confidence boxes with the simplex:

\[
S_c=\{t:\sum_i t_i=1,\;\ell_{ci}\le t_i\le u_{ci}\}.
\]

Project \(h\cdot t\) by minimization and maximization over \(S_c\). The same joint coverage event implies simultaneous coverage of every deterministic comparator projection; there is no additional comparator-count Bonferroni factor when every projection reuses that same simultaneous region. Separate statistical regions or stochastic transport bounds need a joint budget, including any \(\gamma\), with total failure bounded by \(\alpha+\gamma\) without requiring independence between those events.

For a single selected categorical branch with \(K\) categories and \(C\) contexts, two-tail Clopper–Pearson/Bonferroni endpoints can allocate tail error \(\alpha/(2KC)\). Reusing a larger existing simultaneous region is valid but can be conservative. Within-category dependence across multinomial coordinates does not defeat the union bound.

An exact mathematical box-simplex optimizer starts at all lower bounds and allocates residual mass to capacities in increasing coefficient order for the minimum, decreasing order for the maximum. Feasibility requires \(\sum\ell_i\le1\le\sum u_i\). Empty numerical regions must be reported as a construction/numerical failure, not biological rejection. For fixed nonnegative context weights, summed contextwise extrema are extrema on the product region.

The coefficients are generally irrational. A floating-point optimizer evaluates these bounds approximately; certified rational confidence endpoints for \(J\) do not certify log-score thresholds. Label numerical decisions accordingly or introduce rigorous coefficient/optimization enclosures. The finite-sample score claim concerns held-out outcomes conditional on independently frozen training information; it does not automatically include uncertainty in a new target population or biological transport.

## 5. Boundaries, denominators, and observation maps

Zero observed counts are valid sampling boundaries; they are not proof of zero population probability. Zero trial denominators provide no measurement, and recovery controls need a known positive integer introduced denominator. Unknown concentration totals, reads, clonal descendants, and multi-cell wells are not authenticated Bernoulli denominators.

The interior contrast requires positive true supply/triad probabilities. A structural \(q_i=0\) implies \(p_i=0\) under the family and places the logarithmic contrast outside its stated domain. After observing outcomes, arbitrary pseudocounts cannot restore that domain. Positive fixed smoothing of predictive distributions can make log scores finite, but changes the forecast and must be locked before testing.

If a target assigns zero probability to an outcome of positive true probability, its expected log score is \(-\infty\). A zero comparator alone can give an infinite gain; both zero lead to undefined subtraction. Require positive forecasts for the ordinary finite linear comparison, or explicitly use extended-real rules. Reject nonnormalized, nonfinite, or invalid forecast inputs.

Writing \(r_{hi}=a_hd_{hi}e^{\xi_{hi}}\), the corrected contrast is \(\theta^{\rm bio}+v\cdot(\xi_1-\xi_0)\), with \(v=(-1/2,1,-1/2)\). The stated \(E\) and multiplicative \(G\) expansions are valid worst-case contrast bounds. A bound on this one differential contrast does not identify \(r_1\), the full observation map, or an all-category forecast. Per-route bounds on \(\delta_i=\xi_{1i}-\xi_{0i}\), together with an explicit paired-baseline law, instead permit bounded predictions of

\[
t_i\propto b_i(d_{1i}/d_{0i})\exp\{\theta1_{i=A}+\eta s_i+\delta_i\};
\]

that stronger model must be stated and its inputs/uncertainties propagated. Linear score projection applies to observed \(t\); recovery-corrected latent probabilities are generally nonlinear functions of the observed inputs and need projection through the observation map.

An Other/no-event category requires its own probability prediction or an explicitly declared conditional-triad estimand. The triad contrast is insensitive to a shared triad renormalization, but that does not supply the missing all-category forecast or validate changing Other recovery composition.

## 6. Sampling and ridge transfer conditions

Exact marginal binomial coverage requires justified count laws: independent repeated units with the declared common category law and a fixed or appropriately conditioned denominator. Founder IDs help authenticate units but do not prove the assumptions. Descendant colonies, shared lineage/batch effects, paired media, and technical replicates must not inflate independent denominators; preserve their bundles across training/held-out partitions. Cross-context or cross-arm independence is not needed merely to apply a union bound, although independence within the counted sampling units remains necessary for the stated marginal laws. Heterogeneous fixed founder probabilities need their own calibrated model rather than an unsupported binomial assertion.

A ridge covariate rule can fix \(\eta\) in a new context and therefore produce a complete conditional-triad forecast. Its output depends on the chosen features, scaling, penalty, intercept convention, training data, convergence rule, and extrapolation policy. The penalty can select a unique prediction in a rank-deficient design; it does not make the biological decomposition identifiable. Freeze every such choice and any training-only tuning before held-out outcomes; never estimate a new context tilt from those outcomes and call the result a complete transfer forecast. Verify optimization against the penalized objective and sensible limiting cases, including rank deficiency and unseen/missing covariates.

Penalizing only the axis-covariate coefficients does not guarantee a finite shared \(\theta\): no Aws outcomes can drive an unpenalized \(\theta\) to \(-\infty\), and all Aws outcomes can drive it to \(+\infty\). Use a declared penalty on every fitted coefficient, a justified finite parameter constraint, or explicit boundary/unbounded-fit handling. Positive quadratic ridge on every fitted coefficient makes the fixed-positive-supply penalized log likelihood strictly concave and ensures a finite unique optimum; convergence still needs verification. A finite iteration cap is not a convergence certificate.

## Independent checks completed

An independent standard-library calculation checked five identities: quadratic equivalence; \(J=e^{2\theta}\); conditional multinomial probabilities invariant between \(\eta=-2\) and \(\eta=3\); symmetric pooling; and the recovery counterexample. The nonuniform-supply conditional example used \(N=8,D=2\), with count support \((5,0,3),(4,2,2),(3,4,1),(2,6,0)\). A delegated independent mathematical subreview also assessed the score linearity, shared-region multiplicity argument, boundaries, and marginal-law requirements. The archived implementation checks below provide the reproducible computational evidence. These verify calculations in the stated domain; they are not biological validation, power certification, or a full implementation review.

## Candidate documentation review

The candidate README and registry correctly define the primary score for observed qualifying conditional-triad outcomes. They explicitly freeze an operational \(q^\star\propto b\,d_1/d_0\), Jeffreys-smoothed point predictions, an equal-context training curvature estimate, and a centered closed-form least-squares ridge rule for the tilt. Raw admitted counts, rather than smoothed pseudo-counts, remain the confidence inputs. This closed-form estimator is finite with valid positive smoothed inputs; the preceding unbounded multinomial-MLE caveat does not apply to this candidate algorithm.

The documentation discloses the missing laboratory/study inputs and does not present null registry fields as resolved registration, sample-size justification, biological evidence, or a certified score-decision implementation. Comparator information and all probability vectors are required to be frozen independently of selected held-out endpoints. There is no substantive mathematical objection to that stated design-only scope.

The flexible response offsets satisfy \(g_A=\theta_c-\eta_c\), \(g_M=-2\eta_c\). Since both responses use the same centered ridge operator, its predicted tilt is exactly the restricted model's predicted tilt, while its predicted curvature is the same operator applied to training \(\theta_c\). Thus this particular comparison tests constant versus feature-varying curvature; it is not a likelihood-ratio test or a general unrestricted context model.

The illustrative oracle gain was independently recomputed as \(\sum_i p_i\log(3p_i)=0.019620080790526365\) nats for \(p=(2/7,3/7,2/7)\), consistent with the printed value to floating precision. The \((0.9,0.6,0.4)\) recovery vector indeed has zero contrast curvature while changing the probabilities. The stated exchangeable maximum-envelope requirement \(m\ge\lceil H/\alpha_{\rm transfer}-1\rceil\) follows from per-target exceedance probability at most \(1/(m+1)\) and a union bound. It requires a declared scalar discrepancy with justified exchangeability and valid calibration measurement; uncertainty in measured residuals cannot be silently treated as known transfer error. This optional procedure is correctly marked unconfigured and outside the primary design.

## Candidate implementation review and disposition

The source was read and its stored verification receipt reproduced. The implemented smoothing, \(q^\star\), equal-context curvature, centered least-squares ridge, frozen target predictions, and flexible-response identities agree with the candidate description. Positive denominators, exact integer counts, empty frames, and missing/nonfinite ridge features are checked. Held-out selected counts do not enter the forecast builder. The CP root equations have the correct tail direction and preserve raw zero/all-success endpoints.

Two reviewer findings were corrected by the candidate owner before the final snapshot: nonfinite score coefficients now raise an error, and a tiny truly empty box/simplex intersection is rejected rather than admitted by a feasibility tolerance. The final source also checks exactly three independent route cells per assay and tests the flexible forecast identity. This reviewer did not edit candidate owner files or repository files.

The archived `review/verify_review.py` independently checks the candidate optimizer against exact rational vertex extrema in 240 deterministic feasible boxes with three through six categories; 16 CP boundary closed forms; three ridge normal-equation cases; six invalid/empty/bool/float count cases; four nonfinite-coefficient/tiny-empty-region cases; and five independent core identities. It also reruns the owner's synthetic receipt checks. Both reviewer and owner checks passed against the reviewed bytes. These are finite synthetic verification cases, not coverage certification over all populations, general power, or an inference engine for the unresolved study.

Disposition: **accepted for the stated design-only scope, with no remaining blocking mathematical finding in that scope**. A confirmatory study remains unready: the null laboratory, denominator, clustering, route, target-context, fixed-stopping, effect-threshold, alpha/transfer-budget, and numeric-inference fields must be resolved and independently reviewed. Biological interpretation remains conditional on independently justified observation/transport contracts. Registration, biological measurements, external peer review, publication, and causal identification have not occurred in this review.

Reproduce from this directory with `python review/verify_review.py --check`; the receipt binds the reviewer checks to the inspected candidate and reviewer file hashes.

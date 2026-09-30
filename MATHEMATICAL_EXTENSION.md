# TMD next step: separate the evolutionary clock from route choice

**Date:** 30 September 2026. **Status:** mathematical and implementation proposal; not an empirical result, external novelty claim, or replacement for the published v2.6.5 release.

The strongest next step is to ask whether the routes keep the same relative shares while the overall pace changes. This adds a time-resolved falsifier to winner counts without pretending that a heavy-tailed waiting-time distribution identifies a biological mechanism. A second correction makes the WS invariant portable when independently measured mutation baselines differ across contexts.

The historical handoff describes a pooled Kruskal–Wallis comparison and a method-of-moments Lomax fit on explicitly synthetic times. It also records missing censoring treatment and ambiguity about the gamma-race assumptions. The proposal below supplies the missing model distinctions and a small diagnostic that can be added alongside the historical runner. It does not reinterpret synthetic data as biological evidence.

## 1. What is being observed

Within a prespecified context c, let T be the time of the first **operationally defined successful arrival**, and W its route among K exhaustive, mutually exclusive categories. A replicate stops contributing to the risk set after that first event. A first detected colony, a later dominant allele, and a first established lineage are different measurement rules; this analysis requires the rule to be locked.

Let λ_ci(t) be the cause-specific hazard while no successful arrival has occurred. It has units of inverse time. With locally integrable nonnegative hazards and no instantaneous event masses, define

\[
\lambda_{c+}(t)=\sum_i\lambda_{ci}(t),\quad
\Lambda_{c+}(t)=\int_0^t\lambda_{c+}(s)\,ds,\quad
S_c(t)=\exp[-\Lambda_{c+}(t)].
\]

The joint subdensity and cumulative incidence are

\[
f_{ci}(t)=P(T\in dt,W=i\mid c)/dt=S_c(t)\lambda_{ci}(t),
\qquad F_{ci}(t)=\int_0^t S_c(s)\lambda_{ci}(s)\,ds.
\tag{1}
\]

These are properties of the observed competing-risk process. They do not require independent hypothetical route-only failure times. Independent arrival Poisson processes are one sufficient generative construction, but the observed cause-specific hazards do not identify the counterfactual time of each route in isolation. This distinction is the nonidentifiability problem in [Tsiatis (1975)](https://pmc.ncbi.nlm.nih.gov/articles/PMC432231/); its abstract was accessible in search, while the full-text page was blocked during this review.

For constant λ_ci, Λ_c+=tΣ_iλ_ci, and, if Σ_iλ_ci>0,

\[
P(W=i\mid c)=\lambda_{ci}/\lambda_{c+}.
\tag{2}
\]

For time-varying hazards, the general formula is the integral in (1), not a ratio at an unspecified time. If Λ_c+(∞)<∞, some replicates never experience an event. Equation (2) and the independence statements below must then be understood conditional on an event occurring; “no event” is a distinct outcome, not an omitted route count.

## 2. A precise equivalence: common clock versus time-dependent route choice

Assume a proper continuous event-time distribution, P(T<∞|c)=1. The following statements are equivalent on times at which the event density is positive:

1. T and W are independent within c.
2. There are constants p_ci≥0, Σ_i p_ci=1, such that

\[
\lambda_{ci}(t)=p_{ci}\lambda_{c+}(t).
\tag{3}
\]

**Proof.** If (3) holds, f_ci(t)=p_ci S_c(t)λ_c+(t)=p_ci f_c+(t). Integrating gives P(W=i|c)=p_ci and the joint density factorizes. Conversely, independence gives f_ci=p_ci f_c+; divide by S_c(t)>0 to obtain (3). Values where S=0 or f_c+=0 supply no restriction. With an improper time distribution the same argument applies to the finite-event subdensity after normalization, but W is undefined for never-event replicates.

Thus a changing total hazard, a heavy tail, and even a nonlinear environmental clock do not alone violate the normalized route-share model. The falsifier is **changing relative hazards**, not simply a nonexponential survival curve. Define the instantaneous route share

\[
r_{ci}(t)=\lambda_{ci}(t)/\lambda_{c+}(t).
\]

Equation (3) restricts this share to be constant within context. It permits a completely different clock and different p_ci in each context. Testing pooled T⊥W can reject solely because contexts differ in both speed and route shares, even if (3) holds in every context.

**Pooling counterexample.** Take two equally frequent contexts. One has total constant hazard 2 per time unit and p_1=.9; the other has total hazard .1 and p_1=.1. Within each context the route is independent of time. Pooled early arrivals are mostly from the first context, so their route mixture differs from late arrivals. Stratification is required.

## 3. What common gamma frailty predicts, and what it does not identify

For a fixed context, let a_i≥0 have inverse-time units, a_+=Σ_i a_i>0, and let h(t)≥0 be a dimensionless common clock multiplier. Let H(t)=∫_0^t h(s)ds have time units. Suppose a replicate has a common dimensionless latent multiplier Z>0 and

\[
\lambda_i(t\mid Z)=Z a_i h(t).
\tag{4}
\]

Conditional on Z, S(t|Z)=exp[-Za_+H(t)]. Integrating over **any** distribution of Z gives

\[
S(t)=E[e^{-Za_+H(t)}],\qquad
f_i(t)=a_i h(t)E[Ze^{-Za_+H(t)}]
=\frac{a_i}{a_+}f_+(t).
\tag{5}
\]

The common-clock independence property survives mixture over Z because the route shares are fixed across its values. The same conclusion applies to a random common clock path if its route shares remain fixed and the conditional competing-risk process is well defined. If Z or the path also changes route shares, the conclusion no longer follows.

For Z~Gamma(k, rate k), E[Z]=1 and Var(Z)=1/k. Its Laplace transform is (1+s/k)^(-k), so

\[
S(t)=\left(1+\frac{a_+H(t)}{k}\right)^{-k},
\quad f_i(t)=a_i h(t)\left(1+\frac{a_+H(t)}{k}\right)^{-k-1}.
\tag{6}
\]

With h(t)=1 this is Lomax survival with dimensionless shape k and inverse-time coefficient θ=a_+/k. The k→∞ limit, holding a_+ fixed, is exp(-a_+t). Its mean is k/[a_+(k−1)] only for k>1, and variance is k³/[a_+²(k−1)²(k−2)] only for k>2. Therefore the historical finite-variance moment fit cannot be used for k≤2, but maximum-likelihood survival analysis need not assume finite moments. Gamma-frailty marginalization is standard background; [Zeng, Chen and Ibrahim (2009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4063334/) gives a broader multivariate transformation-model treatment. Equations (5)–(8) here are directly derived for this competing-route observation rule.

### An exact three-way observational equivalence

Let α_i>0, α=Σ_iα_i, β>0 have time units. Each of the following gives exactly the same first-event joint law:

\[
S(t)=\left(\frac{\beta}{\beta+t}\right)^{\alpha},\qquad
f_i(t)=\frac{\alpha_i}{\beta+t}S(t),\qquad
P(W=i)=\frac{\alpha_i}{\alpha}.
\tag{7}
\]

**A. Common frailty.** Use a_i=α_i/β and Z~Gamma(α, rate α) in (4), with h=1. Substitute into (6).

**B. Deterministic declining hazards.** Use λ_i(t)=α_i/(β+t), with no replicate-level frailty. Integrating their sum gives Λ_+(t)=α log(1+t/β), hence (7).

**C. Independent route-specific random hazards.** Draw independent rates X_i~Gamma(α_i, rate β), where X_i has inverse-time units, and run constant hazards λ_i(t|X)=X_i. Independence gives S(t)=Π_iE[e^(-tX_i)]=(β/(β+t))^α. Differentiating the route's Laplace factor gives E[X_i e^(-tΣ_jX_j)]=α_i S(t)/(β+t), hence (7).

The gamma “rate” parameter β in C has time units because it multiplies X_i in the exponential; the gamma rate α in A is dimensionless because Z is dimensionless. These distinct uses must not be merged.

**Consequence:** even an arbitrarily large sample of first-event (T,W) pairs cannot distinguish A, B and C. Lomax survival plus route–time independence is compatible with common frailty; it does not establish common frailty or a specific biological mechanism. Shared replicate measurements, repeated events where meaningful, population histories, or independent rate assays supply information absent from the first-event law.

### Route-specific heterogeneity can also produce dependence

With probability 1/2, take constant route rates (4,1); otherwise take (1,1), all in inverse-time units. Then

\[
S(t)=\tfrac12 e^{-5t}+\tfrac12 e^{-2t},\quad
r_1(t)=\frac{4e^{-5t}+e^{-2t}}{5e^{-5t}+2e^{-2t}}.
\tag{8}
\]

Here r_1(0)=5/7 and r_1(t)→1/2, while P(W=1)=.5(.8)+.5(.5)=.65. Endpoint route counts alone hide the changing route shares. Route-specific frailty can therefore break (3), but case C proves that it need not.

## 4. Implementable next diagnostic: route shares across fixed time intervals

Use independent replicate records containing context, elapsed entry time l_r, stop time y_r, event indicator δ_r, and route W_r when δ=1. Initially support exact first-event times and independent right censoring only. Entry time defaults to zero; delayed-entry use needs an explicit independent-truncation justification.

Choose a common time unit and finite prespecified interval edges before examining route labels. Let e_rb be the length of the overlap of [l_r,y_r] with interval b. Aggregate

\[
E_{cb}=\sum_{r:c_r=c}e_{rb},\quad
d_{cbi}=\sum_{r:c_r=c}\mathbf1(\delta_r=1,W_r=i,y_r\in b),
\]

\[
d_{cb+}=\sum_i d_{cbi},\quad n_{ci}=\sum_b d_{cbi},\quad n_c=\sum_i n_{ci}.
\]

E_cb is replicate-time exposure. The same E_cb applies to every route because each replicate is at risk for all declared competing routes until its first event or censoring. A route-specific risk set is a different model and is not covered here.

For piecewise constant cause-specific hazards, the likelihood ignoring independent censoring factors is

\[
\ell=\sum_{c,b,i}\{d_{cbi}\log\lambda_{cbi}-E_{cb}\lambda_{cbi}\}.
\tag{9}
\]

This follows by multiplying event hazards and survival to the stop time, or survival conditional on entry for valid delayed entry. It is the same parameter-dependent form as a Poisson exposure likelihood, but it is derived from the stopped survival process; the event counts need not be asserted to be independent Poisson draws.

Compare:

| Model | Restriction | MLE, when the denominator is positive |
| --- | --- | --- |
| Time-varying route shares | λ_cbi unrestricted nonnegative | λ̂_cbi=d_cbi/E_cb |
| Common clock within context | λ_cbi=a_cb p_ci; Σ_i p_ci=1 | â_cb=d_cb+/E_cb; p̂_ci=n_ci/n_c |

Differentiating (9) obtains these estimates. The exposure terms in the maximized log-likelihoods both sum to −Σ_cb d_cb+. The route–interval deviance is consequently

\[
D_{\rm time}=2\sum_{c,b,i:d_{cbi}>0}
d_{cbi}\log\frac{d_{cbi}n_c}{d_{cb+}n_{ci}}.
\tag{10}
\]

All logarithm arguments are dimensionless. Writing event frequencies explicitly shows

\[
\frac{D_{\rm time}}{2\sum_c n_c}
=\sum_c\frac{n_c}{\sum_{c'}n_{c'}}
I_{\rm nats}(B;W\mid c,\text{observed event}),
\tag{11}
\]

so D_time/(2n_events ln 2) is **bits per observed event**. It is not bits per randomized replicate when censoring occurs, and it is not an unconditional time-information estimate beyond the follow-up horizon. Equation (10) gives a route×time interaction test whose overall clock is unrestricted by interval. The cancellation of exposure in this test does not remove the need to preserve censoring and exposure: they determine the fitted clock and hazard estimates.

### Inference and boundary rules

- Under the null with independent identically distributed replicates within context and censoring independent of (T,W) given context, observed event labels are exchangeable over event times within context. Condition on route totals and event times and permute labels **within each context**, recomputing (10). This avoids reliance on sparse-table chi-square approximations. For M Monte Carlo permutations use p_MC=(1+#(D_perm≥D_obs))/(M+1), with an explicit numerical comparison tolerance, fixed seed and recorded M. Do not pool contexts or shuffle a route label onto a censored observation.
- This is a test of a binned route-share restriction over observed follow-up. It can miss changes inside an interval. Pick a scientifically meaningful locked resolution; choosing interval edges to maximize observed route separation requires repeating that selection inside each permutation or using independent selection data.
- With adequately populated interior tables, the usual likelihood approximation has Σ_c(B_c−1)(K_c−1) degrees of freedom, where B_c and K_c are prespecified supported interval and route counts. Do not present that approximation as reliable with sparse margins, zero empirical routes or data-selected support.
- Zero cells contribute 0 log 0=0; do not add pseudocounts to the likelihood. A zero observed route does not establish a biological zero hazard. No-event contexts have no route-share estimate and no route–interval test; report `not_evaluable`, while retaining their exposure and zero estimated clock.
- E_cb=0 with any event in that interval is invalid input. E_cb=0 and no events means the interval has no hazard information; rate estimates are null/undefined, not zero measured hazard. E_cb>0 and no events gives the likelihood boundary rate zero with uncertainty.
- One informative time interval or one observed route supplies no route–interval association information. A computed zero deviance in that case is `not_evaluable`, not support for separability.
- Nonsignificance means “no departure detected at this resolution and sample size.” It must not produce a scientific `PASS` for independence. An equivalence claim needs a prespecified practical-effect bound and calibrated confidence method; that is beyond the first implementation.
- Shared populations, plates, laboratories or lineages can correlate replicates. The simple label permutation is invalid if the exchangeability unit is a cluster rather than a replicate. Reject/flag unmodeled clustering rather than inventing independent observations. A cluster-aware follow-up should be designed separately.

### Toy table for a numerical check, not biological evidence

For one context, two routes and two time intervals, let d=[[8,2],[2,8]], n=20. Both route and interval margins are [10,10].

\[
D_{\rm time}=4[8\ln(1.6)+2\ln(.4)]\approx7.70979028,
\qquad I_{\rm bits}\approx.27807191.
\]

Changing exposure E from [10,10] to [5,50] changes rate estimates but leaves D_time unchanged. Replacing the table by [[8,2],[8,2]] yields D_time=0. These are exact arithmetic fixtures for verifying equation (10), not simulated empirical confirmations.

## 5. Correct the WS invariant for context-specific baselines

Suppose independently justified positive mutation-supply baselines q_ci differ across contexts. The WS model is

\[
p_{ci}=\frac{q_{ci}\exp[\theta_1\mathbf1(i=A)+\theta_{2,c}s_i]}{Z_c},
\quad s_W=1,\ s_A=0,\ s_M=-1.
\tag{12}
\]

Here W, A and M stand for Wsp, Aws and Mws. All p and q are dimensionless triad probabilities, θ_1 and θ_2,c are dimensionless, and Z_c normalizes the context. Direct multiplication and cancellation give

\[
\frac{p_{cA}^2}{p_{cW}p_{cM}}
=e^{2\theta_1}\frac{q_{cA}^2}{q_{cW}q_{cM}}.
\tag{13}
\]

Thus the raw K_c=p_cA²/(p_cWp_cM) need not be constant. The portable object is the **baseline-adjusted** invariant

\[
J_c=\frac{p_{cA}^2q_{cW}q_{cM}}
{p_{cW}p_{cM}q_{cA}^2}=e^{2\theta_1},
\tag{14}
\]

or the equivalent log contrast

\[
\theta_1=\log(p_{cA}/q_{cA})
-\tfrac12\log(p_{cW}/q_{cW})
-\tfrac12\log(p_{cM}/q_{cM}),
\]

\[
\theta_{2,c}=\tfrac12\log\frac{p_{cW}q_{cM}}{p_{cM}q_{cW}}.
\tag{15}
\]

**Converse.** For positive p and q, define θ_1 and θ_2,c by (15). Their unnormalized weights have the observed W/M ratio and the observed A/geometric-mean ratio. These two ratios determine an interior three-category probability vector after normalization, so (12) reconstructs p exactly. Across contexts the model restriction is precisely shared θ_1, or shared J_c. This is an algebraic equivalence, not biological causality.

**Counterexample to raw K portability.** Take θ_1=θ_2,c=0. In context 1 let q=(W:.25,A:.5,M:.25), yielding raw K_1=4. In context 2 let q=(.4,.2,.4), yielding raw K_2=.25. Both satisfy the same model and J_1=J_2=1. A raw-K constancy test would falsely diagnose a model violation solely because the measured baseline changed.

Empirical zero counts make (14) and (15) undefined or divergent. Fit (12) using the multinomial likelihood rather than treating a pseudocount ratio as a measured law. Baseline zero probabilities are substantive support restrictions: if q_ci=0, finite tilts cannot yield p_ci>0. Independent q-calibration uncertainty must eventually be propagated; treating noisy measured q as exact understates uncertainty. Fitting q from the same winner counts can erase the falsifier and must be disclosed.

The contrast has homogeneous degree zero, so renormalizing just W/A/M among a larger route set leaves (14) numerically unchanged. That algebra does **not** authorize omitting an “Other” category from an event-time likelihood or claim that the triad models its arrival process. The corresponding WS likelihood must explicitly condition on a triad outcome or model all routes.

## 6. Two falsifiers can be separated exactly

For an exhaustive triad with valid first-event data, define three nested models using the same piecewise total-clock specification:

1. Free route shares in each context and time interval.
2. Constant route shares within each context, free between contexts.
3. Constant route shares obeying context-specific-q WS with shared θ_1.

Because each model fits the same total hazard a_cb=d_cb+/E_cb, the maximized log-likelihood differences satisfy

\[
D_{\rm free:WS}=D_{\rm time}+D_{\rm common:WS},
\quad D_{\rm common:WS}=2\sum_{c,i:n_{ci}>0}
n_{ci}\log\frac{n_{ci}/n_c}{\hat p^{WS}_{ci}}.
\tag{16}
\]

This is an exact likelihood decomposition, provided the WS probabilities are maximum-likelihood fits in the stated model and use the same observations. It identifies whether a poor total fit comes from time-changing route shares, cross-context WS structure, or both. It is not additive independent biological evidence, since both pieces use the same events. With positive supported data the WS restriction has C−1 fewer route parameters than the free context probability model; sparse boundaries require calibrated inference.

A prospective route forecast requires θ_1 and any new-context θ_2,c to be fixed from training data, covariates or independent measurements before the new outcomes are examined. Re-estimating θ_2,c from each new context tests the constrained curve, but supplies a weaker restriction than predicting all three new probabilities in advance. A held-out clock forecast additionally requires specifying how a_cb transports to the new context.

## 7. What time data can identify about μ, A and F

Winner counts identify only relative route shares in the constant/common-clock model. Multiplying all hazards by a positive number leaves those shares unchanged. Valid measured times with a justified censoring model can constrain the **observable cause-specific hazard scale** as well as relative shares. They still do not uniquely split it into biological factors.

For an explicitly operationalized mechanism, one possible dimensional construction is

\[
\lambda_{ci}(t)=B_c(t)\mu_{ci}(t)A_{ci}(t)F_{ci}(t),
\tag{17}
\]

where B_c is divisions per time, μ_ci is route mutation probability per division, A_ci is the probability of accessible entry conditional on that mutation, and F_ci is establishment probability conditional on accessible entry. This uses sequential conditional probabilities; A and F need not be independent. Independent Poisson marking/thinning with stable operational probabilities is a sufficient approximation for interpreting (17) as a successful-arrival intensity. Interference, ecological feedback and detection lag may prevent that interpretation. Other supply definitions require their own unit conversion.

For any positive g_ci(t), the change μ′=gμ and A′=A/g preserves λ. Likewise A′=hA and F′=F/h preserves λ. Probability bounds can restrict this ambiguity, but wherever A and F are strictly interior, sufficiently small changes still leave multiple admissible decompositions. More accurate winner/time measurement does not remove this invariance.

Two independently calibrated factors and the opportunity flux can constrain the remaining factor, e.g. F=λ/(BμA). When A and F are probabilities this supplies the feasibility bound 0≤λ≤BμA. Violation challenges at least one measurement, unit conversion or mechanism assumption. Uncertainty and covariance must be propagated. A marginal hazard from a mixed population is not automatically the intrinsic factorized hazard of a particular replicate.

## 8. Censoring, detection and sampling cannot be repaired by a fitted curve

Independent right censoring contributes survival to the recorded stop time; it is not an event with an “Unknown” route. The exact event likelihood is S(y)λ_i(y), and the censored likelihood is S(y), conditional on entry if applicable. If an event of known route occurred somewhere in (L,U], its contribution is

\[
\int_L^U S(t)\lambda_i(t)\,dt,
\tag{18}
\]

not S(U)λ_i(U). A first observed detection can also satisfy D=T+L_W, with a route-specific detection lag L_W. Unequal lags can create apparent winner–time dependence or even reorder the first detected route relative to the first true arrival. The initial diagnostic should refuse interval-censored/detection-only records unless they are explicitly declared a separate observable endpoint; it should not silently substitute upper bounds or midpoints as exact biological arrival times.

Unrecorded competing routes remove replicates from the true risk set. “Other” must be included if it can win, or the conditioning and interpretation must be changed. Missing winner labels, nonrandom sequencing, selecting only successful replicates, event-dependent censoring, ambiguous simultaneous winners and later endpoint takeover likewise need explicit models. A fitted heavy tail does not cure any of these biases.

## 9. Implemented diagnostic and future extensions

The separate diagnostic is `tmd_time_diagnostic.py`, schema version 0.1. Required record fields are `replicate_id`, `context`, `time`, `event` (0/1), `route`, and `provenance` (`observed`, `synthetic`, or `literature_transcription`). The CLI records one time unit, event definition, cuts plan, input hash, and explicit independence declarations. Each replicate ID is globally unique; units must be independent across all records, including different contexts.

All records enter at time 0 and have finite positive stop times. Event records contain an exact first successful arrival; censored records have event=0 and no route. Optional `entry_time` must be 0, `observation_type` must be `first_successful_arrival`, and `cluster_id` must be blank. Paired or clustered designs, delayed entry, interval-censored arrivals, and endpoint/detection times are unsupported. Optional metadata cannot silently override these requirements. Missing or malformed CSV cells are rejected cleanly.

Bin intervals use **(left,right]**, beginning at time 0, with the last bin extending through observed follow-up. An event exactly at a cut belongs to the preceding bin. The implementation fits the rates and computes the deviance derived above, then shuffles observed event routes within context while keeping times, bins, censoring, and route margins fixed. This requires route exchangeability under the null, independent units, independent joint time/route censoring conditional on context, and prespecified cuts.

The JSON records descriptive Aalen–Johansen cumulative incidence through observed follow-up, exposures, free and common hazards, observed event proportions, common-clock route estimates, deviance, Monte Carlo resolution, and provenance warnings. Event proportions are not unconditional winner probabilities absent the model and observation assumptions. Mixed provenance is flagged for separate review. User declarations do not independently authenticate data or assumptions.

All-censored, single-route, or single-occupied-bin contexts cannot supply a route/time interaction test; if all contexts are uninformative, no p-value is emitted. Nonrejection is not independence proven. Results concern the chosen bins and can miss changes within a bin. The tool does not return a biological-validation or frailty-confirmation certificate.

Meaningful verification includes an independent full survival-likelihood oracle for the toy deviance, tied-event/censor incidence, pooling and route-relabeling behavior, exposure effects, unsupported observation rejection, malformed input rejection, no-event handling, and mixed-provenance flags. Synthetic calibration explores selected generators only. A future q-aware WS fitting module and properly modeled interval or clustered designs should be added only with their own validation and compatible observations.

The priority for new evidence remains a prospective condition with independent replicates, recorded follow-up, justified first-event measurement, all competing routes, calibrated detection, and independent q. Time constancy and baseline-adjusted WS portability are distinct restrictions; mechanism identification still requires independent assays.

## In More Basic Terms

Two things can change in evolution: how fast a successful change happens, and which kind of change succeeds. TMD needs to check both. If every route speeds up or slows down together, the winner shares can stay the same even when waiting times change greatly. If some routes become relatively stronger later, time records can reveal a pattern that final winner counts miss.

A long waiting-time tail does not tell us what caused it. Different biological stories can produce exactly the same mathematical curve. The useful advance is a test that can expose a specific failure of the model, together with clear records of what was observed and what is still unknown. For the WS comparison, we must also account for changes in mutation supply before calling a change in winner shares a new biological effect.

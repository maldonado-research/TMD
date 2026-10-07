# Mutation by Natural Dominance: formulation and next empirical test

**Research note · 1 October 2026 · Exploratory hypothesis and prospective analysis**

The public TMD methods package currently reaches version 0.5.0. Its statistical tools make a restricted evolutionary-route hypothesis testable under explicit sampling and measurement assumptions. No complete authenticated biological panel combining matched mutation baselines, selected route outcomes, and route-specific recovery controls was admitted for the current Wsp/Aws/Mws estimand from the public material inspected. The next empirical advance requires those measurements; additional synthetic examples alone cannot establish the biological hypothesis.

This original formulation uses public TMD documentation. The accompanying literature update and source audit use attributed public primary sources. It separates the proposed model, its observable restrictions, and a protocol for obtaining evidence. The bounded recovery calculation below extends an existing sensitivity approach; no discovery or external mathematical priority is claimed.

## What “natural dominance” means operationally

For this analysis, **natural dominance means the relative propensity of an evolutionary route to produce a specified successful, heritable outcome in a specified context**. This is an operational interpretation of the public route models, rather than evidence for a separately identified causal force. The successful outcome and context must be defined before analysis. A route may occur most often because it arises frequently, establishes readily, or is recovered preferentially by an assay; those explanations require different measurements.

This usage differs from Mendelian dominance: the phenotype of a heterozygote relative to the two homozygotes. Wsp/Aws/Mws route frequencies in bacterial cultures do not measure a heterozygote dominance coefficient. Nor does a frequent winning route necessarily have the greatest fitness, account for a majority of events, or become fixed in its population.

Mutation supplies genetic variants. Inheritance allows a variant to persist through reproduction. Selection changes lineage reproduction or survival, while drift produces stochastic gains and losses. The TMD route framework does not introduce a new inheritance rule or show that mutations arise because organisms need them. Environment-dependent mutation rates remain possible, but their measurement must separate mutation production from subsequent survival and recovery.

## Successful arrivals and their assumptions

Let $T$ be the first operationally defined successful-arrival time and $W$ its route. In context $c$, the cause-specific hazard $\lambda_{ci}(t)$ is the instantaneous event rate for route $i$ while no successful arrival has occurred. With continuous event times,

$$
S_c(t)=\exp\!\left[-\int_0^t\sum_j\lambda_{cj}(u)\,du\right],
\qquad f_{ci}(t)=S_c(t)\lambda_{ci}(t).
$$

For constant hazards with positive total rate and eventual arrival,

$$
P(W=i\mid c)=\frac{\lambda_{ci}}{\sum_j\lambda_{cj}}.
$$

One possible mechanistic approximation is

$$
\lambda_{ci}(t)=B_c(t)\mu_{ci}(t)A_{ci}(t)F_{ci}(t).
$$

Here $B$ is divisions per time, $\mu$ is route mutation probability per division, $A$ is accessible-entry probability conditional on that mutation, and $F$ is establishment probability conditional on accessible entry. Sequential conditional probabilities do not require $A$ and $F$ to be independent. Their definitions must avoid counting the same barrier twice. A marking/thinning approximation needs justification; ecological feedback, clonal interference, changing population composition, and shared ancestry can defeat a simple constant-rate interpretation.

Establishment probabilities can reflect ordinary selection and stochastic lineage loss. Establishment, fixation, first detected colony, and endpoint predominance nevertheless remain distinct. Detection lags and recovery efficiencies require a separate observation model. Relative winner counts identify relative effective rates under the model; appropriately measured times can add their scale. Neither uniquely separates $\mu,A,F$: multiplying $\mu$ by a positive factor and dividing $A$ by it leaves the product unchanged wherever probability bounds permit.

## The restrictive prediction, rather than a general slogan

For positive Wsp/Aws/Mws supply probabilities $q_{ci}$, the fixed-axis model is

$$
p_{ci}\propto q_{ci}\exp\{\theta\,1_{i=A}+\eta_c s_i\},
\qquad s=(1,0,-1).
$$

Its cross-context prediction is a common supply-adjusted contrast,

$$
J_c=\frac{p_{cA}^{2}q_{cW}q_{cM}}
{p_{cW}p_{cM}q_{cA}^{2}}=e^{2\theta}.
$$

Every positive three-route distribution can be fitted in one context using its two free parameters. With $C$ contexts, a shared $\theta$ provides $C-1$ restrictions relative to unrestricted context-specific triad probabilities. Raw $p_A^2/(p_Wp_M)$ need not be constant when supply changes. Estimating supply from the same selected outcomes can erase the intended falsifier.

A genuinely held-out prediction must fix both the shared parameter and the new context's $\eta_c$ through training data, covariates, or independent assays before examining its selected outcomes. Refitting $\eta_c$ on held-out winners tests a weaker curve restriction; it does not forecast the complete route distribution. Rare and unassigned routes require an explicit “Other” category or a declared conditional-triad analysis.

A separate timing hypothesis is

$$
\lambda_{ci}(t)=p_{ci}\lambda_{c+}(t).
$$

For a proper continuous event-time distribution, this is equivalent to route–time independence within context. It allows a changing common clock. Pooling contexts can create an apparent time association even when the restriction holds within each context.

## What current evidence supports

The public documentation distinguishes published observations from simulations and software checks:

- Leehan and Nicholson's rpoB study supplies a secondary transcription of 111 sequenced resistant-isolate observations across two media and three blocks. A reported held-out-block gain of 13.126 bits shows predictive information from medium in this dataset. These are selected isolates, not newly collected experiments or exact first arrivals; the result does not identify a TMD-specific cause.
- Lind and colleagues' 46/41/18 Wsp/Aws/Mws samples came from different pathway-isolated backgrounds. They do not supply competing-route winner frequencies from one ancestor.
- The [2 October primary-source follow-up](panel_eligibility/README.md) authenticates Lind's 109-mutant inventory, including four rare-pathway mutants, while retaining the cross-background boundary. Sun and Lind's 2023 Aws table reuses the same 41 prior occurrences. Hotspot and repair studies inform stronger supply alternatives; none of the inspected measurements supplies the full matched route/control panel.
- Version 0.5.0 reports 13 automated tests and 160 synthetic count datasets, including reused datasets. Those checks concern implementation and selected generating scenarios. They provide no new biological measurements or certified general power.

Mathematically equivalent mechanisms impose another limit. A first-event law

$$
S(t)=\left(\frac{\beta}{\beta+t}\right)^{\alpha},
\qquad f_i(t)=\frac{\alpha_i}{\beta+t}S(t),
\qquad \alpha=\sum_i\alpha_i,
$$

can arise from common gamma frailty, independent route-specific gamma rates, or deterministic declining hazards. First-event observations alone cannot distinguish those constructions. A long waiting-time tail and constant route shares therefore do not uniquely establish a latent biological mechanism. Independent rate, lineage, or population-history measurements are needed.

## Bounded recovery transport: an extension of existing methods

Write observed baseline and selected probabilities as $b_c,t_c$, control recovery probabilities as $d_{0c},d_{1c}$, and $v=(-1/2,1,-1/2)$. The 0.5.0 target is

$$
\theta_c^{\rm corrected}
=v\cdot[\log t_c-\log b_c-\log d_{1c}+\log d_{0c}].
$$

Its simultaneous confidence construction uses established Clopper–Pearson and Bonferroni methods, with certified outer endpoints and rational interval decisions. Correct marginal count laws remain essential; exact arithmetic cannot authenticate a trial denominator or biological transport assumption. Nonempty interval overlap is compatibility, not proof of equality.

To allow bounded mismatch, suppose actual biological recovery is

$$
r_{hci}=a_{hc}d_{hci}\exp(\xi_{hci}),\qquad h=0,1.
$$

The branch-wide scale $a_{hc}$ cancels in the contrast. Under the specified route model,

$$
\theta_c^{\rm corrected}
=\theta_c^{\rm biological}+v\cdot(\xi_{1c}-\xi_{0c}).
$$

If independent control-transfer work justifies prespecified bounds

$$
|\xi_{1ci}-\xi_{0ci}|\le\Delta_{ci},\qquad
E_c=\tfrac12\Delta_{cW}+\Delta_{cA}+\tfrac12\Delta_{cM},
$$

then a corrected-contrast interval $[\ell_c,u_c]$ becomes the conservative biological interval $[\ell_c-E_c,u_c+E_c]$. Reject a common biological contrast only when these expanded intervals have an empty intersection. The conditional simultaneous coverage guarantee carries through if the admitted transport bounds actually hold. The bounds must be chosen before selected outcomes, rather than tuned to preserve a preferred conclusion. If another statistical procedure provides bounds with simultaneous failure probability at most gamma, combine its uncertainty with the confidence projection: the union bound gives total failure probability at most alpha + gamma, without requiring independence. A nominal 5% claim must budget both components. A residual shared across every context cancels in the cross-context restriction; independent contextwise bounds are a conservative allowance for varying residuals.

For multiplicative bounds $\Gamma_{ci}=e^{\Delta_{ci}}$, expansion in $J$-space uses $G_c=\Gamma_{cW}\Gamma_{cA}^{2}\Gamma_{cM}$: replace $[L_c,U_c]$ by $[L_c/G_c,U_cG_c]$. Rational admitted bounds permit exact decisions using the certified rational endpoints. This integrates the transport sensitivity already developed in 0.3.0 with 0.5.0's confidence construction. Without defensible finite mismatch bounds, biological contrast and recovery artifact remain confounded.

## Acquisition and preregistration protocol

1. **Authenticate eligible observations.** Obtain a matched common-background panel from a laboratory or licensed public source. Record source accession, immutable input hashes, assay protocol, strain/genotype, environment, culture and batch lineage, outcome definition, missingness, exclusions, and exact denominators. Preserve original data and distinguish raw measurements from derived summaries. Existing isolate summaries cannot be relabeled as independent binomial trials. Preserve founding-culture, lineage, mutation-step and immediate-ancestor identifiers; keep paired media and technical replicates together in biologically justified held-out partitions.
2. **Measure supply and recovery independently.** Estimate context-matched supply with justified units and its own uncertainty, including mutation spectrum, local sequence hotspots, repair background and temporal variation. Measure growth and descendant variance separately when using them to inform establishment; a growth proxy is not itself an establishment probability. Obtain known introduced totals and binary recovered outcomes for fixed-route controls. Challenge control-to-biology transfer with independent mixtures or relevant biological states. Sequencing reads, clonal descendants, uncertain cell concentrations, and multi-cell wells do not automatically provide independent cell trials.
3. **Lock the study before selected test results.** Prespecify contexts, routes, sample sizes, fixed stopping rule, alpha, denominators, transport bounds, admissibility checks, loss functions, effect thresholds, and exclusions. Reserve a whole context and preferably a later independent block. Use blinded design simulations with weak effects, rare routes, censoring, and plausible baseline uncertainty to plan precision and power. Data-dependent stopping or context selection needs another calibrated procedure.
4. **Compare meaningful alternatives fairly.** Include independently measured mutation supply alone; supply plus independently measured establishment/performance; the restrictive TMD model; and an appropriate flexible context/background model. Assess sequence hotspots, repair effects, epistasis, demographic drift, missing routes, clonal interference, and detection/recovery artifacts. Give models the same eligible observations and training information. Report held-out log score, calibration, uncertainty, and failures; a uniform comparator alone is inadequate.
5. **Keep timing and endpoint branches distinct.** Use the current timing diagnostic only for independent replicates with justified exact first-arrival times, all competing routes, independent censoring, and prespecified bins. Interval censoring, route-dependent detection lags, shared clusters, or endpoint-only observations require another observation model. Report unevaluable cases and unresolved assumptions alongside results.

A successful held-out forecast would support the stated predictive restriction within its tested domain. Causal identification would still require independently measured factors or interventions that discriminate the competing mechanisms. A failed forecast, or a residual removed by a better supply baseline, is an informative outcome.

## In More Basic Terms

One mutation route can appear common because mutations enter it frequently, because its descendants survive and reproduce, or because the experiment detects it more easily. Calling it dominant does not tell us which explanation is correct.

The useful TMD question is whether a particular adjustment predicts route frequencies in a new condition before its results are known. We need independent supply measurements, reliable recovery controls, and records showing what each sample represents. Simulations can test a calculation; biological conclusions require biological observations. The immediate task is to obtain an authenticated matched panel and test the frozen prediction against strong alternatives.

## Public sources and references

Model and evidence sources: the public [mathematical extension](https://github.com/maldonado-research/TMD/blob/main/MATHEMATICAL_EXTENSION.md), [claims ledger](https://github.com/maldonado-research/TMD/blob/main/EVIDENCE_AND_CLAIMS.md), [prospective test plan](https://github.com/maldonado-research/TMD/blob/main/PROSPECTIVE_TEST_PLAN.md), and [0.5.0 overview](https://github.com/maldonado-research/TMD/blob/main/TMD_RESEARCH_EXTENSION_0_5_0.md). The public 0.3.0 and 0.5.0 methods packages supply the recovery sensitivity and confidence constructions summarized here.

**Bibliographic note:** the identifiers and descriptions below are inherited from public TMD documentation; this follow-up did not independently reverify every earlier citation. A separate [targeted five-source update](literature/LITERATURE_UPDATE_2026-10-01.md) verifies recent mutation-bias, growth-effect, drift and transmission-modifier studies, with explicit abstract/full-text inspection limits. The [public source audit](public_dataset_audit/AUDIT_REPORT.md) reproduces one article-table inventory and its dependence qualifications. Neither is a systematic review or a matched TMD biological test.

The subsequent [four-source eligibility audit](panel_eligibility/README.md), dated 2 October 2026, independently authenticates the Lind 2019, Sun 2023 and Horton 2025 primary articles listed below, plus Torres and Alonso 2026. Its source manifests and internal review state inspection depth and acquisition limits.

- Lind, Libby, Herzog and Rainey (2019). *Predicting mutational routes to new adaptive phenotypes*. DOI: [10.7554/eLife.38822](https://doi.org/10.7554/eLife.38822). Mutation supply, pathway architecture, and selected outcomes.
- Leehan and Nicholson (2021). *The Spectrum of Spontaneous Rifampin Resistance Mutations in the Bacillus subtilis rpoB Gene Depends on the Growth Environment*. DOI: [10.1128/AEM.01237-21](https://doi.org/10.1128/AEM.01237-21). The attributed rpoB source experiment.
- Sun and Lind (2023). *Distribution of mutation rates challenges evolutionary predictability*. DOI: [10.1099/mic.0.001323](https://doi.org/10.1099/mic.0.001323). Mutation-rate heterogeneity and rare-route limitations.
- Horton, Cherry, Waugh and Taylor (2025). *G_nT Motifs Can Increase T:A→G:C Mutation Rates Over 1000-fold in Bacteria*. DOI: [10.1093/molbev/msaf183](https://doi.org/10.1093/molbev/msaf183). Local sequence context as a competing supply explanation.
- Thulin (2014). *The cost of using exact confidence intervals for a binomial proportion*. DOI: [10.1214/14-EJS909](https://doi.org/10.1214/14-EJS909). Exact-interval conservativeness and precision costs.
- Clopper and Pearson (1934). *The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial*. DOI: [10.1093/biomet/26.4.404](https://doi.org/10.1093/biomet/26.4.404). Established binomial confidence construction.

## Later measurement follow-up — 7 October 2026

The [SBW25 figure-data audit](sbw25_data_audit/README.md) supplies an authenticated exploratory reconstruction of reporter endpoint frequencies, not a common-route experiment. Its [independent methods assessment](sbw25_data_audit/METHODS_RECOMMENDATION.md) writes native relative supply as proxy supply times a normalized log-transfer factor. Because the contrast coefficients sum to zero, proxy contrast error is the coefficient-weighted transfer factor; prespecified supply and recovery widths add. This is standard algebra, not a measured new force or theorem. Single-marker C565T measurements do not supply those three-route bounds, so unknown native transfer remains unbounded and all 26 actual study inputs remain unresolved.

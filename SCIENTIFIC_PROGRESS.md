# TMD scientific progress — 30 September 2026

**Author: Ricardo Maldonado. Status: exploratory research and reproducible software.**

This page preserves the 30 September report. Later reviewed progress, including the prospective design, certified score computation and targeted source watch, is indexed in the [current research notes](research/README.md). [Publication status](research/PUBLICATION_STATUS.md) records the actual GitHub/Zenodo boundary.

This release makes TMD easier to challenge with appropriate data. It adds a time-resolved diagnostic, distinguishes observationally equivalent explanations, corrects an important WS sampling interpretation, and performs a descriptive reanalysis of published rpoB counts. These are advances in the project's research methods. They do not establish a new law of evolution, confirm a biological mechanism, or demonstrate a breakthrough in physics.

## In More Basic Terms

Imagine several evolutionary routes leading to the same useful trait. Some routes appear more often; some survive better after appearing. An experiment may recover more examples of one route for either reason. TMD asks whether a specified model can predict those outcomes across conditions.

The next useful question is about timing: within the same condition, do early and late successful arrivals use the same mix of routes? If that mix changes, a model with fixed relative route chances needs revision. If it stays similar, several biological explanations can still fit. Timing adds a test; it does not automatically reveal the cause.

## An important correction to the WS evidence

The Wsp, Aws and Mws samples in Lind and colleagues' 2019 WS mutation-supply experiment were obtained in **separate pathway-isolated genetic backgrounds**, with the other two pathways deleted. The 105 sequenced mutants comprise 46 Wsp, 41 Aws and 18 Mws samples. Those totals are not counts of routes competing to win in the same ancestral background. The paper explicitly restricts comparisons of the unselected mutant spectra to within-operon comparisons; its separately measured pathway mutation rates provide the between-operon supply information. [Lind et al., *Predicting mutational routes to new adaptive phenotypes*](https://doi.org/10.7554/eLife.38822).

The assay uses shaken cultures and a cellulose-linked kanamycin reporter to recover WS-causing mutants without selection for growth at the air–liquid interface. Recovery of a colony is also different from measuring the time of its first successful establishment. Treating these isolate totals as first-winner probabilities would confuse experimental design with biological dominance.

This correction does not negate mutation-biased adaptation. It establishes which observations can estimate supply, which can assess selected outcomes, and which cannot test the new time diagnostic. Existing retrospective TMD fits need a panel-by-panel provenance audit before being described as empirical support for a successful-arrival race.

## A sharper mathematical question

For a context c, let T be the first operationally defined successful-arrival time and W its route. With cause-specific hazards λ_ci(t), the event-free survival is

\[
S_c(t)=\exp\left[-\int_0^t\sum_i\lambda_{ci}(u)\,du\right].
\]

The joint event density is S_c(t)λ_ci(t). Under a proper continuous event-time distribution, route and time are independent within a context exactly when

\[
\lambda_{ci}(t)=p_{ci}\lambda_{c+}(t),\qquad\sum_i p_{ci}=1.
\]

This restriction allows the total evolutionary pace to change. It asks whether relative route shares remain fixed. Pooling contexts can produce route–time association even when the restriction holds separately in each context, because fast and slow contexts can favor different routes.

The release also derives a concrete nonidentifiability example. Common gamma frailty, deterministic declining hazards, and independent route-specific gamma rates can produce the **same first-event joint distribution**:

\[
S(t)=\left(\frac{\beta}{\beta+t}\right)^\alpha,
\qquad f_i(t)=\frac{\alpha_i}{\beta+t}S(t),\qquad
P(W=i)=\frac{\alpha_i}{\alpha},\quad \alpha=\sum_i\alpha_i.
\]

Consequently, a Lomax-shaped survival curve and route–time independence do not identify common frailty. Measuring more first-event pairs cannot distinguish these exact alternatives. Independent rate assays, population histories or other mechanistic observations are needed. This is an application of standard probability and the established identifiability problem of competing risks; no external mathematical priority is claimed. [Tsiatis, *A nonidentifiability aspect of the problem of competing risks*](https://doi.org/10.1073/pnas.72.1.20).

For the WS triad, a second clarification applies when independently measured mutation baselines q_ci change across contexts. The model's shared quantity is the **baseline-adjusted** ratio

\[
J_c=\frac{p_{c,A}^2q_{c,W}q_{c,M}}
{p_{c,W}p_{c,M}q_{c,A}^2}=e^{2\theta_1}.
\]

The unadjusted ratio p_A²/(p_Wp_M) need not remain constant when q changes. This algebraic correction is useful for model specification; shared J across future contexts remains an unconfirmed empirical hypothesis. Zero counts and uncertainty in q require statistical treatment, not infinite plug-in log ratios.

## What the new diagnostic does

The implementation compares route fractions across prespecified time intervals **within contexts**. It preserves event-free exposure, right censoring and route labels, calculates a likelihood deviance, and calibrates it by shuffling event labels within contexts. Descriptive cumulative-incidence estimates accompany the test.

The method requires independent replicate units, exact first-successful-arrival times, exhaustive route labels, independent censoring, and bins chosen before inspecting outcomes. Paired units or shared populations require a different exchangeability design. An endpoint mutation, a later dominant allele and a first detected colony are not interchangeable measurements. Nonrejection means no departure was detected at the chosen resolution; it does not prove independence or certify TMD.

## Synthetic calibration: software behavior, not biological evidence

The calibration used 200 generated datasets per scenario, 240 replicates per dataset, fixed cuts at times 1 and 2, 399 Monte Carlo permutations per test, and a 0.05 rejection threshold. The intervals below are Wilson 95% intervals for rejection proportions across these generated datasets.

| Generated scenario | Rejections | Proportion | 95% interval |
| --- | ---: | ---: | ---: |
| Exponential common-clock null, stratified | 12/200 | 0.060 | 0.03465–0.10193 |
| Gamma-frailty common-clock null, stratified | 9/200 | 0.045 | 0.02385–0.08330 |
| Strong time-switching route alternative, stratified | 200/200 | 1.000 | 0.98115–1.00000 |

Pooling the two exponential-null contexts produced **194/200 rejections**. Within each context, the null was true; the pooled hypothesis was different and false. This demonstrates why context handling matters. The gamma scenario draws gamma frailty and conditional exponential times, giving marginal Lomax waiting times; it does not simulate gamma-distributed waiting times. These results establish behavior under the chosen simulations, not calibration for every possible dataset or universal power. [Saved calibration](synthetic_calibration.json).

## Secondary reanalysis of the 2021 rpoB table

We transcribed 96 cells from Leehan and Nicholson's Table 1, retaining its three experimental blocks and original route categories. The table represents **111 sequenced resistant-isolate observations**: 59 from LB and 52 from SMMAsn. Excluding “No mutation found” and “Other” leaves 104 identified point substitutions, with 53 LB and 51 SMMAsn observations. These are published resistant-isolate counts, not new experiments or timed first arrivals. [Leehan and Nicholson, *The Spectrum of Spontaneous Rifampin Resistance Mutations in the Bacillus subtilis rpoB Gene Depends on the Growth Environment*](https://doi.org/10.1128/AEM.01237-21).

For all 111 observations, the plug-in context–route mutual information is **0.26084 bits per observation**. A descriptive leave-one-experimental-block-out comparison gives the context-specific model **13.12573 bits** more predictive log score than a context-pooled model, or **0.11825 bits per held-out observation**. The three fold gains are 0.15078, 0.02965 and 0.18353 bits per observation. Both models use a fixed 0.5 pseudocount per route; this smoothing applies to prediction, not to raw mutual information.

This checks whether medium information helps prediction across the published blocks. It is **not a test of TMD's μ/A/F decomposition or the common-clock model**. It reuses an existing TMD source, has only three blocks, uses a route dictionary from the published table, and was not preregistered. Sparse-table mutual information can be upward biased. No significance claim or p-value is supplied because treatment randomization and the appropriate inferential exchangeability have not been independently established.

## Literature priorities and the next empirical test

Two recent primary studies sharpen the next questions. Horton and colleagues' 2025 work shows that G_nT sequence motifs can strongly change local mutation rates and links previously observed awsR and wspF mutations to hotspot motifs. Its experimental phenotype is motility restoration, so it does not validate the WS curve. It motivates an **exact sequence-context audit of q**. [Horton et al., primary paper](https://doi.org/10.1093/molbev/msaf183), [data and R script](https://doi.org/10.17605/OSF.IO/HSYFX).

Torres and Alonso's 2026 study examines B. subtilis repair/translesion-synthesis backgrounds, DNA damage, viability and rpoB spectra. Its supplementary Table S6 is a candidate external panel after verifying denominators, isolate independence and recovery protocol. Predominant resistant isolates alone do not identify the highest-fitness route. [Torres and Alonso, primary paper](https://doi.org/10.1093/nar/gkag673).

The priority is a prespecified external test with independently measured supply, defined establishment criteria and timed replicate outcomes. Compare TMD's restricted model with mutation-only and context-dependent alternatives; retain failed predictions. A result that reduces the unexplained residual after improving q is useful progress. The goal is a model that predicts data it has not already seen, with explicit uncertainty and a clear way to be wrong.

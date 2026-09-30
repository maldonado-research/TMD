# A prospective route-prediction test for TMD

This is a proposed analysis specification, not a registered experiment or a claim that experiments have occurred. The most informative next step is a matched, independently replicated biological test. Protocol implementation requires a suitably equipped laboratory and its normal review.

## Separate two questions

**Endpoint prediction:** Can context-matched mutation supply and a restrictive TMD route model predict newly sampled genotypes better than established alternatives?

**First-event timing:** Does the fraction of events assigned to each route stay constant across prespecified time windows within each context?

Endpoint colony genotypes and first successful-arrival times are different observations. Analyze them separately. A detection time depends on growth, assay sensitivity, and sampling; do not relabel it as an exact arrival time.

## Freeze the design before receiving test outcomes

Use one documented genetic background and at least four genuinely distinct, well-described conditions for the WS prediction. Retain independent cultures and experimental blocks. Estimate mutation supply q separately in each condition with a matched assay, including uncertainty and sequence-context hotspots. Avoid transferring SBW25 reporter/deletion rates into Pf-5 without measurement.

Choose route classes before outcome inspection, including uncommon and unassigned outcomes. Specify missingness, eligibility, denominators, detection limits, and whether selection has already acted. Never collapse a knockout-background collection into a shared competing-route distribution. Keep genotype and fitness assays traceable to the same experimental background.

Hold out at least one complete condition for a genuine transfer prediction. Where possible add a later independent experimental block. Freeze candidate models, smoothing, loss functions, and any model-selection rule before seeing those held-out outcomes.

## Strong comparison models

Compare independently measured context-specific supply alone, supply plus independently measured performance, a flexible context-specific multinomial where training permits it, and the restrictive TMD model. A uniform route baseline may be reported for orientation, but it is insufficient as the main biological alternative.

Report held-out log score, predictive probabilities, calibration, and uncertainty. Give every model the same eligible observations and comparable access to training information. An extra fitted parameter is not an explanation until its predictive contribution survives held-out evaluation.

The WS fixed-axis restriction implies a supply-adjusted quantity

\[
J_c=\frac{p_{A,c}^2q_{W,c}q_{M,c}}{p_{W,c}p_{M,c}q_{A,c}^2}
\]

that is constant across contexts under the specified shared parameterization. Raw p_A²/(p_W p_M) need not be constant when q changes. Treat zero counts with a prespecified likelihood or uncertainty method; do not substitute arbitrary tiny numbers to force a ratio. Propagate q uncertainty. The derivation and its assumptions are in `MATHEMATICAL_EXTENSION.md`.

## Timing branch, only with appropriate observations

For each globally independent replicate, record a common origin, exact event time or censoring time, route at first successful arrival, context, and source lineage. Obtain a justified measurement method for the event definition. The current software supports no delayed entry, interval censoring, paired units, or unmodeled culture clusters.

Prespecify physical time units and cuts without looking at route outcomes. The current diagnostic tests route proportions across these bins, conditional on context. Censoring must be independent of time and route within context, and ascertainment must not favor a route. If those assumptions fail, develop an observation/cluster model before computing a p-value.

Calculate the required replicate count with simulations spanning weak effects, censoring, rare routes, plausible q uncertainty, and realistic measurement limitations. The checked-in strong-switching demonstration is not a sample-size justification for a real experiment.

## Decisions and stopping rules

Define practically meaningful held-out score improvement and uncertainty before testing. Lock any multiplicity correction and follow-up analyses. Report failures and excluded observations with the same visibility as favorable results. If time dependence is detected, constant route fractions are inadequate at that resolution, but the test does not identify which mechanism caused the departure. If it is not detected, report compatible effect sizes and limited power rather than declaring independence proven.

Distinguish a successful replication of known environmental effects from a new TMD-specific prediction. Mechanism identification requires independent measurements or interventions because identical first-event distributions can arise from different latent mechanisms.

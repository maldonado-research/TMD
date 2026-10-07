# What this SBW25 source can identify

Independent original methods assessment · Mutation by Natural Dominance · 7 October 2026 (America/Los_Angeles)

The Farr et al. source can strengthen a competing **mutation-supply explanation** for repeated cell-chaining adaptation, and its released measurements permit a provenance and frequency reconstruction audit. It does not provide a common-background Wsp/Aws/Mws competing-route panel, a TMD validation, a native-site mutation-rate measurement, or a complete observation-to-biology transfer map. The prospective study remains unregistered, with all 26 actual-study inputs unresolved. This review introduces neither an experiment nor a mathematical-priority claim.

## What was read

Farr et al., *An extreme mutational hotspot in nlpD depends on transcriptional induction of rpoS*, PLOS Genetics (2025), [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572): cached primary XML, especially Results sec007, Discussion sec008, Methods sec009/sec013/sec015/sec016 and embedded S2–S4 captions. The R4 notes were read as prior assessments; the primary text was checked separately. Supporting PDF contents were not independently acquired or read.

Hall et al., *Fluctuation AnaLysis CalculatOR*, Bioinformatics (2009), [10.1093/bioinformatics/btp253](https://doi.org/10.1093/bioinformatics/btp253): independently acquired original-method **abstract and metadata only** from NCBI. The XML omitted the body; the nominal HTTP-200 HTML response contained a browser-check page. No full-text or program execution is claimed. The abstract identifies frequency, Lea–Coulson median, and MSS maximum-likelihood methods as distinct options.

Foster, *Methods for Determining Spontaneous Mutation Rates*, Methods in Enzymology (2006), [10.1016/S0076-6879(05)09012-9](https://doi.org/10.1016/S0076-6879(05)09012-9): independently acquired and read **full-text methodological chapter**, especially Terminology, Lea–Coulson Model, Experimental Design, MSS maximum likelihood, Calculating the Mutation Rate, and Departures from the Model. This is a methodological synthesis, not a second independent biological replication. Its older recommendations are reported within their model domain; their historical software/design restrictions are not assumed to delimit all present-day estimators.

All four new acquisition attempts and source-byte SHA-256 hashes are recorded in `METHODS_ACQUISITION_RECEIPT.json`. Third-party raw text remains external to the public repository; these notes are original commentary. This was a targeted reading, not a systematic review or an entire-web search.

## Preserve the experimental hierarchy

| Item | What it represents | Interpretation limit |
| --- | --- | --- |
| Genotype/background | SBW25 or SBW25 ΔpsrA carrying an engineered attTn7 reporter | A ΔpsrA intervention changes more than one molecular variable; it is not automatically a clean transcription-only mediation experiment. |
| Reporter transformant | One of six reporter transformants per background | Transformant identity repeats across two occasions; preserve identity to assess blocking or heterogeneity. Shared transformants alone do not prove that newly founded cultures are dependent. |
| Culture occurrence | One transformant cultured on one occasion; 12 per background, 24 total in Fig. 4A | This is the fluctuation-distribution unit. Justification of conditional culture independence requires founding and run information. |
| Selective plate | An aliquot of a culture, with genotype-specific dilution and 72-hour colony-size gates | Plates from one culture are technical samples, not extra evolutionary replicates. Dilution and recovery must be modeled. |
| Candidate colony | A thresholded kanamycin-resistant colony | Earlier mutations may produce many sibling colonies. Candidate resistance can have other causes. |
| Sanger-confirmed colony | A candidate sampled for marker confirmation | A nested assay of candidate composition, not an independent culture, a W/A/M winner, or a newly born mutation. |
| Terminal CFU estimate | Dilution-plating estimate of viable colony-forming units | An estimated denominator is not a fixed known number of independent single-cell trials or a directly observed division count. |

The released workbook correction is candidate concentration times a sampled genotype-confirmation fraction, divided by estimated terminal CFU concentration. With raw candidate count H across I plates, dilution J, terminal nonselective plate count E, and L/M confirmed/sample colony counts, the workbook recipe's equal 50-µL factors cancel:

    f_hat = H L / (I J M E × 10^6).

That expression is a **terminal genotype-corrected mutant-frequency estimate**, conditional on the recorded sampling/volume recipe. An exact rational reconstruction removes arithmetic ambiguity; it does not remove sampling, classification, colony growth, or denominator uncertainty. A fraction L/M requires an authenticated sampling frame and selection rule. In occasion 1, SBW25 transformant 5 records H=7 counted candidate colonies but M=8 sampled colonies, with L=2 confirmations. Independent raw-workbook readback confirms these values. Additional plates or a different counting scope may explain them, but the released row does not establish a closed seven-colony sampling pool. Do not assume either a hypergeometric closed-pool law or a binomial confidence law, and do not alter the original values to manufacture that contract. Exact arithmetic is reproducible even when a sampling frame remains unresolved.

The independent root reconstruction checks 24 recorded culture frequencies and matching cached arithmetic with stated rounding tolerances. Pooled arithmetic means differ by about 118.97-fold. The article's reported MSS point estimates, 4.2×10^-7 and 7.2×10^-9 per base pair per replication, differ by 58.33-fold. These are **different estimands**. Arithmetic frequency means neither reproduce an MSS likelihood fit nor provide its confidence intervals. Preserve occasion-specific summaries rather than counting the two occasions as two independent replications of every inference.

The candidate-confirmation burden is genotype-specific: the workbook records 60/96 confirmed SBW25 candidates and 95/95 confirmed ΔpsrA candidates across occasions. This difference warrants retaining candidate specificity separately from terminal frequency. It is not a W/A/M effect or a known assay sensitivity. The reported trial-1 sequencing archive has 94 reads against 95 workbook sampled-colony entries; a missing read and unresolved calls must stay explicit. A strict sequence-flank caller failing to assign a read is not proof that the specimen lacked the marker.

## Fluctuation-estimator questions that remain open

Foster separates numbers of mutations from numbers of mutant descendants. A classical MSS likelihood concerns the distribution of descendant counts under a clone-growth model. Its use here requires auditing the actual FALCOR input, program/version, parameter convention, partial-plating correction, integer treatment of genotype-corrected fractional counts, individual CFU denominators, and culture grouping. The reported MSS estimates are not reproduced merely by discovering raw colony counts.

The classical model assumes, among other things, adequately described clone growth, an appropriate mutation process, limited pre-existing mutants, negligible death/reversion, and a justified detection and post-plating mutation model. Farr deliberately moved the selectable promoter away from the fitness-altering native nlpD context. Its S2 caption nevertheless reports significantly lower fitness of C565T reporter mutants in both reporter backgrounds. Therefore **no fitness advantage** and **exactly equal fitness** are different claims. The cost can matter to clone-size likelihoods; its magnitude and relevance need independent quantification. This observation alone does not establish the direction or size of rate-estimation bias.

The 22-hour stationary-phase endpoint and changing promoter induction deserve attention to mutation and growth histories; they do not automatically satisfy a constant per-division mutation rate. Genotype-dependent dilution, candidate-size thresholds, and delayed detection alter the observation model. The size gate was designed to reduce post-plating spontaneous mutations; it does not itself certify that none occurred. The controlled PsrA deletion demonstrates dependence of the observed reporter assay on regulator genotype, conditional on its measurement and growth controls, and supports a plausible supply mechanism. It is stronger evidence than an observational correlation. Identifying transcription as the sole mediator or a specific chemical mutagenic mechanism needs additional interventions/measurements. The authors explicitly leave the native-site mutation rate and its quantitative association with parallelism indirect.

Independent source-well mapping confirms that the plotted log₂ proxy equals Ct5′−Ct3′ after averaging the two supplied technical Ct values per amplicon. Reconstructing all 12 plotted biological-replicate labels gives a 5.9603 geometric-mean ratio of linear proxies and a 6.1488 ratio of arithmetic means of linear proxies, under the supplied ideal-doubling transform. This corrects an initially reversed 5′/3′ label in the candidate output without changing its calculations. No PCR-efficiency, raw-fluorescence or causal transcript estimate is newly fitted. The source's roughly 4-fold figure-caption versus roughly 6-fold main-text description remains unresolved. A ratio of log₂ means, about 3.8307, is not a linear fold change and does not establish why the caption differs.

## Zero observations and time-series boundaries

Zero confirmed colonies are compatible with a positive underlying marker frequency. If no target genotype is seen among an initial colony sample, the source describes further sequencing; retain that outcome-dependent sampling rule and the expanded denominator rather than quietly substituting a fixed eight-colony design. Missing reads, unreadable marker context, no confirmed marker, no candidate colony, no qualifying evolutionary endpoint and a missing measurement are distinct categories.

The S4 time series uses destructively sampled cultures, not repeated measures of the same population. More than one culture appears per occasion/time point. Candidate frequency, CFU concentration and transcription can change together with clone expansion and detection. This is not a list of exact mutation times or of first established W/A/M arrivals; it does not enter the route–time independence test unchanged. No zero needs replacement with a positive pseudo-count for a biological contrast. Undefined or unsupported log-ratio targets remain unevaluable.

## A transparent native-supply sensitivity calculation

The existing TMD restriction is ordinary quadratic loglinear curvature, not a newly identified force. With route order W,A,M, let v=(-1/2,1,-1/2), so v sums to zero. Let q_proxy and q_native be positive relative supply vectors. Suppose, as a **declared transport model**,

    q_native,ci = q_proxy,ci exp(ζ_ci) / Z_c.

For the same underlying selected distribution, the contrast calculated using the proxy differs from the one using native supply by

    θ_proxy,c = θ_native,c + v·ζ_c.

The normalization term disappears because the coefficients sum to zero. This is an algebraic extension of the existing recovery sensitivity calculation. It is not a novel theorem or an estimated effect. If independent, prespecified work justifies |ζ_ci|≤Δ_supply,ci, then

    E_supply,c = ½Δ_supply,cW + Δ_supply,cA + ½Δ_supply,cM

is a conservative contrast-error bound. If differential recovery contributes its existing bound E_recovery,c, expand a valid statistical contrast interval [l_c,u_c] to

    [l_c-E_supply,c-E_recovery,c, u_c+E_supply,c+E_recovery,c].

An empty intersection of these expanded context intervals can reject the declared common biological contrast under the statistical and transport contracts. Nonempty overlap only shows compatibility. If supply and recovery bounds themselves are statistical, allocate their failure probabilities in addition to the outcome-interval error budget; a union bound adds the budgets without assuming independence.

A context-shared contrast error cancels in cross-context differences. Independently bounded per-context errors are conservative; tighter prespecified bounds on differences could be useful when justified externally. Neither the C565T single-marker assay nor its ΔpsrA contrast measures ζ for all three W/A/M routes, provides a finite native-reporter bound, or establishes cross-context transport. Unknown supply transfer remains unbounded. Without defensible finite bounds, this sensitivity extension produces no biological test.

## Measurements that would distinguish explanations

1. **Mutation production:** independent native-site or route-complete assays in the same ancestry, contexts and division/population-history frame, sequenced before the selected endpoints being predicted. Record allele/route maps, detection limits, false positives/negatives, cell death, clonal ancestry and culture-level denominators. Error-corrected endpoint sequencing measures variant burden; interpreting it as new mutation production still requires growth/history and selection assumptions. Birth events cannot be inferred by treating sequence reads or descendants as independent events.
2. **Native-reporter transport:** paired native/reporting constructs with controlled insertion, sequence and regulator state, measured across the proposed context/phase range. Reconstructed mutation controls can reveal different fitness and recovery; they cannot by themselves measure the rate of creating that mutation. Preserve both wild-type and deletion effects, and require intervention designs that address pleiotropy if transcriptional mediation is the causal target.
3. **Establishment/selection/drift:** known low-frequency mutant introductions with independent cultures, prespecified binary lineage-survival endpoints and measured descendant variance/population history. A 1:1 growth competition estimates relative performance in that assay, not establishment probability or fixation. The lineage-survival trial definition, inoculum uncertainty and genotype/recovery controls need their own contract.
4. **Phenotypic visibility/plasticity:** genotype-confirm the route, reconstruct it in a common background, assay phenotype after washout or condition changes, and preserve detection windows. Reversible phenotype, delayed gene expression and heritable genotype are not interchangeable explanations.
5. **Recovery:** define known introduction and recovery events with calibrated denominators and fixed windows; include matched biological states and mixed-route checks. Multiplying a terminal CFU estimate by a sampled confirmation fraction is not such a recovery calibration.
6. **A falsifiable forecast:** freeze positive full route forecasts and independently measured supply plus establishment/recovery comparators before held-out outcomes, hold out whole culture blocks/contexts as appropriate, retain Other/no-qualified/unresolved/missing outcomes, and compare the same information and sampling units. The existing shared-θ model has C−1 curvature restrictions but one context is saturated. Refitting a held-out η or deriving q from the selected outcomes eliminates the intended forecast. A supply-only or supply-plus-establishment success is a useful competing result, not evidence for an added dominance mechanism.

The priority is a verified source-to-measurement ledger and, next, a matched native-site/route-complete supply and recovery contract. This released dataset is valuable evidence about an alternative mechanism and assay transport, but it cannot populate the TMD registry by relabeling its cell-chaining or reporter data. No result presently exceeds established population-genetic and observation-model explanations.

Original commentary: Ricardo Maldonado, prepared with AI assistance; CC BY 4.0. Raw source files and third-party full text are excluded from the public candidate.

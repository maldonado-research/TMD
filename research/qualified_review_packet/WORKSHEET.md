# Qualified biological and statistical review worksheet

R28 · 11 October 2026 · Unfilled feasibility worksheet; no external assessment obtained.

Use each numbered row with its exact registry field. Record an answer, evidence locator/version and relevant section, reviewer identity/qualification, claim scope, uncertainty, and ACCEPT_FOR_NAMED_SCOPE / REVISE_WITH_NAMED_EVIDENCE / REFUSE_NAMED_SCOPE / NOT_ASSESSED. An answer is not an admitted input until its gate dependencies and independent review are satisfied. The machine-readable [worksheet](REVIEW_WORKSHEET.json) is authoritative for field identity and response slots. All 44 actual answers remain NULL.

## S01 · ancestral_genotype_and_stock_id

Gate **G0**; suggested expertise: biology.

Which physical ancestral stock and reference genotype could be authenticated, and are starting eligible variants excluded or measured independently?

**Deliverable:** Stock accession and custody record; reference sequence/version; independent parental genotype assay; documented starting-variant sensitivity and unresolved states.

**Refuse or revise if:** A published strain label without a stock-to-experiment join, or smooth/colour phenotype used to certify no starting variant.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S02 · molecular_allele_route_registry

Gate **O1**; suggested expertise: molecular biology.

What molecular allele definition maps an endpoint to W, A or M in this stock, including coordinate convention and marker background?

**Deliverable:** Versioned allele-to-route table with reference coordinates, indel convention, molecular confirmation and marker/plasmid joins; resolve the reported awsX 32-bp versus endpoint-span ambiguity before actual selection.

**Refuse or revise if:** Morphology or reporter colour substituted for molecular route; an unresolved coordinate silently corrected.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S03 · compound_and_unknown_route_rules

Gate **O1**; suggested expertise: biology and statistics.

How will compound, other-route and unresolved calls remain observable before selecting the conditional triad?

**Deliverable:** Exhaustive mutually exclusive adjudication rules and a worked blinded example retaining W/A/M/Other/no-qualified-outcome/unresolved/missing denominators.

**Refuse or revise if:** Dropping discordant colonies or assigning all WS morphology to the triad.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S04 · within_route_heterogeneity_bound

Gate **B3**; suggested expertise: biology and statistics.

Can a route-level control stand for the eligible alleles aggregated within that route, and what independently supported mismatch remains?

**Deliverable:** Allele-resolved control comparisons and aggregation rationale with a proposed uncertainty/transport treatment; distinguish observed route prediction from mechanistic route homogeneity.

**Refuse or revise if:** A single engineered allele assumed to represent all native route variants.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S05 · qualified_endpoint_and_fixed_time

Gate **O1**; suggested expertise: biology.

What endpoint and observation time can yield exactly one adjudicated outcome per eligible run?

**Deliverable:** Operational endpoint definition, timing justification, assay completion states and ties/compounds/censoring rules; retain the source unit hierarchy.

**Refuse or revise if:** A final sampled colony treated as the first mutation, first arrival or every lineage in its well.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S06 · supply_event_division_denominator_frame

Gate **B1**; suggested expertise: molecular biology and statistics.

Which acquisition episode and exposure can be counted independently of surviving endpoint winners?

**Deliverable:** Episode/ancestor ledger and division or opportunity exposure; state how pre-existing variants, repeated origins, transfers, jackpots and missed episodes enter a justified likelihood.

**Refuse or revise if:** Endpoint CFU fraction, recovered descendants or aggregate historical WS rates relabelled as independent mutation births.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S07 · establishment_binary_outcome_definition

Gate **O2**; suggested expertise: imaging and biology.

What operational establishment event can be observed before terminal recovery, and how will observer errors be independently bounded?

**Deliverable:** Known introduced-lineage record linked to an earlier fate observation; independent reference/calibration including false events, missed events, identity swaps and unknown fates; preserve timing and ecological context.

**Refuse or revise if:** Establishment defined by final recovered colony, or unobserved fate scored as loss.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S08 · known_introduced_recovery_trial_definition

Gate **O2**; suggested expertise: assay science and statistics.

What exactly enters each recovery calibration stage and how is the true introduced denominator verified?

**Deliverable:** Route/allele/context/phase challenge ledger, entry stage, verified introduced lineages, technical aliquot ancestry, correct/incorrect/ambiguous/unrecovered outputs.

**Refuse or revise if:** Nominal concentration, reads or a late spike-in used as known earlier lineage totals.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S09 · independence_and_cluster_admissibility_rule

Gate **O1**; suggested expertise: statistics.

Which experimental unit supports the proposed marginal count law and which records share founders, wells, paired arms or batches?

**Deliverable:** Founder/run/batch dependency graph; one-outcome rule or justified alternative marginal likelihood; complete inclusion/exclusion map with correlated descendants retained as clusters.

**Refuse or revise if:** Treating image fields, plate suffixes, descendant colonies or repeated measurements as independent biological runs.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S10 · training_contexts_and_blocks

Gate **O3**; suggested expertise: biology and statistics.

Which entire contexts and blocks could train the unchanged forecast without leakage into evaluation?

**Deliverable:** Candidate membership table with founder/batch/paired-arm grouping and prior-access history; explicit allowed training outcomes and calibration sources.

**Refuse or revise if:** Splitting linked descendants across training and test or selecting contexts because curvature agrees.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S11 · heldout_contexts_and_later_blocks

Gate **O4**; suggested expertise: statistics and data stewardship.

Which genuinely unexposed endpoint records or future independent blocks can remain inaccessible until freeze?

**Deliverable:** Outcome-access ledger, dated custodian attestations and split made before access; a later independent block if published/inspected endpoint outcomes informed design.

**Refuse or revise if:** Calling already-known source outcomes held-out after hiding columns, redownloading or assigning a new split.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S12 · training_to_target_feature_admissible_range

Gate **O3**; suggested expertise: biology and statistics.

Over what independently supported establishment-feature range and context changes may training information transfer?

**Deliverable:** Training/target feature and ecological-state ranges, predeclared extrapolation rejection criteria and independent support for proposed transport.

**Refuse or revise if:** Using favourable target winners to admit an extrapolation or deriving missing target F from those winners.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S13 · declared_heldout_context_weights

Gate **O4**; suggested expertise: statistics.

What population of contexts do the score weights represent, and can the weights be fixed independently of outcomes?

**Deliverable:** Target-context rationale and a proposed normalized nonnegative weight vector with timing/provenance; no actual weights selected here.

**Refuse or revise if:** Reweighting by favourable results or post-outcome sample totals.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S14 · trials_per_context_and_measurement_arm

Gate **O4**; suggested expertise: statistics and operations.

What independent trial numbers in each arm are feasible after accounting for rare eligible events, clustered controls and losses?

**Deliverable:** Costed arm-by-context design options with independent-unit counts, anticipated attrition, instrument capacity and blinded precision/power analysis; technical repeats shown separately.

**Refuse or revise if:** A chosen sample size inferred from a paper total or repeated image count without an eligible-trial model.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S15 · exclusion_and_missingness_rules

Gate **O1**; suggested expertise: biology and statistics.

How will every allocated record, failed introduction, lost track, unresolved call and excluded run be retained?

**Deliverable:** Predeclared reason codes, stage-wise denominator reconciliation and missingness sensitivity plan, distinguishing structural absence from not measured.

**Refuse or revise if:** Missing cells made zeros, lost lineages made origin-negative or exclusion based on observed route.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S16 · total_study_alpha

Gate **O4**; suggested expertise: statistics.

What total inferential noncoverage budget is scientifically acceptable for this single fixed study?

**Deliverable:** Signed proposed study-level error rationale covering the declared claims; explicit relation to prior looks and no renewal across research rounds.

**Refuse or revise if:** A default alpha adopted by this worksheet or silently refreshed after each round.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S17 · count_and_transfer_error_allocation

Gate **O4**; suggested expertise: statistics.

How will count uncertainty and estimated control/transport uncertainty share that same total budget?

**Deliverable:** Complete component/error ledger and valid joint coverage argument for the intended comparisons; no independent-errors assumption unless justified.

**Refuse or revise if:** Treating estimated calibration bounds as exact or spending the same allocation twice.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S18 · primary_effect_threshold_nats

Gate **O4**; suggested expertise: biology and statistics.

Which improvement in nats per qualifying observed triad would matter scientifically and be plausible?

**Deliverable:** Domain rationale and blinded effect scenarios under all comparators; explicit distinction from mechanistic effect or all-category performance.

**Refuse or revise if:** Selecting a threshold after seeing scores or transferring a synthetic illustration as a biological effect estimate.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S19 · primary_success_and_failure_gates

Gate **O4**; suggested expertise: biology and statistics.

Which possible score, uncertainty or admissibility results mean success, failure or unevaluable?

**Deliverable:** Prospective decision table covering every comparator, missing forecast, empty numerical region, non-rejection and category attrition.

**Refuse or revise if:** Calling overlap proof of equality or a predictive gain proof of a mutation force.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S20 · fixed_stopping_rule

Gate **O4**; suggested expertise: statistics and operations.

What fixed collection endpoint and stopping rule can be committed before evaluation outcomes?

**Deliverable:** Time/sample-based stopping specification and operational deviations plan; any sequential alternative requires its own admitted calibration and amendment.

**Refuse or revise if:** Stopping at a favourable score or introducing new interim tests without a calibrated rule.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S21 · blinded_design_precision_and_power_plan

Gate **O4**; suggested expertise: statistics.

Can a blinded design study show feasible precision under sparse supply, observer error, dependence and comparator similarity?

**Deliverable:** Executable independently reviewed design scenarios, success/failure probabilities and resource totals over plausible nuisance ranges; preserve the unchanged forecast algorithm.

**Refuse or revise if:** Simulation success with oracle truth used as empirical calibration or generic power from ideal independent cells.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S22 · route_phase_control_transfer_bounds

Gate **B3**; suggested expertise: biology and statistics.

How large can control-to-native mismatch be in each route, phase and ecological state?

**Deliverable:** Independent matched transfer evidence across the R27 transport key and proposed uncertainty bounds; identify unbounded components and limits of J-only bounds.

**Refuse or revise if:** Bounds fitted from held-out winners or an unknown mismatch declared zero.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S23 · full_observation_map_if_biological_forecast_requested

Gate **B3**; suggested expertise: assay science and statistics.

If biological full-vector prediction is requested, what complete truth-to-called-category observation model is identifiable?

**Deliverable:** Route-by-called-category matrix including off-diagonal, Other, unresolved and unrecovered/no-event handling plus phase/context transfer; identify the separately scoped estimand.

**Refuse or revise if:** Diagonal recovery alone or a contrast-only J bound used to recover latent full-vector/all-category probabilities.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S24 · numeric_score_decision_implementation

Gate **O4**; suggested expertise: numerical statistics.

Which implementation can make the specified score decision with adequate numeric guarantees?

**Deliverable:** Versioned code and independent boundary tests, logarithm/interval policy, underflow/empty-region handling and signed implementation review.

**Refuse or revise if:** Floating-point diagnostic output advertised as a certified decision engine.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S25 · actual_laboratory_or_data_partner

Gate **G0**; suggested expertise: biology and operations.

Which qualified group has materials, instrumentation, independent truth capacity and authority to assess this proposal?

**Deliverable:** Capability statement, roles, independence/conflict record, access/license constraints and itemized feasibility quotation when separately commissioned; no partner selected here.

**Refuse or revise if:** An author list or AI review treated as a laboratory commitment or qualified external assessment.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## S26 · preregistration_accession_and_frozen_hash

Gate **O4**; suggested expertise: statistics and data stewardship.

What dated registration and byte-level freeze will bind inputs, forecasts, categories, error allocation and stopping before unblinding?

**Deliverable:** Accession, immutable file manifest, independent timing/access receipts and amendment policy covering TMD and every complete comparator vector.

**Refuse or revise if:** A hash created after outcomes or a publication date represented as proof of prospective freezing.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N01 · matched_system

Gate **G0**; suggested expertise: biology.

Which eligible biological system can support the intended native-origin question and common-background comparison?

**Deliverable:** Scientific system rationale, actual material availability and a match/mismatch table against the bacterial candidate or separately scoped translation target.

**Refuse or revise if:** A cancer or E. coli method lead treated as an admitted SBW25 system.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N02 · founder_identity

Gate **G0**; suggested expertise: molecular biology.

How can the actual founder and its pre-existing genotype be independently established?

**Deliverable:** Founder identity/custody, parental molecular truth and ancestry links with uncertainty; distinguish stock authentication from event-origin certification.

**Refuse or revise if:** Assuming all founders are reference because an endpoint is smooth or a database record is labelled WT.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N03 · native_event_catalogue

Gate **B1**; suggested expertise: molecular biology.

Which native events are eligible, including event types the observer cannot see?

**Deliverable:** Versioned native catalogue with allele/locus/structural-event coverage, exclusions and molecular truth requirements; catalogue selection independent of winners.

**Refuse or revise if:** An assay limited to mismatches presumed to census all route-changing indels or structural events.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N04 · ordered_axis_rationale

Gate **B3**; suggested expertise: biology and statistics.

Is the existing ordered axis biologically meaningful for this candidate, or is this a different unadmitted model?

**Deliverable:** Independent scientific rationale relating eligible event classes to the fixed W/A/M order and axis; explicit separate-review requirement for any adaptation.

**Refuse or revise if:** Reordering labels or choosing a new axis to improve curvature, including automatic cross-system transplantation.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N05 · event_unit_and_episode_rule

Gate **B1**; suggested expertise: molecular biology and statistics.

How will one new acquisition episode be distinguished from inheritance, recurrence, transfer and descendant copies?

**Deliverable:** Parent-child event rules with time resolution and independent validation; record unresolved episodes and exposure intervals rather than exact unsupported birth times.

**Refuse or revise if:** Repeated carrier calls counted as repeated births or sequence identity alone used to infer a single origin.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N06 · native_caller_version

Gate **B2**; suggested expertise: molecular bioinformatics.

What exact native caller and reference produce variant and origin calls, and which stages are adaptive?

**Deliverable:** Version, configuration, reference genome, support/callability filters, training sources and adaptation audit; all failed/no-call states retained.

**Refuse or revise if:** A caller-selected truth set or undocumented sample-specific thresholds used as independent calibration.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N07 · complete_inclusion_predicate

Gate **B2**; suggested expertise: bioinformatics and statistics.

What complete predicate determines whether a true episode can be included in analysis?

**Deliverable:** Formal carrier/reference/support/quality/recurrence predicate, eligible universe and zero-inclusion states; separate per-cell recovery from event inclusion.

**Refuse or revise if:** At-least-one recovered carrier substituted for a caller requiring several carriers and an informative reference branch.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N08 · independent_origin_truth_source

Gate **B1**; suggested expertise: molecular biology.

What evidence establishes origin truth independently of the assay being tested, at the intended stage?

**Deliverable:** Paired ancestral/newly acquired evidence or another qualified independent reference with its own error limits; separately assess variant, ancestry and episode truth.

**Refuse or revise if:** Bulk rate agreement, a fluorescent focus or reconstructed tree accepted as per-event molecular-origin truth.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N09 · truth_carrier_and_reference_sets

Gate **B2**; suggested expertise: molecular biology and statistics.

Which truth carriers and comparison/reference states jointly challenge the actual native predicate?

**Deliverable:** Predefined independent carrier/reference sets with ancestry, callability, multiplicity and selection history; blind truth assessment includes assay failures.

**Refuse or revise if:** Reference absence treated as a true negative when uncallable; only successful calls included in a truth set.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N10 · lost_lineage_truth_limits

Gate **B1**; suggested expertise: imaging and molecular biology.

Which dead, detached, washed-out, unrecovered or unsequenced lineages retain molecular-origin truth?

**Deliverable:** Stage-by-stage loss ledger, last observation/time window, independent lost-state truth where feasible and explicit nonidentifiable/unbounded components.

**Refuse or revise if:** Tracking disappearance called extinction without adjudication, or an imaged division used to infer a missing cell genotype.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N11 · negative_truth_and_false_positive_rule

Gate **B2**; suggested expertise: molecular biology.

How will false new-origin labels be tested using inherited/pre-existing variants as well as absent variants?

**Deliverable:** Distinct origin-negative variant-positive and variant-negative panels, each independently established with context-specific false-positive/no-call records.

**Refuse or revise if:** Absence controls alone used to validate de novo classification, or unknown loss treated as origin-negative.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N12 · independent_replication_unit

Gate **O1**; suggested expertise: statistics.

Which independent founder/culture is the replication unit for native controls and how are nested genomes/calls clustered?

**Deliverable:** Biological-unit and shared-lineage graph linking cells, technical aliquots, sequencing libraries and batches to a justified likelihood.

**Refuse or revise if:** Genomes from one pedigree called independent biological replicates.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N13 · locus_and_genotype_state_matching

Gate **B3**; suggested expertise: molecular biology.

How do truth controls match locus, genotype, copy/allele state, burden, physiology and ancestry of target events?

**Deliverable:** State-specific match table and residual transport evidence, including marker/repair perturbations and lineage survival.

**Refuse or revise if:** Engineered or bulk controls assumed to mimic native event states without a measured match.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N14 · joint_call_control_design

Gate **B2**; suggested expertise: statistics and bioinformatics.

How will joint carrier/reference calls and their dependence be validated for the complete inclusion rule?

**Deliverable:** Joint outcome records per independent episode/cluster, failure patterns and an admitted joint law or justified bounds.

**Refuse or revise if:** Multiplying marginal call probabilities without a dependence model or equating caller concordance with independent truth.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N15 · batch_and_context_transport_rule

Gate **B3**; suggested expertise: biology and statistics.

Across which batches/contexts can measured controls transfer, and what makes that transport defensible?

**Deliverable:** Predeclared transport key, independently observed discrepancies and bounds; exchangeability assessment if an envelope is proposed.

**Refuse or revise if:** Deliberately chosen media assumed exchangeable or a common instrument taken as complete context matching.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N16 · uncertainty_and_error_allocation

Gate **O4**; suggested expertise: statistics.

How does the native-origin uncertainty plan integrate with the single study error budget if that branch is pursued?

**Deliverable:** Cross-reference to the study error ledger, count/measurement/transport components and declared claim family; proposed bounds and missing-truth handling.

**Refuse or revise if:** A second hidden error budget, oracle truth assumptions or unreported multiple claims.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N17 · algorithm_adaptation_rule

Gate **O3**; suggested expertise: statistics and bioinformatics.

Which training-only adaptations are permitted, and how will a different candidate be identified before evaluation?

**Deliverable:** Versioned adaptation/freeze policy with allowed training information, independent evaluation access and explicit rejection of target-informed changes.

**Refuse or revise if:** Adapting caller, axis, eta, comparator or eligibility after seeing held-out outcomes and retaining the original-candidate claim.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL

## N18 · frozen_stopping_and_analysis

Gate **O4**; suggested expertise: statistics and data stewardship.

How will native analysis and stopping be jointly locked with the observed-forecast study?

**Deliverable:** Linked dated manifests, fixed analysis/stopping rules and deviations record consistent with study registration; no values supplied by this template.

**Refuse or revise if:** Stopping by favourable mutation counts or reusing known outcomes as an untouched validation set.

**Answer:** NULL  
**Evidence/version/section:** NULL  
**Reviewer and decision:** NULL  
**Rationale, uncertainty and unresolved dependencies:** NULL


# TMD recovery-transport research follow-up

Ricardo Maldonado · 1 October 2026 · Exploratory methods and prospective research

Start with [the formulation and next empirical test](FORMULATION_AND_NEXT_EMPIRICAL_TEST.md), then [the reproducible sensitivity analysis](transport_robustness/README.md) and [independent internal review](TRANSPORT_MATH_REVIEW.md). The [five-source literature update](literature/LITERATURE_UPDATE_2026-10-01.md) develops competing explanations; the [public source eligibility audit](public_dataset_audit/AUDIT_REPORT.md) verifies a published table inventory without relabeling its measurements as TMD trials.

The biological priority remains an authenticated, prespecified matched route/control panel. This follow-up reuses all 160 published synthetic outputs and adds a chosen-count recovery-confounding counterexample. It integrates earlier methods rather than claiming a new mutation mechanism or statistical principle. All 44 tests pass. Independent checks confirm 640 original projections, 800 sensitivity-grid evaluations and 40 exact compatibility-frontier certificates.

Reproduce from this directory with Python 3.12.14 (only the standard library is needed):

```sh
python3 -m unittest discover -s transport_robustness -p 'test_transport_robustness.py' -v
python3 transport_robustness/run_reanalysis.py --check
python3 verify_transport_review.py --public-archive ../TMD_research_extension_0_5_0_2026-09-30.zip
```

The independent oracle writes its deterministic review receipt beside itself. Copy this directory to a scratch location before regenerating receipts or result files if preserving an untouched checkout. `run_reanalysis.py --check` compares outputs without rewriting them.

[Environment reproduction evidence](ENVIRONMENT_REPRODUCIBILITY.md) distinguishes successful computational checks from the original release's strict floating-result identity failure. [Publication candidate](PUBLICATION_CANDIDATE.md) describes a proposed next methods version; it is not a publication receipt. The current released archive remains 0.5.0, expanded report 0.1.0, and historical software v2.6.5.

New code is MIT; new documentation is CC BY 4.0 under the repository licensing terms. Preserved public source artifacts retain attribution and their existing terms. Prepared with AI assistance; internal independent review is not external peer review.

## Public-source audit reproduction

The source XML remains outside this repository. To reproduce against the inspected local snapshot, supply its path explicitly:

```sh
python3 public_dataset_audit/reproduce_audit.py --source /path/to/sane_pmc.xml --output /tmp/tmd_public_source_audit.json
```

Alternatively, the script can attempt an official public acquisition with `--fetch-source`. Only the pinned source hash is accepted. The supplementary workbooks were not acquired, and no raw-workbook analysis or new biological test is reported.

## Continuing research rounds

The [continuation protocol](continuation/README.md) records the requested GPT-6.1 Sol Ultra setting, persistent checkpoints, an hourly workflow and a daily changed-source watch. The workflow is merged and explicitly paused. Its [single manual test](continuation/MANUAL_TEST_2026-10-02.json) skipped inference; the [checksum-verified artifact](continuation/ARTIFACT_READBACK_2026-10-02.json) now identifies the historical missing provider key and reproduces the collector's blocked receipt. Current Actions secret metadata remains inaccessible. The first new [drift-source audit](drift_audit/DRIFT_AUDIT_2026-10-01.md) reconciles biological and technical units and a model-conditional census residual; it supplies no matched W/A/M panel or establishment estimate. [Independent internal review](drift_audit/INDEPENDENT_REVIEW.md) checks the source identities, calculations and limits.

The second [matched-panel eligibility audit](panel_eligibility/README.md), dated 2 October 2026 UTC, authenticates four primary articles. Original notes, structured measurement ledgers and offline verification preserve source overlap, actual sampling units and unacquired-data limits. No complete matched panel is admitted. The [prospective design round](prospective_design/README.md) is now complete as design-only, with a frozen operational prediction algorithm and independently checked synthetic fixtures. Twenty-six study inputs remain unresolved; this is not a registered experiment. Subsequent source-watch and raw-data audits strengthen the measurement contract; the actual study remains blocked.

## Latest source and numerical follow-up — 2 October 2026

The [bounded source watch](source_watch/2026-10-02/README.md) inspects three primary articles and two unchanged preprint records. A transcription-dependent hotspot in SBW25 provides a specific mutation-supply alternative, while population-history and plasmid-masking studies sharpen endpoint and observation limits. New in this watch means absent from the inspected public baseline notes, not a new scientific discovery or independent cohort. All three source identities/dates, 72 paragraph pins and 12 response hashes replay against the external cache; [independent source review](source_watch/INDEPENDENT_REVIEW_2026-10-02.json) checks the claims and licenses.

The [certified score candidate](certified_score/README.md) implements the R3 expected-log-score target using exact rational CP brackets, bounded logarithm series and box/simplex projection. The same simultaneous region covers all frozen comparators. It preserves full endpoint ledgers, strict gates, explicit resource caps and conditional-law requirements; zero qualifying counts remain unevaluable. The illustrative result is inconclusive. Its pre-outcome 0.05-nat half-width calculation needs 527/921 qualifying endpoints, beyond the 500-unit prototype cap. This supplies no power, biological effect, causal mechanism or registered study, and none of the 26 actual study inputs is filled.

Current [publication status](PUBLICATION_STATUS.md) supersedes the earlier draft checkpoint: record23113326 is now published with inherited0.5.0 files and no version label. The reviewed0.6.0 ZIP remains absent. On7 October, user-confirmed publication responsibility and fresh ownership checks allowed creation of replacement draft 23219776 in the existing family. MetadataPUT500 and multipart POST HTTP 400 prevent complete staging; the draft remains unpublished with inherited files intact. Reuse that draft and verify metadata/files before publication; no redundant credential or additional draft is needed.

## Authenticated figure-data follow-up — 7 October 2026

The [SBW25 data audit](sbw25_data_audit/README.md) authenticates a 7,880,751-byte CC BY 4.0 source ZIP and 28 research-file fingerprints, preserving 24 culture occurrences and 711 sequencing reads as different units. It reconstructs the source’s terminal-frequency, time-course, supplied competition and transcript-proxy arithmetic. Its 118.97-fold descriptive frequency contrast differs from the author-reported 58.33-fold MSS rate contrast; the likelihood fit and its assumptions remain unreproduced.

Ten source-to-measurement gaps remain explicit. In particular, one row has 7 counted candidates and 8 sequenced colonies, and one sequencing file is missing a read included in the workbook denominator. The independent [methods note](sbw25_data_audit/METHODS_RECOMMENDATION.md) separates mutation production, clone expansion, genotype confirmation and native/reporter transfer, and derives an ordinary supply-transfer sensitivity extension. No finite W/A/M transfer bounds or actual study inputs are inferred.

The [October 7 metadata/abstract watch](source_watch/2026-10-07/README.md) adds two screened records: a eukaryote mutation-accumulation study and an E.coli–P1 recombination study. Full texts/data were not analyzed in that watch. The latter motivates a later mutation-versus-transfer scope check; it does not establish that transfer occurred in SBW25. All 26 actual study fields remain unresolved.

## Fluctuation observation and inheritance follow-up — 7 October 2026

R000007's [measurement contract and conditional benchmarks](fluctuation_contract/README.md) reconstruct nominal geometry from the final article and workbook. The wild-type assay samples nominally 0.0075%, 0.0167% or 0.075% of a 6-mL culture, and the deletion assay 7.5%. These fractions do not calibrate recovery or actual end-of-assay volume. A classical compound-Poisson model shows why mutation production, clone size and detection cannot be identified from zeros alone; full count distributions may add information under a validated model. Exact finite synthetic identities and independent mathematical review are separate from the biological source reconstruction. No biological MSS fit, new rate or confidence interval is produced.

R000008's [recombination scope assessment](recombination_scope/README.md) reads the complete main primary paper behind the earlier abstract lead. Six identity checks and thirteen selected source anchors replay; sixteen measurement rows separate genotype origin, culture, recovered colony and molecular-event units. The reported 380-fold comparison concerns recombinant versus mutant CFU abundance, not independently counted event rates. Horizontal transfer must be excluded with evidence or included in an explicitly measured entry domain; no E.coli–P1 parameter is transferred to SBW25.

The [previous continuation handoff](CONTINUATION_HANDOFF_2026-10-07_R7_R8.md) records that checkpoint's next questions. Older source-watch/R6 receipts retain their original inspection depth and results. The same cohort and additional reading do not create an independent biological replication. All 26 actual study inputs remain unresolved; publication still uses the preserved existing Zenodo draft.

## Source input and paired sampling follow-up — 7 October 2026

[R000009](source_input_authentication/README.md) reproduces 144 arithmetic comparisons for 24 source culture rows, identifying nine fractional wild-type candidate-pool estimates. It distinguishes source-derived counts/densities/conversions from unauthenticated historical software submissions. Four new bounded access attempts acquired no software or author-response body; no biological fit is executed.

[R000010](paired_aliquot/README.md) implements classical paired-disjoint, overlapping and independent-history observation laws with exact finite synthetic coefficients. It supplies a candidate conditional allocation check requiring a prespecified ratio and rejection rule, and examples showing why a passing check, covariance or endpoint agreement cannot alone identify mutation intensity or mechanism. Invisible zero-terminal marks can preserve the entire observation law while changing latent event intensity. The code's triangular coefficient table is truncated, not normalized complete biological data.

The [previous R9/R10 handoff](CONTINUATION_HANDOFF_2026-10-07_R9_R10.md) carries forward the blocked actual-input authentication and prioritizes independent cell/CFU and absolute capture calibration. All older immutable files, forecasts and study budgets remain preserved. No Zenodo staging or publication operation was performed in these rounds.

## Absolute recovery follow-up — 7 October 2026

[R000012](recovery_calibration_sources/README.md) authenticates two public primary main-text methods/results sources and screens an abstract-only microscopy lead, retaining20 source-specific measurement rows. Instrument enumeration, membrane/redox classifications, terminal colony recovery and mutation origins remain separate. Raw calibration supplements and matched native-control transport remain unresolved.

[R000013](capture_calibration/README.md) supplies standard finite binomial inversion, sharp void bounds and explicit complete-law ambiguity witnesses. Known capture and positive terminal marks can identify positive terminal intensities from a complete population jump vector; unknown capture or invisible events retain ambiguity. This is conditional synthetic methods work with independent internal review, not a finite-data likelihood fit, biological rate, new theorem or cancer-prevention result.

The [latest R12/R13 handoff](CONTINUATION_HANDOFF_2026-10-07_R12_R13.md) preserves earlier checkpoints and queues source-pinned raw normalization and lineage/control denominators. All26 actual study fields remain unresolved. No Zenodo staging, publication request or GitHub release was made in these rounds.

## Cancer translation and normalization — 7 October 2026

[R000014](normalization_audit/README.md) completes a source-specific reporting audit while raw acquisition remains blocked. A synthetic log-median example gives10 from a raw midpoint50 under explicit zero-handling/reporting assumptions; a separate paired example gives marginal ratio550 and paired median12. These are not clinical data or corrections. No DOCX, actual reporting convention or introduced-unit/lineage calibration is authenticated.

[R000015](cancer_translation/README.md) prepares a prospective cancer-domain measurement contract and a growth/recovery competing explanation. Generic R1/R2/R3 catalogs and axis remain unchosen. The human2018 source's844samples are nested in9donors; mouse2021 lesions and micro-biopsies are nested in animals and simulations remain separate. A common-curvature expected-mixture pattern can occur without changed mutation generation. This is not a lineage likelihood or TMD cancer validation.

Producer checks comprise30normalization arithmetic,52source/acquisition,222cancer synthetic and26cancer source checks. Independent oracles perform105unit/source checks over36volume cases and11561checks over1280rational cases. These are internal checks, not independent biological replications or external qualified peer review. Read the [latest continuation handoff](CONTINUATION_HANDOFF_2026-10-07_R14_R15.md). All26actualstudyfields remainNULL. Immutable0.6.0 excludes these later rounds.

## Epithelial lineage and bounded curvature — 7 October 2026

[R16's source-specific lineage audit](epithelial_lineage/README.md) identifies a published optical-pedigree and sequencing architecture. Its 24 primary sequenced subclones descend from two displayed founders. Realized sequenced/available fractions11/45 and13/26 are descriptive nested observations, not calibrated route recovery or independent mutation births. Unequal cell backgrounds and ungenotyped losses prevent a matched TMD test.

[R18's exact bounded-curvature tool](curvature_bounds/README.md) tests conditional common-curvature feasibility after independently supplied supply, growth and recovery bounds. It separates free common curvature, a fixed curvature forecast and full conventional supply-growth-recovery proportionality. Wide bounds can leave the question unresolved; empty intersection is conditional algebraic incompatibility, not an empirical rejection without a justified joint uncertainty envelope. The expected-mass model does not supply a culture/founder or first-arrival count law.

Both packages are internally independently checked. No cancer prevention, new mutation mechanism, new theorem or biological fit is established. Read the [current continuation handoff](CONTINUATION_HANDOFF_2026-10-07_R16_R18.md).

Producer checks: R16source/software/stage62; R18synthetic353across10fixtures. Independent R16oracle enumerates494nested stage cases with3516checks. Independent R18blind oracle evaluates65740corner curvatures in38contexts and466comparison/guard checks; an additional semantic reviewer checks10fixture certificates and4160corner values. These are computational checks, not biological replications or external qualified peer review. Frozen0.6.0 excludes these later rounds.

# CNV inference: independent fitness checks and an unresolved formation rate

Ricardo Maldonado · 15 October 2026 · Original analysis with AI assistance

Avecilla et al. (2022), [Neural networks enable efficient and accurate simulation-based inference of evolutionary parameters from adaptation dynamics](https://doi.org/10.1371/journal.pbio.3001633), supplies a useful conventional comparator for TMD. It jointly infers a GAP1 CNV formation rate δ_C and an effective selection coefficient s_C from population reporter trajectories. The paper reports experimental checks of fitness, while explicitly stating that its inferred CNV formation rate in nitrogen limitation still requires experimental confirmation. Fitness agreement therefore must not be treated as independent observation of mutation births or validation of the inferred formation rate. This boundary is explicit in Discussion section sec010, direct paragraph 4, authenticated in the full article XML.

The article was published on 27 May 2022. It is a distinct primary study, not a correction to Lauer et al. (2018) or a newly published discovery. Its eleven trajectories reuse gln_01–gln_09 and bc01/bc02 populations from the [2018 study](https://doi.org/10.1371/journal.pbio.3000069). New barcode sequencing of frozen source material and new competitions add assay evidence, but do not create a new independently evolved population cohort. The study is newly assessed in this continuation; its underlying evolution data are shared with the source assessed in R38.

## What the conventional model actually estimates

The source compares Wright–Fisher and continuous chemostat simulators, using ABC-SMC and neural posterior estimation. Its formation-rate symbol δ_C must retain its source meaning; the article also uses μ for chemostat growth. Other beneficial mutation parameters are fixed in the principal model, with sensitivity analyses. A single effective CNV rate and selection coefficient are a stated limitation, rather than a complete independently measured distribution of route-specific mutation supply and establishment.

| Source result | Interpretation and limit |
| --- | --- |
| Empirical MAP ranges: s_C approximately 0.04–0.1 per generation; Wright–Fisher δ_C 10^−4.1–10^−3.4 per cell division; chemostat δ_C 10^−4.7–10^−4 per cell division | Ranges across population fits, not simultaneous confidence intervals or new TMD estimates. |
| Empirical inference restricts observations with a generation-116 cutoff after later posterior-predictive mismatch | An outcome-informed source analysis window, not a prospectively frozen TMD holdout. |
| Strong-selection synthetic cross-model example overestimates formation rate by about 3–5 fold | Source-reported simulator misspecification result; no numerical replay or empirical TMD rejection was performed here. |
| Three held-out observations used for DFE inference checks | Synthetic observations; they are not native biological TMD test sets. |
| Barcode analysis infers establishment time, fitness and population mean fitness iteratively | Model-derived quantities from trajectories; they do not constitute an independent earlier mutation-origin observer. |

The barcoded reporter has a slight source-specific fitness cost, for which the competition analysis adjusts. This is useful evidence for retaining explicit marker and assay controls. Its numerical correction cannot be imported into a different organism or native SBW25 study. Exact source anchors and paragraph identities appear in [INFERENCE_DEPENDENCIES.json](INFERENCE_DEPENDENCIES.json).

## What the actual code artifact adds

An immutable repository blob authenticates the actual `figures/Figure7andSup.Rmd` inspected here. Its Git identity and decoded SHA-256 are recorded in the [static code audit](CODE_AUDIT.json) and [code report](CODE_REPORT.md). This is a repository snapshot, whose identity with the exact publication-execution script remains unverified. No source-author code was executed.

The competition DFE selects positive estimated fitness coefficients after excluding ancestor identifiers. This agrees with the article's beneficial-variant comparison, but a positive point estimate is not statistical significance and cannot be identified with the 2018 study's 18/28 significantly fitter clones. Barcode identifiers are attached by row position before key-based joins; a bc04-to-bc01 alias is used; unmatched barcodes receive a plotting label of noCNV; and retained trajectory counts are renormalized. These are concrete input-verification requirements. No input-order mismatch, numerical error or author coding fault has been established.

The actual CSV inputs, clone rows, retained-row counts, alias documentation and join cardinality are unverified. The required CSV filenames are absent from the inspected nontruncated 62-entry repository tree; their absence elsewhere is not asserted. Transformed plot cell numbers are not an independent cell census, and absence of a CNV join is not independent DNA-genotyped negative truth.

## What remains unresolved

The complete 2018 article XML now authenticates its CC BY 4.0 article license and the literal S4 workbook attachment `pbio.3000069.s021.xlsx`, described as clone-summary and CNV read-depth boundary/size data. It also makes the selection chain explicit: plating on YPD, random colony selection, 24-hour regrowth in the evolution-limitation medium, fluorescence comparison, then a subset selected for sequencing. The workbook bytes were not recovered. Publisher redirection and a PMC browser challenge yielded no XLSX; neither is evidence that the data do not exist. The 29 sequenced-clone versus 28 competition-clone membership and missingness still need actual identifiers.

Both article XML representations explicitly state CC BY 4.0. Separate OSF data/code terms and the inspected GitHub software license body remain unverified; article licensing is not transferred to those materials. Public files contain original analysis and selected bibliographic facts, not full articles, code bodies, figures, raw sequences, private archive paths or contacts.

The result strengthens the conventional mutation–selection–drift comparison and narrows the measurement contract for a future TMD test. It supplies no native matched W/A/M panel, independently measured birth rate and establishment pair, biological fit, new theorem or confirmed TMD mechanism. All 26 actual study inputs and 18 planning inputs remain NULL. R5/R11/R17, theta/eta, frozen predictors/comparators/evaluation, error allocation, fixed stopping and the paused runner are preserved. Methods 0.6.0 remains frozen; this source addendum does not justify a new Zenodo methods version.

The next useful record is a lawful versioned source table that joins clone identity, genotype, fluorescence, selection and fitness, or the named CSV inputs with row-order, alias and missingness records. It must distinguish newly measured assays from shared evolution material, positive-estimate selection from significance, and unmatched joins from independently validated negatives. Unchanged source-access failures remain parked. Internal review here is AI-assisted source review, not qualified external biological review.

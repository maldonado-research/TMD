# Rendered Figure 7 outputs and the binned plot contract

Ricardo Maldonado · 16 October 2026 · Original analysis with AI assistance

R42 authenticates an original-author rendered Figure 7 notebook and README for [Avecilla et al. (2022)](https://doi.org/10.1371/journal.pbio.3001633). The notebook preserves a machine-readable four-category summary, typed input-column reports and a binned plotting specification. It adds concrete source-output evidence without recovering the three competition CSVs or verifying the publication execution.

The [audit](AUDIT.json) records ten findings and fifteen source anchors. The [provenance record](SOURCE_PROVENANCE.json) gives exact source sizes, SHA-256 identities and Git blob checks. All reading and comparison was static; no R, JavaScript, serialized R frame, source-author analysis or biological simulator was executed.

## A stored summary has a defined denominator

The HTML contains one paged-table JSON payload with four rows and four columns; separate notebook frame metadata agrees with those dimensions. Its bc01 entries report:

| Source join label | Source fitness label | Stored count |
| --- | --- | ---: |
| CNV | adaptive | 1,513 |
| CNV | neutral | 6,888 |
| noCNV | adaptive | 56 |
| noCNV | neutral | 72,294 |

These factual counts sum to 80,751. They are stored output attributed to the authors' grouped summary, not independently replayed results or authenticated counts of distinct biological lineages. The visible recipe first binds numerical inference results to a separate identifier file by row position, assigns the population name, and left-joins the CNV annotation. It then classifies positive `Mutation_Fitness` as adaptive and counts rows with `n()`. Missing joined CNV annotation becomes the displayed noCNV label. That label does not establish independently genotyped negative truth.

The source does not establish unique barcode identities or one-to-one join cardinality. The previously authenticated preprocessing can add an aggregate low-count row, and the FitMut export combines lineage-length and time-length arrays with padding. The actual input/output/identifier manifest is still needed to determine whether any such row entered this summary. No aggregate-row inclusion, padding failure, identifier mismatch or published numerical error has been demonstrated.

This summary uses the joined inference table. Panel A's trajectory display applies a separate sequence of initial-zero and later reappearance exclusions. The 80,751 total is consequently not authenticated as a count of plotted trajectories. Panel C selects positive inferred fitness for CNV-labeled entries and positive competition estimates after its ancestor-name exclusion. The 1,513 stored CNV/adaptive count does not certify the final number contributing to the displayed plot, which also has an x-axis scale limited to 0–0.2. No odds ratio, biological association test, mutation rate or selection estimate is computed from this table.

## The authenticated recipe is binned

The visible HTML code, its embedded downloadable R Markdown source and the separately authenticated R Markdown file all specify `geom_density_ridges2(stat = "binline", bins = 25, scale = 1)`. The source call requests binned ridgelines. Its function name does not establish a kernel density estimate.

This is a narrow correction to R41's handoff language calling the combined comparison a KDE with automatic bandwidth. The inspected Figure 7 snapshots specify binline with 25 bins; they do not substantiate an automatic KDE bandwidth. Historical checkpoint files remain preserved. The correct limitation remains: R41's conditional empirical-CDF bounds do not directly certify this plotted distribution, its binning, the combined barcode/competition sample, or mutation-origin truth. The Lauer-derived one-to-three repetition assumption cannot be applied to the barcode summary.

Matching statistical recipes do not prove identical execution. There are 183 nonblank R code lines in each of the three representations. Comparing visible HTML code with either embedded or separate R Markdown, 180 lines match exactly; the three differences are assignments to `bar_dir`, `param_dir` and `fit_dir`. Embedded and separate R Markdown differ only in `bar_dir`; their complete bodies are 9,835 and 9,832 bytes. All eighteen visible R source blocks also match their respective notebook source comments after removing the Markdown fences. The audit records hashes and variable names for the directory differences while withholding private path strings. The plot recipe itself agrees across the snapshots. The different input-directory assignments reinforce the need for actual input checksums and execution provenance.

## Column reports improve the measurement contract

Stored reader output names `clone` and `fitness_coef` for the fitness export. The Lauer-derived competition input reports eleven columns: `anc`, `timept`, `sample`, `evo`, `prop`, `transformed`, `hours`, `generation`, `run`, `strain` and `type`. The presence of both time columns is useful for locating the eventual clock audit. It does not authenticate their values, the construction of `transformed`, a conversion between hours and generations, exclusions, missingness, clone/run multiplicities or the exported row count.

The inference reader reports eight numeric fields, including fitness, establishment time, three likelihood fields, mean fitness, a noise parameter and mutant fraction. The stored table's positive-fitness label must still be interpreted in the context of the previously inspected upstream model classification. It is not direct observation of mutation births or independently measured establishment.

## Source identity and remaining admission gates

The README is 2,449 bytes and verifies Git blob `b7ff6cf77072b6e795941c9c8fa893a2e4b5e4e7`. The rendered notebook is 1,732,366 bytes and verifies Git blob `b1d81e85d194665438cac46f001e39ac3e5d0838`. The README associates the HTML files with the figure R Markdown and directs the data to OSF E9D5X. It supplies no alternate CSV download location or separate data terms. The three R40 competition CSVs remain unrecovered, with their previously recorded API-advertised hashes unchanged. No blocked OSF download host was requested.

The cached repository MIT license is authenticated. It does not settle independent OSF data terms or every bundled HTML dependency. Publication candidates contain original assessment, identity facts and the four necessary aggregate counts; full third-party code, notebook bodies, figures, raw measurement rows and private paths stay outside Git.

Four acquisition attempts are conservatively charged to this producer: two local command/setup failures and two successful pinned GitHub blob requests. Captures, failure text and receipts total 1,737,712 bytes. No additional full source body was saved by the producer; the embedded source and comments were decoded only in memory. Independent reviewers' explicit source-derived copies are accounted separately in the round ledger. Two of the producer's six permitted attempts remain unused.

The next useful source records remain the actual competition files with applicable terms and execution checksums, plus the barcode count/time inputs, retained and aggregate-row manifest, identifier map, CNV annotation uniqueness and missingness records. The stored output strengthens provenance; it does not satisfy those gates. All 26 study and 18 planning inputs remain NULL, with zero native matched panels. R5/R11/R17, theta/eta, separately frozen predictors/comparators/evaluation, error allocation, fixed stopping, methods 0.6.0 at DOI [10.5281/zenodo.23219776](https://doi.org/10.5281/zenodo.23219776), and the paused runner remain unchanged. No native biological fit, source numerical replay, new theorem, new Zenodo version, outreach or laboratory work is admitted.

## Separate recent inference-method assessment

The [BASIL assessment](WATCH.md) and [12-claim source record](BASIL_SOURCE_ASSESSMENT.json) concern a distinct February 2026 barcode-inference study. Better fitness inference does not supply an independent count of new mutation births, invisible losses or establishment. The source compares FitMut2, not the original FitMut artifact inspected in R40. No algorithm or numeric parameter is adopted into the frozen TMD test.

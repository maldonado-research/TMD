# Fitness-table construction and barcode identity contract

Original static source audit · 15 October 2026 · AI-assisted review

Four immutable objects from the repository linked by [Avecilla et al. (2022)](https://doi.org/10.1371/journal.pbio.3001633) now identify how the competition fitness table and barcode fitness output are constructed. Their Git-framed SHA-1, API byte sizes, inspected-tree membership and independent SHA-256 hashes were verified. This is an inspection of repository artifacts; identity with the exact publication execution remains unverified. No author code, model fit or simulation was run. Object identities and source anchors appear in [PIPELINE_AUDIT.json](PIPELINE_AUDIT.json).

The principal new result is an explicit input contract. The competition aggregation retains rows while assigning clone means; the barcode pipeline can append an aggregate low-count row before producing fitness output without barcode identifiers. The actual CSV rows and mapping records are required to determine clone weighting and barcode correspondence. Neither an erroneous published value nor an actual identifier mismatch has been established.

## Competition measurements and units

`fitness_assays/fitness_assays.R` reads `data_props_bc.csv` and `data_props_Lauer2018.csv`; it does not construct the imported `transformed`, `hours`, `run`, `strain` or `type` fields. It excludes Lauer controls DGY500 and DGY1315, then fits each available clone separately within run2, run3 and run4. Each fit regresses the supplied transformed measurement on supplied hours, and divides its slope by the natural log of two.

For barcoded clones, the script fits an evolved-versus-ancestral interaction with time, adjusting for run. Its comparison set uses three named ancestors, GAP1_bc_anc1, GAP1_bc_anc2 and GAP1_bc_anc3. It takes the coefficient named `typeevo_bc:hours`, divides by the natural log of two, and scales that interaction's confidence interval in the same way. Correct interpretation still needs the strain-to-type table, factor/reference coding, assay replicates and the transformation applied before import.

The [source article](https://doi.org/10.1371/journal.pbio.3001633), Methods section sec016, explicitly describes competitions lasting 92 hours or about 16 generations and states the same division by the natural log of two. The agreement authenticates the source's stated convention. It does not independently calibrate the imported time variable or establish a common unit with the barcode pipeline, whose command-line contract declares time points in generations. A conversion audit needs the original time values, their preprocessing, the log-ratio definition and the source's generation-time normalization. No numerical correction is inferred here.

One intermediate reporting detail is bounded: the unbarcoded helper scales the coefficient and calculated standard error but leaves the `confint` interval on its original slope scale. The calculated standard error is not returned, and all confidence intervals and p values are dropped before the final CSV export. This observation therefore establishes neither an error in the exported point estimates nor a demonstrated error bar in the publication.

## The exported table can retain clone/run multiplicity

The script first obtains one result per available clone/run pair. It groups those rows by clone and assigns each row that clone's mean estimate, then selects and renames columns. It does not collapse the group to one row or remove duplicates. Consequently, if a clone contributes more than one fitted run, its identical mean remains on multiple rows in the constructed table. The mean does not explicitly request missing-value removal.

The combined output contains only `clone` and `fitness_coef`: barcoded clone estimates followed by the retained Lauer rows. The already inspected `Figure7andSup.Rmd` excludes clone identifiers containing DGY1657, then passes positive fitness coefficients to its distribution plot without an explicit deduplication step. Conditional on this source script generating that input, different numbers of fitted runs can give different clone weights. Equal numbers of fitted runs would still leave repeated records; the relative contribution of the Lauer and barcoded groups also depends on their row counts. No actual duplication, clone count, weighting distortion or change to a published result has been quantified.

The export omits p values, confidence intervals and batch identifiers. The downstream positive-coefficient criterion therefore is not a significance threshold and does not identify the 2018 study's 18 significantly fitter clones. The actual table and the earlier S4 workbook are still needed for the 29-sequenced-versus-28-competed membership reconciliation.

## Barcode construction supplies a stronger, still conditional, identity chain

The authenticated analysis notebook explicitly states that bc04 is bc01 in the paper. This is now an author-code alias statement, a stronger source anchor than the later plotting label alone. It is not an independently checked sample or biological provenance crosswalk.

Notebook cell 1 reads `bc04_PyFit.csv`, takes its first four count columns, retains rows whose four-column total is at least 20, and, if lower-total rows exist, appends one row containing their column sums. It writes a numeric matrix with no barcode identifier or row index. It also takes the first four rows of `timepts.csv`. The notebook does not construct the later `bc04_bcfiltered_barcodes.csv` list used to label fitness results. An aggregate row, if generated, needs an explicit mapping or exclusion record; it cannot be assumed to represent one biological lineage.

The authenticated `fitmut_v2_a_20210916.py` reads the numeric count matrix, substitutes 0.1 for zero counts, obtains effective population-cell inputs from the time file, and converts the count matrix to estimated cell numbers. It fills fitness, establishment-time and likelihood arrays in input-row index order. It then sets fitness and establishment time to zero where the adaptive-minus-neutral log likelihood is nonpositive and writes those arrays to `_MutSeq_Result.csv`, without a barcode identifier. These are model-derived quantities and classification decisions.

This adds an upstream condition to the prior Figure 7 audit: if this script generated the consumed CSV, its positive `Mutation_Fitness` selector can inherit an upstream adaptive-versus-neutral likelihood decision. This is not a formal p-value significance test or an independent mutation-birth observation. Notebook cell 6 writes another thresholded derivative, but Figure 7 names the original `_MutSeq_Result.csv`; the original generator already includes its own thresholding.

The later Figure 7 code attaches `bc04_bcfiltered_barcodes.csv` by row position, then joins CNV labels by barcode and population. The missing records are the original barcode-to-count ordering, the threshold/aggregate-row mapping, the exact emitted fitness output, the barcode-list length and order, and CNV join uniqueness. Source instructions alone cannot establish actual alignment. Missing CNV joins still supply only a plotting label, not independent DNA-negative truth.

Saved notebook displays are not accepted as current input counts or reproduced outputs: cell 1's saved display contains two shape lines although its current loop names only bc04, and the command cell lacks an execution count while retaining output. These observations limit execution provenance; they do not establish the cause of the saved state or contradict a particular published count.

## Licensing and unresolved admission gates

The exact repository `LICENSE` object contains the MIT License and a 2022 copyright notice for Grace Avecilla. This resolves the previously uninspected software-license body. Its terms concern the software and associated documentation; they do not establish a license for separately hosted OSF datasets. The article's CC BY 4.0 terms likewise do not supply those missing data terms. This report publishes original interpretation and identity facts, not source code, notebook output, article passages or private acquisition paths.

The named competition CSVs and barcode data dependencies are absent from the previously inspected, nontruncated 62-entry repository tree. That is a statement about one tree snapshot, not absence from the study or other deposits. Separate OSF metadata can identify files without authenticating their row contents. No source-data table, clone intersection, missingness reason, row-order validation, observed birth denominator or independent establishment measurement has been admitted here.

All native W/A/M and biological-fit gates remain unchanged. This source audit supplies no new TMD theorem or empirical confirmation and does not justify changing frozen Methods 0.6.0.

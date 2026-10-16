# R43: barcode identity requires a row crosswalk

Ricardo Maldonado · 16 October 2026 · Original analysis with AI assistance

Two newly authenticated author scripts extend the evidence upstream of R42's saved Figure 7 summary: they specify barcode extraction and clustering, followed by combining six nominal timepoints. They recover no individual barcode-to-CNV assignments or retained-row manifest. The material result is an explicit observation contract linking read clusters, retained rows, model outputs and annotation labels. It identifies the exact records needed before any grouped count can be admitted as a count of distinct biological lineages.

The [ten-claim audit](AUDIT.json) contains 14 reproducible source anchors and the observation contract. [Provenance](SOURCE_PROVENANCE.json) records four bounded acquisitions, 55,027 saved body-and-receipt bytes, authenticated cached sources and two request slots frozen unused. Full source bodies, local source paths and author-local directory values remain outside Git. No author code, shell recipe, JavaScript, serialized R, model or biological simulation was executed.

## What the new sources add

The pinned [extraction script](https://api.github.com/repos/graceave/cnv_sims_inference/git/blobs/ff53af609c6e3201bd5ef894d1747822d29ba53d) selects a named Bartender version and gives extraction and clustering arguments. Its comment says a quality cutoff of 30, while the literal command supplies `-q ?`. This audit does not resolve that tool-specific interpretation or the runtime argument. A script recipe alone does not establish observed quality, barcode-clustering errors or genotype truth. The [combining script](https://api.github.com/repos/graceave/cnv_sims_inference/git/blobs/1b030f7ef15ed1ed1c191bec4031753c6d2beeb2) names bc02 and bc04 inputs at labels 5, 37, 62, 99, 124 and 149. A comment describes removing clusters smaller than 10 and each command supplies `-c 10`. Exact tool semantics, actual exclusions and clock calibration remain unverified.

The cached preprocessor then takes four count columns and uses a total-read threshold of 20. When lower-count rows exist, its displayed code appends their columnwise sum as one aggregate row. It writes filtered numerical counts; this displayed cell does not export the corresponding ordered barcode identifiers. These conditional rules do not establish that an aggregate row actually appears in the Figure 7 inputs.

The complete cached Git tree was inspected before acquisition. It contains no CSV paths. A small Figure 6 source was checked and found to concern aggregate inference, so its rendered notebook was not fetched. The acquired root history repeats Figure 7 construction. This is a scoped result for the inspected artifacts, not a claim that no copy exists elsewhere.

## The identity and classification contract

| Stage | Authenticated source behavior | Record still required |
| --- | --- | --- |
| Extraction and combining | Named barcode extraction/clustering recipe; six nominal time labels; a documented filtering intention | Actual input and output checksums, tool execution arguments, cluster mapping and retention records |
| Count preprocessing | First four count columns; sum at least 20 retained; lower-count rows may become one aggregate | Original-to-final row mapping, aggregate membership and exclusion reason per row |
| Model export | Numerical result dictionary lacks explicit population/barcode keys; `zip_longest` combines result arrays and summaries | Explicit keyed results or an independently authenticated one-to-one crosswalk, including any aggregate/padding/summary row roles |
| Figure 7 identity | Barcode identifiers are attached by column binding; population is assigned bc01 | Ordered correspondence to numerical rows, key completeness and uniqueness; authenticated bc04-to-bc01 alias |
| CNV classification | Join on barcode/population; imported annotation rows receive CNV; absent joined labels become noCNV | Unique annotation keys, assay provenance and explicit positive/negative/unknown status; join-cardinality and unmatched-key report |
| Summary and display | Adaptive summary uses positive inferred fitness; trajectory branch applies additional exclusions and renormalization | Run-linked row manifest for each view, denominator definition, time calibration and before/after counts |

Equal row counts cannot validate a positional pairing. Conversely, source use of a positional binding does not prove an actual misalignment. Duplicate keys, join multiplication, aggregates and padded rows are unresolved possibilities; none was demonstrated in the empirical inputs. A structural preflight can demand the missing declarations and reject ambiguous tables. It cannot create an identity crosswalk, infer row roles from zero fitness or row position, or validate biological identities.

Missing CNV annotation must remain **unknown** for any new evidentiary use. The Figure 7 label noCNV reflects absence of a matched annotation in the shown pipeline. It supplies no independent negative genotype assay. Likewise, the word adaptive denotes a source-model selection rule; direct mutation births, losses and establishment require separate observations.

## Saved notebook views cannot be merged into one census

The cached preprocessing notebook has a concrete execution-continuity gap. Its visible first-cell loop names only bc04, but that cell's saved output prints two raw array shapes: 75,676 by 4 and 113,109 by 4. These cannot be unambiguously assigned to that one visible loop invocation. A later saved output reports 1,772 rows selected by positive `Likelihood_Log`. R42 separately authenticates 1,569 grouped rows labeled adaptive by positive `Mutation_Fitness`, after identifier binding and CNV joining.

These are different predicates and saved views without authenticated shared input bytes and run identity. Their numerical difference is not an attrition estimate, missing-lineage count, demonstrated contradiction or proof of author error. The notebook evidence strengthens the requirement for an execution-linked row manifest; it does not authorize reconstructing one from counts.

R42's four-row grouped summary remains intact: CNV/adaptive 1,513; CNV/neutral 6,888; noCNV/adaptive 56; noCNV/neutral 72,294; arithmetic total 80,751. None becomes a certified distinct-lineage count here. The trajectory branch additionally removes specified zero/reappearance patterns and normalizes each retained time column by its own sum. Its displayed abundance is conditional on that retained set, so the summary total is not a trajectory census or the original-cell denominator.

## Consequence for TMD

The next useful evidence is a versioned, run-linked package containing actual count/time/identifier vectors, numerical results, annotation assays and a row crosswalk with retention, aggregate and padding roles. Until then, structural source provenance supports a validation contract only. All 26 study and 18 planning NULLs remain unchanged, with zero native matched panels and zero biological fits. R5/R11/R17, theta/eta, frozen predictors/comparators, error allocation, stopping, methods 0.6.0 at DOI 10.5281/zenodo.23219776 and the paused runner are preserved. This is an addendum outside that methods archive; it justifies no new Zenodo version.

## Original structural preflight

[preflight.py](preflight.py) implements the narrow [normalized interface contract](VALIDATION_CONTRACT.json). It checks explicit experiment/population/barcode keys, unique result row IDs, unique annotation keys and finite decimal-string estimates. It rejects positional-only output arrays and implicit identifier coercion. It retains zero and negative estimates as individual rows, requires explicit aggregate/padding roles, accounts for excluded rows and orphan annotations, and keeps absent annotation unknown. Supplied CNV/noCNV labels are source annotations only; neither becomes independent genotype truth.

This is an original data-structure utility, not an author-code replay, raw-file converter or modification of frozen TMD admission rules. The analyst must supply an independently justified keyed and row-role record. Merely supplying keys can give structurally valid but biologically wrong pairings: two different synthetic bindings can both pass, demonstrating why external identity provenance remains necessary. The interface rejects explicit ambiguous annotation labels; preserve the complete assay-state record, including unknown states, separately. Aggregate/padding rows use null barcode and fitness only in this normalized interface; original source rows must remain available in their original records.

Eight own-code adversarial tests pass; a separate internal checker verifies 67 additional assertions. These are entirely synthetic table examples, not recovered biological inputs or a biological simulation. Tests cover permutations, cross-population isolation, duplicate join expansion, numeric/identifier ambiguity, zero estimates, unknown/orphan annotations, explicit row roles and duplicate JSON members. Source, biological identity, clock, execution and native-admission flags remain false even when structural checks pass.

Run the original tests from this directory:

```sh
python -B -m unittest -v test_preflight.py
```

For a separately prepared and justified input satisfying the contract:

```sh
python -B preflight.py INPUT.json
```

The CLI hashes exact prepared JSON bytes, not unavailable original CSVs. It emits a structural report on success and exits 2 on rejection. No actual source rows have been processed through this utility. A structural PASS does not resolve any of the 26 study or 18 planning fields.

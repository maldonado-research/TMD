# TMD data and provenance audit — September 30, 2026

The immediate empirical priority is to replace ambiguous benchmark panels with source-authenticated observations and preserve what was actually sampled. The available software and mathematics substantially exceed the independently validated biological evidence. This audit found a useful real secondary-data foundation, resolved a denominator question, and identified a more consequential mismatch in the WS flagship panel.

**2 October 2026 primary-source follow-up:** [Research round R000002](research/panel_eligibility/README.md) authenticated the main Lind 2019 and Sun 2023 articles and two hotspot/repair studies. Lind's Results explicitly reports 109 collected mutants: 105 Wsp/Aws/Mws plus four rare-pathway mutants. This resolves the aggregate rare-four provenance gap recorded below; per-isolate/background allocation remains unauthenticated. It does not make the pathway-isolated collection a common-background race. Sun's 41 Aws occurrences reuse Lind's collection and provide no additional independent biological cohort. Supplementary workbooks remain unacquired; the follow-up admits no complete matched panel.

## Audit scope

Read-only inspection covered the April 24 archive extraction and its inventory in `export_work`, relevant local TMD count/rate files, the two May 1 archives in untitled folder 253, and TMD-specific handoffs in D-Blast 3's vector store. Original files were not edited or executed. The May archives were listed and their short notes read without extraction. The broader local listing was scoped after it proved large; this is not a claim that every file on the computer was examined.

The project's archive inventory contains 41 distinct archive hashes and 597 distinct file hashes. It records byte-identical aliases separately. Archive alias counts, repeat output folders, replay ledgers, and software validation cases are not independent biological replicates. Four project sources did not sync; uninspected originals may add evidence, but that evidence cannot be assumed.

## Data classifications and corrections

| Material | What is present | Evidential status / required action |
|---|---|---|
| `rpob_counts_tidy.csv` | 16 route classes in LB and SMMAsn; counts total 59+52 | Now reconciled against primary Table 1; restore three experimental blocks; use endpoint genotype sampling rather than first-arrival language. |
| `ws_triad_counts_tidy.csv` | Four labels with counts 26,40,105,26 | Two labels repeat (17,6,3), and the 105-cell panel has incompatible sampling design for cross-route winner comparison; primary portability claims need recalculation with eligible panels. |
| `ws_all4_counts_tidy.csv` | Pf-5 (16,14,10,3), plus 2019 (46,41,18,4) | Pf-5 totals supported in a primary article; the 2019 cross-route panel remains unsuitable as competing winners. The provenance of its four Other observations is unverified here. |
| `ws_triad_null_muonly.csv` | q=(0.3382084,0.5941499,0.0676417) repeated across contexts | Exactly matches normalized SBW25 rate estimates (3.7,6.5,0.74)×10^-9. A measured origin exists, but context transport and uncertainty require justification. |
| `ws_all4_null_muonly.csv` | q=(0.3303571,0.5803571,0.0660714,0.0232143) | Algebra matches total rate 11.2×10^-9 with residual Other=0.26×10^-9. Residual subtraction and rate uncertainties are not an independently measured Other-route rate. |
| WS arrival-time CSV | 197 rows, generated independently of winner | Explicitly synthetic according to the saved v0.6 demo note; retain as fixture only. |
| Mechanistic evidence ledger | Literature assertions, heuristic scores/seed priors | Mechanism candidates and planning assumptions; no route-specific measured q for rpoB is supplied. Overall resistance mutation rates do not determine the 16 route probabilities. |
| April/May campaign result CSVs | Deterministic dry-run examples, hash chains, controller validation | Software correctness and integrity examples; no new authenticated experiments. |

### rpoB: an apparent contradiction is an eligibility distinction

[Leehan and Nicholson 2021, Table 1](https://journals.asm.org/doi/10.1128/aem.01237-21) contains the archived 59/52 counts and three experimental blocks. Excluding no-identified-mutation and insertion classes produces 53/51, matching the abstract's point-mutation denominators. This is a sample-definition distinction; totals alone are not inconsistent. We transcribed its 96 body cells, with exact row/column mapping, in [rpoB secondary analysis](RPOB_ANALYSIS.md). These are attributed secondary observations, not TMD-generated raw measurements.

New exploratory analysis yields context-route MI 0.260835 bits for all111 and 0.251382 for104 point substitutions. A context-specific multinomial improves prediction over a pooled multinomial in each held-out experimental block, with total gains 13.125729 and 12.700734 bits respectively using pseudocount 0.5/route. These calculations add a reproducible batch-aware benchmark. They do not establish a new mechanism or give a prospective TMD test. The original study already documented environmental spectrum differences.

### WS: sample counts are not always route frequencies

The primary [Lind et al. 2019](https://elifesciences.org/articles/38822) Figure 8 caption restricts preselection mutation-spectrum comparisons to within-operon comparisons. Mutants were isolated in strains missing the other two operons. Therefore the counts46/41/18 are sequenced sample sizes in different genetic backgrounds, not a common multinomial winner distribution. Using them as a competing-route context in the shared manifold can confound experimental sampling with biology. Exclude that panel from confirmatory portability tests; retain within-route mutation-spectrum information separately.

The primary study's Figure 2 route-rate estimates restore the numerical origin of the triad q. The local folder58 file `Pseudomonas_WS_mutation_rates_Lind2019.csv` also supplies those measured rate summaries. Its own case-study note calls the combination with older selection outcomes a pilot because conditions differ. Preserve that qualification. Reporter/deletion rates in SBW25 do not automatically become mechanistic q for Pf-5 or altered environments.

The local folder58 `Pseudomonas_WS_route_counts_McDonald2009_derived.csv` explicitly attributes (17,6,3) to McDonald2009. Both `SBW25_WS_2009` and `Pf_WS_routes_v1` carry that vector in the current triad. No source establishes that the latter is a separate collection. Treat it as a source alias pending an independent collection record; do not count it twice. After removing that alias and incompatible2019 cross-route samples, the surviving selected-route summary contains two study panels and66 triad isolates, not four independent contexts and197 isolates. Two different studies/species still do not establish a controlled cross-environment manifold.

The [Pf-5 primary study](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1009722) supports the local16/14/10/3 aggregate and supplies mutation and fitness spreadsheets. Triad and all4 versions of this same experiment overlap; they cannot be counted as separate replication. This paper also reports a strain-specific WspF hotspot, so q transport deserves direct sensitivity analysis.

### Timing and mechanism boundaries

`TMD_locked_analysis_demo_results_v0_6.md` explicitly labels the arrival times synthetic and generated independently of winner. The saved p≈0.978 and Lomax fit therefore cannot authenticate biological winner-time independence or heavy tails. A time test requires prospectively observed detection windows, route labels, censoring, physical time units, and repeat cultures. Hash integrity cannot establish that such observations were made.

The empirical μ/A/F product is not separately identifiable from route frequencies. A fitted residual log odds can represent mutation supply, development/accessibility, fitness, detection, unmodeled sampling, or any combination. Separate measurements and interventions are necessary before calling it a fixation factor or quantum effect. No relevant direct quantum-rate observation was found in the scoped TMD/D-Blast material.

## Concrete open-data retrieval plan

1. **Already completed:** transcribe primary rpoB Table1 and authenticate against the archived count panel. Publish the attributed transcription and exploratory analysis with the observations' source, sample definitions, and lack of timing made explicit.
2. **WS genotype and fitness data:** retrieve publisher source files [eLife Figure6 mutation data](https://doi.org/10.7554/eLife.38822.015) and [Figure9 fitness data](https://doi.org/10.7554/eLife.38822.021). Store exact source URLs, download date, byte hashes, sheet/column mapping, assay background and replicate group. Analyze within-operon mutation spectra and independently measured fitness; keep genetic deletion design visible. eLife materials are openly licensed; verify the file-specific terms before redistributing entire source files.
3. **Independent Pf-5 case:** retrieve [PLOS S2 mutation table](https://doi.org/10.1371/journal.pgen.1009722.s002) and [S3 fitness table](https://doi.org/10.1371/journal.pgen.1009722.s003). The source lists [BioProject PRJNA737653](https://www.ncbi.nlm.nih.gov/sra/PRJNA737653), useful for later mutation reidentification. Begin with spreadsheets; do not download a large sequence archive without a defined reanalysis question and storage plan. Preserve primary PLOS attribution and licensing.
4. **Stress-test against mutation hotspots:** [the2023 hotspot study's OSF collection](https://doi.org/10.17605/OSF.IO/8BT2W) and [the2025 nlpD study's Zenodo data](https://doi.org/10.5281/zenodo.14335473) are candidate external panels with published mutation-bias mechanisms. Inspect data dictionaries, metadata, sampling independence and licenses before integrating; accessibility does not establish compatibility with TMD's endpoint or race models.

The eLife page and PMC intermittently returned browser challenges. Indexed primary-source text and the normal publisher pages were used; no access control was bypassed. Supplementary spreadsheets above are identified retrieval targets, not files falsely claimed as downloaded or analyzed in this audit.

## Strongest empirical next test

The fastest robust step is a prospective rpoB spectrum-and-competition experiment in controlled matched media with independent cultures and retained experimental blocks, rather than more fitting to the old outcomes. Lock route eligibility, mutation-rate estimation, endpoint sampling and potential time module separately. Obtain route-specific mutation supply under the same conditions, measure relative performance independently, then score blinded held-out experimental blocks. Compare a context-specific supply-only model, a measured supply-plus-performance model, and the restrictive TMD model. Evaluate log-score gain and calibration against those baselines, not uniform q alone. This could detect an explanatory gap or show that known mechanisms account for it; both are scientific progress.

For the strongest distinctive WS prediction, define at least four genuinely new environments in one genetic background. Estimate q independently in each environment; record endpoint route outcomes with identical sampling and assay units; derive the fixed-axis restriction without reusing outcomes to choose q. Count each culture once, retain all noncommon routes and censoring, and hold at least one whole environment out. Replicate an already fitted law before escalating it to a broad theory. Any paired fitness or transport experiment should be designed and carried out by an equipped lab with appropriate expertise.

## Local audit boundary

The read-only local audit used content inventories, original extracted count and rate files, source notes, and relevant TMD handoffs. Personal filesystem paths and unrelated material are omitted from this public package. Those references do not substitute for the cited primary publications. Original source files were preserved.

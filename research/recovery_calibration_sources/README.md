# Absolute recovery and the cell/CFU measurement contract

Mutation by Natural Dominance · R000012 · 7 October 2026, America/Los_Angeles

A colony is an observed growth outcome, not automatically one original cell or one mutation. This bounded primary-source screen identifies useful ways to measure the difference while retaining exact denominator and transport limitations. It admits no new matched common-background Wsp/Aws/Mws panel, fills none of the 26 actual study fields, and provides no TMD biological validation or cancer-prevention result.

## Sources and inspection level

One targeted PubMed search returned 45 matching records; the eight newest metadata/abstract candidates were screened. Two selected primary main-text methods/results were inspected, with source hashes pinned. A 5 October 2026 microscopy paper remains an abstract-only lead. The review and other candidate abstracts are explicitly distinguished from the two primary assessments. This is not a systematic or complete web search.

- **De La Motte et al. (2026), [DOI10.1128/spectrum.03910-25](https://doi.org/10.1128/spectrum.03910-25), PMC13228076.** Seventy-two clinical urine specimens were compared in treated/untreated aliquots using bead-normalized membrane-integrity cytometry and plate counts. The reported CFU marginal medians change from10 to5,500 CFU/mL while the cytometry comparison detects no difference (P=.470). That is an observation about assay processing; a nonsignificant test is not an equivalence test or proof of preserved viability. Membrane integrity and culturability are distinct operational measurements. The data do not establish a mutation mechanism or verified VBNC state.
- **[DOI10.1007/s00203-026-04995-3](https://doi.org/10.1007/s00203-026-04995-3), PMC13272224 (2026).** P. aeruginosa PA14 and two clinical isolate backgrounds provide redox/membrane cytometry, CFU survival and post-antibiotic regrowth contrasts. The gate normalizes to an approximate OD/CFU inoculum;1,000–50,000 technical events and at least three biological replicates are different denominators. Regrown descendants are not independently tracked mutation births. Similar MIC profiles support the paper's operational persistence interpretation, without proving that no new mutations occurred.
- **[NanoSpacer DOI10.1039/d6lc00655h](https://doi.org/10.1039/d6lc00655h), PMID42831674 (electronic date5 October2026).** Its abstract compares relative fluorescent-mixture ratios across microscopy, flow and CFUs. Relative agreement does not authenticate absolute recovery. Full text, raw measurements, independent-founder counts and supplement methods remain unacquired here.

The two inspected PMC main texts declare CC BY4.0. Original source bodies, clinical raw data and supplements are not redistributed. [SOURCE_SCREEN.json](SOURCE_SCREEN.json) records all eight screening decisions; [MEASUREMENT_LEDGER.json](MEASUREMENT_LEDGER.json) records20 source-specific rows and exact source anchors.

## A useful limit exposed by the clinical example

The DTT paper reports10 mL urine resuspended in1 mL,1 µL plated and a12 h readout. A single colony in1 µL nominally represents1,000 CFU/mL of suspension, or100 CFU per original mL **if** a tenfold concentration conversion applies. Its stated<10 CFU/mL negative threshold and untreated median10 CFU/mL therefore need an explicit dilution, volume, concentration and censoring map. This is an unresolved reporting/normalization gap, not evidence that the study is erroneous. Declared DOCX Data set S1 remains unacquired and unreanalyzed.

The ratio5,500/10=550 is a **ratio of reported marginal medians**. It is not a median paired fold change, a recovery probability or a mutation-rate ratio. Cross-method comparisons use N69 untreated andN71 treated after three versus one below-quantification exclusions; within-method comparisons retain72 pairs where applicable. Main-text Pearson correlations.45/.44 and reported log10 method biases1.22/.64 show why correlation and absolute agreement must be assessed separately. No new statistical inference is made from these summaries.

## What a TMD calibration would still need

1. Define the denominator: independently introduced individuals, physically counted cells, CFU packets, or tagged lineages. Record independent founders/occasions separately from technical flow events, sequencing reads and aliquots.
2. Audit instrument volume and classification with explicit reference values, dilution/concentration mapping, singlet/doublet or microscopy checks, and missing/low-count handling. A bead reference can support instrument enumeration without establishing biological recovery.
3. Measure terminal culturability and culture/selection-specific recovery with controls appropriate to the route, physiological state and assay. A known introduced-cell control needs justified independence and a measurement of the actual introduction, not an approximate OD conversion.
4. Determine whether groups of cells produce one CFU and whether invisible lineages or terminal zero marks exist. Track ancestry and state transitions where needed; mutation birth, survival, regrowth, allele origin and transfer remain distinct mechanisms.
5. Justify reference-to-native and state-to-state transport before using controls as absolute capture probabilities. None of these clinical/PA14 methods supplies numerical capture, genotype, growth or recovery parameters for SBW25 or a three-route TMD experiment.

The paired-allocation check in R10 conditions away common loss and can also pass for CFU packets. It does not replace these measurements. R13 separately studies what a known capture probability would identify under a finite conditional model; this source audit does not provide that probability.

## Offline reproduction

```bash
python -B verify_calibration_sources.py --source-dir /path/to/public-source-cache \
  --output /tmp/tmd-r12-source-checks.json --check-against SOURCE_CHECKS.json
python -B review/independent_r12_source_anchors.py --source-dir /path/to/public-source-cache \
  --output /tmp/tmd-r12-independent-source-checks.json
```

The cache must contain the four exact files named in [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json). Hashes alone are not restored sources. Missing caches mean UNRUN; the verifier performs no requests. The Python standard library is sufficient; optimized Python verification is refused. Source-anchor checks verify declared identity and text, not medical efficacy, biological equivalence or the hypothesis.

No author message, clinical recommendation, Zenodo request or publication release was made in this round.

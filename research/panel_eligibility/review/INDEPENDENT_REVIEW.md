# Independent primary-source eligibility review

Original internal review · 2 October 2026 UTC · TMD round R000002

**The revised candidate passes this bounded primary-source review. No complete biological panel is authenticated for the current matched common-background Wsp/Aws/Mws estimand in the inspected material.** This conclusion concerns the observation contract in the public TMD formulation: independent context-matched mutation supply, locked competing selected outcomes, fixed-route introduced/recovered controls with justified transport, and a frozen whole-context prediction. It does not show that eligible data are absent elsewhere, invalidate the source studies, or test TMD statistically.

This review was conducted separately from the two source-author audits, using their already acquired primary XML and final public ledgers. An additional read-only methodological pass checked the same key boundaries. No new source was acquired, no private research files were read, no GitHub action was taken, and no source experiment was reproduced. This is internal review with AI assistance under the configured GPT-6.1 Sol ultra agent settings, not external peer review. Scheduled API inference was not tested.

## Authentication and inspection

The offline verifier independently matches each top-level article's DOI, PMCID, PMCID version and SHA-256 against the acquired bytes. It also verifies main-article CC BY 4.0 notices. Review correspondence and subarticles are excluded from the XML ID index. The full hashes and byte lengths are in [the receipt](REVIEW_RECEIPT.json).

| Primary article | DOI | Main-article snapshot | Bytes |
| --- | --- | --- | ---: |
| Lind et al. (2019) | [10.7554/eLife.38822](https://doi.org/10.7554/eLife.38822) | PMC6324874.1 | 297,863 |
| Sun and Lind (2023) | [10.1099/mic.0.001323](https://doi.org/10.1099/mic.0.001323) | PMC10268835.1 | 180,237 |
| Horton et al. (2025) | [10.1093/molbev/msaf183](https://doi.org/10.1093/molbev/msaf183) | PMC12344412.1 | 117,119 |
| Torres and Alonso (2026) | [10.1093/nar/gkag673](https://doi.org/10.1093/nar/gkag673) | PMC13335488.1 | 206,305 |

Nineteen short attributed source excerpts match the stated main-article XML IDs. Normalization joins XML `itertext()` and collapses whitespace; it does not rewrite symbols, repair claims, or infer missing words. Matching hashes authenticate these snapshots, not the correctness or reproducibility of the experiments. The 24 public source-author files agree with their explicit whitelists; all 22 checksum entries validate. Source XML and failed-access responses remain outside the public bundle.

## Sampling and methodological conclusions

**Lind 2019.** Results `s2-4` independently supports 109 collected mutants = 46 Wsp + 41 Aws + 18 Mws + four rare-pathway mutants. The rare-four aggregate is authenticated, while its isolate-level route and background allocation is unresolved. The 109 aggregate overlaps its component counts and adds no separate replication. Results `s2-1`, Methods `s4-2` and Figure 8's caption identify different pathway-isolated backgrounds; 46/41/18 cannot become competing-route proportions in a common genetic background. The reporter-based colony assay has ascertainment even though it avoids selection for occupation of the static air–liquid interface.

Methods `s4-2` states 60 independent cultures per assay, repeated at least four times for the double-deletion strains and twice for wild type. Figure 2 independently reports n=200 for Wsp and Aws, n=400 for Mws, and n=100 for wild type. Those protocol and caption totals do not directly reconcile without well, exclusion and workbook mapping; neither is silently substituted for the other. The reported rates are Wsp 3.7, Aws 6.5, Mws 0.74 and combined wild type 11.2 ×10⁻⁹. These remain useful background-specific rate estimates. Their culture sample sizes are neither sequenced-mutant denominators nor fixed-route binary recovery trials. The article itself qualifies the between-strain significance calculation; this review does not recalculate significance or reject the rates on that basis.

Results `s2-7` supports the historical Wsp fraction 15/24. Equivalence to the older archived 17/6/3 vector has not been authenticated; these numbers are not reconciled by relabelling the eligible population. Methods `s4-4` supports independently inoculated quadruplicate fitness competitions, before/after ratios, marker/deletion/reporter-cost controls, and exclusion of two cases with >5% smooth colonies. Those are controls for competition measurements, not one binary recovery outcome per known introduced fixed-route unit on each baseline and selected branch. Competitive performance does not by itself identify stochastic establishment probability.

**Sun and Lind 2023.** Methods `s6` explicitly uses previously published experimental data. Table 3 has 12 mutation categories totaling 41 Aws occurrences; Appendix B and reference `R21` connect them to Lind 2019. The factual CSV transcription matches each primary table row, not just the total. These are reused observations, not a second independent cohort. Table 2's 16 genes and estimated 500 possible targets are a model inventory, not 500 observed cultures or isolates. The authors expressly qualify that estimate. Numerical random draws and a calibrated rate distribution cannot supply independent biological recovery controls or measured context-matched W/A/M supply.

**Horton 2025.** Figure 1 independently supplies G-tract group totals 29, 112, 434 and 47, summing to 622 selected sequenced populations. Methods `msaf183-s4.5` samples the first motile zone per plate and then sequences one colony's `ntrB`; three motif variants begin with four colonies per plate, which does not create four independent winners per sampled plate. Figures 1 and 2 do not establish separate biological cohorts merely by displaying related measurements.

Figure 5 separates 49/52/52/51 seeded populations from 38/43/44/19 evolved populations sent for sequencing within eight days. Their differences, 11/9/8/32, are derived nonemergence totals, not raw fixed-route introduction/recovery failures. Daily motility emergence, censoring at the experimental window, detection lag and possible mutations during initial colony growth prevent exact mutation-time or first-successful-arrival claims. Selected hotspot proportions and Fisher odds ratios measure experimental hotspot potency under motility selection. The Salmonella reanalysis instead normalizes inferred changes by motif-site opportunities. Neither quantity supplies an independent matched WS-route mutation probability per division. Motif and strand interventions are useful evidence for specifying supply calibration, not a newly acquired W/A/M supply vector.

**Torres and Alonso 2026.** Methods `SEC2-5` supports 30 independent cultures per strain and a mean Rif-resistant-colony/viable-cell frequency. It states a 50-mL harvest; each Figure 2–5 mutagenesis caption states a 10-mL treated aliquot, at least five independent experiments, and Rif-resistant CFUs normalized to LB CFUs from untreated cells. These quantities may belong to different protocol levels or aliquots; the inspected material does not authenticate the mapping. This review preserves that uncertainty and does not multiply 30 by five, equate the two volumes, or assume the denominators are identical.

The Methods claim of at least ten independent Rif-resistant colonies per strain/condition is relevant design information. It does not provide checked culture-to-isolate identifiers, a one-isolate-per-culture mapping, or lineage/jackpot handling. Neither resistant endpoint frequencies nor chronic-MMS population survival ratios are automatically per-division mutation rates or fixed-route binary recovery trials. Results `SEC3-24` explicitly says fitness costs were not assessed; enrichment of an allele does not independently establish its fitness advantage. Different repair backgrounds and the Rif-resistance outcome supply no authenticated matched Wsp/Aws/Mws route ledger.

## Corrections incorporated in the reviewed candidate

No count or DOI correction was needed. Four wording and scope improvements were requested and incorporated before receipt generation:

- The public formulation bounds its opening missing-panel statement to the current estimand and inspected material.
- The hotspot notes describe requirements for stronger sequence- and repair-dependent supply calibration, without implying a new measured supply baseline.
- The Lind/Sun ledger gives all eligibility flags and its overall verdict an explicit current-estimand and inspection scope.
- The Lind/Sun notes explicitly retain the unresolved relation between 60 cultures per assay, stated repetitions and Figure 2 totals.

The 20 ledger rows are measurement summaries with some overlapping populations, not 20 biological studies, independent cohorts, or formal inferential tests. Their false admission flags agree with the independently checked assay units and missing target measurements. Missing target counts remain null rather than zero. The twelve study-by-component missing-measurement rows cover common background, matched supply, selected outcomes, culture/lineage mapping, fixed-route controls and whole-context holdout.

## Offline reproduction and publication boundary

Run the review against public ledgers and the separate acquired raw cache:

```sh
python research/panel_eligibility/review/verify_review.py \
  --ledger-root research/panel_eligibility \
  --raw-source-root /workspace/tmd-research-progress/panel_eligibility \
  --receipt research/panel_eligibility/review/REVIEW_RECEIPT.json \
  --self-check
```

The verifier uses only the Python standard library and fails on a changed primary source, identity, critical count, excerpt/locator, ledger agreement, public checksum or reviewed snapshot. No network request, source-author flag alone, hypothesis test, or statistical significance recomputation supplies a passing result. Four negative checks confirmed rejection of a changed Lind spectrum count, a misattributed excerpt locator, changed public notes and modified primary XML bytes. `--self-check` uses disposable local copies and cleans them up. The bounded acquisition record remains 11 attempts and 851,374 downloaded bytes; failed access does not prove data absence.

The review's public whitelist is exactly `INDEPENDENT_REVIEW.md`, `REVIEW_RECEIPT.json`, and `verify_review.py`, also recorded in the receipt. Original review documentation is CC BY 4.0 and code is MIT under the repository terms. Neither raw publication nor license transfer to uninspected workbooks, OSF assets or supplemental archives is authorized by this review. Their rows, joins, exclusions and licenses remain uninspected; follow-up acquisition must preserve that distinction.

# Which published observations can test the restricted TMD model?

Original source audit · 2 October 2026 (UTC) · Research round R000002

Four authenticated primary articles clarify useful measurements and the missing data needed for the current matched Wsp/Aws/Mws test. No complete matched biological panel was admitted from the material inspected. This is a targeted eligibility audit, not a systematic literature review, a rejection of the source studies, or evidence that an eligible dataset does not exist elsewhere.

The target is the cross-context, independently supply-adjusted restriction described in [the formulation](../FORMULATION_AND_NEXT_EMPIRICAL_TEST.md). “Natural dominance” means a route's propensity to produce an operationally defined successful heritable outcome in a specified context. The restriction needs independently measured mutation supply and justified ascertainment; recovered genotype counts alone cannot distinguish mutation production, selection, stochastic establishment and recovery.

## Primary-source results

| Source | Useful authenticated observations | Boundary for the current test |
| --- | --- | --- |
| Lind, Libby, Herzog and Rainey (2019), [10.7554/eLife.38822](https://doi.org/10.7554/eLife.38822) | Fluctuation-assay design, within-pathway mutation spectra, and independently assayed fitness. The article reports 109 collected mutants: 46 Wsp, 41 Aws, 18 Mws and four rare-pathway mutants. | The 46/41/18 spectra use pathway-isolated backgrounds; these sequenced sample sizes do not estimate common-background competing-route shares. The rare-four total has article-level provenance, but isolate-level allocation has not been authenticated. Figure-data workbooks were not acquired. |
| Sun and Lind (2023), [10.1099/mic.0.001323](https://doi.org/10.1099/mic.0.001323) | Numerical analysis of mutation-rate heterogeneity and rare-route discovery; explicit reuse of previously published experiments. | The reused Lind observations are not another independent cohort. Simulated mutation distributions are not new measured supply or recovery controls. |
| Horton, Cherry, Waugh and Taylor (2025), [10.1093/molbev/msaf183](https://doi.org/10.1093/molbev/msaf183) | Synonymous motif interventions in an engineered motility assay, selected hotspot proportions, and site-normalized comparative mutation estimates. Exact sequence context matters for a supply baseline. | Motility restoration, engineered backgrounds and selected genotypes do not provide matched WS route probabilities per division. Seeded and evolved population totals differ; daily emergence observations are not exact mutation times. OSF files and supplementary PDF contents were not acquired. |
| Torres and Alonso (2026), [10.1093/nar/gkag673](https://doi.org/10.1093/nar/gkag673) | Repair-by-treatment contrasts, Rif-resistant endpoint frequencies and mutation-spectrum descriptions. Primary text explicitly states that fitness costs were not assessed. | An endpoint Rif-resistant CFU ratio is not automatically a per-division mutation rate. Culture-to-isolate linkage, assay denominator hierarchy and numerical supplementary files remain unresolved. These are different repair backgrounds and a different phenotype, with no authenticated fixed-route W/A/M recovery ledger. |

Detailed source anchors, inspection depth, sampling units, source hashes and missing-field ledgers accompany the [Lind/Sun audit](lind_sun/NOTES.md) and [hotspot/repair audit](hotspot/NOTES.md). Keep their acquired article text separate from uninspected supplements and data repositories. A source saying “independent colonies” is relevant design information, but cannot supply absent culture identifiers or prove that each isolate represents a distinct founding culture.

Lind's historical selected comparison quotes 15 Wsp mutants among 24. This audit does not substitute that comparison for the archived 17/6/3 vector or claim they share an identical eligible population. Resolving that mapping requires the original earlier collection and its sampling definitions; it is separate from the authenticated 2019 preselection inventory.

## What changes scientifically

The rare-four count is now supported at the article level, closing a narrow provenance gap in the September 30 data audit. It does not repair the cross-background sampling problem. The 2023 source is a simulation and reanalysis extension rather than an independent biological replication. The hotspot study motivates recording the exact ancestral motif, flanking bases, replication orientation and route aggregation before constructing mutation supply. The repair study motivates separating mutant frequency from mutation rate and measured fitness from an interpretation based on abundant survivors.

These source-specific findings strengthen competing explanations and the next acquisition request. They provide neither a new TMD-specific causal mechanism nor biological confirmation of its cross-context prediction. They also do not falsify that prediction: the inspected material does not satisfy its full observation contract.

## Measurements needed next

An eligible panel needs a documented common ancestor, context-matched independent supply measurements, locked selected-outcome sampling, culture and lineage identifiers, and fixed-route introduced/recovered trials on both baseline and selected branches. The control-to-biological recovery relation must be justified or bounded independently. Reserve a complete context, and freeze both shared theta and the held-out eta rule before inspecting its selected outcomes. Missing fields remain missing; sequencing depth, endpoint colony counts, censored motility populations and population CFUs cannot silently become independent recovery trials.

The next queued round is a prospective discriminating design. No experiment is claimed to have occurred, and the proposed design will need suitable biological measurements before inferential execution. Existing [prospective requirements](../../PROSPECTIVE_TEST_PLAN.md) remain applicable.

## Review and reproduction

The published candidate contains original audit notes, structured ledgers, manifests and review code. Full primary XML, failed-download responses and uninspected third-party datasets are excluded. Source hashes refer only to bytes actually obtained from identified public endpoints. The acquisition ledger records failures and the bounded search scope; an access failure is not proof that the underlying data are absent.

The [independent internal review](review/INDEPENDENT_REVIEW.md) and its [receipt](review/REVIEW_RECEIPT.json) authenticate the source identities, count extraction, attributed evidence anchors, ledgers and interpretation boundaries. Internal review is not external peer review.

With the acquired source cache arranged as `lind_sun/raw/` and `hotspot/raw/`, verify a checkout without modifying its public artifacts:

```sh
python research/panel_eligibility/review/verify_review.py \
  --ledger-root research/panel_eligibility \
  --raw-source-root /path/to/panel-source-cache
python research/panel_eligibility/lind_sun/reproduce_audit.py \
  --raw-dir /path/to/panel-source-cache/lind_sun/raw --check
```

The public manifests identify the acquisition URLs and exact inspected source hashes. This round verifies reproduction against the acquired local snapshots; it does not claim that a fresh future fetch will be byte-identical. An unavailable or changed snapshot must be resolved explicitly rather than silently replacing a pin.

New code is MIT and original documentation is CC BY 4.0 under the repository's licensing terms. The source experiments and articles remain attributed to their authors. Prepared with AI assistance under the configured GPT-6.1 Sol ultra agent settings; no scheduled API inference is claimed.

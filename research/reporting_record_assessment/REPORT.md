# R31: reporting form and author response for Lind et al. Figure 9

The named transparent reporting form identifies where the authors addressed reporting requirements; it does not supply the original Figure 9 row-21 calculation record. The accompanying author response supplies a separate, useful constraint: the authors explicitly distinguish their mutation-pathway model and explanatory fitness assays from a forecast that combines mutation rates and selection coefficients. These records do not resolve the stored mean/SD discrepancy and do not supply an establishment parameter or an admitted TMD comparison.

Lind, Libby, Herzog and Rainey, *Predicting mutational routes to new adaptive phenotypes* (2019), [article DOI 10.7554/eLife.38822](https://doi.org/10.7554/eLife.38822), remains the source. This assessment concerns its [Transparent reporting form, DOI .023](https://doi.org/10.7554/eLife.38822.023), [decision letter, DOI .026](https://doi.org/10.7554/eLife.38822.026), and [author response, DOI .027](https://doi.org/10.7554/eLife.38822.027). It is an internal source assessment, not external peer review of TMD or author validation.

## What the reporting form actually adds

The publisher-linked [DOCX](https://cdn.elifesciences.org/articles/38822/elife-38822-transrepform-v1.docx) was acquired as a Firecrawl representation. All five headings and their author answers in that representation were inspected. The original DOCX bytes and completeness against those bytes were not independently authenticated.

| Reporting heading | Author answer or destination |
| --- | --- |
| Sample-size estimation | Fitness assays; Fluctuation tests and isolation of WS mutants before selection |
| Replicates | Figure 2 legend; Figure 9 legend; those two methods sections |
| Statistical reporting | Figure 2 legend; Figure 9 legend; those two methods sections |
| Group allocation | “No group allocation in the manuscript” |
| Additional source data | Figure 6 source data; Figure 9 source data; supplemental file |

The form's generic instructions list SD and SEM among possible dispersion/precision measures. That list is publisher template language. The author answer points to manuscript locations; it does not identify E21 as SEM or redefine the published Figure 9 error bars. Likewise, the template's request for a power analysis is not evidence that one was performed, and the group-allocation answer alone does not establish a complete randomization or masking procedure. No new row-specific replicate IDs, exclusion mapping, marker/background inputs, weights or aggregation calculation are supplied in the inspected form.

## What the author response establishes

Following the named author-response DOI returned the publisher's [version-1 peer-review page](https://elifesciences.org/articles/38822v1/peer-reviews). It includes a decision letter, an initial author revision plan, quoted reviewer comments, and the authors' response after formal invitation to revise. The assessment keeps those voices and stages separate.

In their revision plan, the authors give three reasons why their measured fitness coefficients cannot simply be used as proposed in an origin-fixation forecast: WS fitness changes with its own frequency; it also depends on frequencies of other WS types and other phenotypes at the air–liquid interface; and the assay measures fitness against a **wspF WS competitor**, rather than the wild-type ancestor. These are source-stated limitations of this assay context, not a general rejection of origin-fixation theory.

In the final response, the authors explain that the previous title incorrectly suggested their model combined mutation and selection. They state that they do not attempt to predict the outcome of experimental evolution using mutation rates and selection coefficients. They describe the fitness assays as explaining differences between mutation spectra obtained with and without selection, including underrepresentation of some mutation types. They also report adding statistical tests, replicate counts and fitness-control information to the manuscript. Those reporting additions do not themselves reveal the row-21 inputs or arithmetic.

The decision letter contains a suggested origin-fixation calculation and selection coefficients estimated by eye from a manuscript figure. These are reviewer suggestions, not an accepted author calibration or new observations. Figure numbers in the prepublication exchange are not automatically a crosswalk to final Figure 9. No reviewer estimate is used to fill a TMD input.

The practical consequence is narrow: source fitness requires its assay reference and frequency context before transport to a different competition or establishment setting. The author response strengthens the existing gate against treating pathway simulation output, a relative-fitness summary, or a proposed reviewer calculation as an observed Wsp/Aws/Mws forecast. It does not change TMD's model or prove that a future context-specific calibration is impossible.

## What remains unresolved

R29 and R30 retain the original row-21 coefficients and stored summaries, their arithmetic diagnostics, and the scoped finding that the named supplement/repository contains pathway simulation code rather than the missing fitness aggregation. This round reuses those pinned assessments; it performs no new arithmetic extension and does not reinterpret source values.

The remaining useful evidence is an authoritative calculation record linking the row-21 mutant to original microcosm/replicate identities, the excluded cultures, marker/background control inputs and correction order, and the exact aggregation/dispersion definition used to obtain D21 and E21—or a versioned author/publisher correction identifying the intended values. This is an evidence specification, not an assertion that such a record exists or is absent everywhere. Two named acquisitions are a bounded inspection, not an exhaustive deposition search.

No author values were replaced, missing observations imputed, biological error declared, matched panel admitted, stock selected, experiment initiated, or new TMD fit made. All 26 study and 18 planning fields remain NULL. R5/R11/R17, core theta/eta forecasts and comparators, count-law admission, error allocation, fixed stopping, the paused runner and immutable methods 0.6.0 archive remain unchanged.

## Provenance and replay

There were **2 fresh logical scientific calls and 102,415 saved JSON bytes**, against allocations of 5 calls and 8 MiB. Both calls used the independent Firecrawl connector; no shell network, direct source download, credential, outreach or source-code execution was used. One reused R29 publisher API representation supplied the exact named links and is excluded from new-call/byte totals. Saved JSON bytes include duplicated provider text and structured representations; they are not wire bytes. Full captures remain outside Git.

The read-only verifier checks the public file/checksum closure, pinned dependencies, acquisition accounting, the 44 NULL fields and admission guard. With caches it additionally replays five form answers, locates template versus author language, separates author response stages from reviewer quotations, and verifies source identities and discovery links:

```sh
python research/reporting_record_assessment/verify_reporting_record.py
python research/reporting_record_assessment/verify_reporting_record.py --source-cache /path/to/r31/reporting-record/sources --r29-source-cache /path/to/r29/summary-reconciliation/sources
```

Public-only execution reports source replay as **UNRUN**. A full-cache PASS verifies the retained representations and extraction, not unpublished calculations, original DOCX bytes, experimental truth or model transport. Original assessment text and derived records are CC BY 4.0; new verifier code is MIT. Third-party rights remain unchanged; no source body, binary, private data, author email or credential is republished.

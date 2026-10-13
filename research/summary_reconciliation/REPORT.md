# R29: Lind Figure 9 summary reconciliation

**A fourth equal-weight coefficient cannot reconcile the MwsR I844L row's stored mean and sample standard deviation while retaining its three visible coefficients.** This is a conditional arithmetic result, not an author correction or a finding of biological error. The intended aggregation remains unresolved, and the author values remain intact.

The fresh publisher material confirms the reported quadruplicate competition design, two exclusions, and marker/background controls. A new inspection of the exact R28 workbook shows that its embedded chart also carries the stored summaries. Neither source supplies the calculation linking row 21's visible coefficients to those summaries. No matched panel or biological fit is admitted; all 26 actual study fields and 18 planning fields remain NULL.

## Source evidence and limits

[Lind, Libby, Herzog and Rainey (2019)](https://doi.org/10.7554/eLife.38822), Methods, reports independently inoculated quadruplicates, excluding two microcosms with more than 5% smooth colonies. It describes correcting for the GFP marker cost and control competitions for the double deletions and reporter construct. The Figure 9 caption describes error bars as one standard deviation. These are source-reported procedures; the present source material does not identify which exported cells correspond to the two exclusions or disclose a row 21 aggregation rule.

Four new logical scientific calls comprise two targeted correction-oriented searches, the [publisher article](https://elifesciences.org/articles/38822), and a provider representation of the [publisher API](https://api.elifesciences.org/articles/38822). The latter identifies version 1 and the same [Figure 9 source-data workbook](https://cdn.elifesciences.org/articles/38822/elife-38822-fig9-data1-v1.xlsx), DOI [10.7554/eLife.38822.021](https://doi.org/10.7554/eLife.38822.021). The two searches did not identify an authoritative correction; their limited ranked results do not establish that none exists. The article/API captures are Firecrawl representations, not authenticated original HTML or native API response bytes. Exact arguments, UTC capture intervals and fingerprints are in [SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json).

The workbook was acquired in R28 and reused locally, with SHA-256 `703194d0a3136c3c701687106caec43c6e2bda032734b2762acda1f4f27fd68b` and size 48,950 bytes. It was not downloaded again in R29. Its official Figure 9 identity and internal A1 text, “Figure 6 -source data,” are both retained. The worksheet contains 18 genotype rows, 73 visible coefficients and 49 formula cells, including shared formula nodes. No hidden row or column, or workbook comment part, was found. These are file-structure observations, not proof that all underlying experimental records were exported.

The [selected exact fields](SOURCE_FIELDS.json) retain the numeric XML strings and neighboring formula text. Row 21 is PFLU5329 / mwsR / MwsR I844L. D21 and E21 store constants without formulas; G21:I21 contain three coefficients and J21 has no stored value. E20 contains `STDEV(G20:I20)`; D22 and E22 contain `AVERAGE(G22:J22)` and `STDEV(G22:J22)`. The neighboring formulas support checking an arithmetic mean and sample SD as a stated convention. They do not authenticate that convention for the constant cells in row 21. O21 contains `TTEST($G$3:$M$3,G21:J21,2,2)`; a range ending at blank J21 is not evidence of a fourth measurement.

The named comparable artifact is the same workbook's `xl/charts/chart1.xml`. Its point index 18 is labelled MwsR I844L, references D3:D22 for values and E3:E22 for both error bars, and caches −0.0834227130448469 and 0.0151517203265832. These agree with the stored summary constants at chart-cache precision. This confirms propagation into the embedded chart, not how those constants were computed. The chart is neither an independent experiment nor an authenticated reconstruction of the published rendered figure.

## Conditional calculation

For 17 of the 18 genotype rows, the visible coefficients reproduce the stored mean and sample SD, as already reported in R28. Row 21 remains the exception:

| Quantity | Value |
| --- | ---: |
| Visible G21 | −0.070287998201181173 |
| Visible H21 | −0.11722093095305106 |
| Visible I21 | −0.13723933032329888 |
| Mean of the three visible values | −0.1082494198258437 |
| Sample SD of the three visible values | 0.03436548016776037 |
| Stored mean D21 | −0.083422713044846927 |
| Stored SD E21 | 0.015151720326583237 |

Retain the three visible values $x_1,x_2,x_3$, give every observation equal weight, and require the stored mean $m$. A fourth value would be uniquely forced to $x_4=4m-(x_1+x_2+x_3)$, approximately −0.008942592701856595. The resulting four-value sample SD is approximately **0.057033197611556494**, which cannot equal the stored 0.015151720326583237. The forced value is a diagnostic, not an imputation or proposed replacement source record.

For completeness, the same standard sum-of-squares identity sharply constrains a more general additive explanation. Write $A=\sum_{i=1}^{3}(x_i-m)^2$, $C=\sum_{i=1}^{3}(x_i-m)$, and append $k=n-3\geq1$ unrestricted real numbers while preserving mean $m$. Their centered sum must be $-C$, so the smallest possible total squared deviation is

$$
\mathrm{SSE}_{\min}(n)=A+\frac{C^2}{n-3}.
$$

Equality holds when every added value equals $m-C/k$. To match stored sample SD $s$, the required SSE is $(n-1)s^2$. At $n=4$, the lone added value has no remaining freedom; equality would be necessary and fails. For $k\geq2$, any nonnegative extra SSE can be realized by perturbing two added values symmetrically by $\pm\sqrt{((n-1)s^2-\mathrm{SSE}_{\min})/2}$, leaving the mean fixed. This proves conditional sharpness over unrestricted real values without inventing an experimental row.

| Total $n$ | Added values | Minimum SSE minus required SSE | Compatible under these assumptions? |
| --- | ---: | ---: | --- |
| 4 | 1 | 0.009069633002831572 | No |
| 20 | 17 | 0.00017546169286333926 | No |
| 21 | 18 | −0.00007224132921487966 | Yes, algebraically |

The gap decreases strictly as $n$ increases; therefore 21 is the smallest algebraically feasible total. **This is not evidence of 18 missing measurements, a 21-replicate experiment, or the authors' intended calculation.** The reported design remains quadruplicates. The threshold only restricts the hypothetical explanation that unchanged visible values plus additional equally weighted values produce both stored constants.

The calculation uses exact rational representations of the worksheet's decimal strings before presenting rounded results. Conservative rational interval bounds allow each visible coefficient and both stored summaries to vary independently by up to $5\times10^{-15}$; the signs at 4, 20 and 21 remain unchanged. This addresses decimal precision, not arbitrary transcription errors, different weighting, transformations, exclusions or control corrections. Those alternatives require source evidence and are not resolved or ruled out here. No novel theorem is claimed.

## Decision and verification

The useful next evidence is a versioned publisher/author correction, or an authoritative calculation record joining row 21's coefficients, exclusions and marker/background corrections to its mean and SD. The source-facing question has become more precise: a single additional equal-weight coefficient alone is insufficient. An unknown aggregation remains unknown. This evidence specification does not initiate outreach.

No author value is replaced, missing value filled, study allele selected, experimental protocol commissioned or new model fitted. R5/R11/R17, core theta/eta forecasts and comparators, count-law admission, error allocation, fixed stopping, paused runner and the methods 0.6.0 archive remain unchanged. This source arithmetic is not biological confirmation, prospective held-out success or external peer review.

Run `python -B research/summary_reconciliation/verify_reconciliation.py` for public-file closure, inherited dependency identities, conditional arithmetic and NULL guards. Add `--source-cache /path/to/R29/sources --r28-cache /path/to/R28/sources` to replay source captures and the exact reused workbook. Missing cache arguments explicitly report source replay UNRUN; the script makes no network requests, writes no files, and does not execute spreadsheet formulas. It checks stored formula text and cached values. [VERIFICATION_RECEIPT.json](VERIFICATION_RECEIPT.json) records the completed checks.

Original assessment and derived diagnostics: Ricardo Maldonado with AI assistance, CC BY 4.0. New verification code: MIT. Source facts are attributed to Lind and colleagues; their article declares CC BY 4.0. No separate embedded workbook license was authenticated. Source bodies, binaries, author workstation metadata and credentials remain outside this public package; third-party rights remain unchanged.

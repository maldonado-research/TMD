# R30: the named code record and the unresolved Figure 9 calculation

**The linked source-code supplement and a newly traced author repository describe pathway simulations; neither inspected record supplies the calculation for the MwsR I844L fitness summary.** The intended aggregation remains unresolved. A separate conditional check narrows one possible explanation: unequal nonnegative weights on the three visible coefficients cannot produce both the stored mean and a population standard deviation as small as the stored SD. Author values remain intact.

The source question concerns Lind, Libby, Herzog and Rainey (2019), [eLife 8:e38822](https://doi.org/10.7554/eLife.38822), Figure 9 source data, row 21. [R29](../summary_reconciliation/REPORT.md) established that D21 and E21 are constants, G21:I21 contain three coefficients, J21 is blank, and the embedded chart propagates the stored summaries. The article reports quadruplicate competitions, two exclusions, and GFP/background controls, without a row-specific calculation joining these operations to the constants. R29 excluded one additional equally weighted value as a sufficient reconciliation. These findings are inherited, not new acquisitions here.

The cached publisher API representation names source data for Figures 6 and 9 and points to supporting files. Following those links and a new repository-oriented search produced the following bounded record assessment:

| Named record | Inspected evidence | Consequence for row 21 |
| --- | --- | --- |
| [Supplementary file 1, “Equations and source code”](https://doi.org/10.7554/eLife.38822.022) | Firecrawl's PDF representation reports 9 of 9 pages. It contains Wsp/Aws/Mws differential equations, Julia solvers and sampling, and MATLAB pathway-probability contour plotting. | It supplies simulation calculations, without the fitness replicate, exclusion or marker-correction mapping needed for D21/E21. |
| [Libby and Lind (2019), Bio-protocol e3407](https://doi.org/10.21769/BioProtoc.3407) | The related protocol names `RunModelComparison` and `PlotModelComparison` and directly links [ericlibby/BioProtocol](https://github.com/ericlibby/BioProtocol). | This documents the published association of the named repository with the protocol. The protocol computes probabilities of pathway-induced phenotypic change; it does not supply the row 21 calculation. |
| [BioProtocol initial commit e78d2b2](https://github.com/ericlibby/BioProtocol/commit/e78d2b2df7c7af799687e4739f05027f204b3bf8) | The repository listing identifies this commit. Its API representation includes complete added-file patches for `RunModelComparison.m` (166 lines) and `PlotModelComparison.m` (49 lines). Reconstructed bytes reproduce both declared Git blob hashes. | The first file samples reaction rates/concentrations and solves an illustrative Aws model; its second comparison pathway calls the same illustrative pathway function. The second file plots log ratios of output matrices. Neither file contains Figure 9 fitness observations, exclusions, GFP/background correction inputs or D21/E21 aggregation. |

This distinguishes a named, inspected calculation record from a fitness calculation record. No source code was executed, no simulation output was generated, and no pathway probability was promoted to an observed mutation-supply, establishment or Wsp/Aws/Mws outcome vector or an independent comparator. The supplement, protocol and repository are related records, not independent biological experiments.

Five logical scientific calls were used: one nine-page supplement retrieval, one six-result search, and three linked protocol/repository/commit retrievals. All captures are Firecrawl representations. Reconstructing complete patches and matching their declared blob hashes checks internal content consistency; it does not independently authenticate native API bytes or establish a scientific audit by the authors. No fresh copy of the original workbook, main article, publisher API or R29 correction searches was requested. The [provenance](SOURCE_PROVENANCE.json) records exact arguments, UTC capture intervals, saved-byte accounting and fingerprints. Raw captures and reconstructed source bodies are excluded from this package.

The original article also names a transparent reporting form, [10.7554/eLife.38822.023](https://doi.org/10.7554/eLife.38822.023). Its body was not inspected in this bounded pass. The ranked search and inspected linked records cannot establish that an unpublished or differently deposited fitness calculation record does not exist.

For the conditional weights check, retain exactly the three visible coefficients:

| Cell | Stored value |
| --- | ---: |
| G21 | −0.070287998201181173 |
| H21 | −0.11722093095305106 |
| I21 | −0.13723933032329888 |
| D21, mean $m$ | −0.083422713044846927 |
| E21, SD $s$ | 0.015151720326583237 |

Let nonnegative weights sum to one and require their weighted arithmetic mean to equal $m$. Zero weights are allowed. Write $h=H21$ and $g=G21$; the order is $I21<h<m<g$. Every supported coefficient $x$ satisfies $(x-h)(x-g)\geq0$. Taking a weighted expectation therefore gives the standard variance bound

$$
\operatorname{Var}_w(X)\geq(m-h)(g-m).
$$

Equality is attained with weights $(m-h)/(g-h)$ on G21, $(g-m)/(g-h)$ on H21 and zero on I21. These are diagnostic weights, not inferred author weights. The sharp minimum population variance is **0.00044392995444833853**, with SD **0.02106964533276103**. The stored variance $s^2$ is **0.00022957462885499563**, with SD **0.015151720326583237**. The positive variance gap is **0.0002143553255933429**.

Thus changing weights alone, including discarding a visible value by assigning it zero weight, cannot reconcile both constants if E21 is the weighted population SD, or an SD whose variance is at least that population variance. This also covers usual bias corrections that increase the variance. It does **not** rule out SEM or other uncertainty measures, transformations, different underlying records, or GFP/background corrections. It does not identify an author mistake. Exact rational arithmetic and conservative bounds under independent perturbations of every input by at most $5\times10^{-15}$ preserve the positive gap; this handles decimal precision only. No novel theorem is claimed.

The needed next evidence is an authoritative calculation record joining row 21 to its microcosm/replicate identifiers, exclusion decisions, marker/background correction inputs and formulas, and final mean/SD definition. That record could resolve the source gate. The named pathway-simulation code does not do so. This evidence specification does not initiate outreach or select an experimental stock.

All 26 actual study fields and 18 planning fields remain NULL; no matched panel or biological fit is admitted. R5/R11/R17, core theta/eta forecasts and comparators, count-law admission, error allocation, fixed stopping, paused runner and methods 0.6.0 remain unchanged.

Run `python -B research/calculation_record_assessment/verify_calculation_record.py` for public-file closure, dependency identities, exact conditional arithmetic and NULL guards. Optional `--source-cache`, `--r29-cache` and `--r28-cache` arguments replay the corresponding captures and original workbook. Missing cache arguments explicitly report source replay UNRUN. The verifier makes no network requests, writes no files, and executes neither spreadsheet formulas nor third-party code. [VERIFICATION_RECEIPT.json](VERIFICATION_RECEIPT.json) records completed verification; [INDEPENDENT_REVIEW.json](INDEPENDENT_REVIEW.json) records internal AI review, not external peer review.

Original assessment and derived diagnostics: Ricardo Maldonado with AI assistance, CC BY 4.0. New verifier: MIT. Source facts are attributed to Lind and colleagues, Libby and Lind, and the named repository. No separate repository-code, supplement-code or workbook license was authenticated; third-party rights remain unchanged.

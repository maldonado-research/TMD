# TMD research extension 0.2.0: What changes when we account for measurement?

**Ricardo Maldonado · exploratory methods update · 30 September 2026**

Mutation by Natural Dominance is a hypothesis about evolutionary routes under specified conditions. This update develops ways to test a supply-adjusted restriction while keeping mutation supply, selection and observation separate.

## Download the complete reviewed package

- [TMD research extension 0.2.0 ZIP](TMD_research_extension_0_2_0_2026-09-30.zip)
- [Archive SHA256 checksum](TMD_research_extension_0_2_0_SHA256SUMS.txt)

The ZIP contains **42 files**, including the complete source code, mathematical notes, synthetic examples, source-data provenance, licensing and validation record. Its SHA256 is:

```text
2e7345e2b8369436a570fb3ceca2698db1049c318babf2b45bc8906db4939b25
```

Extract the ZIP, open `research_extension_0_2_0/README.md`, and follow its reproduction instructions. Python 3.10 or later and NumPy are required for inference; the planning calculation uses the standard library. The optional original-workbook inspection requires pandas and openpyxl. The package records the exact tested versions. **23 automated checks passed**: 16 inference checks and 7 design checks.

## In More Basic Terms

Imagine three roads leading to the same destination. One road may be used more often because more people can enter it, because it is easier to travel, or because our camera misses travelers on the other roads.

Counting arrivals alone cannot tell us which explanation is right. We need a separate, justified measurement of access to each road, and we need to understand what the camera can detect.

In this research, the roads are evolutionary routes. The update adds a way to combine selected-route counts with independent baseline counts, so uncertainty in both measurements enters the calculation. It also shows how different recovery rates can create an apparent change even when the underlying restriction remains the same.

## What the methods add

The joint model fits independently sampled baseline and selected counts together. Its approximate parametric bootstrap resamples both. A finite fit is reported only after geometry, optimization and information checks. Observed zeros can be handled when a finite fit is supported; unsupported boundaries or failed fits decline inference. One context cannot test a restriction shared across contexts.

The baseline counts must have a biologically justified sampling model. Pathway-isolated sequencing totals, fluctuation-assay colonies, pooled sequencing calls and preferentially recovered survivors cannot simply be relabeled as independent mutation-supply samples. Earlier project code already represented uncertainty through assumed Dirichlet concentration; this update adds an explicit independent calibration-count likelihood.

The measurement calculation shows that halving selected-sample Aws recovery while baseline recovery stays fixed shifts its supply-adjusted log contrast by minus log(2), and divides the corresponding contrast ratio by four. More endpoint observations alone cannot identify an unknown recovery bias.

In a selected balanced design with 100 baseline and 100 endpoint observations, the full approximate standard error is 0.30, compared with 0.212 when baseline uncertainty is ignored. The full uncertainty is about 41% larger. These are planning calculations under specified probabilities, not a prescription for a biological experiment.

## What the simulations establish

In the documented synthetic calibration, the shared-restriction null was rejected in 1 of 40 simulated datasets at the 5% threshold; a deliberately strong alternative was detected in 40 of 40. Each scenario used four contexts, 600 baseline and 600 selected observations per context, and 99 bootstrap draws per dataset. All 7,920 bootstrap draws resolved.

Those results concern the selected simulation settings. Forty datasets per scenario give limited precision and do not establish general calibration, broad power, or biological validity. The package reports uncertainty intervals and preserves unsuccessful-fit rules.

A separate synthetic example changes route recovery while keeping the underlying restriction fixed. The observed-data test rejects at approximately 0.005 with 199 bootstrap draws. This demonstrates a measurement failure: rejection does not by itself identify a biological cause.

## What the 2026 literature inspection adds

The package reviews six primary papers and includes an attributed factual transcription of 75 isolates from [Barber and Couce (2026), Nature Communications](https://doi.org/10.1038/s41467-026-74044-6). These isolates were selected for long survival. They are not unbiased first-winner observations or a direct test of TMD.

Source-cell references and workbook checksums accompany the derived counts. Differences between workbook counts, a block label and article summaries remain explicitly documented. No unresolved count is silently repaired, and no new significance claim is attached to this descriptive transcription. Original publisher workbooks are not redistributed.

## Versions, scope and reuse

This downloadable methods package is **research extension 0.2.0**. The repository's earlier expanded report and code remain **0.1.0**, with the [published report on Zenodo](https://zenodo.org/records/23068056). Historical [TMD software v2.6.5](https://zenodo.org/records/22398093) is a separate archive. Neither existing DOI identifies this 0.2.0 package.

No new laboratory experiment, confirmed TMD mechanism, new physical law or external mathematical priority is claimed. The practical advance is a more explicit and reproducible test, with measurement assumptions that can be challenged before new observations arrive.

New code is MIT licensed; new writing is CC BY 4.0. Original publications and datasets retain their own rights. Numerical source observations are attributed and are not presented as newly collected project data. This work used AI assistance under Ricardo's direction. Neither EDISON nor MOSBRI funded TMD.

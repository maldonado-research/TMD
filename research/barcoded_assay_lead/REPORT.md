# R31: a barcoded fluctuation-assay lead and its transfer limits

Husain, Flagg, Pincus and Murugan, *A DNA-barcoded Luria-Delbrück assay resolves mechanisms of adaptation*, [DOI 10.64898/2026.08.03.742544](https://doi.org/10.64898/2026.08.03.742544), [version 1 posted 7 August 2026](https://www.biorxiv.org/content/10.64898/2026.08.03.742544v1), introduces HiDenSeq. This is a recent measurement-method lead for TMD, not an admitted biological result for the hypothesis. The inspected version explicitly states that it has not been certified by peer review. Its organism and selective context differ from the SBW25 Wsp/Aws/Mws comparison.

The authors report using DNA barcodes and sequencing to sample the shape of a fluctuation distribution, rather than only a mean or variance. Their yeast canavanine-resistance experiments compare spontaneous mutation, mismatch-repair perturbations and UV exposure. The reported distribution shape distinguishes those mechanisms under their measurement and model assumptions. This suggests a concrete feasibility question: can independently calibrated, route-specific lineage observations resolve the mechanisms relevant to a native TMD test? It does not answer that question or establish mutation-by-dominance causation.

## What the inspected source actually measures

The initial demonstration uses *Saccharomyces cerevisiae* BY4741 with an msh2 deletion, a 12-nucleotide barcode at trp1, and canavanine selection. The authors report tracking 119,672 barcodes. Approximately ten founder cells share a barcode at the start of the described assay; these are pooled lineages, not 119,672 separately isolated cultures or individually authenticated mutation births. The authors treat barcode lineages as statistical samples and computationally merge them into virtual lineages to account for differing preselection sizes, justified under their fluctuation model's addition property. The independence and grouping contract must be assessed before transport; numerical throughput alone cannot supply it.

Their conversion from reads to absolute mutant numbers uses a total mutant count estimated by colony counting and refined during fitting. This matters for TMD's separation of independently calibrated supply from held-out outcomes. A fitted abundance scale cannot silently become an independently frozen native supply estimate. The source is not being reanalysed here, and no reported rate, confidence interval or lineage count is copied into a TMD study field.

The source reports that 84% of tracked barcodes were undetectable after selection and interprets that outcome within its assay. For a native-origin claim, non-detection requires an explicit detection/loss model. It cannot alone rule out a mutation birth followed by loss, poor recovery or insufficient sequencing. A barcode marks ancestry; it does not identify every mutation event, genotype, inheritance state or developmental episode.

## A useful warning from the authors

The discussion explicitly identifies variation in mutant fitness and competition between lineages as a confound that can distort barcode frequencies. The authors report stable frequencies in their canavanine setting, while stating that other selective environments require additional calibration. This is especially relevant to the frequency-dependent SBW25 WS setting described in the [Lind author-response assessment](../reporting_record_assessment/REPORT.md). The yeast stability observation cannot establish equal growth, independent establishment or stage-specific recovery for WS routes, markers, resident scaffolds or starting frequencies.

| Transfer question | Evidence needed before admission |
| --- | --- |
| What is an independent unit? | Barcode/founder identity, collisions, ancestry, pools and disjoint grouping records; justified dependence/count law. |
| Which denominator is independently measured? | Native exposure, absolute abundance and external calibration separated from fitted outcome information. |
| What happens before versus after establishment? | Independent route/context-matched establishment observations and named-stage recovery/classification controls. |
| Which molecular event occurred? | Parental and new-event genotype/ancestry truth, inherited negatives and invisible-loss/detection bounds. |
| Can the result be evaluated without reuse of outcomes? | Versioned actual data/code/metadata and an independently reviewed freeze with complete predictors/comparators and untouched evaluation. |

These questions connect the new method to the existing 44-field worksheet. They do not replace, fill or loosen any worksheet or admission gate. No laboratory plan is commissioned and no experimental stock is selected.

## Coverage, reproducibility and next artifact

Three logical scientific calls acquired one eight-result research-category web search, the named main PDF representation and its canonical version-one page. The PDF provider reports all 11 main-document pages and resolves the requested unversioned PDF URL to version one. This is consistency between source representations, not authentication of original PDF bytes. The posted date uses the main frontmatter, visible posted banner and agreeing DC.Date/citation_date; an auxiliary citation_publication_date field instead reads 2026/01/01 and is not used as the posting date. Original PDF bytes, supporting information, supplementary-material page contents, analysis code and sequencing data were not acquired. The main document says that analysis code and sequencing data “will be made available” in a public repository, without naming a deposition there. This is a statement about the inspected version, not a certification that no newer deposit exists elsewhere.

The next useful artifact is the version-matched supporting information if it can resolve barcode grouping, calibration or loss assumptions, or an independently identified versioned data/code deposit. Its mere acquisition would still not establish a native TMD panel. The source verifier checks capture identities, selected reported anchors, the page's date/status and unchanged study/planning registries. It does not reproduce the experiment, fit distributions, authenticate raw sequence truth or provide qualified external review.

All 26 actual study and 18 planning fields remain NULL. Historical stock joins, WSX molecular unknown, the Figure 9 aggregation, frozen model/forecasts/comparators, error allocation, fixed stopping and paused runner remain unchanged. This report claims no new theorem, new force, cancer-prevention result or confirmed TMD biological fit. Methods 0.6.0 remains the frozen archive; later GitHub addenda are separate.

Original assessment and derived facts: CC BY 4.0. New verification code: MIT. Ricardo Maldonado with AI assistance. Third-party rights remain unchanged; raw provider bodies stay outside Git.

# Sources and dependency provenance

The strict maximum result is an established order-statistic tolerance bound.
The directly inspected source is Xin Tong, Yang Feng and Jingyi Jessica Li
(2018), “Neyman-Pearson classification algorithms and NP receiver operating
characteristics,” *Science Advances* 4(2):eaao1659,
[doi:10.1126/sciadv.aao1659](https://doi.org/10.1126/sciadv.aao1659),
[PMCID PMC5804623](https://pmc.ncbi.nlm.nih.gov/articles/PMC5804623/).
Proposition 1 and Equation (1) state the strict order-statistic score rule and
binomial-tail bound, tight for continuous score laws. Taking order index `n`
gives the strict maximum formula. The article explicitly separates score
training from calibration and requires iid within-class observations.

The inspected cached primary JATS XML is 171,426 bytes, SHA-256
`f25ce747226b449ed9c6d6f720d90e6ceb1bf0bd288d47f7fb654fff52d2a7ff`.
The full text is a reading artifact and is not redistributed here. Wilks (1941),
“Determination of Sample Sizes for Setting Tolerance Limits,” *Annals of
Mathematical Statistics* 12(1):91–96,
[doi:10.1214/aoms/1177731788](https://doi.org/10.1214/aoms/1177731788),
provides classical bibliographic context; metadata was checked, not original
full text. The inclusive-maximum quantile proof is supplied explicitly in the
README. No novelty or priority claim is made for it or the probability algebra.

The source-audit comparison refers to the already inspected Orcel et al.
(2026), [doi:10.3389/fcimb.2026.1807759](https://doi.org/10.3389/fcimb.2026.1807759),
[PMCID PMC13231282](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/).
Relevant sections are Results s2_3 (twelve blanks, maximum 50, and sample
exclusion threshold), Methods s4_6 (separate UMI-family read filter and its
background rationale), and s4_7 (workflow water blanks). Cached primary JATS
XML is 126,193 bytes, SHA-256
`8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4`.
The earlier audit and its source hash remain authoritative provenance; this
extension adds a selection-aware interpretation rather than new experimental
values. No raw article body, supplementary workbook or individual record is
redistributed, and no study-author code is executed.

The original TMD computational dependencies are unchanged. Paths are relative
to the checkout supplied with `--repository`:

| Dependency | SHA-256 | Reuse |
| --- | --- | --- |
| `research/classification_bounds/classification_bounds.py` | `66996adfd4f90bccf7315a82022d6b96d390378f4be781f992e7229058bfb368` | Strict bounded input parsing and one-sided CP wrapper. |
| `research/classification_bounds/sources/boundary_confidence.py` | `23feb7547d481fc4d361b25da28fe9d46d79be2f9fe66376f9c9ca85c069c79d` | Original TMD certified scalar CP endpoint routines. |

Both sources are hash-checked before inference and imported with bytecode
writes suppressed. No dependency bytes are vendored here. Python 3.10 or later
and the standard library suffice. The dependency and surrounding project were
inspected at TMD commit `dc3f486` after the eligibility extension. The earlier
eligibility gate mixture and its confidence composition are reused only as
documented algebra; its fixed-gate count contract is not changed.

Original code is MIT, copyright (c) 2026 Ricardo Maldonado, under the accompanying
[LICENSE](LICENSE) and repository terms. Original prose is CC BY 4.0 under
repository terms. Newly supplied numerical examples are synthetic. All
third-party rights remain unchanged.

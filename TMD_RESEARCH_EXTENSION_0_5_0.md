# TMD methods extension 0.5.0: every success still leaves uncertainty

**Ricardo Maldonado · 30 September 2026 · Exploratory methods research**

This update adds finite-sample confidence bounds for the recovery-corrected W/A/M route comparison. An all-success control can now contribute finite information, where the preceding 0.4.0 interior likelihood declined the count table. Measured zeros are retained; missing observations never become invented zeros.

[Download the complete reviewed package](TMD_research_extension_0_5_0_2026-09-30.zip) · [Verify its checksum](TMD_research_extension_0_5_0_SHA256SUMS.txt) · [Zenodo report version and archives](https://zenodo.org/records/23075312)

The Zenodo identifier is reserved during preparation. A publication receipt, rather than this link alone, confirms the record's publication and DOI activation. Earlier 0.2.0, 0.3.0 and 0.4.0 packages retain their original versions; the expanded repository files remain the 0.1.0 report.

## In More Basic Terms

Recovering all 100 introduced control cells is useful evidence that recovery is high. It does not prove that recovery is perfect. Our new calculation keeps a range of possible rates and includes uncertainty in the biological route counts too.

We compare the corrected ranges across conditions. If they have no value in common, that challenges the proposed common contrast under the stated assumptions. Overlap means the data have not settled the question. It does not prove the hypothesis.

A control with no recovered units can leave the corrected range unbounded. We keep that uncertainty visible. A one-sided unbounded range can still rule out a narrow range elsewhere. A missing record is different from a measured zero, and neither receives an invented count.

Exact arithmetic checks protect the decision from rounding error. They cannot tell us whether a sorting event contained one cell, whether observations are dependent, or whether control recovery transfers to the biological samples. Those require experimental records and checks.

## The conditional mathematical result

For C prespecified contexts there are 12C scalar probabilities: three baseline route shares, three selected route shares, and six control efficiencies. Established Clopper-Pearson intervals allocate alpha/(24C) to each tail. Bonferroni then guarantees simultaneous coverage of at least 1-alpha under valid binomial marginals. Independence between components is unnecessary for that union bound; correct within-sample count laws are still essential.

Project that rectangle onto theta=(-1/2,1,-1/2)·[log(t)-log(b)-log(d1)+log(d0)]. Under a common finite theta, all context intervals must intersect on the coverage event. Rejecting only an empty intersection therefore has false rejection probability at most alpha, conditional on the specified model, fixed sampling plan and relative recovery transport.

The software certifies conservative CP endpoints using exact integer tails, then compares rational bounds for J=exp(2theta). Rounded logarithms do not determine rejection. This is a new implemented project capability using established statistical mathematics. It is not a boundary maximum-likelihood fit, p-value, equivalence test, unique mechanism identification or new physical law. Structural true zero probabilities make this finite log contrast undefined.

## What was checked

All 13 unit tests pass. Independent review checks endpoint certification, exact binomial tails and rational-grid coverage, 4,096 projection corners, six saved deterministic fixtures and touching-intersection decisions. Source hashes tie the reviews to the released code.

The repeated-sample diagnostic retains 160 synthetic datasets, each with four contexts: 40 exact reanalyses of previous high-recovery stress counts and 120 new draws. No dataset was replaced and no bootstrap was needed.

| Scenario | Rejections | Interpretation |
| --- | ---: | --- |
| Reused high-recovery shared contrast | 0/40 | Finite compatible intervals |
| New high-recovery shared contrast | 0/40 | Finite compatible intervals |
| New strong departure | 40/40 | Deliberately large departure distinguished |
| New low-recovery stress | 0/40 | Unbounded compatible intervals |

Every saved dataset was evaluated and every true per-context J value was covered in these sampled checks. These limited results do not prove universal coverage or power; the conditional coverage argument is mathematical. With only 40 datasets, descriptive Wilson 95% intervals for rejection frequency are 0–8.76% for 0/40 and 91.24–100% for 40/40. Low-recovery nonrejection does not confirm constancy.

An ideal all-success control table with C=4, alpha=.05 and L=100 has recovery lower bound about .92719 and a control-correction-only interval half-width .15120. Biological sampling uncertainty is additional. Certified software endpoints can be slightly wider. This is conditional precision for an observed table, not expected precision or a power-based sample-size recommendation.

## Research and measurement context

The targeted review adds binomial boundary-confidence work and two recent recovery/isolation studies. Their relevance is to measurement design; neither supplies a matched TMD test panel. [Thulin's author preprint](https://arxiv.org/abs/1303.1288) explains the conservativeness of exact binomial intervals. [Zöhrer et al.](https://enviromicro-journals.onlinelibrary.wiley.com/doi/10.1111/1462-2920.70209) separates whole-cell and free-DNA recovery. [Ha et al.](https://journals.asm.org/doi/10.1128/spectrum.03033-25) illustrates single-cell isolation and culture constraints. Molecular yields and well denominators cannot automatically become independent binary cell trials.

No suitable matched W/A/M control ledger was authenticated, no raw third-party datasets were analyzed in this update, and no new biological measurement is reported. The archive audit also recovered a historical incorrect interval inversion; references remain preserved while the new implementation uses independently checked inequalities.

The next empirical priority is a prespecified held-out route panel with justified trial units, known introduced totals, binary outcomes, culture/batch lineage and route-relative control transport checks. Optional stopping, clustered observations, misclassification, uncertain denominators or route-dependent transport failure need their own treatment.

## Reproduce and reuse

Extract the ZIP and begin with README.md and methods/BOUNDARY_CONFIDENCE_PROJECTION.md. The inference core uses the Python standard library; the calibration generator uses NumPy 2.3.5. Count tables, seeds, exact rational targets, tests, independent internal reviews and SHA256SUMS are included. Hashes prove byte integrity, not scientific truth.

New software is MIT; new report and documentation are CC BY 4.0. Original researchers retain attribution and rights. AI assistance was used in development and internal review. **Neither EDISON grant 675419 nor MOSBRI grant 101004806 funded TMD.**

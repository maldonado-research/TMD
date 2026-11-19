# Which mutation records were independently checked?

Two published plant datasets let us check aspects of mutation ascertainment against actual verification records. Both describe particular trees and selected candidates. Neither supplies the paired native roster for the TMD route-ranking test.

## Apricot — what does “14 confirmed” count?

Goel et al. reported 14 confirmations and six inconclusive results among 20 targeted somatic-mutation checks. Of the 20 checks, at least 14 and at most 20 could correspond to real mutations if the positive confirmations are correct. Those endpoints follow from assigning the six unresolved outcomes all negative or all positive. They are logical completion bounds for the assay entries. They carry no sampling extrapolation. [Primary paper, Results](https://doi.org/10.1186/s13059-024-03337-0) · [Supplementary figures S7–S8](https://doi.org/10.6084/m9.figshare.26367951.v1)

Tables S7 and S10 list 20 assay IDs. Two use the same printed location and alleles. Matching the printed keys to the S4 candidate list yields 19 distinct candidate records. Both entries at the repeated key occur among the 14 confirmed assay IDs, which map to 13 distinct listed candidates. S10 contains 17 numerical readouts. Three of those 17 belong to inconclusive assays. A nonblank measurement and a confirmed reference outcome have different denominators. We preserve the published count of 14 confirmations and the printed join as separate results. [Supplementary tables S3, S4, S7–S10](https://doi.org/10.6084/m9.figshare.26368540.v1)

| Organ category recorded in S4 | Listed candidates | Distinct candidates represented in S10 |
| --- | ---: | ---: |
| Shared between fruit and leaf | 60 | 16 |
| Leaf only | 10 | 3 |
| Fruit only | 145 | 0 |
| Total | 215 | 19 |

The 145 fruit-only records comprise about two-thirds of the candidate list. The printed verification entries cover no candidate in that category. Consequently the 14/20 figure cannot be applied as a validation rate to all 215, even if the assays resolve perfectly for the targeted records. This is a restriction on reusing their evidence for a different target. It leaves the authors’ reported observations intact. [Published workbook](https://doi.org/10.6084/m9.figshare.26368540.v1)

## Oak — do two detection methods miss the same variants?

Xian et al. compared methods on ten upper-branch variants with prior independent confirmation. Supplementary Table S10 encodes detection by a highlighted cell. Matching the same ten keys across its three blocks preserves the pairing. The authors’ combination approach recovered all ten. For the two Strelka2 analyses the paired comparison is below. The column names follow the study's reference configurations. [Primary paper, Results](https://doi.org/10.1093/g3journal/jkaf143) · [Journal supplement containing Table S10](https://pmc-oa-opendata.s3.amazonaws.com/PMC12341919.1/jkaf143_supplementary_data.zip)

| | Diploid detected | Diploid missed |
| --- | ---: | ---: |
| Haploid detected | 6 | 3 |
| Haploid missed | 1 | 0 |

The totals of 9/10 and 7/10 alone allow six **or** seven shared detections. The actual pairing establishes six. The lower-count analysis found one verified variant its counterpart missed, and their union covered all ten. These ten selected positives establish per-record agreement on recovered events. Specificity requires reference negatives, and general sensitivity requires evidence about how this panel represents other true events. Taking the union on this panel cannot establish its false-positive cost or future performance.

## Reproduce the source comparisons

The apricot replay reads the versioned workbook and uses the confirmation assignments transcribed from supplementary figures S7 and S8. It joins the tables at the published keys. The oak replay reads the original spreadsheet cell styles because the authors encoded the detection flags in the fill color. A text-only export would discard those flags. Both programs check the supplied input file against a published-source identity before counting. Their outputs contain aggregate counts. [Apricot replay](replay_apricot.py) · [Apricot result](apricot_receipt.json) · [Oak replay](replay_oak.py) · [Oak result and source hashes](oak_receipt.json)

The apricot replay ran against the original 1,807,558-byte workbook with Python 3.11.2 and openpyxl 3.1.5. Its SHA-256 is `9cc9ea73b92f335e24670f9b75d2b923feaa120a3467546211d8a879a75046b5`. A second count using a separately rendered copy of S4 and S10 reproduced the numbers of assays, distinct printed locations and organ-category matches. The oak replay ran on both the journal ZIP and the extracted workbook with identical output. These checks used public source files in a hosted retrieval session. Only the original analysis scripts and aggregate results are distributed here.

With the original files downloaded separately, run the following commands from the repository root. The apricot script uses openpyxl. The oak script uses the Python standard library. Substitute the actual paths to your downloaded files.

```sh
python3 -B research/finite_roster_audit/replay_apricot.py /path/to/13059_2024_3337_MOESM2_ESM.xlsx
python3 -B research/finite_roster_audit/replay_oak.py /path/to/jkaf143_supplementary_data.zip
```

## Implication for the TMD evidence

An independently verified call can establish that an event occurred on a listed unit. A statement about which route led also needs the full roster, linkage between frozen pipeline outputs and reference labels, and coverage of gate failures and unresolved calls. The program can propagate the ambiguity in missing labels once the frame is known. It cannot reconstruct units absent from the frame.

A study closer to the native project illustrates the same denominator issue directly. Farr et al. observed their study phenotype in 139 of 153 populations and characterized the positive cases. The 14 populations without the detected phenotype do not acquire independent W/A/M or Other labels from that count. They cannot be entered as 14 verified gate failures of known truth. [Farr et al., Results and Fig. 1A](https://doi.org/10.1371/journal.pgen.1011572) · [Earlier TMD source assessment](https://github.com/maldonado-research/TMD/blob/604390d9bba8471be26487e3737c072a0f5cb9bf/research/transport_sensitivity/SOURCE_ASSESSMENT.md)

A targeted November 2026 search included mutation validation in plants and partial verification under stratified sampling. An October 2026 statistical preprint explicitly targets a fixed cohort with sampled reference reviews. Its example assumes complete, correct review of sampled cases. We handle missing reviews through all possible label completions and condition interpretation on the chosen reference standard. Earlier work on stratified verification documents why estimates from verified cases alone can misrepresent performance. [Tang et al., preprint](https://arxiv.org/html/2610.12059v1) · [Cadieux et al., Medical Care](https://pubmed.ncbi.nlm.nih.gov/25821898/)

A targeted review of project handoffs located no linked dataset that qualifies for this audit in the native W/A/M setting. That search covers the checked sources only. No project input was populated with plant data.

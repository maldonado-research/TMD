# The two earlier branch markers with published split counts

Of 48 peach branch mutations attributed to Wang et al. (2019) in Ji et al.’s Table S2, two appear in the later paper’s Table S7. They are M71 and M101. Across the same 20 Flower #2 lysate pairs, the two sites have 40 complete comparisons with at least two pooled alternate reads. Two were one-sided, compared with **0.06073** expected if the pooled alternate reads in each comparison occupied random positions at its two observed depths. Both one-sided observations occurred at M101. [Wang et al.](https://doi.org/10.1371/journal.pbio.3000191) · [Ji et al.](https://doi.org/10.1371/journal.pgen.1011829) · [S2 origin and citation inventory](https://doi.org/10.1371/journal.pgen.1011829.s016) · [S7 read counts](https://doi.org/10.1371/journal.pgen.1011829.s021)

| Earlier marker | Eligible tissue pairs | One-sided observations | Expected at fixed read margins |
|---|---:|---:|---:|
| M71 | 20 | 0 | 0.00001006 |
| M101 | 20 | 2 | 0.06072127 |
| Both | 40 | 2 | 0.06073132 |

At M101, Pair1 recorded 5 alternate reads out of 117 in aliquot A and 0 out of 108 in B. Pair19 recorded 0 out of 248 in A and 43 out of 215 in B. With 43 pooled alternate reads, every assignment of those reads gives at least one aliquot five or more. This observation shows that the five-read discovery minimum alone cannot force all 43 into a single aliquot. The archive leaves the relative contributions of sample preparation, amplification, read dependence and other sources of imbalance open. [Counts and expectation](historical_result.json)

## Which candidates entered the published comparison?

Table S7 displays the eight major Group 1 and Group 2 markers discussed in the paper. The earlier study’s own S2 Data table lists M71’s A-to-C change at Pp01 position 2,130,859 in two named DHQ1 leaf samples and M101’s G-to-A change at Pp04 position 21,561,355 in 14. The two site identities predate the flower study. The later paper selected these markers for display after analyzing the material. Its S2 inventory flags these same two old sites as present in Flower #2 and labels the other 46 as absent in that flower. S7 provides no per-aliquot read counts for those 46. Treating an absent marker as a pair of zero counts would invent read measurements. The full 48-site split-read comparison remains unevaluated. The two selected markers also share the same flower and preparations as the newer 37-site analysis. The public deposit precedes the prospective prediction. [Wang et al., original S2 Data](https://doi.org/10.1371/journal.pbio.3000191.s019) · [Ji et al., Table S2](https://doi.org/10.1371/journal.pgen.1011829.s016) · [Table S7](https://doi.org/10.1371/journal.pgen.1011829.s021)

In S2, M119 and M120 have “This paper” as the citation despite their association with older branch material. The M120 row records T/deletion, while the S7 columns carry C/T labels. A source crosswalk would be needed to interpret those read counts against the structural variant. The scored two-marker subset uses only S2 rows explicitly attributed to Wang et al., with identical reference and alternate labels across both tables.

## Source verification and replay

The analysis used the native SHA-256-checked S2, S3 and S5 workbooks and the complete worksheet rendering served through the S7 supplement DOI on 19 November 2026. The rendering contains 187 named samples. All 40 S5 aliquot identifiers match unique S7 rows. As a cross-check on its labels and numeric columns, the reference and alternate counts at both overlapping newer Flower #2 markers M21 and M42 agree exactly with native S3 in all 80 sample–site comparisons. The original S7 workbook bytes were unavailable during this replay. The normalized historical count extract preserves the 40 scored rows and S2/S3/S5 checksums. A separate product-of-probabilities calculation independently verifies both marker expectations and the two one-sided observations. [Normalized input](historical_profiles.json) · [Original S7 supplement](https://doi.org/10.1371/journal.pgen.1011829.s021)

Run these commands from this directory. Scoring the saved extract and running the verifier require Python 3.10 or later. The source replay requires openpyxl and accepts the native S7 workbook or its table-formatted Markdown rendering. A successful comparison against S7 workbook bytes would provide a further source check.

```sh
python3 -B historical_panel.py | diff - historical_result.json
python3 -B verify_historical.py
python3 -B historical_panel.py --extract /path/to/S2.xlsx /path/to/S3.xlsx /path/to/S5.xlsx /path/to/S7.xlsx | diff - historical_profiles.json
```

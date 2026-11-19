# What two repeat libraries recover from the same orange DNA

Beaulieu et al. prepared two additional libraries for six of the 28 leaves originally sampled from one historic Washington navel orange tree. Each pair used the same DNA as its original sample. Table S3 reports average per-haplotype depth by library. Tables S4 and S5 give whole percentages of original calls encountered again, separately for clonal, mosaic and leaf-specific calls. The four original row labels are 6A, 6B, 7A and 7B. We matched each repeat pair with its labelled canopy location. The six columns therefore represent two repeat libraries per leaf for six leaves at four original row locations in one tree. [Primary study, published 18 September 2026](https://doi.org/10.1093/plcell/koag288) · [Tables S3–S5](https://pmc.ncbi.nlm.nih.gov/articles/instance/13690466/bin/koag288_supplementary_data.pdf)

## Repeat overlap among original leaf-specific calls

| Matched repeat pair | Repeat 1 % | Repeat 2 % | Either % | Both % | Neither % | Either minus better repeat, points | Both minus product of marginals, points |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6A1 | 47 | 47 | 49 | 45 | 51 | 2 | 22.91 |
| 6A2 | 60 | 51 | 60 | 51 | 40 | 0 | 20.40 |
| 6B1 | 40 | 67 | 67 | 40 | 33 | 0 | 13.20 |
| 6B2 | 53 | 67 | 67 | 53 | 33 | 0 | 17.49 |
| 7A1 | 54 | 62 | 67 | 49 | 33 | 5 | 15.52 |
| 7B1 | 62 | 54 | 69 | 47 | 31 | 7 | 13.52 |

The first three percentage columns come from the tables. The others are calculated from their displayed values. If the two repeat percentages are P and Q, and U is their union, both equals P + Q − U and neither equals 100 − U. Equal weighting of the six displayed unions gives 63.17%. Estimating a pooled fraction of distinct calls requires candidate counts and identities. The article's technical-repeat paragraph gives 47–67% for individual leaf-specific repeats. The matched Table S4 cell at row 6B, column 6B1 replicate 1, reads 40%, making the range in those matched cells 40–67%. Table S5 gives 100% for all six matched unions of original clonal calls and all six for mosaic calls. [Displayed cells and source labels](matched_percentages.csv) · [Article technical-repeat section](https://pmc.ncbi.nlm.nih.gov/articles/PMC13690466/)

The product of the two marginal recovery fractions gives a simple benchmark for overlap. Subtracting that benchmark from the recovered-in-both fraction gives 13.20–22.91 percentage points across all six leaf-specific comparisons. As a rounding sensitivity check, allow each of P, Q and U to vary independently by one full percentage point, clipped to 0–100. The gap in points is P + Q − U − PQ/100. It increases with either marginal and decreases with U, so substituting the two lower marginals and the upper union gives a conservative lower bound. Every comparison retains at least an 11.26-point gap under this assumption. These are finite proportions on the original-positive rows. Heterogeneous detectability across sites, shared preparation and selection of the original calls can all affect overlap. The study does not identify the cause or the state of sites absent from the original calls. The six matched columns come from a single tree. [Complete calculation](citrus_receipt.json)

The sweet-orange study predates the published peach prediction. Its unit is a repeated variant call on the same DNA. The deposited percentages also omit paired per-site reference and alternate read counts. The orange comparison therefore addresses repeat recovery among previously called sites. The prospective peach score requires independent site ascertainment, paired read counts and a later public data release.

The supplemental tables were read through a rendering of the publisher’s PDF. The matching calculation was checked against the displayed rows. The SHA-256 in the result identifies the derived CSV. Original PDF bytes were unavailable for a separate file-level check.

## Reproduce the calculations

The CSV contains 18 location- and category-matched records extracted from the primary supplementary tables. The calculation verifies its SHA-256 checksum before use. The table rendering retrieved from the PMC supplement was checked against each leaf-specific matched cell. The digest in the receipt identifies the derived CSV. The primary PDF remains available from the authors' article. The direct PDF byte stream was unavailable in the local retrieval environment.

```sh
python3 -B replay_citrus.py | diff - citrus_receipt.json
```

To regenerate the CSV from a pipe-delimited text rendering of Tables S3–S5 that preserves their source columns, captions and row labels, use the extractor.

```sh
python3 -B extract_citrus.py tables.s3-s5.md | diff - matched_percentages.csv
```

# M101 read counts in the original leaf and marker transmission into peach seedlings

Version 0.9.1 identified the sequencing run for DHQ1_B1-1-L1 but reported that a site-specific M101 count was unavailable in the inspected records. **Ji et al.’s native S7 Table does report the count.** In the row dated 2016 for this exact leaf, two reads carry the alternate A and 57 carry the reference G (2/59, 3.39%). Its neighbor DHQ1_B1-1-L2 has four alternate and 44 reference reads (4/48, 8.33%). At M71 those same leaves have alternate fractions of 15/32 and 4/14, respectively. These are published counts from bulk leaf libraries. The 2019 flower-associated leaf used for a separate targeted measurement was a different specimen. The actual presence of M101 in an individual cell from the focal leaf, and co-occurrence of both markers in a cell from L2, remain unresolved. [Ji et al., S7 Table](https://doi.org/10.1371/journal.pgen.1011829.s021) · [Wang et al., original mutation catalogue](https://doi.org/10.1371/journal.pbio.3000191.s019) · [0.9.1 report](https://doi.org/10.5281/zenodo.24378187)

The 75 parental sample identifiers in S7 exactly match the old DHQ1 leaf roster. Wang et al.’s native S1 and S2 Data workbooks now independently reproduce the archived 75-sample and 48-site TSV transcriptions byte for byte. Ji et al.’s S11 Table repeats the reference and alternate counts at M101 and M120 for 26 of the same leaves. All 52 overlapping marker–leaf count pairs agree. S11 omits the two focal leaves. This is a cross-check between tables containing the same underlying leaf data. [Wang sample roster](https://doi.org/10.1371/journal.pbio.3000191.s018) · [Ji progeny and parental subset](https://doi.org/10.1371/journal.pgen.1011829.s025)

## How the relation changes with read support

All 14 leaves listed by Wang at M101 have three to seven alternate reads in Ji S7. Of the 61 unlisted leaves, ten have two alternate reads, three have one and 48 have zero. All 13 positive-read unlisted leaves belong to branch B1. M71 has four and 15 alternate reads in the two listed leaves and zero in the other 73. In this dataset at these two sites, a three-alternate-read indicator reproduces both original membership lists. For a mutation reported in multiple samples, Wang et al.’s Methods required at least five supporting reads in one sample and at least three in other carrier samples. Both M71 and M101 have at least one sample meeting the five-read condition. The observed three-read separation agrees with that part of the original rule. The authors also considered call quality, physical branches, comparator samples and manual review. Two M101 reads in L1 are therefore consistent with its omission from the original list. The study supplies no independently established error rate for a one- or two-read M101 observation. [Original discovery methods](https://doi.org/10.1371/journal.pbio.3000191)

| Minimum alternate reads at each marker | M71 leaves | M101 leaves | Leaves at both | Observed relation |
|---|---:|---:|---:|---|
| 1 | 2 | 27 | 2 | M71 strictly contained in M101 |
| 2 | 2 | 24 | 2 | M71 strictly contained in M101 |
| 3 | 2 | 14 | 1 | Crossing |
| 4 | 2 | 9 | 1 | Crossing |
| 5 | 1 | 4 | 0 | Disjoint |
| 6 or 7 | 1 | 2 | 0 | Disjoint |
| 8 | 1 | 0 | 0 | M101 empty |

All four M101 additions shared by the two minimum tables of version 0.9.0 have a recorded count. The alternate/total fractions are 2/59 for B1-1-L1, 0/70 for B1-11-L2, 2/60 for B1-6-L2 and 2/51 for B1-8-L2. Ten other leaves unlisted at M101 also have one or two alternate reads. These four leaves in one marker’s panel cannot establish relative costs of adding or removing a membership. A zero at finite depth may miss a rare cellular population, and a small positive count may have a technical source. [Prior minimum-completion result](https://doi.org/10.5281/zenodo.24377898) · [Joined source rows](peach_inputs.json) · [Exact counts](peach_result.json)

## The measured offspring

Ji et al. collected seven seeds from B1 in 2019, grew the saplings in 2020, and screened the first true leaves. The authors report a mixture of selfed and outcrossed progeny with uncontrolled pollen donors. Their S11 Table reports zero M101 alternate reads among the seven leaves, at depths of 46 to 73 per leaf (414 reads in aggregate). The seven seedlings are the observational units for a progeny comparison. Pooling the reads does not create 414 separate offspring. [Study Methods, screening of progeny](https://doi.org/10.1371/journal.pgen.1011829) · [S11 Table](https://doi.org/10.1371/journal.pgen.1011829.s025)

| Marker | Author-called absent | Heterozygous | Homozygous alternate |
|---|---:|---:|---:|
| M101, Group 1 marker | 7 | 0 | 0 |
| M103, Group 2 marker | 1 | 4 | 2 |
| M120, Group 2 marker | 2 | 3 | 2 |

Four progeny carried both Group 2 markers, two carried only M103 and one carried only M120. Each Group 2 marker alone missed at least one of the seven offspring positive for the pair’s union. The direct observation is seven offspring with an alternate call at one or both Group 2 markers and none at M101. The parent’s bulk leaf fractions do not identify the pollen contribution, gamete frequencies or first mutational route. These are sampled and germinated progeny of one tree.

A distinct tree, GZ, supplies another check on what “transmission” means. Across nine progeny, Wang et al.’s S2 Table lists 61 inherited and 32 de novo mutation observations. The inherited proportion among the 93 offspring observations is 61/93 (65.6%). For the proportion of parental premeiotic mutation opportunities detected in progeny, the paper reports 61/124 (49.2%). The denominators answer different questions. One GZ sample was taken directly from a seed and the other eight from saplings. Repeated inheritance of a site across progeny can contribute multiple observations. Neither fraction measures when the mutations arose. [Wang et al., GZ S2 Table](https://doi.org/10.1371/journal.pbio.3000191.s010) · [Primary Results](https://doi.org/10.1371/journal.pbio.3000191)

## Reproduce

The reduced data include all 75 DHQ1 leaf rows at the three stored S7 markers, 26 parental rows from S11, all seven matched progeny rows, and the inherited and de novo counts for each of the nine GZ progeny. Pairs of read counts are ordered reference, alternate. Run the first command offline with Python 3.10 or later. The optional native extraction requires openpyxl and the exact files named below. The extractor checks all five byte digests. The downloaded Ji S11 workbook also matched the PLOS Figshare record’s MD5, `783dedef54d4fffe4c19bd5d2982f9f0`. [S11 Figshare file record](https://api.figshare.com/v2/articles/29935289)

```sh
python3 -B peach_reads.py | diff - peach_result.json
python3 -B peach_reads.py --extract pbio.3000191.s018.xlsx pbio.3000191.s019.xlsx pgen.1011829.s021.xlsx pgen.1011829.s025.xlsx pbio.3000191.s010.docx | diff - peach_inputs.json
```

The three Wang supplements are in the [PMC6456163.1 public archive](https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC6456163.1/). The two Ji workbooks are in the [PMC12370204.1 public archive](https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC12370204.1/). The SHA-256 values and normalized roster checks are recorded with the [archived input](peach_inputs.json).

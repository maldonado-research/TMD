# Kennedy pedigree substitutions

Kennedy and colleagues published serial daughter observations in baker’s yeast and a separate table of directional base changes. Of 237 author-assigned events in the pedigree matrix, **236 link exactly to a directional change** by lineage path and genomic position. One event has unknown type. The linked events include 110 C>A, 0 C>G, 74 C>T, 5 T>A, 33 T>C and 14 T>G substitutions, giving 107 transitions and 129 transversions. These are substitutions recorded in seven mutation-prone founding pedigrees under the study’s measurement conditions. [Kennedy et al. (2015)](https://doi.org/10.1371/journal.pgen.1005151)

## Timing and classification

The S1 Dataset gives positive daughter observations and highlights each new event. The S3 Dataset gives the path, division, position identifier and directional change in columns A, B, D and E. The join uses path and the full position identifier, standardizing the two separators used in S1. Timing follows the explicit S1 daughter index. Five-prime sequence context and gene annotation play no part in the join or classification. Anonymous event identifiers and positive daughter calls reproduce TMD 0.13.0’s 239-row observations table byte for byte. The derivative table contains one row per assigned event. [S1 Dataset](https://doi.org/10.1371/journal.pgen.1005151.s010) · [S3 Dataset](https://doi.org/10.1371/journal.pgen.1005151.s012)

For each matched change, the base preceding the arrow is the source base. When the source base is A or G, complement both sides of the arrow to obtain the pyrimidine-normalized substitution. For example, G→A maps to C>T and A→C maps to T>G. C>T and T>C are transitions. The other four classes are transversions. The TSV uses inclusive daughter-index bounds and the strings `unknown`, `Ts` and `Tv`. The bounds give author-assigned observation windows. Molecular errors can occur earlier. [Methods and Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC4395103/)

## Source differences

- The S1 and S3 tables each contain 237 assigned rows. Each has one unmatched row from F. The two positions are five bases apart on the same chromosome. The S1 event V133 has window [8, 9] and S3 places its unmatched change at division 9. That proximity leaves their identity uncertain. V133 is recorded with unknown direction and type. The unmatched S3 row has no independent pedigree event in the derivative.
- Among the 236 exact matches, 30 have different S1 and S3 division labels. On C, S1 daughter 12 maps to S3 division 13 for six events, daughter 13 maps to division 14 for five, and daughter 14 maps to division 12 for one. On G2, S3 labels all 18 events two divisions later than S1. The linkage table retains the timing convention used in the earlier pedigree analysis.
- G1 and G2 share the same founding family. Two events on the G1 sheet also occur on G2 as inherited observations. Each contributes one G1 row to the derivative. One position has a separate assignment on each of E and F. S3 gives both the same substitution class, and the table preserves both author-assigned events.
- The S2 Table gives a third source for checking spectra. Its lineage totals sum to 236, compared with 237 in S3. Every reported path differs on at least one directional count between these objects. The number of strict S1/S3 matches also happens to be 236. Differences in S2’s per-path counts preclude treating that table as the catalog of exact matches. The JSON records every discrepancy. S2 provides no event-specific assignments that would recover the missing type. [S2 Table](https://doi.org/10.1371/journal.pgen.1005151.s002)

## Reproduction

Download these three public source files into one directory. The script checks their SHA-256 hashes before reading the Office XML using the Python standard library.

| Original file | SHA-256 |
| --- | --- |
| [pgen.1005151.s010.xlsx](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s010.xlsx) | `e6005dbf96624706897b630bf36fcab64eeaf7c794266e16db08ae6461852ed3` |
| [pgen.1005151.s012.xlsx](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s012.xlsx) | `471723155bbc46d1087c9ed1e1fc19c6a4039141f8568cc9d3e5046b89988fb1` |
| [pgen.1005151.s002.docx](https://pmc-oa-opendata.s3.amazonaws.com/PMC4395103.1/pgen.1005151.s002.docx) | `94c19389a1c29b06e9ccf4d735103be27804008733203e571e00241daf43708e` |

```sh
python3 extract_kennedy_classes.py /path/to/sources rebuilt
diff kennedy_events.tsv rebuilt/kennedy_events.tsv
diff kennedy_linkage.json rebuilt/kennedy_linkage.json
```

Source credit goes to Scott R. Kennedy, Eric M. Schultz, Thomas M. Chappell, Brendan Kohrn, Gary M. Knowels and Alan J. Herr. The authors released the source study under the Creative Commons Attribution license. [Original publication and license](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1005151)

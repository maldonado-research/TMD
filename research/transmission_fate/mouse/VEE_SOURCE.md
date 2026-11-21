# Parental mosaicism and transmission in the four smaller mouse pedigrees

Lindsay et al. searched parental whole-genome data for very early embryonic (VEE) mutations and tested candidate sites in the corresponding offspring. A parent could qualify for this analysis even when every assayed offspring lacked a recorded transmission. This ascertainment complements the separate experiment that discovered mutations in offspring in the two larger pedigrees. [Article, Methods, “Estimation of VEE contribution to germline mutation rate”](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/) · [Original study](https://doi.org/10.1038/s41467-019-12023-w)

A parent’s initial genome sequence supplied candidate sites. The four smaller pedigrees had deeper parental genome sequencing and greater power to detect parental mosaicism. The study reports 44 candidates after initial filtering. Supplementary Table 3 lists the 40 candidates the authors attempted to validate. The Methods identify 29 sites with high sequencing depth in parents and offspring. The authors classified 26 as parental VEE on the basis of parental variant allele fractions (VAFs) inconsistent with both sequencing error and a constitutive variant. Of those, 21 had at least one recorded carrier offspring and five had zero. Individual candidate exclusion reasons cannot be assigned to all attrition steps from Table 3. The authors also already reported a Pearson correlation of 0.71 between parental VAF and the proportion of offspring carrying the variant in this dataset. [Study, Results and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/) · [Supplementary Table 3 and Figure 3](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM1_ESM.pdf)

| Pedigree | PASS sites | FAIL sites | Assayed offspring per PASS site, observed values | Recorded carrier calls summed over PASS sites |
| --- | ---: | ---: | --- | ---: |
| CBGP4 | 5 | 2 | 40, 50 | 21 |
| CBGP7 | 5 | 3 | 41, 46 | 49 |
| GPCB9 | 11 | 5 | 52, 54, 55 | 128 |
| GPCB11 | 5 | 4 | 46, 47 | 12 |

Table 3 supplies a site-specific number assayed. The 26 PASS sites have a total of 210 recorded transmissions in 1,266 site–offspring assays. An offspring may contribute assays at several sites. This table cannot establish the number of distinct carrier pups from the sum of transmissions, exact birth order, or any reproductive advantage. The table prints a denominator of 50 for one CBGP4 PASS site. We retain it exactly as published. Site-level offspring counts supersede a roster from any other experiment in this paper.

## Columns and reproduction

The table preserves all 40 native rows in order and assigns anonymous site labels V01 through V40. The pedigree and parent fields are the study's group labels. Validation is the authors' PASS/FAIL label. All three fractions are proportions on a scale from zero to one. The final parental VAF column comes from the targeted validation data. The transmitted fraction is printed to two decimal places, and the analysis can recover its exact value from the integer counts. The average offspring VAF includes information about the offspring outcome and is unsuitable as a predictor of transmission. Five FAIL rows have NA for every numeric field. The other nine FAIL rows have measured values and retain their FAIL label. Coordinate and allele identifiers are omitted from the exported file.

With Python 3 and Poppler’s pdftotext, run from the directory containing the script and table.

```sh
python3 -B extract_vee.py 41467_2019_12023_MOESM1_ESM.pdf | diff - vee.tsv
```

The extractor verifies SHA-256 `c9a6d54c936e93c3c6202b40a294cfef4fc1fc17eb17a10505f5d6435061f27c` before reading PDF pages 6 and 7. Source credit goes to Lindsay, Rahbari, Kaplanis, Keane and Hurles (2019). This derivative replaces site identifiers with sequential labels and preserves the reported qualification and measurement fields. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · [Publisher supplement](https://static-content.springer-cdn.net/esm/art%3A10.1038%2Fs41467-019-12023-w/MediaObjects/41467_2019_12023_MOESM1_ESM.pdf)

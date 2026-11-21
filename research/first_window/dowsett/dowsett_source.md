# Source of the Dowsett division-level substitution counts

Dowsett et al. (2021) released Data 1 with mutation assignments across laboratory yeast pedigrees. The 50 scored maternal divisions in seven pedigrees contain 13,801 assigned changes. The archive gives substitution labels for 13,800 of them. Its design, high mutation burden and division-level ascertainment set the population to which these counts apply. [Article](https://doi.org/10.1038/s42003-020-01544-6) · [Data 1 workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC7782790.1/42003_2020_1544_MOESM4_ESM.xlsx) · [TMD v0.13.0 division totals](https://doi.org/10.5281/zenodo.24427132)

## Division membership and coding

The extractor reads lineage, physical division, division ID and the native `Mutation` entry from `Full Mutation List` columns A, B, F and G. It checks each row against the independent lineage, division and segregant counts in `MutInSegGroups`. Pedigrees Y1–Y7 encode ascending native numeric lineage ID as in v0.13.0. The first three columns reproduce that release's division table exactly, including gaps in the physical division numbering.

The left and right bases of each printed pair give its direction. For a left A or G, complement both letters to express the substitution from C or T. For example, G:A and C:T both count as C>T. The first six count columns partition the assigned changes with a valid pair. Transitions repeat the counts for C>T and T>C. Transversions sum the other four classes. The final column records a missing or unrecognized label. Each division satisfies `assigned_changes = transitions + transversions + unclassified`.

| C>A | C>G | C>T | T>A | T>C | T>G | Transitions | Transversions | Unclassified |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2,512 | 37 | 5,734 | 825 | 3,613 | 1,079 | 9,347 | 4,453 | 1 |

The workbook leaves the mutation label and additional notes blank for one assigned change in Y6, division 9. Its type is unresolved. A separate audit compared the left base of each valid native pair with the exact S288C R64-2-1 reference named in the workbook's SRA sheet. It agreed at 13,799 of 13,800 entries. One entry in Y1, division 3 is printed as C:T at a position with reference A. The counts above preserve the printed label. A sensitivity analysis can move this single C>T entry from classified to unknown, reducing the Y1 division 3 transition count from 124 to 123 and its C>T count from 68 to 67. The reference difference alone cannot identify an ancestral allele. [SGD reference archive](https://downloads.yeastgenome.org/sequence/S288C_reference/genome_releases/S288C_reference_genome_R64-2-1_20150113.tgz)

## Reproduction

Python 3.9 or newer and the standard library suffice. Download the linked Data 1 workbook, then run the following command from this directory.

```sh
python3 extract_dowsett.py 42003_2020_1544_MOESM4_ESM.xlsx > rebuilt.tsv
cmp rebuilt.tsv dowsett_classes.tsv
```

To reproduce the allele-direction audit, also download the linked SGD reference archive and pass its path with `--reference-tgz`. This prints pedigree, division and native allele labels for reference-discordant classified calls on standard error. The substitution table goes to standard output.

| File | SHA-256 |
| --- | --- |
| Original Data 1, 4,874,094 bytes | `cb2ebd86284731f8386f58ee67effbd1e6eeca0e3f73fbbe08897caf0c738fc7` |
| Reference FASTA inside the SGD archive | `dbf065ffc3f5bbaa7554ef53c6861399eecc597fe058df5f81ba557944e3f86b` |
| Projection onto prior division counts | `fa570d44673511a2b6f7f4e07cfe2e3726b5fda437bac6b87d4325537ce70a33` |
| Six-class division table | `4a2f65f5ef4770bf9be70b2ed3858c48f5c4f0f02dd68a8ee11ce9a5cd0d91cb` |

# Grapevine accessions that distinguish previously identical marker pairs

Tello et al. examined 185 vegetatively propagated ‘Tempranillo’ vines. They selected 56 markers from 158 shared variants to represent branches already inferred from 50 vines. An additional 135 vines were assayed on the selected panel. This collection allows a direct question about sampling. When two markers always occur together in the first 50 vines, can another accession distinguish them? The genotype profiles, vine identifiers, selection roles and two-platform measurements can be cross-checked in five sheets of the authors’ native workbook. [Primary paper, methods and Figures 2–3](https://doi.org/10.1093/hr/uhaf237) · [Native supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC12679915.1/web_material_uhaf237.zip)

**Twelve pairs with identical sets of heterozygous vines in the 50 selection samples became strictly nested when all 185 vines were represented.** Eight of the pair distinctions came from a single vine with the newly observed genotype GT-20. Three came from GT-21 (three vines) and one came from GT-22 (three vines). The additional 135 vines represented 14 genotype classes, of which 11 were already present in the first 50. Several individuals with the same genotype contribute the same carrier pattern. All 12 pairs involved markers for which the authors inferred a homozygous ancestral state from the cultivar’s parents.

For example, B_chr02_19352340 and B_chr08_07685896 were both heterozygous in the same four of the first 50 vines. The other 46 were homozygous at both sites. In the additional 135 vines, eight were heterozygous at both, 124 were homozygous at both, and three were heterozygous only at the second site. All three were GT-21. Under a single origin and permanent inheritance, the second group could therefore represent an earlier event on the shared lineage. The archive contains no observation of the first transmission or its date. [Counts and the twelve named pairs](grape_result.json)

## Cross-checking two representations of the selection vines

Sheet S4 gives separate Illumina and Fluidigm calls for each of the 50 selection vines. Every one of the 2,800 paired genotype strings agrees across platforms, comprising 2,577 homozygotes and 223 heterozygotes. The authors reported complete concordance for this selected panel. Sheets S3 and S5 separately list each named clone genotype. Assigning the S3 and S5 profiles back to the 50 sample IDs reproduces 2,791 of 2,800 S4 allele calls. The nine differences below occur in both comparisons. Heterozygosity alone differs for five calls. S4 identifies this disagreement even though its two assay columns agree throughout. The source gives no adjudication between its two representations. [Named records and reduced profiles](grape_inputs.json)

| Locus | Selection vines affected | S4, both platforms | S3 and S5 clone profile |
|---|---:|---|---|
| B_chr08_00848520 | 4, all assigned GT-16 | C:C | C:T |
| B_chr08_21422396 | 1, assigned GT-11 | G:T | T:T |
| B_chr10_05943585 | 4, assigned GT-09 or GT-10 | A:G | G:T |

For each marker pair we counted whether the combinations 00, 01, 10 and 11 appear, where 0 means homozygous and 1 means heterozygous. Four binary combinations are incompatible with two single irreversible changes on an unrooted tree of faithfully observed lineages. This four-pattern criterion is invariant to reversing the coding at either locus. The expanded panel includes one marker with an unresolved ancestral state. The analysis also enumerates rooted carrier-set relations separately for the 55 markers with a supplied ancestral state. The supplemental class profiles give the additional vines’ calls through their S1 genotype assignments. The authors supply individual paired measurements in S4 for the selection vines.

| Selection-vine data and markers | Pairs | Two / three patterns in first 50 | Two / three patterns with 135 additional vines | Pairs gaining a third pattern |
|---|---:|---:|---:|---:|
| S5 genotype classes, all 56 | 1,540 | 82 / 1,458 | 70 / 1,470 | 12 |
| S4 specimen calls, all 56 | 1,540 | 137 / 1,403 | 69 / 1,471 | 68 |
| Either source, 54 markers with matching heterozygosity | 1,431 | 81 / 1,350 | 69 / 1,362 | 12 |
| Either source, 53 markers with matching allele calls | 1,378 | 81 / 1,297 | 69 / 1,309 | 12 |

No marker pair showed four binary combinations in any row. In the 50 specimen-level S4 profiles, every vine is homozygous at B_chr08_00848520. Apparent resolution gains involving that marker depend heavily on the table used. On the 53 fully concordant markers, the 12 pairs that became distinguishable are identical to those found in the 56-marker class comparison. At B_chr10_05943585 the union of the two representations includes two distinct heterozygous allele calls. Counting full genotype strings in the mixed source yields 54 marker pairs with four distinct combinations and one with five. All 55 include B_chr10_05943585, whose union has three genotypes. The binary incompatibility criterion requires two states at each locus.

The paper removed singletons and selected the 56 markers to span the branching pattern already seen in the initial sample. Consequently even a completely compatible panel supplies limited evidence for a general mutation model. High agreement across assays at selected sites leaves the accuracy of other sites, including absences in a different fruit tree, unresolved. These grapevine genotypes also come from historical clonal propagation and regional collecting. They identify no prespecified first-success endpoint or waiting time. The study predates the separately frozen 2026 prospective split-read test and lacks the specified paired-lysate read design.

## Reproduce

The offline calculation uses the Python 3 standard library. Reopening the public supplement additionally requires openpyxl. The 555,426-byte source ZIP has SHA-256 `271fe37052332e3889e8142358dbbebbb68e1d1775ea9bf5eda1f83c35ad1332`. Extract `Sup_files_Tello_v2.xlsx`, which is 151,092 bytes and has SHA-256 `135002ebe85ea2307238cf7d866e7b799fdf27968e1f628a67ed76c91fae1b60`. The extractor verifies the workbook identity, the selected marker sets, counts by cohort and genotype, and all paired assay entries. Allele order is immaterial when comparing genotypes. The comparison of full S4 and S5 strings treats G:A and A:G as the same heterozygous call.

```sh
python3 -B grape_panels.py | diff - grape_result.json
python3 -B grape_panels.py --extract Sup_files_Tello_v2.xlsx | diff - grape_inputs.json
```

The independent verifier reads the native workbook XML directly and provides named examples for the 12 additional joint states. [Workbook checks and reproduction command](WORKBOOK_CHECK.md)

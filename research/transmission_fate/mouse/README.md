# Predicting carriage of a measured mutation in another mouse offspring panel

Lindsay et al. (2019) recorded somatic variation in parents and transmission in mouse pedigrees. For variants discovered through offspring, we compared the parental tissue allele fraction with the carrier fraction among ten offspring selected for whole-genome sequencing (WGS). For variants discovered through parents, we compared the parental allele fraction with a transmission rate learned from other families. Both analyses use the authors’ reported assays. Fitness, lineage competition and subsequent reproduction were unmeasured. The two comparisons use different baselines and different ascertainment criteria. [Article](https://doi.org/10.1038/s41467-019-12023-w) · [Analysis specification](../DESIGN.md)

## Offspring-discovered mutations in two pedigrees

All 17 early-embryonic single-nucleotide variants in these families had detectable somatic mosaicism in a parent. The unit is a marker and an assayed offspring outside the family’s ten WGS discovery pups. The source Table 2 caption defines its per-site denominator as the total number of offspring assayed. It gives 57 in CBGP8 and 77 in GPCB2 at every included site. Figure 1 shows both full assay cohorts, including the ten WGS pups per family named in Supplementary Table 1. The assayed denominators equal those entire cohorts. Per-marker sensitivity and negative-call quality for individual pups are not given by a list of positive carriers. The methods describe targeted validation in WGS pups and other offspring. We subtracted the ten WGS pups and their individually identifiable positive calls to obtain 47 and 67 additional assayed offspring per marker. The validated catalogue includes a call in at least one WGS pup at every included site. [Methods, Figure 1 and experimental validation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/) · [Supplementary Tables 1–2 and Figures S1–S2](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM1_ESM.pdf) · [Supplementary Data 1](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM5_ESM.xlsx)

The paired binary Brier gain is the reference loss minus the candidate loss. Positive values favor the candidate. Each variant has equal weight in its family. Each family has equal weight in the combined gain and mean frequencies. The opportunities sum assays over markers, so a pup can contribute to several counts.

| Pedigree | Variants | Positive / assayed outside WGS | Observed | Parent forecast | WGS forecast | Parent gain vs WGS | Mean of parent and WGS gain vs WGS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CBGP8 | 8 | 42 / 376 | 11.17% | 4.09% | 17.50% | +0.003456 | +0.009251 |
| GPCB2 | 9 | 71 / 603 | 11.77% | 4.21% | 13.33% | −0.005326 | +0.000186 |
| Equal-family mean | 17 total | — | 11.47% | 4.15% | 15.42% | −0.000935 | +0.004719 |

The raw parent frequency had lower loss at eight markers and the discovery frequency had lower loss at nine. The fixed midpoint averaged 9.78% across families. Its paired gain was positive in both families, with most of the improvement in CBGP8. The prespecified smoothed WGS forecast averaged 18.56% and had a gain of −0.002592 against raw WGS. Workbook sensitivity gives a parent gain of −0.001022 and midpoint gain of +0.004675. These are retrospective comparisons in two pedigrees. The variants share parents and inherited cell lineages. [Detailed scores and count sensitivities](results.json)

**Source reconciliation.** The extractor joined Table 2 with the workbook on pedigree, chromosome, position and both alleles. It stripped the workbook's final T tissue suffix and counted each offspring once. All 17 parental labels and source lineage assignments matched. Table 2 counted 9 carriers at one GPCB2 site where the workbook names 10 distinct pups, one from WGS. We used the Table 2 total for the primary analysis and the 10 explicitly recorded pups for the workbook sensitivity. The source supplies aggregate per-site totals and lists of positive samples. It omits the complete site-by-individual no-call matrix. Membership of the ten WGS pups in each site's assay denominator follows from the validation design and the source totals. Individual negative genotypes cannot be independently reconstructed. The union of all positive workbook labels across the entire catalogue includes just 52/57 and 73/77 pups in these families. [Source workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM5_ESM.xlsx)

**Ascertainment and order.** WGS discovery included five pups born in litter 1 and five born in litter 8 (CBGP8) or litter 9 (GPCB2). The other assayed pups include the same litters and intervening litters. GPCB2 also has positive calls in litter 10. The source reports incomplete offspring genotyping. It combined tissue measurements per individual during targeted validation, using three tissues from parents, two from WGS pups and one from other pups. Its large-family discovery filter limited alternate reads in parental WGS data, which are a separate measurement from the parental deep-validation allele fraction. The source's definition of an EE mutation requires an offspring-discovered variant with evidence of parental mosaicism at validation. That selection can affect calibration. The source validation likelihood used allele counts from offspring and parents. Thus other pups are held out of the frequency forecast and the WGS carrier numerator, but can contribute evidence used to validate catalogue membership. The source had already compared parental and offspring carrier fractions using all assayed offspring (Figure S2). [Study and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/) · [Figure S2](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM1_ESM.pdf)

The auxiliary WGS table counts 76 CBGP8 markers and 97 GPCB2 markers present in the five earliest WGS pups. Four and six markers, respectively, also had a recorded carrier among the five later WGS pups. Source-marked adjacent multinucleotide variants are collapsed to one event. All 173 rows before grouping belong to the validated catalogue and counting them supplies the observed overlap for balanced WGS-profile comparisons. [Anonymous WGS margins](early_wgs.tsv) · [Prior event and roster reconstruction](https://github.com/maldonado-research/TMD/blob/246d02bd66389ab50637f423dd62220aa852c754/research/pedigree_timing/mouse/README.md)

## Parent-discovered mutations in four different pedigrees

For the 26 confirmed parental very early embryonic (VEE) mutations, parental VAF beat a constant transmission probability learned from the three other qualifying families by a mean Brier gain of **+0.012258**. Each training family contributes its mean of site-specific transmission fractions. Each test family contributes its own mean paired loss. Parental VAF had lower loss at 19 of 26 sites. Five confirmed sites transmitted to zero assayed offspring.

| Test family | Confirmed variants | Mean observed | Mean parent forecast | Other-family forecast | Parent gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| CBGP4 | 5 | 10.10% | 15.60% | 16.36% | −0.002900 |
| CBGP7 | 5 | 22.42% | 17.20% | 12.26% | +0.014264 |
| GPCB11 | 5 | 5.11% | 10.20% | 18.03% | +0.013092 |
| GPCB9 | 11 | 21.56% | 23.09% | 12.54% | +0.024575 |

Lindsay et al. previously reported a correlation of 0.71 on these confirmed variants. The comparison above quantifies predictive performance relative to a held-family-out baseline. Including all 35 numerically measured attempted candidates, of which nine failed validation, gives +0.008093 after recalculating each training-family rate on that expanded roster. Five other failures have no measurements. The confirmed panel supplies the biological comparison. [Original Table 3 and ascertainment details](VEE_SOURCE.md) · [All 40 targeted candidates](vee.tsv)

**Exploratory decomposition after scoring.** The other-family constant can miss the test family's overall transmission level. For a constant probability q in a test family with observed mean event transmission r, the difference between its mean Brier loss and that of the best constant fitted to this same family is exactly (q − r)². Therefore the reported gain equals this squared calibration gap plus the gain of the parental forecasts over the fitted constant r. The fitted constant uses test outcomes and serves only to interpret the score. With the original equal-event and equal-family weights, the 0.012258 gain decomposes into **0.009768** from the other-family constant's calibration gap and **0.002489** from parental forecasts versus the family's fitted constant. The latter term was positive in CBGP7 and GPCB9 and negative in CBGP4 and GPCB11. [Per-family decomposition](results.json)

## Reproduce

The scorer uses the Python standard library. Source reconstruction also uses Poppler's pdftotext and the source readers committed with the earlier pedigree study. Both native documents are verified by SHA-256. The two source tables print parental allele fractions on different scales. The EE extractor preserves the printed percentage. The VEE extractor preserves the printed proportion. The scorer converts both to probabilities.

```sh
python3 -B score_mouse.py | diff - results.json
python3 -B extract_ee.py 41467_2019_12023_MOESM1_ESM.pdf 41467_2019_12023_MOESM5_ESM.xlsx rebuilt
diff ee.tsv rebuilt/ee.tsv
diff early_wgs.tsv rebuilt/early_wgs.tsv
python3 -B extract_vee.py 41467_2019_12023_MOESM1_ESM.pdf | diff - vee.tsv
```

Derived tables omit coordinates, alleles and individual offspring labels. Source family and lineage labels retain grouping for audit. Lindsay et al. (2019) made the underlying work available under CC BY 4.0. [License](https://creativecommons.org/licenses/by/4.0/) · [Original article](https://doi.org/10.1038/s41467-019-12023-w)

The original study also fitted a linear model of carrier proportion against parental allele fraction on confirmed parent-discovered variants and applied the relationship to estimate germline contribution. Our four-family calculation uses the tissue fraction itself and compares it with a family-held-out constant. [Lindsay et al., estimation of VEE contribution](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/)

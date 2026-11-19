# What can be recovered from the published pine seedling figure?

The Figure 7 source file in the Guner et al. repository draws 571 individual colored circles. Each circle is encoded by a closed path of four cubic arcs. This allows us to count marks even where they overlap visually. Its horizontal position identifies one of nine labelled genotype and family combinations. Its fill color identifies the reported dwarf or normal phenotype. The published caption supplies that color key and identifies Nana as the combined offspring of three related maternal trees. Seedlings were classified using compact branching habit and reduced height relative to siblings. The figure has no individual identifiers, and these data should be described as plotted records. [Pinned author PDF](https://raw.githubusercontent.com/pgnrnr/dwarfism/5d3e28d59955ae5c40e9988c80d399cb9018fd11/Figure%207.pdf) · [Published caption](https://www.nature.com/articles/s41437-025-00814-5/figures/7) · [Study Methods](https://doi.org/10.1038/s41437-025-00814-5)

| Group | A/A dwarf / shown | A/G dwarf / shown | G/G dwarf / shown | Total marks |
|---|---:|---:|---:|---:|
| WB-10 | 2 / 46 | 53 / 70 | 18 / 18 | 134 |
| WB-20 | 3 / 40 | 41 / 63 | 14 / 14 | 117 |
| Nana, pooled | 8 / 69 | 120 / 188 | 54 / 63 | 320 |
| All three | 13 / 155 | 214 / 321 | 86 / 95 | 571 |

A deterministic phenotype call using only the marker and displayed group must assign the same phenotype to every observation in a given cell. It must therefore disagree with at least the smaller color count in that cell. The nine lower bounds sum to **129 of 571**. The genotype-only rule that calls A/A normal and the other two genotypes dwarf attains the bound in every group. Heterozygotes account for 107 of the 129 disagreements. This describes this figure. The peak marker was selected using the study’s association data, and a relationship with a phenotype does not identify the causal DNA change or its time of origin. The three Nana families have been combined. Separate-family performance there cannot be determined.

The Results report 55 of 64 dwarf G/G offspring in Nana and 14 of 156 dwarf A/A offspring overall. The file yields 54 of 63 and 13 of 155, respectively. Both sources describe only dwarf G/G offspring in WB-10 and WB-20. The Methods give 584 individuals in the association analysis. Subtracting the 571 marks does not identify any particular omitted offspring. For example, WB-10 has 134 marks here and a sample size of 120 in Table 1. The narrative also gives 78 dwarf plus 67 normal phenotyped offspring in WB-10. Which samples connect these frames remains unresolved. [Original Results](https://doi.org/10.1038/s41437-025-00814-5) · [Table 1](https://www.nature.com/articles/s41437-025-00814-5/tables/1)

The journal PDF at PMC has SHA-256 `3b04c31c7e1ca68be38a3e1c519f8057d0e4af32fc76b086223f2c01056e1a14`. Page 9 contains a production rendering of the graph with fragmented shapes. Registering the two graphs on the nine genotype tick labels and three height tick labels gives 30,883 overlapping red pixels among 31,456 in the journal render. The author source render has 33,998 red pixels. The pixel intersection divided by the union is 0.89332. This checks the overall correspondence of the two visible graphics. Overlaid points, color conversions and compositing limit what a raster comparison can establish about individual marks. The exact counts above come from the original vector file. [PMC journal PDF](https://pmc-oa-opendata.s3.amazonaws.com/PMC12811388.1/PMC12811388.1.pdf) · [Published raster](https://pmc-oa-opendata.s3.amazonaws.com/PMC12811388.1/41437_2025_814_Fig7_HTML.jpg)

The authors' pinned public repository contains the README and six PDFs. Three earlier files named data, figures and scripts were one-byte placeholders. The native journal supplement contains a single seven-row maternal tree table and five figures. Its 2,696,975 bytes have SHA-256 `b84d2322ef47808ae09d7ddf92ab169cf201d2b6c815fc9613ae5960d52d181d`. The seven tree ages in Table S1 range from 40 to 115 years. They describe maternal tree ages at sampling. No sampled branch’s first qualifying heritable event is timed in that inventory. [Pinned repository tree](https://github.com/pgnrnr/dwarfism/tree/5d3e28d59955ae5c40e9988c80d399cb9018fd11) · [Earlier repository tree](https://github.com/pgnrnr/dwarfism/tree/03a09c3691) · [Native supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC12811388.1/41437_2025_814_MOESM1_ESM.docx)

## Reproduction

After downloading the original Figure 7 PDF, run the standard-library extractor. It verifies the full source digest, all panel labels, nine category ticks, the color key, each circle’s geometry, and all 2,284 cubic segments in the page content stream. A separate check using MuPDF’s vector-drawing decoder returned the same contingency table.

```sh
python3 -B extract_points.py 'Figure 7.pdf' | diff - fig7_counts.json
```

For the optional visual comparison with the native journal PDF, run the following command. The archived receipt used PyMuPDF 1.26.5 and NumPy 2.2.6. Renderers and library versions can affect exact pixel counts.

```sh
python3 -B register_figures.py 'Figure 7.pdf' PMC12811388.1.pdf
```

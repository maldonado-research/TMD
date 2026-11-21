# When did a second carrier provide evidence of a parental mutation?

Lindsay, Rahbari, Kaplanis, Keane and Hurles followed mouse pedigrees and tested their offspring and parental tissues for spontaneous variants. A mutation carried by multiple siblings supports a shared parental germline origin under a single-origin interpretation. The litter containing the first carrier and the litter containing the second carrier can differ. We reconstructed that difference from the individual carrier lists in the authors’ Supplementary Data 1. The two largest pedigrees were the authors’ comparison group for early timing. The measurements were collected retrospectively. [Study and Figure 1](https://doi.org/10.1038/s41467-019-12023-w) · [Open full text and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/) · [Native workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM5_ESM.xlsx)

## Two routes to evidence of earlier origin

| Explicit offspring calls | Parental somatic mosaicism recorded | No parental somatic signal recorded | Total |
| --- | ---: | ---: | ---: |
| Two or more distinct offspring | 16 | 53 | 69 |
| One distinct offspring | 1 | 318 | 319 |
| Total mutation events | 17 | 371 | 388 |

The parents’ tissues supplied one measurement. The offspring supplied another. Under the common-origin interpretation, 53 of 388 validated events (13.7%) had evidence of an earlier parental lineage from siblings even though parental somatic mosaicism was undetected. Those 53 are 76.8% of the 69 events shared across offspring. A single offspring and a negative parent tissue result leave the occurrence time unresolved. The fraction is conditional on the authors’ discovery and validation process. These figures cannot estimate the proportion of all mutations that arise before any particular developmental stage.

The workbook contains 387 of 388 events recorded in two or more distinct sample labels. Only 69 occurred in two or more distinct offspring. The investigators sequenced multiple tissues from offspring. Treating two tissue samples as two independent descendants would change the result substantially. The source has one duplicated sample token, which the extractor counts as one distinct sample.

## How much later did the second carrier appear?

For each shared event, we sorted the recorded carrier **individuals** by numerical litter identifier, allowing two pups in the same litter. The difference between the first two identifiers counts litter-number intervals. A separate calculation records the span from the earliest to the latest carrier. The lists were not in chronological order. In 17 events in GPCB2 a first-listed carrier in litter 10 preceded an earlier litter in the file. [Source pedigree diagram](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/figure/Fig1/) · [Genealogies and litter notation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/figure/Fig6/)

| Second carrier’s litter number minus first carrier’s | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Shared events | 17 | 21 | 8 | 5 | 7 | 5 | 3 | 1 | 2 |
| With no recorded parental somatic signal | 13 | 12 | 6 | 5 | 6 | 5 | 3 | 1 | 2 |

In **52 of 69** shared events (75.4%), sibling evidence required a later litter than the one with the first recorded carrier. The median difference was one litter number. The two largest differences were eight. The 17 events already shared in the first positive litter all had another carrier later. Across all 69 events, the latest carrier’s litter differed from the earliest by 1–9. Restricting to single-nucleotide events gave 51 of 68 requiring a later litter. Among the 53 shared events with no parental somatic signal, 40 required a later litter.

| Pedigree | Events | Shared | Shared with no parental signal | Two carrier pups in first positive litter | Median second-pup lag | Earliest-to-latest span |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBGP8 | 172 | 29 | 22 | 11 | 1 | 3–7 |
| GPCB2 | 216 | 40 | 31 | 6 | 2 | 1–9 |

All integer litter numbers from 1 through 8 in CBGP8 and 1 through 10 in GPCB2 occur somewhere in the native positive calls. The source explicitly reports incomplete offspring genotyping. These intervals measure when the available carrier record could first show sibling sharing if read in birth order. The biological event can predate the first sampled carrier. The workbook supplies neither the date the laboratory discovered it nor its precise cellular birth time. Several events may descend along the same parental germ-cell lineage. The 69 events therefore cannot be interpreted as 69 independent pedigrees.

## Unit and annotation checks

The workbook covers six pedigrees and contains 746 SNP rows and 14 rows labelled MNV (multinucleotide variant). The latter form seven two-base events with identical carriers and source annotations and with the two changes at most five bases apart. The authors specify that these adjacent changes count as one mutation. Collapsing them gives 753 events across the six pedigrees, as reported. The two largest pedigrees contain 391 nucleotide rows and 388 events. One shared MNV with undetected parental mosaicism contributes two nucleotide rows in GPCB2. Counting such rows separately gives **70 shared rows and 54 shared rows with no parental signal**. Counting each MNV once gives **69 and 53 events**, respectively. The former numerators match the study text exactly. The calculation identifies a unit choice that reconciles the figures, while the source authors’ historical calculation remains unverified. [Source results and MNV definition](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/)

All 388 event-level binary sharing flags in the two large pedigrees agree with the presence of at least two distinct listed pups. Two private rows’ numeric sharing columns show 2 beside two tissues of one pup, and another shared row’s numeric column shows 9 beside eight distinct pups. Directly thresholding the numeric column at two gives 71 shared events. The timing calculation uses the explicit carriers. The other four pedigrees were less deeply sampled for discovery. The JSON shows their results separately, including one source-positive sharing flag with only one listed pup. These distinctions qualify the use of a hard sharing threshold for inference.

## Reproduce

Run the following commands from this directory with Python 3.9 or newer. The first uses the bundled anonymous aggregate table. The final two use the original authors’ file.

```sh
python3 -B score_mouse.py | diff - mouse_results.json
python3 -B extract_mouse.py 41467_2019_12023_MOESM5_ESM.xlsx > regenerated.tsv
cmp regenerated.tsv litter_counts.tsv
```

The input workbook is 60,808 bytes. The extractor verifies SHA-256 `a8b69ab1c059f9bc341e22ed78119af9583db489789b7c814eb0196c6a8e1519`. The publisher and PMC rendered the same 760 source rows. We also retrieved the native PMC workbook and used its unmodified XML cells for extraction. The study and supplement are credited to Lindsay et al. (2019), under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This analysis derives and groups carrier information and removes sequences, variant coordinates and individual identifiers from the distributed table. [Publisher workbook](https://media.springernature.com/full/springer-static/esm/art%3A10.1038%2Fs41467-019-12023-w/MediaObjects/41467_2019_12023_MOESM5_ESM.xlsx)

`litter_counts.tsv` contains event multiplicities by pedigree, number of base changes, number of specimen tokens and distinct specimens, number of distinct pups, minimum, second-pup and maximum litter identifiers, and the source mosaic and sharing annotations. A zero second-pup litter marks the absence of a second recorded carrier. Identical codes with or without the source’s final T belong to one individual. An event with two carriers in the same litter has two equal positive litter identifiers. Empty intermediate litters for a particular variant are not counted as assayed negatives.

## Discovery offspring and subsequent sibling measurements

Restricting carriers to the 20 offspring selected for whole-genome discovery in the two large pedigrees gives **23** events detected in at least two of those offspring (12 and 11 by family). Using all subsequently genotyped siblings gives **69** (29 and 40). All 388 events in this comparison have at least one carrier in the discovery offspring. Of the 46 additional shared events revealed by expanded sampling, 37 had no recorded parental somatic signal. These are two views of the same validated discovery roster. Mutations absent from all discovery offspring could have escaped that initial ascertainment.

The verifier reads the original Supplementary Table 1 roster and Supplementary Data 1 workbook, checking the SHA-256 of each. It requires Poppler's `pdftotext` and Python. [Supplementary Table 1, pages 2–3](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM1_ESM.pdf) · [Verified aggregate results](discovery_results.json)

```sh
python3 -B check_discovery_panel.py 41467_2019_12023_MOESM1_ESM.pdf 41467_2019_12023_MOESM5_ESM.xlsx | diff - discovery_results.json
```

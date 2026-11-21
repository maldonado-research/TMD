# Arabidopsis endpoint substitution benchmark

A spectrum estimated from 47 Arabidopsis mutation-accumulation lines predicted the substitution class in the 48th line better than assigning equal probability to each of six classes. Across all 48 held-out lines, mean multiclass Brier loss was **0.64314** for the learned spectrum and **0.83333** for equal probabilities. The gain was positive for 46 of 48 lines. This result concerns a randomly drawn recorded line-private substitution at generation 25. The source provides one endpoint per line. The generation when each mutation arose, its effect on fitness, and its probability of establishment remain unknown. [Source article](https://doi.org/10.1534/genetics.118.301721)

## Design and results

Weng et al. sequenced 107 lines derived by single-seed descent from one Col-0 founder. We use the 48 lines marked with an asterisk in their Supplementary Table S1 as the primary plant subset. For each fold, the forecast pools single-base changes in the other eligible lines and adds one count to each class. The reference probability is 1/6. Within the held-out line, each eligible substitution receives equal weight. Each line then receives equal weight in the overall mean. Positive gain favors the learned spectrum. Log gains use natural logarithms. Top-class hit gains split credit over tied predictions. [Study scoring specification](../DESIGN.md) · [Supplement and native data](https://doi.org/10.25386/genetics.6456065)

| Analysis | Lines | Private substitutions | Brier gain | Log gain (nats) | Top-class hit gain |
|---|---:|---:|---:|---:|---:|
| Author-designated primary subset | 48 | 925 | +0.19020 | +0.42267 | +0.39426 |
| After removing four lines named in the shared-event file | 44 | 841 | +0.18903 | +0.42208 | +0.39243 |

C>T and its complement G>A account for 528 of the 925 primary observations. Combining the six predicted probabilities into transitions and transversions gives the reference a transition probability of 1/3. On this binary outcome, the two-category Brier gain was +0.26898 for the 48 lines and +0.27471 for the 44 lines. The scores describe these observed lines. A common founder, differences in callability, ancestral base composition, known mutational biases and the survival of lines to sampling all limit interpretation. A comparison with equal class probabilities cannot isolate the contribution of natural dominance. [Machine-readable results](results.json)

## Source reconciliation

The supplement contains 1,694 author-labeled private single-nucleotide mutation (SNM) rows across 107 lines. Every raw private count equals the printed Table S1 total SNMs minus shared SNMs for its line. We excluded one SNM explicitly marked PCR-rejected, yielding 1,693 entries in the exported counts across all 107 lines. It is outside both scored subsets. We kept the three rows marked “bad amplification” alongside other source-called mutations lacking independent validation. One of these rows is in the primary 48. The remaining private rows comprise 72 PCR-validated and 1,618 with an empty validation field. All 1,694 calls have classifiable REF and ALT bases. We omitted private indels and used only the unique-event table for class counts. Shared calls and fixed founder differences contribute zero to the predictor and score. [Supplementary File S1](https://ndownloader.figshare.com/files/11878307)

Table S1 identifies 48 lines with zero shared SNMs and zero shared indels. File S1's separate shared-event table explicitly names four of those lines. Three (43, 52, 69) appear only in rows annotated as ancestral. Line 16 appears in a shared SNM row without that annotation. Two other shared-site records identify carriers only by their total number (15 or 56). We therefore retain the authors’ printed 48-line designation, and repeat the calculation after removing the four named exceptions. The remaining 44 have no explicit shared-table line identifier. The unnamed carrier groups and common founder preclude certification of pedigree independence. [Supplementary Table S1](https://ndownloader.figshare.com/files/13345196) · [Supplementary File S1](https://ndownloader.figshare.com/files/11878307)

## Reproduction and attribution

The counts derive from the Weng et al. supplementary dataset released under CC BY 4.0. The study authors are Mao-Lun Weng, Claude Becker, Julia Hildebrandt, Manuela Neumann, Matthew T. Rutter, Ruth G. Shaw, Detlef Weigel and Charles B. Fenster. This derivative aggregates strand-complementary classes by study line and includes the authors’ subset flags and accessible-site counts. Accessible-site counts describe coverage and have no role in the scoring formula. [Original dataset and license](https://doi.org/10.25386/genetics.6456065) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

Run from this directory with Python 3.10 or newer. The score uses the bundled aggregate counts and the Python standard library. Rebuilding counts from source also requires Poppler's `pdftotext`. The extraction checks native SHA-256 hashes before parsing. An independent calculation using direct per-event squared errors and an explicit 12-to-6 lookup reproduced both six-class Brier gains to ten decimal places.

```sh
python3 score_weng.py > /tmp/weng-results.json
cmp /tmp/weng-results.json results.json
curl -fL https://ndownloader.figshare.com/files/11878307 -o /tmp/weng-file-s1.zip
curl -fL https://ndownloader.figshare.com/files/13345196 -o /tmp/weng-supplement.pdf
python3 extract_weng.py /tmp/weng-file-s1.zip /tmp/weng-supplement.pdf > /tmp/weng-counts.tsv
cmp /tmp/weng-counts.tsv line_counts.tsv
```

| Figshare file ID | Bytes | Figshare MD5 | SHA-256 of verified native bytes |
|---|---:|---|---|
| 11878307 | 59,421 | `7444608c2f051364ff0c6599e8878951` | `cb2a229257b26013348e9447a19fe2220a6e920b11c30f05430a7ac524ac9ca4` |
| 13345196 | 177,461 | `25ba8ad3a09b6fec46526dc2028ad810` | `b1e24da381e9787aa4c87545e1176257ff0e1dd321cd78583c798788983cb79c` |

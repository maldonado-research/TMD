# Huseby 2017: recovered endpoint sampling map

Ricardo Maldonado · 30 October 2026 · Original source assessment with AI assistance

The official supplement to [Huseby et al. (2017), DOI 10.1093/molbev/msx052](https://doi.org/10.1093/molbev/msx052) is now accessible through the connected research provider. [Table S6](https://pmc.ncbi.nlm.nih.gov/articles/instance/5400412/bin/msx052_Supp.pdf) maps ten evolved lineages to two sampled endpoint colonies each. This resolves the earlier aggregate-only bounds on sampled presence:

| Quantity | Aggregate-only bound | Recovered table |
| --- | ---: | ---: |
| Lineages with at least one sampled colony carrying a listed parC mutation | 9–10 | 10 |
| Lineages with both sampled colonies carrying listed parC mutations | 8–9 | 8 |

There are 18 listed parC-mutant colonies among 20 sampled colonies, seven reported amino-acid substitutions, and 16 lineage/substitution observations after collapsing repeated alleles within each lineage. Both sampled colonies have the same listed parC allele in two lineages. These are sampled observations; they do not establish independent mutation origins, fixation, or complete clone identity.

The ten evolved lineages are the experimental clusters described by the study. Colonies within a lineage share an evolutionary history. All inherit gyrA S83L; it is excluded from acquired-hit counts. A source dash means no parC mutation is reported for that colony, not a mutation-free genome. S6 is a parC table, so unlisted genes cannot be assigned zero mutations. Other supplementary tables have different sampling frames and cannot be pooled as additional S6 lineages.

The main article's 18/20 aggregate, its ten S80-mutant colonies, and S80I in three independent lineages agree with the recovered table. Mutation-rate selection at 4×MIC and the evolved-line experiment at 0.5×MIC remain different observational regimes. This acquisition does not supply the independent establishment/recovery controls or native Wsp/Aws/Mws panel needed by the frozen TMD forecast.

## Provenance and reproduction

Firecrawl returned the official supplement as a nine-page parsed representation, reporting HTTP 200 and `application/pdf`. No raw PDF bytes were saved; the recorded hashes identify saved parsed JSON. A separate root retrieval returned the same S6 entries, and independent internal review matched all twenty records. This is AI-assisted internal review, not external peer review.

The acquisition record is [SOURCE_REPRESENTATIONS.json](SOURCE_REPRESENTATIONS.json). Full parsed source and the transcribed table remain external. The source article displays CC BY-NC 4.0; the repository's original software/documentation terms do not relicense that source content.

For separately obtained JSON representations containing `markdown` and `metadata` fields, run:

```sh
python -B research/huseby_lineage_audit/extract_table.py \
  --source-json /path/to/supplement.json \
  --article-json /path/to/article.json \
  --output-dir /tmp/huseby-audit
```

The original standard-library parser checks all twenty lineage/isolate keys and reproduces the counts and an external CSV. It performs no downloads or author-code execution. Its output is a source-table audit, not a new biological fit or TMD validation.

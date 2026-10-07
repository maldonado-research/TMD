# Targeted changed-source watch — 7 October 2026

A single PubMed query screened records newly indexed from 2–7 October for bacterial/Pseudomonas mutation supply, spontaneous mutation, fluctuation assays and transcription-associated mutagenesis. It returned two records. Both abstracts and their publication metadata were read; neither full text or underlying dataset was acquired. Indexing dates are not publication dates. This is a bounded source watch, not a systematic or complete web review.

| Primary record | Actually inspected | Relevance and boundary |
| --- | --- | --- |
| *Spontaneous mutation rate estimation in the large-genome unicellular eukaryote Euglena gracilis*, DOI [10.1093/jeb/voag096](https://doi.org/10.1093/jeb/voag096), PMID 42832043; online 5 October 2026 | PubMed abstract and metadata | The abstract reports ten mutation-accumulation lines, 153 de novo nucleotide mutations and a false-negative-corrected rate. This is a eukaryote mutation-accumulation source, not a matched SBW25 assay or transferable bacterial supply parameter. No raw mutation calls or correction model were audited. |
| *Herd immunity underlies homologous recombination in stationary phase bacteria*, DOI [10.1093/molbev/msag238](https://doi.org/10.1093/molbev/msag238), PMID 42827080; journal date 3October 2026 | PubMed abstract and metadata | The abstract reports E.coli–P1 phage/CRISPR-mediated gene exchange in stationary phase. It motivates checking whether inherited changes arose through mutation or horizontal exchange under the relevant ecology. Its reported comparisons are the authors' abstract claims, not independently reproduced measurements; no quantitative transfer to SBW25 or W/A/M is admitted. |

A later full-text source/methods check of the recombination study is queued. Its existence does not show phage-mediated transfer in the current SBW25 experiment. A route model that assumes mutation-only entry needs to justify that scope; genetic inheritance and spontaneous mutation are distinct mechanisms.

No matched Wsp/Aws/Mws panel, new cohort, confirmatory test or new TMD prediction is added by this watch. The actual study registry remains unresolved. Raw PubMed responses remain external; only bibliographic metadata, original commentary and hash receipts are public. Cite the original papers if using their observations.

The independent internal methods reviewer also checked both cached abstracts and their metadata. This is internal source checking, not external peer review.

Reproduce the metadata/hash check with the original cached responses:

```sh
python verify_watch.py --raw-source-root /path/to/source_watch_2026-10-07/raw
sha256sum -c SHA256SUMS.txt
```

Without that cache, the verifier checks the public receipt only and reports raw-source replay as UNRUN. It does not silently fetch or change expected hashes.

Original documentation: CC BY 4.0; verification code: MIT under the repository terms. Prepared with AI assistance.

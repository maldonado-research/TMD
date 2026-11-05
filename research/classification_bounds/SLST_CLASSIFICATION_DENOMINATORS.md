# SLST assignment counts and the calibration denominator

The new source result is an exact partition of observed reconstructed sequences, plus a bounded inventory of the public archive. It does not supply a native Wsp/Aws/Mws confusion matrix or classwise correct-call lower bounds.

[Orcel et al. (2026), Table 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#T1) gives the following counts. The first three numerical columns reproduce the published labels; the last two are arithmetic differences.

| Mix | Full-length SLST sequences reconstructed | Sequences assigned to any SLST type | Sequences assigned to expected SLST types | Derived unassigned | Derived assigned outside expected set |
|---|---:|---:|---:|---:|---:|
| FixedMix | 8,192 | 7,639 | 7,634 | 553 | 5 |
| StaggeredMix-L1 | 7,732 | 7,368 | 7,367 | 364 | 1 |
| StaggeredMix-G1 | 7,043 | 6,739 | 6,739 | 304 | 0 |

The reconstructed-sequence denominator is downstream of read filtering, the requirement for at least 50 reads per UMI family, assembly, and full-length-locus screening (Methods `s4_6`). It is not the number of introduced cells, input molecules, initial UMI families, or independent library preparations. Thus, for example, 553/8192 is an unassigned fraction conditional on reconstruction. Units lost before that stage are not counted in the 553.

“Assigned to expected SLST types” means membership in the known mixture's set of types. A wrong call from one expected type to another expected type still enters that column. Therefore 7634/7639 is an expected-set fraction among assigned sequences; it is not the diagonal accuracy of a classifier. Table 1 does not identify true-type-by-call cells, and pooling technical replicate counts does not supply them. The six single-isolate controls in Figure 2 are more relevant to that question, but the main text reports an average of 93% across those controls without an exact per-isolate correct/wrong/unassigned count table. An average alone cannot be used as a common lower bound for every class.

The finite-calibration requirement depends on the estimand. For independently prequalified true-W/A/M units, define the eligibility gate and count every eligible, truth-labelled control unit exactly once in its class denominator, including wrong calls and terminal failed/no-call outcomes recorded as U. A conditional classifier bound applies at that same gate; it does not automatically become sensitivity from introduced cells. Sensitivity from introduced cells additionally needs the full introduced-cell denominator and upstream losses. The SLST controls use purified genomic DNA and reconstructed molecular sequences, so neither their trial unit nor their workflow establishes the proposed native calibration. E. coli background or other genuinely non-W/A/M units are a separate truth-category issue: recording their observed failures as U does not make a three-true-class model valid unless the prequalification gate excludes them or the model explicitly handles their contribution.

The official [BioProject PRJNA1422617](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1422617) links to [TLS master KJKS00000000.1](https://www.ncbi.nlm.nih.gov/nuccore/3279182772). The retrieved version-01 master lists 338,437 sequence records and 106 BioSamples. Metadata for all 106 listed BioSamples were acquired and inspected: 6 defined-mixture samples (2 per mixture), 12 mock controls, 40 SpikeMix samples, and 48 clinical samples. No record in this master-linked roster was labelled as a Figure 2 single-isolate control or negative control. This bounded inventory does not prove those controls are absent from every deposit. Its two named samples per defined mixture also leave an unresolved coverage difference from the paper's statement that these mixtures were prepared and sequenced in triplicate. No correction to the paper is inferred.

One sequence record, KJKS01000001.1, was inspected; it is a 484-base clinical SLST sequence linked to BioSample SAMN55197832, not a table of known truth and classifier outcomes. The BioProject-to-SRA link query returned no links; that result is not proof that no raw reads exist elsewhere. The 338,437 underlying sequences were not downloaded or reclassified.

The PMC page exposes seven XLSX links. The first exact attachment link returned HTTP 200 with reCAPTCHA HTML, not an XLSX file; inspection stopped without solving or bypassing the challenge. No supplementary workbook was acquired. The JATS repeats the DataSheet1.xlsx link under multiple different figure/table captions, so those links alone do not establish which workbook contains each table. The remaining six workbooks were not downloaded. Neither absence of a matrix in the inspected material nor an inaccessible attachment is a claim that no such matrix exists.

`verify_slst_classification.py` replays Table 1 and the bounded metadata inventory offline using SHA-256 pins. `SLST_CLASSIFICATION_REPLAY.json` contains original labels, exact count differences and rational rates, the public sample roster, source hashes, and explicit non-admission to native calibration. Both checks passed:

```sh
python -B verify_slst_classification.py \
  --source /path/to/slst_full.xml \
  --metadata-dir /path/to/acquired/metadata \
  --output /tmp/slst-classification-replay.json
```

Omit `--metadata-dir` to replay only the article table; the metadata status then reads `UNRUN_METADATA_NOT_SUPPLIED`. No network request or author-code execution occurs. The original JATS hash is `8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4` (126,193 bytes). `acquisition_receipts.json` records the network outcomes separately. No numerical SLST result is transferred to TMD.

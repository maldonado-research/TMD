# What the SLST controls establish about an eligibility gate

The cached source supplies a concrete sample-count threshold, a partial identification of its behavior on twelve workflow blanks, and a retained-sample roster separately cross-checked against cached metadata. It supplies no native Wsp/Aws/Mws false-entry calibration. Keep the native false-entry bound unset; the next useful evidence would be independently established Other units evaluated with the frozen target gate, including every pass and failure in the control denominator.

[Orcel et al. (2026)](https://doi.org/10.3389/fcimb.2026.1807759) reports two separate filters whose numerical cutoffs happen to coincide:

| Stage | Published rule | Unit |
|---|---|---|
| Before assembly, Methods [s4_6](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#s4_6) | UMI families need at least 50 reads | Reads per UMI family |
| Clinical sample inclusion, Results [s2_3](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#s2_3) and [s2_5](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#s2_5) | Samples with fewer than 50 reconstructed full-length sequences are excluded | Reconstructed sequences per sample |

The twelve negative controls were nuclease-free water carried through the full workflow (Methods [s4_7](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#s4_7)). Results s2_3 gives their maximum reconstructed-sequence count as 50 and says that this value was used to choose the background threshold. Applying the literal complementary count gate, `N >= 50`, to those same count values gives between 1 and 12 positive blanks, or a descriptive fraction between 1/12 and 1. The individual counts are unavailable in the inspected main text; only a maximum and denominator are reported. This is not a statement that the authors included negative-control records in their downstream clinical analysis. A hypothetical strict rule `N > 50` would give zero passes on these same counts, but it is a different comparator from the published exclusion rule. No correction or alternative implementation is inferred.

These are threshold-selection observations, not an independent validation of a gate fixed beforehand. They do not justify a fixed-gate population false-positive interval. Moreover, water blanks measure workflow background or contamination. They are not known-Other biological units drawn from a target native cohort. Sequence counts within a blank must not be promoted into independent control trials. Supplementary Table 3 is described as the per-run negative-control table, but its contents were not acquired.

The positive Mock control contains six intended SLST types and E. coli DNA at a 2:98 target-to-background mass ratio. The four SpikeMix conditions contain target DNA at 50%, 10%, 5%, and 0.5%, with ten technical replicates per condition (Methods [s4_2](https://pmc.ncbi.nlm.nih.gov/articles/PMC13231282/#s4_2)). Every listed condition therefore contains intended target DNA; none is a pure E. coli negative condition. Target DNA mass fraction is not a fraction of independently truth-labelled input units, and the output sequences are not labelled by their originating target/background input molecules. Thus neither 98% background nor the reported low “Others” output fraction measures `P(gate passes | true Other)`. “Others” here means called SLST types outside the intended mixture set; it is not the true native Other category. The main text and Supplementary Table 2 describe twelve Mock runs, while the Supplementary Figure 2 caption says eleven. This wording difference is preserved without selecting a replacement count.

The clinical inclusion result is exact at its stated sample level: 48 of 60 site samples passed, so 12/60 were excluded and the observed pass fraction is 4/5. It is not target truth prevalence, positive predictive value, or a fraction of independent donors. The design has 30 donors with two sampled sites each.

| Retained roster | Article s2_5 | Cached BioSample metadata aggregate |
|---|---:|---:|
| Face samples | 25 | 25 |
| Back samples | 23 | 23 |
| Paired coded subjects | 22 | 22 |
| Face only | 3 | 3 |
| Back only | 1 | 1 |

The cached sample-name and isolate fields agree on all 48 site labels and their coded pairing, yielding 26 distinct coded subjects. Only aggregates are emitted. The preceding article sentence says four donors lost both sites and four additional samples were lost from the back only; that arithmetic instead implies 26 retained face and 22 retained back samples. Both descriptions yield 48 total. These are two records of the same study. The metadata corroborates the stated retained roster but does not repair the exclusion narrative or identify which account of individual losses is intended.

The earlier bounded archive inventory covers 106 BioSamples linked by TLS master KJKS00000000.1: 6 defined-mixture samples, 12 Mock samples, 40 SpikeMix samples, and 48 clinical samples. No record in that roster was identified as a negative control. This is a bounded inventory, not a claim that such controls are absent from every deposit. This follow-up uses the already cached metadata and makes no further archive requests. The previous supplementary download returned a reCAPTCHA challenge; no workbook was acquired and no challenge was solved or bypassed.

The three denominators needed for a native bridge remain distinct. A false-entry probability needs all prequalified true-Other controls, including failures; predictive value needs independent truth adjudication among gate-positive units; a full-cohort target fraction needs the original cohort denominator and appropriate information about gate failures. An observed gate-pass fraction alone supplies none of those truth quantities. The [native source note](native_controls/NATIVE_CONTROL_NOTE.md) gives concrete non-focal WS examples while preserving their selected-collection and genetic-background conditioning; it likewise admits no numerical native bound.

`verify_slst_eligibility.py` checks the source hash, exact section statements, threshold boundary arithmetic, clinical inclusion arithmetic, both source wording discrepancies, and the aggregate cached clinical metadata. It emits `SLST_ELIGIBILITY_REPLAY.json`. Source omissions remain omissions, and the output explicitly leaves numerical native calibration unset.

```sh
python -B verify_slst_eligibility.py \
  --source /path/to/slst_full.xml \
  --metadata-dir /path/to/cached/metadata \
  --output /tmp/slst-eligibility-replay.json
```

The metadata argument is optional; omission yields `UNRUN_METADATA_NOT_SUPPLIED`. The replay is offline, uses only the Python standard library, and executes no author code. The JATS source is 126,193 bytes with SHA-256 `8e86d14d30a55fa672ec950379d03a7d3b57df2ece2ea297f2b5720fb09c7cb4`; it identifies CC BY 4.0 licensing. The original analysis and aggregate outputs contain no raw article body, workbook, individual clinical code, or raw BioSample record. Third-party rights remain unchanged.

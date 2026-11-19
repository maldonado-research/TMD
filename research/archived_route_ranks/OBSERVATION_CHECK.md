# Does the same group lead under a second observation rule?

Goel et al. reported 123 L1-exclusive versus 70 L2-exclusive somatic mutation candidates in layer-enriched fruit samples from one apricot tree. Under their leaf call rules, zero of those 123 and 49 of those 70 were called in adjacent leaves. The authors already reported both pooled results. Their targeted follow-up found weak read support for many L1 events. A missing leaf call therefore cannot establish that a mutation was biologically absent. [Primary paper, Figs. 1 and 3](https://doi.org/10.1186/s13059-024-03337-0)

We matched the original S1 branch/tissue roster to S3 and S4 candidate records. We kept each event's fruit-layer assignment fixed across the tree, and counted its fruit and leaf calls within the same branch. All seven branches had more L1-exclusive candidates in fruit and more L2-exclusive candidates with a leaf call. This held on every branch after excluding all 15 candidates flagged low confidence in S3. The filtered pooled comparison is 0/116 versus 43/64. Both-layer and leaf-only events are separate categories in the result. Some mutations recur across branches of this tree, so these seven comparisons cannot serve as seven independent biological replicates. [Published workbook](https://doi.org/10.6084/m9.figshare.26368540.v1) · [Paired counts](apricot_layers_receipt.json)

An independent potato study also measured tissue-dependent visibility. In Désirée, the mean read fraction at L1 sites fell from 0.25 in trichomes to 0.06 in mixed leaves. A 2026 sweet-orange study repeated sequencing on the same DNA from six leaves. Across two repeat libraries considered together, 49–69% of previously called leaf-specific sites were rediscovered per sample, compared with 100% for mosaic and clonal calls in those comparisons. These estimates concern rediscovery conditional on an original call. Neither study measures errors for TMD's bacterial route labels. [Amundson et al., Fig. 1](https://doi.org/10.1073/pnas.2514507122) · [Beaulieu et al.](https://doi.org/10.1093/plcell/koag288) · [Sweet-orange Table S5](https://pmc-oa-opendata.s3.amazonaws.com/PMC13690466.1/koag288_supplementary_data.pdf)

The apricot workbook is the same public version used in the preceding verification-coverage audit. Its SHA-256 is checked before replay. The program emits aggregate counts only. [Replay](replay_apricot_layers.py)

```sh
python3 -B research/archived_route_ranks/replay_apricot_layers.py /path/to/13059_2024_3337_MOESM2_ESM.xlsx
```

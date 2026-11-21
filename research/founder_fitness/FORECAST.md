# Founder-assay forecast rules

**20 November 2026 Pacific.** We fixed this benchmark after reading the Fasanello study design and before joining founding fitness measurements to the head-to-head outcomes. The day-25 outcomes and earlier abundance-only forecasts have already appeared in TMD 0.11.0. The comparison below is retrospective. It scores already published populations. [Previous benchmark](https://doi.org/10.5281/zenodo.24382132) · [Source study](https://doi.org/10.7717/peerj.10118)

## Forecast and endpoint

Use every well in the previously frozen 76-well Fasanello panel with two matched founding labels and all four generation-zero assay repetitions. The two labels carry the same orientation as the 0.11.0 count table. Pair assay measurements by native source condition, identity and repeat. Use exclusively the generation-zero samples of the separate competition assay and the day-0 starting mixture in the longitudinal well. Assess each label relative to its own reference within its assay. A shared measured reference cancels algebraically. Keep the author's stored count convention for this rate estimate and disclose any adjustment. Use the earlier reconstructed assigned counts for longitudinal shares. Missing or unusable inputs cause an explicit abstention. Do not select wells by the strength of a fitness difference or by the endpoint.

For each assay repetition r compute the difference in per-generation log fitness between the two founders. Each log fitness is the change in log focal/reference count ratio from assay start to finish divided by the source's 20 generations. Let s be the unweighted mean of the four paired differences. Equal weights ensure that this primary rate uses only founding observations. It need not equal the difference of the authors' separately weighted fitness summaries.

Let L₀ be the log ratio of the longitudinal starting counts for labels A and B. Evaluate four fixed predictions.

- The **baseline leader** has the larger day-0 count.
- The **assay leader** is A when s is positive and B when s is negative.
- The **combined forecast** selects A when L₀ + T s is positive and B when it is negative. T is the published approximate generation horizon by regime, 250 for standard schedules, 200 for the lower-dilution condition (0.004), and 300 for the higher-dilution condition (0.00025). Its predicted endpoint share for A is the inverse logit of L₀ + T s. This projection assumes the assay difference persists through follow-up.
- For **direction of relative gain**, predict that the higher-assay-fitness label increases its observed share between day 0 and day 25. A founder can gain share while finishing second.

For the leader endpoint, a strict hit requires the unique predicted label to match the unique leader at day 25 in the authors' selected longitudinal measurement. Report the baseline, assay-only and combined scores, paired successes in both directions for combined versus baseline, assay-direction hits, abstentions and endpoint ties. Also compare the mean absolute error of the combined and baseline share forecasts at day 25. No coefficient is fitted to these wells. Assess scores separately for standard, stressed and altered-dilution settings and for the full roster, using the source conditions. Four repeats of a pooled ancestor assay are technical measurements and supply no extra evolved populations.

## Sensitivity checks

Use each ancestor assay replicate alone in turn and compare with the primary four-repeat score. Check agreement of replicate signs. Where feasible compare the archived authors' generation-zero fitness summary with the primary estimate, the original and repeat endpoint libraries, and the earlier day-10 forecast with its later issue time. Interpret disagreements relative to pooled acquisition, shared labels and assay context. Any additional comparison or study located afterwards is exploratory. No confidence interval treats wells sharing pools or technical counts as independent replicates. These outcomes concern relative abundance among established founders. New mutation origins and first establishment require different data.

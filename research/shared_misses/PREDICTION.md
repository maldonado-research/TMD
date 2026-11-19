# Prospective check of the split-read allocation prediction

The question is whether counts of alternate reads at a previously established set of sites separate less evenly between paired tissue splits than a simple random-allocation calculation predicts. Flower #2 in Ji et al. motivated the direction and the choice of at least two alternate reads. Its observations belong to the exploratory analysis. This dated GitHub specification sets the terms for one new observational comparison. [Exploratory result](README.md#does-random-allocation-between-splits-explain-the-positive-records)

## Which archive will count?

Use the first eligible publicly deposited plant dataset identified through a documented search whose initial public data release **postdates the GitHub commit introducing this specification**. Use the earliest verifiable original data-release timestamp among eligible datasets found in that search. Break timestamp ties by lexicographic order of the persistent dataset identifiers. Record search sources, dates, all candidates considered, reasons for exclusion and coverage limitations. Log the selected dataset identifier, version, inclusion frame and raw-file hashes before viewing the split-agreement result. Earlier publications, revisions or reuse of the Ji samples do not qualify.

Eligibility requires identifiable paired technical subsamples from the same plant tissue, candidate sites established independently of the two splits being scored, reported alternate and reference counts for both splits, and documentation sufficient to identify missing or duplicate entries. Include every reported tissue–site pair in the declared frame and report the counts missing either half or lacking positive depth. If multiple technical pairs are available for one preparation, use a pair explicitly designated by the source, or the first two technical subsamples in stable source-identifier order. Keep repeated measurements belonging to the same tissue together and report organism and tissue counts. Record eligibility before calculating the score. A study that cannot supply interpretable counts does not yield a numerical test.

## What outcome would count against the prediction?

Use the source-defined reference and alternate for each candidate. For pairs with both depths positive and at least two alternate reads in total, let O count pairs with all alternates in one half. Compute E by summing the exact uniform-allocation probability over the same pairs, conditional on their two depths and their total alternate counts. The signed primary score is R = O − E. Evaluate the sign from the exact fractions, before rounding. Report O, E, the number of eligible pairs, organisms and tissues, and R divided by the number of eligible pairs. [Probability calculation](allocation/read_allocation.py)

The prediction is R > 0. Zero or a negative value fails this directional prediction on the selected archive. If no informative comparison remains, or all probabilities are forced to zero or one by the input depths, declare the result uninformative. Publish that outcome for the selected archive. This protocol supplies a descriptive directional test with no significance threshold, biological mutation-rate claim or estimate of the probability of missing a true mutation. At the time this rule was written the independent outcome was unknown.

## Score the selected archive

Prepare a tab-separated file with one row for every declared plant, tissue and site combination, including rows whose measurement is missing. Use these seven header names, with the source-defined identifiers and nonnegative integer counts. Keep the same source-to-split mapping throughout.

```text
plant_id	tissue_id	site_id	a_ref	a_alt	b_ref	b_alt
```

An empty count field marks a missing measurement. A recorded zero stays zero. The scorer rejects duplicate plant–tissue–site keys and missing identifiers. A tissue is identified by its plant and tissue IDs together. The input roster must be reconciled with the source before use, since an omitted row cannot be detected from the TSV alone. The scorer first sets aside rows with missing counts, then rows with zero total depth in either half, then rows with zero or one pooled alternate read. It reports the resulting flow of records and the numbers of plants and tissues in both the supplied frame and the eligible set.

Run the score and its constructed-data checks from the repository root with Python 3.10 or later.

```sh
python3 -B research/shared_misses/allocation/score_replication.py /path/to/complete_frame.tsv
python3 -B research/shared_misses/allocation/verify_replication.py
```

The JSON output records exact fractions for E, R and the per-comparison difference. All eligible rows enter the denominator, including rows where the depths force the outcome. A positive exact R yields `positive_direction`. Zero or negative R yields `direction_failed` when an informative row exists. A frame with no eligible rows or with only forced outcomes yields `uninformative`. [Scoring program](allocation/score_replication.py) · [Constructed-data checks](allocation/verify_replication.py)

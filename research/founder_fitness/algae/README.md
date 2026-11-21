# An independent green-algae check of growth rate and final abundance

Bestion and colleagues independently measured monoculture growth and the relative abundance of competing freshwater green algae. They previously tested whether growth traits predict which species becomes more abundant. This exploratory reanalysis asks a further question about the size of that advantage. For the ten retained pairs at the last sample, the faster-growing species finished ahead in 125 of 179 decisive trials. The exponential forecast missed the final fraction by an average of 36.7 percentage points. Predicting equal shares missed by 30.0 points. These measurements concern competing species with equal nominal starting densities. They provide an ecological comparison for a founder model and supply no direct measurements of lineage founders or unequal starting fractions. [Paper](https://doi.org/10.1111/ele.12932) · [Open full text, equations 5 and 8 and Figure 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849607/)

## Source and scope

The authors deposited two native data tables. `Growth rate raw data.csv` contains 938 fitted monoculture growth-rate estimates. Each row identifies species, temperature, phosphate concentration and replicate. `Competition data.csv` contains 1,620 rows from 540 competition units measured at three times. Each row identifies day, species pair, temperature, phosphate concentration and replicate. Its cell densities are classifier estimates. The authors measured 78% overall cell identification accuracy for their primary linear discriminant analysis (LDA) on their independent in-silico discrimination test. The same competition sample received all three classifiers. [Archive and data dictionary, CC BY 4.0](https://doi.org/10.5281/zenodo.1161963) · [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849607/)

The retained set comprises native species codes 1–5. The authors identified unusually poor discrimination and unexpectedly low mixed-culture yields for code 6. Source-based exclusion of this species changes which pairs can be scored and makes this a selected subset. The archive identifies freshwater green algae and does not report strain-specific toxin assays. The sources credit Elvire Bestion, Bernardo García-Carreras, Charlotte-Elisa Schaum, Samraat Pawar and Gabriel Yvon-Durocher (2018). [Source discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849607/) · [Native archive](https://zenodo.org/records/1161963)

## Prediction and observations

For each species and observed environment, take the arithmetic mean of all available replicate monoculture `mu` values at that exact numeric temperature and phosphate concentration. Across the five retained species, 75 records cover 26 of 30 possible species–environment combinations. String representations of the lowest overlapping phosphate concentration differ between files. Join by numeric value. No competition outcome enters any rate estimate. Predictor and response come from separate assays of the same species and environmental conditions. The populations have a nominal 1∶1 starting ratio. The archive has no per-replicate measured starting fractions. [Native data dictionary](https://zenodo.org/records/1161963)

Equation 8 fits a straight-line segment to base-10 log cell density. For species A and B with slopes μA and μB, let Δr = ln(10)(μA − μB). At elapsed time t in days, the forecast fraction of A is 1 / [1 + exp(−t Δr)]. Its direction is the sign of Δr. The observed fraction is the estimated count for A divided by the sum of the two estimated counts. Absolute fraction error includes observed ties. The direction denominator omits exact ties. A constant forecast of 0.5 gives a reference for fraction error. The paper itself fitted nutrient and temperature responses and compared the direction of competitive advantage. Its reported 72% at day 14 uses a different predictor and a different set of rows. [Methods and original comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849607/)

The extrapolation applies the monoculture exponential-phase slope throughout each competition and ignores lag, resource depletion and saturation. The authors report that some cultures had already left exponential growth by day 14. Days 5, 14 and 23 are repeated observations from the same units. Day 14 is the authors’ primary endpoint and day 23 is the last archived observation. These fractions measure relative abundance at a specified time, with no requirement for competitive exclusion or equilibrium. [Methods and discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849607/)

## Coverage and sensitivity

Each time point starts with 540 native competition rows. Removing comparisons involving species code 6 leaves 360. Apply the authors' low-density flag first, then exclude rows lacking an exact-condition monoculture rate for either competitor. Each usable pair–environment occurs in up to six units. Available environments differ among endpoints, and the density filter selects especially heavily at day 5.

| Day | Low density excluded | Missing rate excluded after density filter | Fractions scored | LDA ties | Correct direction | Rate forecast MAE | Equal-share MAE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 217 | 9 | 134 | 1 | 90/133 | 28.7 pp | 32.8 pp |
| 14 | 68 | 77 | 215 | 2 | 152/213 | 33.4 pp | 32.4 pp |
| 23 | 108 | 72 | 180 | 1 | 125/179 | 36.7 pp | 30.0 pp |

At day 23 all ten pairs were represented across 39 pair–environment combinations. For LDA, the rate ordering agreed with the direction of the mean observed fraction in 27 of 39 combinations, and with the median in 26 of 39. Giving equal weight to each pair, then equal weight to its represented environments, gave 67.3% agreement across decisive replicates and increased mean absolute error by 6.7 percentage points relative to equal shares. Omitting each pair in turn yielded a balanced agreement range of 64.6–71.7%. This is a sensitivity range. Pairs share species and endpoints share competition units.

| Final-day classifier | Correct direction | Rate forecast MAE | Equal-share MAE | Equal-pair and equal-environment agreement |
| --- | ---: | ---: | ---: | ---: |
| Linear discriminant analysis | 125/179 | 36.7 pp | 30.0 pp | 67.3% |
| Random forest | 131/180 | 34.5 pp | 29.4 pp | 70.9% |
| Recursive partitioning | 125/178 | 35.9 pp | 28.3 pp | 66.8% |

## Reproduction

The portable verifier uses Python 3 and its standard library. Download the two original CSV files and place them alongside `verify_algae.py`. The script verifies each archive MD5 checksum and each row’s unique key before writing `algae_attrition.csv` and `algae_validation.csv`. The derivative tables contain aggregate measurements. [Native growth-rate CSV](https://zenodo.org/api/records/1161963/files/Growth%20rate%20raw%20data.csv/content) · [Native competition CSV](https://zenodo.org/api/records/1161963/files/Competition%20data.csv/content) · [Repository metadata with published checksums](https://zenodo.org/api/records/1161963)

```sh
python3 verify_algae.py 'Growth rate raw data.csv' 'Competition data.csv' --out-dir results
```

| File | MD5 |
| --- | --- |
| Growth rate raw data.csv | `afc8b00678c0f107840ac80e6c474fb5` |
| Competition data.csv | `2cefeaabfb4ae74bab41d4c8294a9cc4` |

In `algae_validation.csv`, `mean_share_correct` and `median_share_correct` score direction after summarizing observed fractions within each pair–environment. `balanced_accuracy_pairs_conditions` first averages agreement across decisive replicates within each group, then across groups within a pair, then across pairs. `balanced_mae_rate_minus_half` applies the same weighting to differences in absolute error including ties. Positive values mean larger errors from the rate forecast. MSE gives mean squared fraction error. All proportions and errors in the CSV use the 0–1 scale.

# Sensitivity to uncertain training labels and individual pedigrees

The Kennedy six-class Brier gain retained a positive lower bound under each assignment of its unresolved later training event. For Dowsett, every joint assignment of the two flagged later records yielded a negative lower and positive upper bound. The calculation uses the seven primary pedigrees per study, one pseudocount per class and the same first-window candidate sets as the main analysis. Each record has one assignment across all folds in a scenario. It affects only predictions whose training set contains its pedigree. [Scoring specification](../DESIGN.md)

| Study | Training-label scenarios | Range of seven-pedigree lower endpoints | Range of seven-pedigree upper endpoints |
|---|---:|---:|---:|
| Kennedy | 7 | +0.067871 to +0.072621 | +0.415030 to +0.422023 |
| Dowsett | 49 | −0.395952 to −0.395655 | +0.379954 to +0.380202 |

In Kennedy, V133 in family F has a timing interval of 8–9. Its direction could not be linked uniquely to the source substitution table. We varied its training contribution between omission and each of six classes. In Dowsett, Y6 division 9 contains one blank label, and a Y1 division 3 label printed as C>T disagrees with the reference base at that position. Independently for each we allowed omission or one event in any of the six classes. These deliberately broad scenarios examine sensitivity of the forecast and do not resolve the underlying records. [Kennedy linkage](../kennedy/kennedy_linkage.json) · [Dowsett source audit](../dowsett/dowsett_source.md)

In a separate deletion diagnostic, we kept the original seven Kennedy fold forecasts fixed and removed one scored family at a time from the reported mean. Every remaining six-family lower endpoint was positive, ranging from +0.011215 when D was removed to +0.151018 when H was removed. The full seven-family value was +0.070334. The diagnostic measures individual families’ contributions to this observed score. It supplies neither a sampling interval nor a refit to six families. [All deletion values](results.json)

The program uses the distributed source-derived TSVs and computes Brier loss directly with rational arithmetic. Values in the output are rounded to 12 decimal places. From this directory, run with Python 3.10 or newer.

```sh
python3 check_training_labels.py > /tmp/tmd-training-label-check.json
cmp results.json /tmp/tmd-training-label-check.json
```

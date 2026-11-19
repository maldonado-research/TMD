# Reproduce the selection and dependence analyses

Start in `research/split_selection`. Use Python 3.10 or later. All offline statistical calculations use the standard library. The peach workbook extracts also require openpyxl. The optional figure regeneration uses Matplotlib.

## Replay the reported summaries

```sh
set -eu
python3 -B influence/influence.py | diff - influence/influence_result.json
python3 -B influence/verify_influence.py --previous ../shared_misses/allocation/allocation_profiles.json
python3 -B gate/gate_conditioning.py | diff - gate/gate_result.json
python3 -B gate/verify_gate.py
python3 -B tail/peach_tail.py influence/influence_profiles.json | diff - tail/tail_result.json
python3 -B tail/verify_tail.py influence/influence_profiles.json tail/tail_result.json
python3 -B citrus/replay_citrus.py | diff - citrus/citrus_receipt.json
python3 -B historical/historical_panel.py | diff - historical/historical_result.json
python3 -B historical/verify_historical.py
```

The influence check reproduces all 64 archived allocation profiles. It independently checks eight outside-support comparisons and six optimizations over removed groups. The conditional calculation uses exact fractions. Its verifier enumerates 1,840 small configurations. The tail verifier reconstructs joint distributions that attain the indicated extremes and checks all 64 marginal probabilities at each endpoint. The citrus replay uses published rounded percentages. Its input digest identifies the derived CSV. [Citrus source and extraction limits](citrus/CITRUS.md) · [Branch-marker data and check](historical/HISTORICAL.md)

## Replay the source workbooks and figure

Download Ji et al. Tables S2, S3 and S5 from the upstream article package using the earlier guide. With the paths to those files set, run the following commands. The first joins the site inventory, counts and pair labels. The second independently reconstructs the five-read calculation from Table S3 alone. [Upstream files and download commands](../shared_misses/REPRODUCE.md#replay-ji-et-al-from-their-spreadsheets)

```sh
python3 -B influence/extract_influence.py "$s2" "$s3" "$s5" | diff - influence/influence_profiles.json
python3 -B source/verify_site_screen.py "$s3" | diff - source/screen_receipt.json
python3 -B source/verify_wang_markers.py "$s2" | diff - source/wang_marker_receipt.json
python3 -B gate/gate_figure.py
```

The accompanying search log records the database queries and the time window after the prospective rule was published. The results date from that search. Live indexes can change as deposits arrive. [Search log](WATCH.md)

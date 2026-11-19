# Reproduce the shared-miss analysis

Start in `research/shared_misses` in a checkout of the TMD repository. The aggregate calculations use Python 3.10 or later and its standard library. The read-depth, site-call and pairing extractions also require openpyxl. Regenerating the figure requires Matplotlib.

## Run the saved aggregate calculations

```sh
set -eu
python3 -B depth/depth_scenarios.py | diff - depth/depth_scenarios.json
python3 -B allocation/read_allocation.py | diff - allocation/read_allocation_result.json
python3 -B allocation/verify_read_allocation.py
python3 -B allocation/verify_replication.py
python3 -B dependence/shared_miss_bounds.py | diff - dependence/shared_miss_result.json
python3 -B dependence/verify_shared_miss.py
```

The allocation check enumerates read placements directly in 150 small cases and checks all eight reported summaries. The dependence check constructs the sets of attainable counts for the pooled, by-tissue and by-site restrictions. The figure can be regenerated with `python3 -B depth/depth_figure.py`. [Prospective score, required inputs and interpretation](PREDICTION.md)

## Replay Ji et al. from their spreadsheets

Retrieve Tables S1, S2, S3, S5 and S6 from the original open-access article package. The workbooks are identified by their original byte digests in the extraction scripts. These tables supply anatomical labels, site identities, read counts, categorical calls and reported percentages, respectively. [Article](https://doi.org/10.1371/journal.pgen.1011829) · [Supplement index](https://pmc.ncbi.nlm.nih.gov/articles/PMC12370204/#supplementary-materials)

```sh
ji_dir=$(mktemp -d)
ji_base=https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1
for suffix in 015 016 017 019 020
do
    curl -fsSL "$ji_base/pgen.1011829.s${suffix}.xlsx" -o "$ji_dir/$suffix.xlsx"
done
s1="$ji_dir/015.xlsx"
s2="$ji_dir/016.xlsx"
s3="$ji_dir/017.xlsx"
s5="$ji_dir/019.xlsx"
s6="$ji_dir/020.xlsx"
python3 -B depth/replay_depth.py "$s2" "$s3" "$s5" "$s6" | diff - depth/depth_receipt.json
python3 -B allocation/read_allocation.py --extract "$s2" "$s3" "$s5" | diff - allocation/allocation_profiles.json
python3 -B dependence/replay_site_calls.py "$s2" "$s5" | diff - dependence/site_calls.json
python3 -B alignment/replay_alignment.py "$s1" "$s2" "$s5" | diff - alignment/alignment_receipt.json
python3 -B alignment/verify_alignment.py "$s1" "$s2" "$s5" alignment/alignment_receipt.json
```

The pairing check independently recomputes all four distributions and their means using a subset enumeration. Counts refer to observations in the deposited workbooks. Joint use of the workbooks preserves their shared measurements and preparation history.

## Replay Schmitt et al. from their archived tables

The fruit source note gives the exact candidate-selection and tissue-counting rules, the link to the original ZIP and commands for retrieving four tables with a total compressed transfer under 0.9 MB. The replay checks member hashes before use. A separate SQL calculation verifies both candidate sets and the positive counts for seven species–tissue combinations. [Source note and commands](fruit/SCHMITT_SOURCE.md#replay-the-source) · [Author deposit](https://doi.org/10.5281/zenodo.10089692)

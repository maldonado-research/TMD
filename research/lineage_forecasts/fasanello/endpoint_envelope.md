# Endpoint library sensitivity

Each forecast uses the archived choices at days 0 and 10. The early forecast takes the day-10 leader. The change forecast ranks twice the day-10 fraction minus the day-0 fraction. Each uses the two anonymous labels detected by either forecast visit, or the single detected label if only one was observed. A forecast or endpoint tie earns zero strict hits. Zero-depth or absent rerun endpoints supply no alternate reading.

Delta counts strict hits for change minus strict hits for early. Each well can contribute its delta from either allowed endpoint. The attainable totals are all sums obtained by choosing one allowed reading in each well. This allows arbitrary mixtures across wells. The original and rerun columns choose one library consistently in the eligible group. They retain original endpoints in other wells.
When wells share a sequencing pool, assigning different libraries to those wells can produce a mixture that cannot result from a single pool-level choice.

| Scope | Wells | Original delta | Rerun where allowed | Archive-selected delta | Attainable deltas |
|---|---:|---:|---:|---:|---|
| Wells with complete repeat | 70 | -15 | -1 | -1 | -15, -13, -11, -9, -7, -5, -3, -1 |
| All wells, vary complete repeats | 76 | -12 | 2 | 2 | -12, -10, -8, -6, -4, -2, 0, 2 |
| All wells, vary usable endpoints | 76 | -12 | 0 | 2 | -14, -12, -10, -8, -6, -4, -2, 0, 2 |

6 wells lack a complete repeat at the three visits. The second row keeps their original endpoints. The third row also allows their positive-depth rerun endpoints. These results describe sensitivity to observed measurements. They assign no probability or ground-truth status to either library.

Run from the directory containing this script and the normalized technical count table with `python3 verify_envelope.py technical_counts.tsv --out-dir results`. The JSON gives aggregate scores and all attainable deltas. The per-well TSV gives each library's delta and the minimum and maximum under each choice rule. An empty rerun field means that endpoint had no usable counts.

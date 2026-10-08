# Independent source/design review

These original receipts record internal AI-assisted review, not qualified external review or biological validation. The producer source checker performs 70 identity/anchor checks; source semantics require reading. One reviewer read 47 selected primary paragraphs; the separate source/template reviewer conservatively records 51 (17 PTA,18 PTATO,16 NNK), with 156 plus 56 source/integrity checks. Root read all 56 PTA and 56 NNK paragraphs, and only 25 selected PTATO paragraphs plus lead scan. Raw primary XML, abstract bodies, patient reads and source software remain external.

With authorized cached sources available, run from the parent directory:

```sh
python3 -B verify_cached_sources.py --cache-dir /path/to/authorized/cache --output /tmp/tmd_r21_source_replay.json
sha256sum -c INTEGRATED_SHA256SUMS.txt
```

Missing source caches produce UNRUN, not permission to reacquire or an evidence failure. All 18 planning values and 26 actual study registry fields remain unresolved. The native variant-negative truth check differs from ancestry/episode truth required to assess false new-origin assignments.

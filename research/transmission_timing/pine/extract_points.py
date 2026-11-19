"""Extract phenotype and genotype groups from the pinned vector drawing of Guner et al. Figure 7."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import zlib

SHA = "ade8ac17497ac11a3b8cf6392099a732475fde846cca5659ccb226f152fddd79"
GROUPS = ("WB-10", "WB-20", "Nana")
GENOTYPES = ("A/A", "A/G", "G/G")


def source_stream(path):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != SHA:
        raise ValueError("Unexpected source bytes for the original vector Figure 7")
    content = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            decoded = zlib.decompress(m[1]).decode("latin1")
        except zlib.error:
            continue
        if "(A/A) Tj" in decoded and "(Height " in decoded:
            content.append(decoded)
    if len(content) != 1:
        raise ValueError("Expected exactly one figure content stream")
    return content[0]


def vector_counts(path):
    stream = source_stream(path)
    panel_labels = re.findall(r"Tm \((WB-[0-9]{2}|Nana)\) Tj", stream)
    assert tuple(panel_labels) == GROUPS
    # The tick start coordinates align with the centers of the jittered groups.
    xticks = [float(m) for m in re.findall(r"([\d.]+) 16.35 m\n[\d.]+ 18.84 l\nS", stream)]
    genotypes = re.findall(r"Tm \((A/A|A/G|G/G)\) Tj", stream)
    assert len(xticks) == 9 and xticks == sorted(xticks)
    assert genotypes == list(GENOTYPES)*3
    counts = Counter()
    path_segments, rgb = [], None
    for line in stream.splitlines():
        parts = line.split()
        if not parts:
            continue
        op = parts[-1]
        if op == "scn":
            rgb = tuple(map(float, parts[:3]))
        elif op == "m" and len(parts) == 3:
            path_segments = [(op, tuple(map(float, parts[:2])))]
        elif op == "c" and len(parts) == 7:
            path_segments.append((op, tuple(map(float, parts[:6]))))
        elif op == "B" and len(parts) == 1:
            if [seg for seg, _ in path_segments] != ["m","c","c","c","c"]:
                raise ValueError("Unexpected stroke/fill glyph")
            left,cy = path_segments[0][1]
            center,top = path_segments[1][1][-2:]
            right,cy2 = path_segments[2][1][-2:]
            center2,bot = path_segments[3][1][-2:]
            left2,cy3 = path_segments[4][1][-2:]
            assert abs(center-center2)<.02 and abs(left-left2)<.02 and max(abs(cy-cy2),abs(cy-cy3))<.02
            assert abs(right-left-(top-bot))<.03 and 4.5 < right-left < 4.8
            group = min(range(9),key=lambda j: abs(xticks[j]-center))
            assert abs(xticks[group]-center)<5
            state = {(1.,0.,0.):"dwarf",(.549,.549,.549):"normal"}[rgb]
            counts[(GROUPS[group//3],genotypes[group],state)] += 1
            path_segments = []
    assert sum(counts.values())*4 == len(re.findall(r" c\n",stream))
    total = sum(counts.values())
    return {"source_sha256":SHA,"dots":total,"cells":[
        {"group":group,"genotype":gt,"dwarf":counts[(group,gt,"dwarf")],"normal":counts[(group,gt,"normal")]}
        for group in GROUPS for gt in GENOTYPES]}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("figure",type=Path)
    print(json.dumps(vector_counts(parser.parse_args().figure),indent=2))

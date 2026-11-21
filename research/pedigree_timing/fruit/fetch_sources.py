"""Download three checksum-verified members of the 2023 version-2 Schmitt archive."""
import argparse
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen
import zlib

URL = "https://zenodo.org/api/records/10089692/files/treemutation_save.zip/content"
LENGTH = 4239118097
# Inclusive compressed-payload offsets from the pinned archive ZIP directory and local headers.
MEMBERS = (
    ("treemutation_save/02_mutations/02_filtered/angela.leaf_mutations.tsv.gz", 2439894175, 2441709689,
     "13be8a6566d5dfc7883eb6914db2fa9c2d6e8d9d110e0fd90716e7ab0c7469f4"),
    ("treemutation_save/02_mutations/02_filtered/sixto.leaf_mutations.tsv.gz", 2439550311, 2439893557,
     "93724d2809c111a72a55c67dc0885969e2667ccb22c079b2afffd98db620a3fa"),
    ("treemutation_save/02_mutations/04_fruits/fruit_mutations.tsv.gz", 2446508641, 2446548815,
     "ac860196c362ee608dddffb5883a3cab9db2c5c9a4869dc90be1caca96c7d328"),
)


def fetch(out):
    out.mkdir(parents=True, exist_ok=True)
    for path, start, end, expected in MEMBERS:
        destination = out / Path(path).name
        if destination.exists():
            if hashlib.sha256(destination.read_bytes()).hexdigest() == expected:
                continue
            raise FileExistsError(f"Existing file differs from source: {destination}")
        request = Request(f"{URL}?r={start}_{end}", headers={"Range": f"bytes={start}-{end}"})
        with urlopen(request, timeout=45) as response:
            if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{end}/{LENGTH}":
                raise ValueError("Unexpected archive range. Extract the three members from the original ZIP instead.")
            payload = response.read(end-start+1)
        raw = zlib.decompress(payload, -zlib.MAX_WBITS)
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"Archive member changed: {path}")
        destination.write_bytes(raw)
        print(destination.name, expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    fetch(parser.parse_args().destination)

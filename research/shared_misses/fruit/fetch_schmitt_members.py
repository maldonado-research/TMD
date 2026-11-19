"""Fetch four authenticated gzip tables by range from the authors' version-2 ZIP."""
import argparse
import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
import zlib

from replay_schmitt import MEMBERS

URL = "https://zenodo.org/records/10089692/files/treemutation_save.zip"
ARCHIVE_BYTES = 4239118097
# Compressed member payloads. Offsets and lengths from the original ZIP headers.
RANGES = {
    "D_leaves": (2438721210, 688218),
    "S_leaves": (2439409945, 136700),
    "D_list": (2439546806, 3357),
    "fruit": (2446508641, 40175),
}


def fetch(directory):
    directory.mkdir(parents=True, exist_ok=True)
    for key, (start, length) in RANGES.items():
        name, digest = MEMBERS[key]
        path = directory / Path(name).name
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Existing file {path} differs from the published member.")
            continue
        stop = start + length - 1
        req = Request(f"{URL}?download=1&member_offset={start}", headers={"Range": f"bytes={start}-{stop}"})
        with urlopen(req, timeout=45) as response:
            if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{stop}/{ARCHIVE_BYTES}":
                raise ValueError("Server did not return the expected range of this archive version.")
            data = response.read(length + 1)
        if len(data) != length:
            raise ValueError("Truncated or oversized range.")
        member = zlib.decompress(data, -15)
        if hashlib.sha256(member).hexdigest() != digest:
            raise ValueError(f"Checksum differs for {path.name}")
        with TemporaryDirectory(dir=directory) as staging:
            staged = Path(staging) / path.name
            staged.write_bytes(member)
            # Link only the completed file. A concurrent fetch may have finished first.
            try:
                os.link(staged, path)
            except FileExistsError:
                if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    raise ValueError(f"Concurrent file {path} differs from the published member.")
        print(f"{path.name}  {len(member)} bytes")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    fetch(p.parse_args().directory)

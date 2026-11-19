"""Compare decoded cell values in both public copies without exporting source records."""
import hashlib
import json
from pathlib import Path
import sys
from openpyxl import load_workbook

SOURCES = {
    'figshare': ('https://doi.org/10.6084/m9.figshare.28340420.v1',
                 '48f769eb2b49fb02e5a468a0c991d70557848fb79b99629cbd5683233bfbb328'),
    'publisher': ('https://pmc-oa-opendata.s3.amazonaws.com/PMC11847636.1/EMI-27-e70061-s001.xlsx',
                  '19b7352e4a82f93c468a2ab752fa24cfe478e0c05b4d7502cb5c7019a7a0b90c'),
}


def compare(original, publisher):
    receipt = {'sources': {}, 'sheet_values_equal': {}}
    for key, path in [('figshare', original), ('publisher', publisher)]:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        url, expected_digest = SOURCES[key]
        if digest != expected_digest:
            raise ValueError(f'Unexpected {key} supplement digest')
        receipt['sources'][key] = {'url': url, 'bytes': len(raw), 'sha256': digest}
    left = load_workbook(original, read_only=True, data_only=True)
    right = load_workbook(publisher, read_only=True, data_only=True)
    try:
        if left.sheetnames != right.sheetnames:
            raise ValueError('Workbook sheets differ')
        for name in left.sheetnames:
            if list(left[name].values) != list(right[name].values):
                raise ValueError(f'Decoded values differ on sheet {name!r}')
            receipt['sheet_values_equal'][name] = True
    finally:
        left.close()
        right.close()
    return receipt


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: compare_howells_sources.py FIGSHARE.xlsx PUBLISHER.xlsx')
    print(json.dumps(compare(Path(sys.argv[1]), Path(sys.argv[2])), indent=2))

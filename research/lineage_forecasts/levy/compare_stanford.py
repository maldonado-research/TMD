"""Compare a course row, identifier and each count to the primary E1 source."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(course, primary):
    rows = 0
    with course.open(newline='') as left, primary.open(newline='') as right:
        cr = csv.reader(left, skipinitialspace=True)
        pr = (row for row in csv.reader(right) if row)
        ch, ph = next(cr), next(pr)
        if ch[0] != 'Barcode ID' or ch[1:] != ['Reads at ' + name for name in ph]:
            raise ValueError('Source headers do not agree')
        for index, (c, p) in enumerate(itertools.zip_longest(cr, pr), 1):
            if c is None or p is None or int(c[0]) != index or len(p) != len(ph) or list(map(int,c[1:])) != list(map(int,p)):
                raise ValueError(f'Difference at course data row {index}')
            rows = index
    return {'course_sha256': digest(course), 'primary_sha256': digest(primary), 'visit_headers': ph, 'rows_equal': rows, 'counts_equal': rows * len(ph), 'course_id_equals_one_based_primary_data_row_all': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('course_csv', type=Path)
    parser.add_argument('primary_e1_csv', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.course_csv, args.primary_e1_csv), indent=2))

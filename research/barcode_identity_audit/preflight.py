"""Check explicitly keyed table structure; never certify biological identities."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import sys

KEY_FIELDS = ('experiment', 'population', 'barcode')
RESULT_FIELDS = set(KEY_FIELDS) | {'row_id', 'row_role', 'fitness'}
ANNOTATION_FIELDS = set(KEY_FIELDS) | {'cnv_annotation'}
ROLES = {'individual', 'aggregate', 'padding'}
NUMBER = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')


class StructuralError(ValueError):
    """An explicit structural contract was violated."""


def _text(value, field):
    if not isinstance(value, str) or not value or value != value.strip() or not value.isprintable():
        raise StructuralError(f'{field} must be a nonempty, unmodified printable string')
    return value


def _key(row):
    return tuple(_text(row[k], k) for k in KEY_FIELDS)


def _fitness(value):
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise StructuralError('fitness must be an explicit finite decimal string')
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError):
        raise StructuralError('fitness must be an explicit finite decimal string') from None
    if not result.is_finite():
        raise StructuralError('fitness must be finite')
    return result


def _rows(rows, name):
    if not isinstance(rows, list):
        raise StructuralError(f'{name} must be a list of row objects')
    return rows


def audit_tables(result_rows, annotation_rows):
    """Return a deterministic structure report, or reject ambiguous structure.

    Keys and row roles must already be supplied by an externally justified
    identity/row-role record. This function cannot create or authenticate it.
    Numeric result arrays plus an equally long barcode vector are unsupported.
    """
    results = _rows(result_rows, 'result_rows')
    annotations = _rows(annotation_rows, 'annotation_rows')
    if not results:
        raise StructuralError('result_rows must not be empty')
    row_ids, individuals, excluded = set(), {}, []
    roles = Counter({role: 0 for role in sorted(ROLES)})
    for row in results:
        if not isinstance(row, dict) or set(row) != RESULT_FIELDS:
            raise StructuralError('each result row must have exactly the declared result fields')
        row_id = _text(row['row_id'], 'row_id')
        if row_id in row_ids:
            raise StructuralError('duplicate result row_id')
        row_ids.add(row_id)
        role = row['row_role']
        if not isinstance(role, str) or role not in ROLES:
            raise StructuralError('row_role must explicitly be individual, aggregate or padding')
        roles[role] += 1
        _text(row['experiment'], 'experiment')
        _text(row['population'], 'population')
        if role != 'individual':
            # Do not decide that zero, the last row, or a missing barcode is padding.
            if row['barcode'] is not None or row['fitness'] is not None:
                raise StructuralError('excluded rows must use null barcode and fitness in this normalized contract')
            excluded.append({'row_id': row_id, 'row_role': role,
                             'experiment': row['experiment'], 'population': row['population']})
            continue
        key = _key(row)
        if key in individuals:
            raise StructuralError('duplicate individual composite key')
        estimate = _fitness(row['fitness'])
        individuals[key] = {'row_id': row_id, 'fitness': row['fitness'],
                            'positive_numeric_estimate': estimate > 0}
    if not individuals:
        raise StructuralError('at least one explicitly individual row is required')
    calls = {}
    for row in annotations:
        if not isinstance(row, dict) or set(row) != ANNOTATION_FIELDS:
            raise StructuralError('each annotation row must have exactly the declared annotation fields')
        key = _key(row)
        if key in calls:
            raise StructuralError('duplicate annotation composite key')
        if row['cnv_annotation'] not in ('CNV', 'noCNV'):
            raise StructuralError('cnv_annotation must explicitly be CNV or noCNV')
        calls[key] = row['cnv_annotation']
    joined, unknown = [], 0
    for key in sorted(individuals):
        label = calls.get(key)
        if label is None:
            unknown += 1
        joined.append({**dict(zip(KEY_FIELDS, key)), **individuals[key],
                       'source_cnv_annotation': label,
                       'annotation_status': 'unmatched_unknown' if label is None else 'source_annotation_present'})
    orphans = [{**dict(zip(KEY_FIELDS, key)), 'source_cnv_annotation': calls[key]}
               for key in sorted(set(calls) - set(individuals))]
    assert len(joined) + len(excluded) == len(results)
    return {
        'schema_version': 1,
        'status': 'STRUCTURAL_CHECKS_PASSED',
        'result_rows': len(results), 'individual_rows': len(joined),
        'explicit_row_roles': dict(sorted(roles.items())),
        'matched_individual_rows': len(joined) - unknown,
        'unmatched_individual_rows_kept_unknown': unknown,
        'annotation_rows': len(annotations), 'orphan_annotation_rows': len(orphans),
        'individual_records': joined,
        'explicitly_excluded_rows': sorted(excluded, key=lambda row: row['row_id']),
        'orphan_annotations': orphans,
        'biological_lineage_identity_verified': False,
        'source_row_binding_and_role_provenance_verified': False,
        'genotype_negative_truth_verified': False,
        'clock_units_verified': False, 'source_execution_verified': False,
        'native_measurement_admitted': False,
        'scope': 'Supplied keys, roles and labels checked structurally only. No positional binding, alias conversion, automatic filtering or biological validation.'
    }


def _unique_json_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise StructuralError('duplicate JSON object member')
        obj[key] = value
    return obj


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print('Usage: python preflight.py INPUT.json', file=sys.stderr)
        return 2
    try:
        raw = Path(args[0]).read_bytes()
        payload = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_json_object)
        if not isinstance(payload, dict) or set(payload) != {'result_rows', 'annotation_rows'}:
            raise StructuralError('input must have exactly result_rows and annotation_rows')
        report = audit_tables(payload['result_rows'], payload['annotation_rows'])
        report['input_JSON_bytes'] = len(raw)
        report['input_JSON_sha256'] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({'status': 'REJECTED', 'error': str(exc),
                          'native_measurement_admitted': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

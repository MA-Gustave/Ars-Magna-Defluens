"""Candidate-only FR/EN qualification; no PGF compilation or publishing."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from console.core import Settings
from console.semantik import SemantikClient
from console.qualification import CoreQualification, qualification_name, write_qualification


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Defluens v0.11 bilingual qualification (not a release)')
    parser.add_argument('--real', action='store_true', help='Require WordBench-built FR and EN locked PGFs')
    parser.add_argument('--output-dir', type=Path, help='Write new immutable JSON/TSV evidence to this folder')
    args = parser.parse_args(argv)
    paths = Settings().paths
    directory = args.output_dir or (Path(paths['reports']).parent / 'core_qualification')
    try:
        report = CoreQualification(SemantikClient(paths)).run('real' if args.real else 'structural')
        json_path, review_path = write_qualification(report, directory / qualification_name(report))
        print(json.dumps({'status': report['status'], 'totals': report['totals'],
                          'report_path': str(json_path), 'review_path': str(review_path),
                          'released': False, 'linguistically_certified': False},
                         ensure_ascii=False, indent=2))
        return 0 if report['structural_passed'] and (not args.real or report['real_gf_candidate_passed']) else 2
    except (RuntimeError, OSError, ValueError) as exc:
        print(json.dumps({'status':'BLOCKED', 'error':str(exc), 'released':False},
                         ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

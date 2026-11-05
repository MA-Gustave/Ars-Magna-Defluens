"""Windows/local command-line launcher for Defluens FR/EN acceptance v0.10.

Run from the repository root: python tools/recette_core_v010.py [--real]
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from console.core import Settings
from console.semantik import SemantikClient
from console.acceptance import CoreAcceptance, report_name, save_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Defluens FR/EN bounded candidate acceptance (not a release)')
    parser.add_argument('--real', action='store_true', help='Require real locked candidate PGFs and run GF through SemantiK')
    parser.add_argument('--output-dir', type=Path, help='Existing/new directory for immutable JSON reports')
    args = parser.parse_args(argv)
    paths = Settings().paths
    dest = args.output_dir or (Path(paths['reports']).parent / 'core_acceptance')
    try:
        report = CoreAcceptance(SemantikClient(paths)).run('real' if args.real else 'structural')
        target = save_report(report, dest / report_name(report))
        print(json.dumps({'status':report['status'], 'totals':report['totals'],
                          'report_path':str(target),'released':False}, ensure_ascii=False, indent=2))
        return 0 if report['structural_passed'] and (not args.real or report['real_gf_candidate_passed']) else 2
    except (RuntimeError, ValueError, OSError) as exc:
        print(json.dumps({'status':'BLOCKED', 'error':str(exc), 'released':False},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())

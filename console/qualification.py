"""v0.11: bilingual real-GF qualification evidence, explicitly NOT certification.

SemantiK owns all semantic mapping, planning, lexical binding and GF work.
WordBench owns all PGF compilation. Defluens only checks correspondence,
integrity and outputs of those public contracts; no sentence templates exist here.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .acceptance import CoreAcceptance, acceptance_matrix, save_report
from .semantik import CORE_LANGUAGES, SemantikClient


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':')).encode('utf-8')


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _result_failure(result: dict, request: dict, runtime: str, language: str) -> str | None:
    """Independent structural checks on an *upstream* GF output (not a text oracle)."""
    if not isinstance(result, dict):
        return 'No structured GF communication result'
    obligations = request['obligations']
    count = len(obligations)
    rid = result.get('runtime') or {}
    if (result.get('language') != language
        or result.get('locale') != request.get('context', {}).get('target_locale')
        or not isinstance(rid, dict)
        or rid.get('runtime_set_id') != runtime
        or rid.get('capability_profile') != runtime):
        return 'Runtime, locale or language identity mismatch'
    blocks = result.get('blocks')
    coverage = result.get('coverage')
    if not isinstance(blocks, list) or not isinstance(coverage, list):
        return 'GF blocks or coverage missing'
    if len(blocks) != count or len(coverage) != count:
        return 'GF block or obligation count mismatch'
    text_parts = []
    for i, (block, item) in enumerate(zip(blocks, obligations), 1):
        if not isinstance(block, dict):
            return 'Invalid GF block'
        if (block.get('block_id') != f'b{i}' or block.get('kind') != 'utterance'
            or block.get('obligation_ids') != [item['obligation_id']]
            or not isinstance(block.get('text'), str) or not block['text'].strip()):
            return f'Block {i} does not discharge the expected obligation'
        text_parts.append(block['text'])
    if result.get('plain_text') != '\n'.join(text_parts):
        return 'Plain-text reconstruction or order mismatch'
    observed = set()
    for i, (entry, obligation) in enumerate(zip(coverage, obligations), 1):
        if not isinstance(entry, dict):
            return 'Invalid coverage entry'
        oid = entry.get('obligation_id')
        if (oid in observed or oid != obligation['obligation_id']
            or entry.get('block_ids') != [f'b{i}']
            or not isinstance(entry.get('realization_unit_ids'), list)
            or not entry['realization_unit_ids']
            or any(not isinstance(x, str) or not x for x in entry['realization_unit_ids'])):
            return f'Incomplete, duplicated or reordered coverage at obligation {i}'
        observed.add(oid)
    did = result.get('deterministic_result_id')
    comparable = {k:v for k,v in result.items() if k not in ('deterministic_result_id', 'operational')}
    if did != 'sha256:' + _sha(comparable):
        return 'Deterministic output hash mismatch'
    return None


def _preview_failure(result: Any, runtime: str, status: dict) -> str | None:
    if not isinstance(result, dict):
        return 'No upstream batch result'
    if (result.get('schema_id') != 'semantik.candidate-preview-batch'
        or result.get('status') != 'CANDIDATE_PREVIEW_BATCH'
        or result.get('runtime_set_id') != runtime
        or result.get('candidate_only') is not True
        or result.get('released') is not False
        or result.get('activated') is not False
        or result.get('linguistically_certified') is not False):
        return 'Unexpected or published-looking candidate batch envelope'
    if (not isinstance(result.get('pgf_sha256'), str)
        or len(result['pgf_sha256']) != 64
        or result.get('pgf_sha256') != status.get('pgf_sha256')
        or not isinstance(result.get('pipeline_lock_sha256'), str)
        or result.get('pipeline_lock_sha256') != status.get('pipeline_lock_sha256')):
        return 'Candidate hash or WordBench lock changed during realization'
    return None


def _matches(rows: Any, expected_ids: set[str]) -> bool:
    return (isinstance(rows, list) and len(rows) == len(expected_ids)
            and all(isinstance(row, dict) and isinstance(row.get('case_id'), str) for row in rows)
            and {row['case_id'] for row in rows} == expected_ids)


class CoreQualification:
    """Orchestrate audited FR/EN candidate preview; do not certify morphology."""

    def __init__(self, client: SemantikClient):
        self.client = client

    def run(self, mode: str = 'structural') -> dict:
        if mode not in ('structural', 'real'):
            raise ValueError('Qualification mode must be structural or real')
        # Reuse v0.10's 36 checks, unmodified. They call the public SA batch
        # validator and check canonical obligation identities and ordering.
        base = CoreAcceptance(self.client).run('structural', include_canonical=True)
        requests = base.pop('_canonical_requests')
        positive = base.pop('_recipes')
        cases = [dict(x) for x in base['cases']]
        cases_by_id = {x['case_id']: x for x in cases}
        for item in positive:
            key = item['case_id']
            req = requests.get(key)
            expected = CORE_LANGUAGES[item['language']]
            if (not isinstance(req, dict)
                    or req.get('capability_profile') != expected
                    or req.get('runtime_selector', {}).get('runtime_set_id') != expected):
                cases_by_id[key].update(status='FAILED', semantic_validated=False,
                                        error='Canonical candidate profile missing or mismatched')
                continue
            cases_by_id[key]['semantic_fingerprint'] = _sha({
                field: req.get(field) for field in
                ('semantic_graph', 'obligations', 'supporting_context', 'constraints')})
            cases_by_id[key]['intents'] = [x['intent'] for x in item['recipe']['items']]

        parity = []
        for fr in (x for x in positive if x['language'] == 'fr'):
            key_fr = fr['case_id']
            key_en = 'en:' + key_fr.split(':', 1)[1]
            f, e = cases_by_id[key_fr], cases_by_id[key_en]
            ok = (f['semantic_validated'] and e['semantic_validated']
                  and f.get('semantic_fingerprint') == e.get('semantic_fingerprint'))
            parity.append({'case_fr': key_fr, 'case_en': key_en,
                           'equivalent': bool(ok)})
            if not ok:
                for row in (f, e):
                    row.update(status='FAILED', semantic_validated=False,
                               error='FR/EN semantic graph or obligation parity mismatch')

        statuses = self.client.core_status().get('languages', {}) if mode == 'real' else {}
        if mode == 'real':
            for lang, runtime in CORE_LANGUAGES.items():
                eligible = [x for x in positive if x['language'] == lang
                            and cases_by_id[x['case_id']]['semantic_validated']]
                status = statuses.get(lang, {})
                if not status.get('ready'):
                    for x in eligible:
                        cases_by_id[x['case_id']].update(status='BLOCKED_PGF',
                            error='WordBench PGF candidate missing or integrity check failed')
                    continue
                batch_vectors = [{'case_id': x['case_id'], 'request': requests[x['case_id']]}
                                 for x in eligible]
                if not batch_vectors:
                    continue
                result = self.client.preview_candidate_batch(batch_vectors, runtime)
                outcome = result.get('result') if result.get('ok') else None
                failure = _preview_failure(outcome, runtime, status)
                if failure is None and not _matches(outcome.get('results'),
                                                    {x['case_id'] for x in eligible}):
                    failure = 'Incomplete, duplicated or reordered upstream GF batch'
                if failure:
                    for x in eligible:
                        cases_by_id[x['case_id']].update(status='FAILED', error=failure)
                    continue
                by_id = {x['case_id']: x for x in outcome['results']}
                for x in eligible:
                    key = x['case_id']
                    row = cases_by_id[key]
                    output = by_id[key]
                    if not output.get('ok'):
                        row.update(status='FAILED', error=str(output.get('error','GF candidate refused'))[:1000])
                        continue
                    candidate_result = output.get('communication_result')
                    problem = _result_failure(candidate_result, requests[key], runtime, lang)
                    if problem:
                        row.update(status='FAILED', error=problem)
                        continue
                    row.update(status='GF_CANDIDATE_PASS', gf_executed=True,
                               candidate_text=candidate_result['plain_text'],
                               deterministic_result_id=candidate_result['deterministic_result_id'],
                               pgf_sha256=outcome['pgf_sha256'],
                               pipeline_lock_sha256=outcome['pipeline_lock_sha256'],
                               human_review='PENDING')

        failed = sum(x['status'] == 'FAILED' for x in cases)
        blocked = sum(x['status'] == 'BLOCKED_PGF' for x in cases)
        gf_verified = sum(x.get('gf_executed') is True for x in cases)
        structural_ok = (base['structural_passed'] and all(p['equivalent'] for p in parity)
                         and all(x.get('semantic_validated') or x['kind'] == 'forbidden'
                                 for x in cases))
        candidate_pass = mode == 'real' and structural_ok and gf_verified == len(positive)
        status = ('FAILED' if failed or not structural_ok else 'BLOCKED_PGF' if blocked
                  else 'REAL_GF_CANDIDATE_PASS' if candidate_pass else 'STRUCTURAL_PASS_ONLY')
        return {
            'schema_id':'defluens.core-qualification-report', 'schema_version':'1.0',
            'product_version':'0.11.0', 'generated_utc':datetime.now(timezone.utc).isoformat(),
            'mode':mode, 'status':status, 'catalog_sha256':base['catalog_sha256'],
            'matrix_sha256':base['matrix_sha256'], 'structural_passed':structural_ok,
            'cross_language_parity_passed':all(x['equivalent'] for x in parity),
            'parity_pairs':parity, 'real_gf_candidate_passed':candidate_pass,
            'linguistically_certified':False, 'released':False, 'activated':False,
            'totals':{'authorized':len(positive), 'expected_rejections':8,
                      'parity_pairs':len(parity),
                      'structurally_validated':sum(x.get('semantic_validated') is True for x in cases),
                      'gf_candidates_verified':gf_verified, 'blocked_pgf':blocked,
                      'failed':failed, 'human_reviews_completed':0},
            'candidate_status':statuses, 'cases':cases,
            'not_yet_qualified':['condition-real','conditional-instruction'],
            'notice':'Candidate evidence only; human linguistic review still required. '
                     'Conditional intents are not in the six-operation GF profile. '
                     'No RuntimeSet release or activation.'
        }


def qualification_name(report: dict) -> str:
    suffix = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return f'defluens-v011-{report["mode"]}-{suffix}.json'


def write_qualification(report: dict, output_path: Path) -> tuple[Path, Path]:
    """JSON and UTF-8 TSV review sheet, append-only; never declare human approval."""
    output_path = Path(output_path)
    review_path = output_path.with_suffix('.review.tsv')
    if output_path.exists() or review_path.exists():
        raise FileExistsError('Qualification artifact name already exists')
    save_report(report, output_path)
    fields = ['case_id', 'language', 'intents', 'status', 'candidate_text',
              'pgf_sha256', 'deterministic_result_id', 'human_review', 'reviewer_notes']
    # UTF-8 with BOM for Excel/Windows. No free-form text is passed to a shell.
    with review_path.open('x', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter='\t')
        writer.writeheader()
        for case in report['cases']:
            if case['kind'] != 'authorized':
                continue
            row = {name: case.get(name, '') for name in fields}
            row['intents'] = ', '.join(case.get('intents', []))
            row['human_review'] = 'PENDING' if case['gf_executed'] else 'NOT_APPLICABLE'
            # Protect spreadsheet viewers against formula injection in GF output.
            for name in ('candidate_text', 'intents', 'case_id'):
                value = str(row[name])
                if value.lstrip().startswith(('=', '+', '-', '@')):
                    row[name] = "'" + value
            writer.writerow(row)
    return output_path, review_path

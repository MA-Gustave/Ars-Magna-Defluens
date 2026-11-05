"""v0.10: bounded bilingual acceptance *orchestration*, not a language engine.

All semantic requests and their validation come from SemantiK public CLI.
All GF results, when asked for, come from SemantiK's existing locked candidate
adapter; no sentence is synthesized here and no RuntimeSet is published.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .semantik import CORE_LANGUAGES, SemantikClient

EXPECTED_OPERATIONS = {
    'attribute': 'clause.copular_attribute',
    'classification': 'clause.copular_classification',
    'event': 'clause.intransitive_event',
    'transitive': 'clause.transitive_event',
    'location': 'clause.locative',
    'directive': 'directive.action',
}


def _row(catalog: dict, intent: str, *, negative: bool = False) -> dict:
    spec = catalog['intents'][intent]
    choices = spec['options']
    row = {'intent': intent, 'concept': choices[-1] if negative else choices[0],
           'polarity': 'negative' if negative else 'positive'}
    if spec.get('requires_subject', True):
        row['subject'] = 'noa' if negative else 'mira'
    if spec.get('requires_object', False):
        row['object'] = catalog['objects'][-1] if negative else catalog['objects'][0]
    if spec.get('supports_tense', True):
        row['tense'] = 'future' if negative else 'past'
    return row


def acceptance_matrix(catalog: dict) -> tuple[list[dict], list[dict]]:
    """24 individual + 4 composed positive vectors; 8 forbidden recipes.

    This matrix is a *test input* generator, never a lexical/GF planner.
    All vocabulary is read from the canonical SemantiK catalog.
    """
    if not isinstance(catalog, dict) or not isinstance(catalog.get('intents'), dict):
        raise ValueError('SemantiK catalog is not a valid object')
    for intent, operation in EXPECTED_OPERATIONS.items():
        if (not isinstance(catalog['intents'].get(intent), dict)
                or catalog['intents'][intent].get('operation') != operation
                or not isinstance(catalog['intents'][intent].get('options'), list)
                or not catalog['intents'][intent]['options']):
            raise ValueError(f'Core catalog missing expected semantic operation: {intent}')
    if not all(catalog.get(key) for key in ('subjects', 'objects', 'tenses', 'polarities')):
        raise ValueError('Incomplete bounded SemantiK vocabulary')
    if not all(x in catalog['polarities'] for x in ('positive', 'negative')):
        raise ValueError('Missing polarity variation in SemantiK catalog')
    if not all(x in catalog['tenses'] for x in ('past', 'future')):
        raise ValueError('Missing past/future variation in SemantiK catalog')
    if not all(x in catalog.get('languages', {}) for x in CORE_LANGUAGES):
        raise ValueError('Bilingual profiles missing from SemantiK catalog')

    positive, rejected = [], []
    for lang in CORE_LANGUAGES:
        for intent in EXPECTED_OPERATIONS:
            for variant in (False, True):
                key = 'negative' if variant else 'positive'
                positive.append({'case_id': f'{lang}:{intent}:{key}', 'language': lang,
                                 'recipe': {'language': lang, 'items': [_row(catalog, intent, negative=variant)]}})
        trio = [_row(catalog, name, negative=i == 1)
                for i, name in enumerate(('attribute', 'transitive', 'directive'))]
        eight = [_row(catalog, name, negative=i % 2 == 1) for i, name in enumerate(
            ('attribute', 'classification', 'event', 'transitive', 'location', 'directive', 'event', 'location'))]
        for name, rows in (('composition-3', trio), ('composition-8', eight)):
            positive.append({'case_id': f'{lang}:{name}', 'language': lang,
                             'recipe': {'language': lang, 'items': rows}})
        invalid = [
            ('unknown-intent', {'intent': 'invented', 'concept': 'work', 'subject': 'mira'}),
            ('unknown-concept', {'intent': 'attribute', 'concept': '__not_in_catalog__', 'subject': 'mira'}),
            ('missing-patient', {'intent': 'transitive', 'concept': catalog['intents']['transitive']['options'][0], 'subject': 'mira'}),
            ('directive-past', {'intent': 'directive', 'concept': catalog['intents']['directive']['options'][0], 'tense': 'past'}),
        ]
        for name, row in invalid:
            rejected.append({'case_id': f'{lang}:reject:{name}', 'language': lang,
                             'recipe': {'language': lang, 'items': [row]}})
    return positive, rejected


class CoreAcceptance:
    def __init__(self, client: SemantikClient):
        self.client = client

    def run(self, mode: str = 'structural', *, include_canonical: bool = False) -> dict[str, Any]:
        """Run 36 fixed checks; real mode never fabricates a missing PGF.

        The structural mode can run without GF and is never described as a GF
        success. The real mode requires an independently built, hash-locked
        WordBench candidate for each language.
        """
        if mode not in ('structural', 'real'):
            raise ValueError('Audit mode must be structural or real')
        returned = self.client.core_catalog()
        if not returned.get('ok') or not isinstance(returned.get('result'), dict):
            raise RuntimeError('Cannot obtain canonical catalog from SemantiK public CLI')
        positive, rejected = acceptance_matrix(returned['result'])
        canonical=lambda obj: json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
        catalog_hash=hashlib.sha256(canonical(returned['result'])).hexdigest()
        matrix_hash=hashlib.sha256(canonical(positive+rejected)).hexdigest()
        batch=self.client.core_batch([{'case_id':v['case_id'],'recipe':v['recipe']} for v in positive+rejected])
        if (not batch.get('ok') or not isinstance(batch.get('result'),dict)
                or batch['result'].get('schema_id') != 'semantik.defluens-core-batch'):
            raise RuntimeError('SemantiK public batch validator unavailable or failed')
        rows=batch['result'].get('results')
        expected_ids={v['case_id'] for v in positive+rejected}
        if (not isinstance(rows,list) or len(rows)!=len(expected_ids)
                or any(not isinstance(x,dict) for x in rows)
                or {x.get('case_id') for x in rows} != expected_ids):
            raise RuntimeError('SemantiK returned incomplete or inconsistent core batch')
        by_id={x['case_id']:x for x in rows}
        statuses = self.client.core_status()['languages'] if mode == 'real' else {}
        cases: list[dict[str, Any]] = []
        for vector in positive:
            lang = vector['language']
            recipe = vector['recipe']
            case = {'case_id': vector['case_id'], 'language': lang,
                    'kind': 'authorized', 'status': 'FAILED',
                    'semantic_validated': False, 'gf_executed': False}
            cases.append(case)
            mapped = by_id[vector['case_id']]
            request = mapped.get('request')
            if not mapped.get('ok') or mapped.get('validated') is not True or not isinstance(request, dict):
                case['error'] = 'SemantiK request mapping refused the expected valid vector'
                continue
            expected_id = CORE_LANGUAGES[lang]
            statements = request.get('semantic_graph', {}).get('statements', [])
            obligations = request.get('obligations', [])
            count = len(recipe['items'])
            # Invariants are checked independently of the generation adapter's
            # implementation. GF surface and grammatical semantics remain upstream.
            if (request.get('capability_profile') != expected_id
                or request.get('runtime_selector', {}).get('runtime_set_id') != expected_id
                or request.get('context', {}).get('target_language') != lang
                or len(statements) != count or len(obligations) != count
                or [x.get('id') for x in statements] != [f's{i}' for i in range(1, count + 1)]
                or [x.get('obligation_id') for x in obligations] != [f'o{i}' for i in range(1, count + 1)]
                or any(x.get('semantic_refs') != [f's{i}'] or x.get('ordering') != 'FIXED'
                       for i, x in enumerate(obligations, 1))
                or any(x.get('polarity') != item['polarity'] for x, item in zip(statements, recipe['items']))):
                case['error'] = 'Canonical identity, polarity, ordering or obligations invariant broken'
                continue
            case['semantic_validated'] = True
            case['request_id'] = request.get('request_id')
            case['statement_count'] = count
            if mode == 'structural':
                case['status'] = 'STRUCTURAL_PASS'
                continue
            state = statuses.get(lang, {})
            if not state.get('ready'):
                case['status'] = 'BLOCKED_PGF'
                case['error'] = 'No integrity-checked WordBench PGF candidate for ' + lang
                continue
            candidate = self.client.preview_candidate(request, expected_id)
            if not candidate.get('ok'):
                case['error'] = 'SemantiK candidate GF realization failed'
                case['upstream'] = candidate.get('result') or candidate.get('status')
                continue
            result = candidate.get('result', {})
            communication = result.get('communication_result', {}) if isinstance(result, dict) else {}
            expected_obligations = {x['obligation_id'] for x in obligations}
            coverage = communication.get('coverage') if isinstance(communication, dict) else None
            actual_obligations = {x.get('obligation_id') for x in coverage} if isinstance(coverage, list) else set()
            if (result.get('status') != 'CANDIDATE_PREVIEW'
                or result.get('released') is not False or result.get('activated') is not False
                or communication.get('runtime', {}).get('runtime_set_id') != expected_id
                or not isinstance(communication.get('plain_text'), str)
                or not communication['plain_text'].strip()
                or expected_obligations != actual_obligations):
                case['error'] = 'Candidate output lacks correct identity, coverage or source status'
                continue
            case['gf_executed'] = True
            case['status'] = 'GF_CANDIDATE_PASS'
            case['candidate_text'] = communication['plain_text']
        for vector in rejected:
            refused = by_id[vector['case_id']]
            cases.append({'case_id': vector['case_id'], 'language': vector['language'],
                          'kind': 'forbidden', 'status': 'EXPECTED_REJECTION' if refused.get('ok') is False else 'FAILED',
                          'semantic_validated': False, 'gf_executed': False,
                          **({'error':'SemantiK accepted an unauthorized semantic recipe'} if refused.get('ok') is True else {})})
        structural_ok = all(
            (case['semantic_validated'] if case['kind'] == 'authorized' else case['status'] == 'EXPECTED_REJECTION')
            for case in cases
        )
        real_ok = mode == 'real' and structural_ok and all(
            case['status'] == 'GF_CANDIDATE_PASS' for case in cases if case['kind'] == 'authorized'
        )
        blocked = sum(case['status'] == 'BLOCKED_PGF' for case in cases)
        failed = sum(case['status'] == 'FAILED' for case in cases)
        status = ('STRUCTURAL_PASS_ONLY' if structural_ok else 'FAILED') if mode == 'structural' else (
            'REAL_GF_CANDIDATE_PASS' if real_ok else 'FAILED' if failed else 'BLOCKED_PGF')
        report = {'schema_id':'defluens.core-acceptance-report', 'schema_version':'1.0',
                'product_version':'0.10.0', 'mode': mode, 'status': status,
                'generated_utc':datetime.now(timezone.utc).isoformat(),
                'catalog_sha256':catalog_hash, 'matrix_sha256':matrix_hash,
                'structural_passed': structural_ok, 'real_gf_candidate_passed': real_ok,
                'released': False, 'activated': False, 'linguistically_certified': False,
                'totals': {'authorized': len(positive), 'expected_rejections': len(rejected),
                           'structurally_validated': sum(x['semantic_validated'] for x in cases),
                           'gf_candidates_verified': sum(x['gf_executed'] for x in cases),
                           'blocked_pgf': blocked, 'failed': failed},
                'candidate_status': statuses, 'cases': cases,
                'notice':'Development evidence only. Real GF success does not certify linguistic correctness or release a RuntimeSet.'}
        if include_canonical:
            # Internal reuse by v0.11 only: prevent a second SA catalog/batch roundtrip.
            # The public v0.10 JSON report remains unchanged by default.
            report['_canonical_requests'] = {key: by_id[key].get('request') for key in
                                             (v['case_id'] for v in positive)}
            report['_recipes'] = positive
        return report


def save_report(report: dict, path: Path) -> Path:
    """Write a new immutable report; never overwrite an earlier audit."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError('Audit report already exists: ' + str(path))
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True).encode('utf-8') + b'\n'
    # Collision is forbidden, including concurrent attempts.
    with path.open('xb') as stream:
        stream.write(payload)
    return path


def report_name(report: dict) -> str:
    now = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    return f"defluens-v010-{report['mode']}-{now}.json"

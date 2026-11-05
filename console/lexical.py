"""Defluens lexical coordination: public diK/WordBench/SA CLI, never lexical authority.

Local, user-triggered operations; immutable outputs go to Downloads. No import of
another product's internals, no GF function guess, no RuntimeSet publication.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from typing import Any


class LexicalCoordinator:
    def __init__(self, paths: dict[str, str]):
        self.paths = paths

    def _root(self, key: str, probe: str) -> Path:
        p = Path(self.paths.get(key, '')).expanduser().resolve()
        for d in (p, p/'diK') if key=='dik' else (p,):
            if (d/probe).is_file():
                return d
        raise FileNotFoundError(f'{key}: required public CLI missing in configured repository path')

    def _output_root(self) -> Path:
        base = Path(self.paths['reports']).expanduser().resolve().parent / 'lexical_integration'
        base.mkdir(parents=True,exist_ok=True)
        return base

    def _new(self, prefix: str) -> Path:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        return self._output_root()/(prefix+'-'+stamp+'-'+secrets.token_hex(3))

    @staticmethod
    def _exec(root: Path, module: str | None, args: list[str], timeout: int = 120) -> dict[str,Any]:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(root/'src') + os.pathsep + env.get('PYTHONPATH','')
        env['PYTHONIOENCODING'] = 'utf-8'
        cmd = [sys.executable, '-m',module,*args] if module else [sys.executable,*args]
        try:
            cp = subprocess.run(cmd,cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,check=False,shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {'ok':False,'error':str(exc),'exit_code':None}
        output = cp.stdout if cp.returncode == 0 else (cp.stderr or cp.stdout)
        try:
            result = json.loads(output)
        except (TypeError, ValueError):
            result = {'message':output[:3500]}
        return {'ok':cp.returncode==0, 'exit_code':cp.returncode,'result':result,
                'authority':root.name,'status':'CANDIDATE_ONLY', 'released':False}

    def status(self) -> dict[str,Any]:
        root=self._output_root()
        recent=sorted([d for d in root.iterdir() if d.is_dir()],key=lambda d:d.name,reverse=True)[:18]
        return {'ok':True,'status':'CANDIDATE_ONLY','released':False,
                'workspace':str(root),'recent':[{'name':d.name,'path':str(d),
                    'kind': ('knowledge' if (d/'semantik.knowledge.json').is_file() else
                             'mapping' if (d/'lexicon.candidate.json').is_file() else
                             'gf-handoff' if (d/'candidates.jsonl').is_file() else 'unknown')}
                    for d in recent]}

    def diK_handoff(self, observations: str, locale: str) -> dict[str,Any]:
        if not isinstance(observations,str) or not 1<=len(observations)<2048:
            raise ValueError('Provide a local diK lexeme-observations directory')
        if not isinstance(locale,str) or not locale.replace('-','').isalnum() or not 2<=len(locale)<=24:
            raise ValueError('Invalid explicit language locale')
        root=self._root('dik','src/dik/cli.py')
        observation_root=Path(observations).expanduser().resolve()
        if not (observation_root/'lexemes.jsonl').is_file():
            raise FileNotFoundError('Expected an existing diK observations directory with lexemes.jsonl')
        handoff=self._new('dik-gf-'+locale)
        step1=self._exec(root,'dik.cli',['world','gf-handoff','--observations',str(observation_root),
                                       '--output-dir',str(handoff),'--locale',locale],timeout=180)
        if not step1['ok']:
            return {'ok':False,'stage':'dik.gf-handoff','detail':step1,'released':False}
        knowledge=self._new('dik-knowledge-'+locale)
        step2=self._exec(root,'dik.cli',['world','semantik-knowledge','--handoff',str(handoff),
                                       '--output-dir',str(knowledge)],timeout=180)
        return {'ok':bool(step2['ok']),'stage':'dik.semantik-knowledge', 'gf_handoff':str(handoff),
                'knowledge_bundle':str(knowledge) if step2['ok'] else None,'detail':step2,
                'decisions_template':str(knowledge/'gf-mapping-review.template.json') if step2['ok'] else None,
                'status':'CANDIDATE_ONLY','released':False}

    def wordbench_bindings(self, knowledge_bundle: str, review_file: str) -> dict[str,Any]:
        if not all(isinstance(x,str) and 1<=len(x)<2048 for x in (knowledge_bundle,review_file)):
            raise ValueError('Candidate knowledge directory and independently reviewed JSON file are required')
        wb=self._root('wordbench','tools/build_dik_semantik_lexicon.py')
        output=self._new('wordbench-dik-bindings')
        ret=self._exec(wb,None,[str(wb/'tools/build_dik_semantik_lexicon.py'),'build',
                                '--dik-bundle',str(Path(knowledge_bundle).expanduser().resolve()),
                                '--decisions',str(Path(review_file).expanduser().resolve()),
                                '--output',str(output)],timeout=180)
        return {'ok':ret['ok'],'stage':'wordbench.lexical-candidate',
                'candidate_bundle':str(output) if ret['ok'] else None,
                'detail':ret,'released':False}

    def inspect(self, candidate_bundle: str) -> dict[str,Any]:
        if not isinstance(candidate_bundle,str) or not 1<=len(candidate_bundle)<2048:
            raise ValueError('Provide a candidate bundle path')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._exec(sa,'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root',str(sa/'runtime'),'inspect-dik-lexicon',
                           '--bundle',str(Path(candidate_bundle).expanduser().resolve())],timeout=30)

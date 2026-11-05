"""Public CLI adapters for SemantiK Architect and Runtime Orchestrator.

No SemantiK internal modules are imported; no parsing of raw prose, GF
synthetic realization, PGF compilation, RuntimeSet publication or hidden
fallback is implemented in Defluens. Nonzero upstream exits stay failures.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

PROFILE = re.compile(r'^[a-z][a-z0-9-]*-[0-9]+$')
LANG = re.compile(r'^[a-z]{2,3}$')
ATTRIBUTE_PROFILE = 'defluens-attribute-fr-1'
ATTRIBUTE_RUNTIME = ATTRIBUTE_PROFILE
CORE_LANGUAGES = {'fr':'defluens-core-fr-1','en':'defluens-core-en-1'}

class SemantikClient:
    def __init__(self, paths: dict[str,str]):
        self.paths = paths

    def _root(self, name: str, module_file: str) -> Path:
        value = self.paths.get(name)
        if not value: raise ValueError(f'{name} path is not configured')
        root = Path(value).expanduser().resolve()
        if not (root/module_file).is_file():
            raise FileNotFoundError(f'{name} source package not found at configured path')
        return root

    @staticmethod
    def _call(root: Path, module: str, argv: list[str], *, payload: dict | None = None,
              timeout: int = 60, gf_path: str | None = None) -> dict:
        env=os.environ.copy()
        env['PYTHONPATH']=str(root/'src')+os.pathsep+env.get('PYTHONPATH','')
        env['PYTHONIOENCODING']='utf-8'
        if gf_path and Path(gf_path).is_file():
            env['SEMANTIK_GF_EXECUTABLE']=gf_path
        args=[sys.executable,'-m',module,*argv]
        try:
            cp=subprocess.run(args,cwd=root,env=env,
                input=json.dumps(payload,ensure_ascii=False) if payload is not None else None,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',
                timeout=timeout,check=False,shell=False)
        except subprocess.TimeoutExpired:
            return {'ok':False,'exit_code':None,'error':'Upstream tool deadline exceeded', 'timed_out':True}
        except OSError as exc:
            return {'ok':False,'exit_code':None,'error':f'Unable to start upstream command: {exc}'}
        try:
            result=json.loads(cp.stdout if cp.returncode==0 else (cp.stderr or cp.stdout))
        except (ValueError,TypeError):
            result={'message':(cp.stderr or cp.stdout or 'Upstream command returned no JSON')[:5000]}
        return {'ok':cp.returncode==0, 'exit_code':cp.returncode, 'result':result,
                'source':'upstream_public_cli', 'fidelity_claim':'upstream_only'}

    def capabilities(self) -> dict:
        root=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(root,'semantik_architect.adapters.inbound.cli.main',
            ['--runtime-root',str(root/'runtime'),'capabilities'],timeout=15)

    def example(self) -> dict:
        root=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        path=root/'examples'/'orgo_fr_request.json'
        if not path.is_file() or path.stat().st_size>20_000:
            raise FileNotFoundError('SemantiK structured-request example unavailable')
        request=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(request,dict):raise ValueError('Invalid upstream request example')
        return {'example':request,'origin':'SemantiK Architect public example: examples/orgo_fr_request.json'}

    def request(self, action: str, request: Any) -> dict:
        if action not in ('render','validate-request','explain'):raise ValueError('Unknown semantic operation')
        if not isinstance(request,dict):raise ValueError('A structured JSON request is required')
        raw=json.dumps(request,ensure_ascii=False)
        if len(raw.encode('utf-8'))>20_000:raise ValueError('Request exceeds local maximum')
        root=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(root,'semantik_architect.adapters.inbound.cli.main',
            ['--runtime-root',str(root/'runtime'),action,'-'],payload=request,
            timeout=75 if action=='render' else 20,gf_path=self.paths.get('gf'))

    def readiness(self, language: str, profile: str) -> dict:
        if not isinstance(language,str) or not LANG.fullmatch(language) or not isinstance(profile,str) or not PROFILE.fullmatch(profile):
            raise ValueError('Use SA language (e.g. fr) and versioned capability profile (e.g. konstellation-explorer-3)')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        runtime=self._root('runtime_orchestrator','src/semantik_runtime_orchestrator/cli.py')
        return self._call(runtime,'semantik_runtime_orchestrator.cli',
            ['inspect-profile','--runtime-root',str(sa/'runtime'),
             '--language',language,'--profile',profile],timeout=15)

    # --- v0.5 development tools; all semantic work remains upstream. ---
    def _candidate_dir(self, runtime_id: str = 'konstellation-fr-3') -> Path:
        # Stable local development output, not an SA runtime or an activation directory.
        return Path(self.paths['reports']).expanduser().resolve().parent / 'semantik_candidates' / runtime_id

    def candidate_status(self, runtime_id: str = 'konstellation-fr-3') -> dict:
        if runtime_id not in ('konstellation-fr-3', ATTRIBUTE_RUNTIME, *CORE_LANGUAGES.values()):
            raise ValueError('Unknown local candidate runtime')
        root=self._candidate_dir(runtime_id)
        report_path=root/'build-report.json'
        if not report_path.is_file():
            return {'ready':False,'candidate_dir':str(root),'status':'NOT_BUILT',
                    'released':False,'activated':False}
        try:
            report=json.loads(report_path.read_text(encoding='utf-8'))
            lock=json.loads((root/'pipeline.lock.json').read_text(encoding='utf-8'))
            import hashlib
            hashes=lock.get('inputs',{})
            required={'grammar.pgf','bridge.json','lexicon.json','profile.json','conformance.suite.json'}
            ready=(required <= hashes.keys() and
                   all((root/n).is_file() and hashlib.sha256((root/n).read_bytes()).hexdigest()==hashes[n]
                       for n in required) and
                   report.get('status')=='PGF_BUILT_CANDIDATE_ONLY' and
                   lock.get('runtime_set_id')==runtime_id)
            return {'ready':bool(ready),'status':report.get('status','UNKNOWN'),
                    'candidate_dir':str(root),'pgf_sha256':hashes.get('grammar.pgf'),
                    'pipeline_lock_sha256':hashlib.sha256((root/'pipeline.lock.json').read_bytes()).hexdigest(),
                    'released':False,'activated':False,
                    'notice':'Development candidate, NOT an admitted RuntimeSet or linguistic certification.'}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            return {'ready':False,'candidate_dir':str(root),'status':'INTEGRITY_ERROR',
                    'error':str(exc),'released':False,'activated':False}

    def pilot_examples(self) -> dict:
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        file=sa/'profiles'/'konstellation-explorer-3'/'conformance.suite.json'
        if not file.is_file() or file.stat().st_size>100_000:
            raise FileNotFoundError('Canonical five-case SA profile not found')
        suite=json.loads(file.read_text(encoding='utf-8'))
        cases=suite.get('cases',[])
        if not isinstance(cases,list) or len(cases)!=5:
            raise ValueError('Unexpected canonical profile-3 cases')
        return {'profile_id':'konstellation-explorer-3','runtime_set_id':'konstellation-fr-3',
                'cases':[{'id':c['case_id'],'request':c['request'],
                          'expected_from_fixture':c.get('expected',{}).get('plain_text','')}
                         for c in cases],
                'expected_from_fixture_is_not_real_gf':True}

    def build_candidate(self, profile_id: str = 'konstellation-explorer-3') -> dict:
        if profile_id not in ('konstellation-explorer-3', ATTRIBUTE_PROFILE, *CORE_LANGUAGES.values()):
            raise ValueError('Unknown candidate profile')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        wb=self._root('wordbench','src/gf_wordbench/practical/batch.py')
        gf=Path(self.paths['gf'])
        if not gf.is_file():
            return {'ok':False,'status':'BLOCKED','error':'GF executable not found: '+str(gf)}
        script=wb/'tools'/'build_semantik_profile3_candidate.py'
        if not script.is_file():raise FileNotFoundError('WordBench candidate builder v0.5 not installed')
        env=os.environ.copy()
        env['PYTHONPATH']=str(wb/'src')+os.pathsep+env.get('PYTHONPATH','')
        env['PYTHONIOENCODING']='utf-8'
        runtime_id = profile_id if profile_id in (ATTRIBUTE_PROFILE,*CORE_LANGUAGES.values()) else 'konstellation-fr-3'
        cmd=[sys.executable,str(script),'--semantik-root',str(sa),
             '--gf-exe',str(gf),'--profile',profile_id,
             '--output',str(self._candidate_dir(runtime_id)),'--force']
        if profile_id == ATTRIBUTE_PROFILE or profile_id in CORE_LANGUAGES.values():
            rgl=Path(self.paths['rgl']).expanduser().resolve()
            if not (rgl/'src/api').is_dir():
                return {'ok':False,'status':'BLOCKED','error':'RGL API directory missing: '+str(rgl)}
            cmd.extend(['--rgl-root',str(rgl),'--timeout','420'])
        try:
            cp=subprocess.run(cmd,cwd=wb,env=env,text=True,encoding='utf-8',errors='replace',
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=510 if profile_id in (ATTRIBUTE_PROFILE,*CORE_LANGUAGES.values()) else 170,shell=False)
        except subprocess.TimeoutExpired:
            return {'ok':False,'status':'BLOCKED','error':'WordBench GF compilation timed out'}
        try: report=json.loads(cp.stdout)
        except (ValueError,TypeError):
            report={'status':'BLOCKED','error':(cp.stderr or cp.stdout)[-3000:]}
        return {'ok':cp.returncode==0 and report.get('pgf_compiled') is True,
                'source':'gf_wordbench_public_builder','report':report,
                'status':report.get('status','BLOCKED'),'exit_code':cp.returncode,
                'released':False,'activated':False}

    def preview_candidate(self, request: Any, runtime_id: str = 'konstellation-fr-3') -> dict:
        if not isinstance(request,dict):raise ValueError('Structured request JSON required')
        if len(json.dumps(request,ensure_ascii=False).encode('utf-8'))>20_000:
            raise ValueError('Request exceeds local maximum')
        status=self.candidate_status(runtime_id)
        if not status['ready']:
            return {'ok':False,'status':'CANDIDATE_NOT_READY',
                    'error':'First compile the French candidate PGF using GF WordBench.',
                    'candidate':status,'released':False,'activated':False}
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root',str(sa/'runtime'),'preview-candidate',
                           '--candidate-dir',status['candidate_dir'],
                           '--runtime-set-id',runtime_id,'-'],
                          payload=request,timeout=75,gf_path=self.paths.get('gf'))

    def render_many(self, request: Any, languages: Any) -> dict:
        """Send each target to the existing production CLI. No semantic remapping.

        Lexical availability / profile applicability remains entirely an SA decision.
        """
        if not isinstance(request,dict):raise ValueError('Structured CommunicationRequest required')
        if not isinstance(languages,list) or not 1<=len(languages)<=14 or any(
            not isinstance(lang,str) or not LANG.fullmatch(lang) for lang in languages
        ) or len(set(languages))!=len(languages):
            raise ValueError('Choose 1–14 distinct ISO language codes')
        if len(json.dumps(request,ensure_ascii=False).encode('utf-8'))>20_000:
            raise ValueError('Request exceeds local maximum')
        import copy
        from concurrent.futures import ThreadPoolExecutor
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        def attempt(lang):
            adapted=copy.deepcopy(request)
            context=adapted.get('context')
            if not isinstance(context,dict):raise ValueError('Missing canonical request.context')
            context['target_language']=lang
            context['target_locale']=lang
            # A pinned runtime for another language must not be silently reused.
            adapted.pop('runtime_selector',None)
            result=self._call(sa,'semantik_architect.adapters.inbound.cli.main',
                              ['--runtime-root',str(sa/'runtime'),'render','-'],
                              payload=adapted,timeout=45,gf_path=self.paths.get('gf'))
            body=result.get('result',{})
            return {'language':lang,'ok':result.get('ok') is True,
                    'text':body.get('plain_text') if result.get('ok') and isinstance(body,dict) else None,
                    'detail':body, 'exit_code':result.get('exit_code')}
        with ThreadPoolExecutor(max_workers=3) as pool:
            rows=list(pool.map(attempt,languages))
        return {'schema_version':'1.0','source':'semantik_public_render',
                'results':rows, 'all_success':all(x['ok'] for x in rows),
                'success_count':sum(x['ok'] for x in rows),
                'notice':'Only released language/profile pairs can be rendered. Errors are not replaced by text.'}

    # --- v0.7 typed-input authoring; public SemantiK CLI owns canonical request mapping. ---
    def attribute_request(self, subject: str, attribute: str, polarity: str, tense: str) -> dict:
        for value in (subject,attribute,polarity,tense):
            if not isinstance(value,str) or not re.fullmatch(r'[a-z]{2,16}',value):
                raise ValueError('Expected bounded concept ID, not text or GF syntax')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
            ['--runtime-root',str(sa/'runtime'),'defluens-attribute-request',
             '--subject',subject,'--attribute',attribute,
             '--polarity',polarity,'--tense',tense],timeout=20)

    # --- v0.8: six SA operations, two candidate GF languages, bounded multi-block input. ---
    def core_catalog(self) -> dict:
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root',str(sa/'runtime'),'defluens-core-catalog'],timeout=45)

    def core_request(self, recipe: Any) -> dict:
        if not isinstance(recipe,dict):raise ValueError('Structured semantic recipe required')
        if len(json.dumps(recipe,ensure_ascii=False).encode('utf-8'))>20_000:
            raise ValueError('Recipe exceeds local maximum')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root',str(sa/'runtime'),'defluens-core-request','-'],
                          payload=recipe,timeout=20)

    def core_batch(self, vectors: Any) -> dict:
        if not isinstance(vectors, list) or not 1 <= len(vectors) <= 48:
            raise ValueError('Expected 1–48 bounded semantic vectors')
        payload = {'vectors': vectors}
        if len(json.dumps(payload,ensure_ascii=False).encode('utf-8'))>100_000:
            raise ValueError('Core acceptance batch exceeds 100 kB')
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root',str(sa/'runtime'),'defluens-core-batch','-'],
                          payload=payload,timeout=45)

    def preview_candidate_batch(self, vectors: list[dict], runtime_id: str) -> dict:
        """Send complete canonical requests through SemantiK's locked GF batch CLI.

        This method never parses or fabricates surface text. Candidate integrity
        is checked both before calling SA and by SA's CandidateConformance.
        """
        if runtime_id not in CORE_LANGUAGES.values():
            raise ValueError('Only the FR/EN core candidate runtimes are supported')
        if not isinstance(vectors, list) or not 1 <= len(vectors) <= 48:
            raise ValueError('Provide 1–48 canonical requests')
        ids = [x.get('case_id') for x in vectors if isinstance(x, dict)]
        if (len(ids) != len(vectors) or len(set(ids)) != len(ids)
                or any(not isinstance(x, str) or not re.fullmatch(r'[a-z0-9][a-z0-9:_-]{0,79}', x) for x in ids)
                or any(set(x) != {'case_id', 'request'} or not isinstance(x['request'], dict) for x in vectors)):
            raise ValueError('Malformed or duplicated batch vector')
        payload = {'vectors': vectors}
        if len(json.dumps(payload, ensure_ascii=False).encode('utf-8')) > 250_000:
            raise ValueError('Candidate GF batch exceeds 250 kB')
        status = self.candidate_status(runtime_id)
        if not status['ready']:
            return {'ok': False, 'status': 'BLOCKED_PGF', 'candidate': status,
                    'released': False, 'activated': False}
        sa = self._root('semantik', 'src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa, 'semantik_architect.adapters.inbound.cli.main',
                          ['--runtime-root', str(sa/'runtime'), 'preview-candidate-batch',
                           '--candidate-dir', status['candidate_dir'],
                           '--runtime-set-id', runtime_id, '-'],
                          payload=payload, timeout=600, gf_path=self.paths.get('gf'))

    def core_status(self) -> dict:
        return {'schema_version':'1.0', 'candidate_only':True,
                'languages':{lang:self.candidate_status(runtime) for lang,runtime in CORE_LANGUAGES.items()}}

    def core_build(self, language: str) -> dict:
        if language not in CORE_LANGUAGES:raise ValueError('Only fr and en are supported by this development candidate')
        return self.build_candidate(CORE_LANGUAGES[language])

    def core_preview(self, recipe: Any) -> dict:
        if not isinstance(recipe,dict):raise ValueError('Structured recipe required')
        lang=recipe.get('language')
        if lang not in CORE_LANGUAGES:raise ValueError('Candidate language must be fr or en')
        generated=self.core_request(recipe)
        if not generated.get('ok'):
            return {'ok':False,'stage':'request_mapping','detail':generated,'released':False}
        realized=self.preview_candidate(generated['result'],CORE_LANGUAGES[lang])
        return {'ok':realized.get('ok') is True,'stage':'candidate_realization',
                'language':lang,'recipe':recipe,'canonical_request':generated['result'],
                'result':realized,'released':False,'linguistically_certified':False}

    def core_preview_many(self, recipe: Any, languages: Any) -> dict:
        if not isinstance(recipe,dict) or not isinstance(languages,list) or not languages or len(languages)>2 or len(set(languages))!=len(languages) or any(x not in CORE_LANGUAGES for x in languages):
            raise ValueError('Select fr and/or en for candidate preview')
        # No pivot language: each canonical request is independently mapped by SemantiK.
        results=[]
        for lang in languages:
            prepared=dict(recipe, language=lang)
            outcome=self.core_preview(prepared)
            body=outcome.get('result',{})
            inner=body.get('result',{}) if isinstance(body,dict) else {}
            result=inner.get('communication_result',{}) if isinstance(inner,dict) else {}
            results.append({'language':lang, 'ok':outcome.get('ok') is True,
                            'text':result.get('plain_text') if isinstance(result,dict) and outcome.get('ok') else None,
                            'detail':outcome,'released':False})
        return {'schema_version':'1.0','source':'semantik_real_gf_candidate',
                'candidate_only':True,'released':False, 'results':results,
                'all_success':all(x['ok'] for x in results),
                'success_count':sum(x['ok'] for x in results)}

    # --- v0.6: development-only, selectable real GF intent probe. ---
    def practical_intents(self) -> dict:
        sa=self._root('semantik','src/semantik_architect/adapters/inbound/cli/main.py')
        return self._call(sa,'semantik_architect.adapters.inbound.cli.main',
            ['--runtime-root',str(sa/'runtime'),'defluens-intents'],timeout=15)

    def practical_preview(self, language: str, capability: str) -> dict:
        from .core import LANGUAGES, SCENARIOS, normalize_gf_display
        if not isinstance(language,str) or language not in LANGUAGES:
            raise ValueError('Unknown language (expected a prepared three-letter RGL code)')
        if not isinstance(capability,str) or capability not in SCENARIOS:
            raise ValueError('Unknown capability')
        wb=self._root('wordbench','src/gf_wordbench/practical/pilot.py')
        gf=Path(self.paths['gf']).expanduser().resolve()
        rgl=Path(self.paths['rgl']).expanduser().resolve()
        if not gf.is_file():
            return {'ok':False,'status':'GF_NOT_INSTALLED','error':str(gf),
                    'gf_executed':False,'released':False}
        if not (rgl/'src').is_dir():
            return {'ok':False,'status':'RGL_NOT_FOUND','error':str(rgl),
                    'gf_executed':False,'released':False}
        script=wb/'tools'/'preview_defluens_capability.py'
        if not script.is_file():
            raise FileNotFoundError('WordBench v0.6 single-intent preview tool is missing')
        output=Path(self.paths['reports']).expanduser().resolve().parent/'practical_single_previews'
        output.mkdir(parents=True,exist_ok=True)
        env=os.environ.copy()
        env['PYTHONPATH']=str(wb/'src')+os.pathsep+env.get('PYTHONPATH','')
        env['PYTHONIOENCODING']='utf-8'
        argv=[sys.executable,str(script),'--language',language,'--capability',capability,
              '--gf-executable',str(gf),'--rgl-root',str(rgl),
              '--output-root',str(output),'--timeout','90']
        try:
            cp=subprocess.run(argv,cwd=wb,env=env,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',
                              timeout=120,check=False,shell=False)
        except subprocess.TimeoutExpired:
            return {'ok':False,'status':'TIMEOUT','error':'GF preview exceeded 120 seconds',
                    'gf_executed':True,'released':False}
        try:
            data=json.loads(cp.stdout)
        except (ValueError,TypeError):
            data={'status':'UPSTREAM_ERROR','error':(cp.stderr or cp.stdout)[-3000:]}
        if not isinstance(data,dict):data={'status':'UPSTREAM_ERROR','error':'Invalid WordBench result'}
        raw=data.get('candidate') if isinstance(data.get('candidate'),str) else ''
        data['readable']=normalize_gf_display(raw)
        data['ok']=cp.returncode==0 and data.get('status')=='candidate_for_review'
        data['exit_code']=cp.returncode
        return data

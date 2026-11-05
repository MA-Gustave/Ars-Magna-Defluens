"""Configuration, read-only evidence ingestion and bounded WordBench execution.

This module has no third-party dependencies. In particular it does not compile GF,
change RGL sources, approve linguistic golds, or re-interpret GF diagnostics.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import threading
import time
import zipfile
from typing import Any, Callable

LANGUAGES = ('Eng', 'Fre', 'Spa', 'Ger', 'Dut', 'Swe', 'Dan', 'Nor', 'Nno', 'Fin', 'Est', 'Afr', 'Ita', 'Por')
LANGUAGE_NAMES = {
    'Eng': ('Anglais', 'English'), 'Fre': ('Français', 'French'), 'Spa': ('Espagnol', 'Spanish'),
    'Ger': ('Allemand', 'German'), 'Dut': ('Néerlandais', 'Dutch'), 'Swe': ('Suédois', 'Swedish'),
    'Dan': ('Danois', 'Danish'), 'Nor': ('Norvégien bokmål', 'Norwegian Bokmål'),
    'Nno': ('Norvégien nynorsk', 'Norwegian Nynorsk'), 'Fin': ('Finnois', 'Finnish'),
    'Est': ('Estonien', 'Estonian'), 'Afr': ('Afrikaans', 'Afrikaans'),
    'Ita': ('Italien', 'Italian'), 'Por': ('Portugais', 'Portuguese'),
}
SCENARIOS = ('factual-present', 'past-event', 'past-state', 'future-reference', 'factual-negation',
    'temporal-order', 'condition-real', 'possibility', 'source-attribution', 'quantity', 'location',
    'instruction', 'prohibition', 'obligation', 'conditional-instruction')
ROOT = Path(__file__).resolve().parents[1]

def default_paths(root: Path = ROOT, home: Path | None = None) -> dict[str, str]:
    home = home or Path.home()
    parent = root.parent
    return {
        'wordbench': str(parent / 'GF_Wordbench'),
        'dik': str(Path('C:/mycode/diK') if os.name == 'nt' else parent.parent / 'diK'),
        'semantik': str(Path('C:/mycode/SemantiK_Architect/SemantiK_Architect')) if os.name == 'nt' else str(parent / 'SemantiK_Architect'),
        'runtime_orchestrator': str(Path('C:/mycode/SemantiK_Architect/SemantiK_Runtime_Orchestrator')) if os.name == 'nt' else str(parent / 'SemantiK_Runtime_Orchestrator'),
        'observatory': str(parent / 'GF_Observatory'),
        'compendium': str(parent / 'GF_RGL_AI_Compendium'),
        'rgl': str(parent / 'gf-rgl'),
        'gf': str(parent / 'gf-3.12-windows' / 'gf.exe'),
        'reports': str(home / 'Downloads' / 'Ars_Magna_Defluens' / 'practical_pilot_runs'),
        'alignment': str(home / 'Downloads' / 'Ars_Magna_Defluens' / 'alignment14'),
    }

def local_state_dir() -> Path:
    base = os.environ.get('LOCALAPPDATA')
    if base:
        return Path(base) / 'Ars_Magna_Defluens'
    return Path.home() / '.local' / 'state' / 'ars-magna-defluens'

class Settings:
    def __init__(self, store: Path | None = None, defaults: dict[str, str] | None = None):
        self.store = store or (local_state_dir() / 'settings.json')
        self.defaults = defaults or default_paths()
        self.paths = dict(self.defaults)
        if self.store.is_file():
            try:
                loaded = json.loads(self.store.read_text(encoding='utf-8'))
                if isinstance(loaded, dict) and isinstance(loaded.get('paths'), dict):
                    for key, path in loaded['paths'].items():
                        if key in self.paths and isinstance(path, str) and path.strip() and len(path) < 2048:
                            self.paths[key] = path.strip()
            except (OSError, ValueError):
                pass

    def update(self, paths: Any) -> None:
        if not isinstance(paths, dict) or not paths or any(x not in self.defaults for x in paths):
            raise ValueError('Invalid configuration keys')
        clean = dict(self.paths)
        for key, value in paths.items():
            if not isinstance(value, str) or not value.strip() or len(value) > 2048:
                raise ValueError(f'Invalid path for {key}')
            p = Path(os.path.expandvars(os.path.expanduser(value.strip())))
            if not p.is_absolute():
                raise ValueError(f'Absolute path required: {key}')
            clean[key] = str(p)
        self.store.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.store.with_suffix('.tmp')
        tmp.write_text(json.dumps({'schema_id':'defluens.console-settings', 'version':1, 'paths':clean}, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.replace(self.store)
        self.paths = clean

    def health(self) -> dict[str, Any]:
        p = {k: Path(v) for k,v in self.paths.items()}
        return {
            'wordbench': (p['wordbench'] / 'src' / 'gf_wordbench' / 'practical' / 'batch.py').is_file(),
            'dik': any((d / 'src' / 'dik' / 'cli.py').is_file() for d in (p.get('dik', Path('_unconfigured_')), p.get('dik',Path('_unconfigured_')) / 'diK')), 
            'semantik': (p.get('semantik',Path('_unconfigured_')) / 'src' / 'semantik_architect' / 'adapters' / 'inbound' / 'cli' / 'main.py').is_file(),
            'runtime_orchestrator': (p.get('runtime_orchestrator',Path('_unconfigured_')) / 'src' / 'semantik_runtime_orchestrator' / 'cli.py').is_file(),
            'alignment': (p['wordbench'] / 'src' / 'gf_wordbench' / 'practical' / 'alignment14.py').is_file(),
            'observatory': (p['observatory'] / 'Launch_Observatory.bat').is_file(),
            'compendium': (p['compendium'] / 'README.md').is_file(),
            'rgl': (p['rgl'] / 'src' / 'abstract').is_dir(),
            'gf': p['gf'].is_file(),
            'reports': p['reports'].is_dir(),
        }

def normalize_gf_display(raw: str) -> str:
    """Display-only join of GF &+ tokens; never modify stored evidence."""
    return re.sub(r'\s*&\+\s*', '', raw).strip()

class ReportIndex:
    def __init__(self, settings: Settings):
        self.settings = settings

    def archives(self, limit: int = 8) -> list[Path]:
        root = Path(self.settings.paths['reports'])
        if not root.is_dir(): return []
        try:
            matches = [p for p in root.glob('defluens-batch-*.zip') if p.is_file()]
            return sorted(matches, key=lambda p:p.stat().st_mtime, reverse=True)[:limit]
        except OSError:
            return []

    @staticmethod
    def _json_from_zip(z: zipfile.ZipFile, suffix: str) -> dict[str, Any] | None:
        names = [n for n in z.namelist() if n.endswith('/' + suffix) or n == suffix]
        for name in names:
            info = z.getinfo(name)
            if info.file_size > 4_000_000: continue
            try:
                obj = json.loads(z.read(info).decode('utf-8-sig'))
                if isinstance(obj, dict): return obj
            except (UnicodeError, ValueError, OSError): continue
        return None

    def latest(self) -> dict[str, Any] | None:
        for p in self.archives():
            try:
                with zipfile.ZipFile(p) as z:
                    summary = self._json_from_zip(z, 'batch_summary.json')
                if summary and summary.get('schema_id') == 'defluens.pilot-batch':
                    return self._summarize(summary, p)
            except (OSError, zipfile.BadZipFile, ValueError): continue
        return None

    def history(self) -> list[dict[str, Any]]:
        ans=[]
        for p in self.archives():
            try:
                with zipfile.ZipFile(p) as z:
                    summary = self._json_from_zip(z, 'batch_summary.json')
                if summary and summary.get('schema_id') == 'defluens.pilot-batch':
                    ans.append(self._summarize(summary,p))
            except (OSError, zipfile.BadZipFile, ValueError): continue
        return ans

    @staticmethod
    def _summarize(summary: dict[str, Any], p: Path) -> dict[str, Any]:
        entries = []
        totals = {'candidates':0,'failures':0,'timeouts':0,'attempted':0}
        for entry in summary.get('entries',[]):
            if not isinstance(entry,dict): continue
            code = entry.get('language')
            if code not in LANGUAGE_NAMES: continue
            t = entry.get('totals') or {}
            candidates = int(t.get('candidate_for_review',0) or 0)
            failed = int(t.get('probe_failed',0) or 0)
            timeout = int(t.get('timeout',0) or 0)
            attempted = int(entry.get('scenarios_attempted',0) or 0)
            totals['candidates'] += candidates
            totals['failures'] += failed
            totals['timeouts'] += timeout
            totals['attempted'] += attempted
            entries.append({'code':code,'name_fr':LANGUAGE_NAMES[code][0], 'name_en':LANGUAGE_NAMES[code][1],
                            'candidates':candidates,'failures':failed,'timeouts':timeout,'attempted':attempted,
                            'status':entry.get('status','unknown')})
        return {'id': str(summary.get('batch_id','')), 'mode':summary.get('mode','unknown'),
                'started_at':summary.get('started_at',''), 'archive_name':p.name,
                'path':str(p), 'semantic_coverage_verified': bool(summary.get('semantic_coverage_verified',False)),
                'entries':entries,'totals':totals}

    def language(self, code: str) -> dict[str, Any]:
        if code not in LANGUAGES: raise ValueError('Unknown language code')
        newest = self.latest()
        if newest is None: raise FileNotFoundError('No completed campaign archive available')
        path = Path(newest['path'])
        with zipfile.ZipFile(path) as z:
            opts = [n for n in z.namelist() if n.endswith('/pilot_run.json') and '/defluens-pilot-' + code + '-' in n]
            if not opts: raise FileNotFoundError('Language not present in latest archive')
            info = z.getinfo(opts[0])
            if info.file_size > 4_000_000: raise ValueError('Language report is unexpectedly large')
            data = json.loads(z.read(info).decode('utf-8-sig'))
        if data.get('language') != code: raise ValueError('Language evidence identity mismatch')
        rows=[]
        for s in data.get('scenarios',[]):
            raw = s.get('candidate') or ''
            rows.append({'id':s.get('id',''), 'meaning_en':s.get('meaning_en',''),
                         'status':s.get('status','unknown'), 'candidate':normalize_gf_display(raw),
                         'raw':raw,'source_sha256':s.get('source_sha256',''),
                         'reason':s.get('reason','')})
        return {'language':code, 'name_fr':LANGUAGE_NAMES[code][0], 'name_en':LANGUAGE_NAMES[code][1],
                'run_id':data.get('run_id',''), 'scenarios':rows,
                'semantic_coverage_verified':bool(data.get('semantic_coverage_verified',False))}

class JobRunner:
    """One bounded local WordBench process at a time. No shell command injection."""
    def __init__(self, settings: Settings, on_finished: Callable[[],None] | None = None):
        self.settings = settings
        self.on_finished = on_finished
        self.lock=threading.RLock()
        self.process: subprocess.Popen[str] | None = None
        self.job={'state':'idle','mode':None,'started_at':None,'finished_at':None,
                  'exit_code':None, 'error':None,'lines':[],'log_path':None}

    def command(self, mode: str) -> tuple[list[str],Path,dict[str,str]]:
        if mode not in ('check','smoke','full','compare','handoff'):
            raise ValueError('Unsupported action')
        wb=Path(self.settings.paths['wordbench'])
        rgl=Path(self.settings.paths['rgl'])
        gf=Path(self.settings.paths['gf'])
        reports=Path(self.settings.paths['reports'])
        alignment=Path(self.settings.paths['alignment'])
        if not (wb/'src'/'gf_wordbench'/'practical'/'batch.py').is_file():
            raise ValueError('GF WordBench was not found. Check its path in Settings.')
        if not (wb/'src'/'gf_wordbench'/'practical'/'alignment14.py').is_file():
            raise ValueError('WordBench alignment14 module was not found.')
        if mode != 'handoff' and not (rgl/'src'/'abstract').is_dir():
            raise ValueError('GF RGL source root was not found.')
        if mode in ('smoke','full') and not gf.is_file():
            raise ValueError('GF compiler was not found. Check gf.exe in Settings.')
        env=os.environ.copy()
        env['PYTHONPATH'] = str(wb/'src') + os.pathsep + env.get('PYTHONPATH','')
        env['PYTHONUNBUFFERED']='1'
        env['PYTHONIOENCODING']='utf-8'
        runner=[sys.executable,'-u','-m']
        if mode=='check':
            alignment.mkdir(parents=True, exist_ok=True)
            cmd=runner+['gf_wordbench.practical.alignment14','verify','--rgl-root',str(rgl),
                        '--report',str(alignment/'alignment14_check.json')]
        elif mode=='handoff':
            if not (wb/'src'/'gf_wordbench'/'practical'/'semantik_handoff.py').is_file():
                raise ValueError('Install the WordBench SemantiK handoff update first.')
            full_runs=sorted(reports.glob('defluens-batch-full-*.zip'),key=lambda p:p.stat().st_mtime,reverse=True) if reports.is_dir() else []
            if not full_runs:raise ValueError('A completed full WordBench ZIP is required before handoff.')
            alignment.mkdir(parents=True,exist_ok=True)
            cmd=runner+['gf_wordbench.practical.semantik_handoff','--archive',str(full_runs[0]),
                        '--output',str(alignment/'semantik_handoff.json')]
        elif mode=='compare':
            alignment.mkdir(parents=True,exist_ok=True)
            cmd=runner+['gf_wordbench.practical.alignment14','compare','--rgl-root',str(rgl),
                        '--batch-dir',str(reports),'--report',str(alignment/'alignment14_comparison.json')]
        else:
            reports.mkdir(parents=True,exist_ok=True)
            cmd=runner+['gf_wordbench.practical.batch','run','--mode',mode,
                        '--gf-executable',str(gf),'--rgl-root',str(rgl),
                        '--output-root',str(reports),'--timeout','90','--max-minutes','45',
                        '--languages',*LANGUAGES]
        return cmd,wb,env

    def start(self, mode: str) -> dict[str, Any]:
        with self.lock:
            if self.job['state'] == 'running':
                raise RuntimeError('A WordBench campaign is already running')
            cmd,cwd,env=self.command(mode)
            logdir=local_state_dir()/'logs'
            logdir.mkdir(parents=True,exist_ok=True)
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            path=logdir/f'{stamp}-{mode}-{secrets.token_hex(3)}.log'
            self.job={'state':'running','mode':mode,'started_at':dt.datetime.now(dt.timezone.utc).isoformat(),
                      'finished_at':None,'exit_code':None,'error':None,'lines':[], 'log_path':str(path)}
            t=threading.Thread(target=self._execute,args=(cmd,cwd,env,path),daemon=True)
            t.start()
            return self.snapshot()

    def _execute(self,cmd:list[str],cwd:Path,env:dict[str,str],path:Path) -> None:
        try:
            with path.open('w',encoding='utf-8') as handle:
                self._log('Executing WordBench; evidence remains unapproved until reviewed.',handle)
                flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
                proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                    text=True,encoding='utf-8',errors='replace',bufsize=1,creationflags=flags)
                with self.lock: self.process=proc
                assert proc.stdout is not None
                with proc.stdout:
                    for line in proc.stdout:
                        self._log(line.rstrip('\r\n'),handle)
                code=proc.wait()
                with self.lock:
                    self.job['exit_code']=code
                    if self.job['state'] != 'stopped':
                        self.job['state']='completed' if code==0 else 'failed'
        except Exception as exc:
            with self.lock:
                self.job['state']='failed'
                self.job['error']=str(exc)
                self.job['lines'].append('ERROR: '+str(exc))
        finally:
            with self.lock:
                self.process=None
                self.job['finished_at']=dt.datetime.now(dt.timezone.utc).isoformat()
            if self.on_finished:
                try:self.on_finished()
                except Exception:pass

    def _log(self,line:str,handle:Any) -> None:
        handle.write(line+'\n');handle.flush()
        with self.lock:
            self.job['lines'].append(line[:2000])
            if len(self.job['lines'])>600:
                self.job['lines']=self.job['lines'][-600:]

    def stop(self) -> None:
        with self.lock:
            proc=self.process
            if self.job['state']!='running': raise RuntimeError('No active job')
            self.job['state']='stopped'
        if proc and proc.poll() is None:
            if os.name=='nt':
                subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],
                               capture_output=True,timeout=15,check=False)
            else:proc.terminate()

    def snapshot(self) -> dict[str,Any]:
        with self.lock:
            j=self.job
            return {k:(list(v) if isinstance(v,list) else v) for k,v in j.items()}

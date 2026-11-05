"""Loopback-only local UI for Ars Magna Defluens (Python standard library).

This app is an operational *local coordinator*, not the GitOps service described
as a future architecture in the original repository documentation.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import secrets
import threading
from urllib.parse import parse_qs, urlsplit
import webbrowser
import os
import subprocess
import sys

from . import __version__
from .core import ROOT, Settings, ReportIndex, JobRunner, LANGUAGES, LANGUAGE_NAMES, SCENARIOS
from .semantik import SemantikClient
from .acceptance import CoreAcceptance, report_name, save_report
from .qualification import CoreQualification, qualification_name, write_qualification
from .lexical import LexicalCoordinator

STATIC = Path(__file__).resolve().parent / 'static'

class ConsoleApp:
    def __init__(self, settings: Settings | None = None):
        self.settings=settings or Settings()
        self.reports=ReportIndex(self.settings)
        self.runner=JobRunner(self.settings)
        self.semantik=SemantikClient(self.settings.paths)
        self.core_acceptance=CoreAcceptance(self.semantik)
        self.core_qualification=CoreQualification(self.semantik)
        self.lexical=LexicalCoordinator(self.settings.paths)
        self.token=secrets.token_urlsafe(28)
        self.httpd:ThreadingHTTPServer | None=None

    def status(self) -> dict:
        return {'version':__version__,'product':'Ars Magna Defluens',
                'paths':self.settings.paths, 'health':self.settings.health(),
                'languages':[{ 'code':code,'fr':LANGUAGE_NAMES[code][0],'en':LANGUAGE_NAMES[code][1]} for code in LANGUAGES],
                'capabilities':list(SCENARIOS),
                'latest':self.reports.latest(),'history':self.reports.history(),
                'job':self.runner.snapshot(),
                'notice':'Technical GF candidate generation is not linguistic certification.'}

    def open_system(self, target: str, *, launch: bool = False) -> dict:
        if launch and target not in ('wordbench','observatory'):
            raise ValueError('Only installed WordBench/Observatory launchers can be started')
        if target=='defluens': path=ROOT
        elif target in ('wordbench','observatory','compendium','rgl','reports','alignment','semantik','runtime_orchestrator','dik'):
            path=Path(self.settings.paths[target])
        else:raise ValueError('Unknown target')
        if launch:
            if os.name != 'nt':raise RuntimeError('Windows launchers are available only on Windows')
            filename='launch_gui.bat' if target=='wordbench' else 'Launch_Observatory.bat'
            launcher=path/filename
            if not launcher.is_file():raise FileNotFoundError(f'Launcher not found: {launcher}')
            # The launchers are existing local project files, not browser-supplied commands.
            os.startfile(str(launcher))
            return {'message':f'Started {target}', 'path':str(launcher)}
        if not path.is_dir():
            raise FileNotFoundError(f'Directory does not exist: {path}')
        if os.name=='nt':os.startfile(str(path))
        elif sys.platform=='darwin':subprocess.Popen(['open',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:subprocess.Popen(['xdg-open',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return {'message':f'Opened {target}', 'path':str(path)}

class Handler(BaseHTTPRequestHandler):
    server:ThreadingHTTPServer
    protocol_version='HTTP/1.1'

    def log_message(self,fmt,*args):
        # Suppress access log; never log authorization token in GET URL.
        pass

    @property
    def app(self) -> ConsoleApp:
        return self.server.console_app  # type: ignore[attr-defined]

    def _send(self,code:int,body:bytes,content_type:str,headers:dict[str,str]|None=None,csp:str|None=None) -> None:
        self.send_response(code)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',csp or "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
        if headers:
            for k,v in headers.items():self.send_header(k,v)
        self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError):pass

    def _json(self,code:int,obj:dict) -> None:
        self._send(code,json.dumps(obj,ensure_ascii=False).encode('utf-8'),'application/json; charset=utf-8')

    def _authorized(self) -> bool:
        return secrets.compare_digest(self.headers.get('X-Defluens-Token',''),self.app.token)

    def do_GET(self):
        u=urlsplit(self.path)
        if u.path.startswith('/api/'):
            if not self._authorized():return self._json(403,{'error':'Unauthorized local UI request'})
            try:
                if u.path=='/api/status':return self._json(200,self.app.status())
                if u.path=='/api/lexical/status':return self._json(200,self.app.lexical.status())
                if u.path=='/api/semantik/capabilities':return self._json(200,self.app.semantik.capabilities())
                if u.path=='/api/semantik/example':return self._json(200,self.app.semantik.example())
                if u.path=='/api/semantik/practical-intents':return self._json(200,self.app.semantik.practical_intents())
                if u.path=='/api/semantik/pilot':return self._json(200,self.app.semantik.pilot_examples())
                if u.path=='/api/semantik/candidate':return self._json(200,self.app.semantik.candidate_status())
                if u.path=='/api/semantik/core-catalog':return self._json(200,self.app.semantik.core_catalog())
                if u.path=='/api/semantik/core-status':return self._json(200,self.app.semantik.core_status())
                if u.path=='/api/semantik/attribute-status':return self._json(200,self.app.semantik.candidate_status('defluens-attribute-fr-1'))
                if u.path=='/api/language':
                    lang=parse_qs(u.query).get('code',[''])[0]
                    return self._json(200,self.app.reports.language(lang))
                return self._json(404,{'error':'Unknown endpoint'})
            except (ValueError,FileNotFoundError,OSError) as exc:
                return self._json(400,{'error':str(exc)})
        if u.path in ('/','/index.html'):
            target=STATIC/'index.html'
        elif u.path=='/tour':
            target=STATIC/'tour.html'
        else:
            fragment=u.path.lstrip('/')
            target=(STATIC/fragment).resolve()
            if not target.is_relative_to(STATIC.resolve()):
                return self._json(403,{'error':'Forbidden'})
        if not target.is_file():return self._json(404,{'error':'Not found'})
        ct=mimetypes.guess_type(target.name)[0] or 'application/octet-stream'
        try:
            tour_csp = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                        "img-src data: 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; "
                        "base-uri 'none'; frame-ancestors 'none'") if u.path == '/tour' else None
            return self._send(200,target.read_bytes(),ct+'; charset=utf-8' if ct.startswith(('text/','application/javascript')) else ct,csp=tour_csp)
        except OSError:return self._json(500,{'error':'Unable to read asset'})

    def do_POST(self):
        u=urlsplit(self.path)
        if not u.path.startswith('/api/'):
            return self._json(404,{'error':'Unknown endpoint'})
        if not self._authorized():return self._json(403,{'error':'Unauthorized local UI request'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n < 0 or n > 24_000: raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(n) or b'{}')
            if not isinstance(data,dict):raise ValueError('Invalid body')
            if u.path=='/api/lexical/handoff':
                return self._json(200,self.app.lexical.diK_handoff(data.get('observations',''),data.get('locale','')))
            if u.path=='/api/lexical/bindings':
                return self._json(200,self.app.lexical.wordbench_bindings(data.get('knowledge_bundle',''),data.get('review_file','')))
            if u.path=='/api/lexical/inspect':
                return self._json(200,self.app.lexical.inspect(data.get('bundle','')))
            if u.path=='/api/semantik/request':
                return self._json(200,self.app.semantik.request(data.get('action',''),data.get('request')))
            if u.path=='/api/semantik/practical-preview':
                return self._json(200,self.app.semantik.practical_preview(data.get('language',''),data.get('capability','')))
            if u.path=='/api/semantik/core-request':
                return self._json(200,self.app.semantik.core_request(data.get('recipe')))
            if u.path=='/api/semantik/core-build':
                return self._json(200,self.app.semantik.core_build(data.get('language')))
            if u.path=='/api/semantik/core-preview':
                return self._json(200,self.app.semantik.core_preview(data.get('recipe')))
            if u.path=='/api/semantik/core-qualification':
                # Deliberately structural-only over HTTP. GF real mode uses the
                # explicit local Windows CLI and its 600-second upstream budget.
                if data != {'mode':'structural'}:
                    raise ValueError('Browser qualification permits structural mode only')
                result=self.app.core_qualification.run('structural')
                directory=Path(self.app.settings.paths['reports']).parent/'core_qualification'
                report_path,review_path=write_qualification(result,directory/qualification_name(result))
                return self._json(200,{
                    'schema_version':'1.0','status':result['status'],
                    'structural_passed':result['structural_passed'],
                    'cross_language_parity_passed':result['cross_language_parity_passed'],
                    'totals':result['totals'], 'report_path':str(report_path),
                    'review_path':str(review_path), 'released':False,
                    'real_gf_candidate_passed':False,
                    'not_yet_qualified':result['not_yet_qualified'],
                    'failures':[{'case_id':x['case_id'],'error':x.get('error','')}
                                for x in result['cases'] if x['status']=='FAILED']})
            if u.path=='/api/semantik/core-acceptance':
                # Browser mode is structural only: real GF is a separate explicit
                # terminal command, not a long-running HTTP operation.
                if data != {'mode':'structural'}:
                    raise ValueError('Browser audit supports only structural mode')
                result=self.app.core_acceptance.run('structural')
                directory=Path(self.app.settings.paths['reports']).parent/'core_acceptance'
                path=save_report(result,directory/report_name(result))
                return self._json(200,{
                    'schema_version':'1.0', 'status':result['status'],
                    'structural_passed':result['structural_passed'],
                    'real_gf_candidate_passed':False, 'released':False,
                    'totals':result['totals'], 'report_path':str(path),
                    'failures':[{'case_id':row['case_id'], 'error':row.get('error','')}
                                for row in result['cases'] if row['status']=='FAILED']})
            if u.path=='/api/semantik/core-preview-many':
                return self._json(200,self.app.semantik.core_preview_many(data.get('recipe'),data.get('languages')))
            if u.path=='/api/semantik/attribute-request':
                return self._json(200,self.app.semantik.attribute_request(data.get('subject'),data.get('attribute'),data.get('polarity'),data.get('tense')))
            if u.path=='/api/semantik/attribute-build':
                return self._json(200,self.app.semantik.build_candidate('defluens-attribute-fr-1'))
            if u.path=='/api/semantik/attribute-preview':
                return self._json(200,self.app.semantik.preview_candidate(data.get('request'), 'defluens-attribute-fr-1'))
            if u.path=='/api/semantik/build':
                return self._json(200,self.app.semantik.build_candidate())
            if u.path=='/api/semantik/preview':
                return self._json(200,self.app.semantik.preview_candidate(data.get('request')))
            if u.path=='/api/semantik/render-many':
                return self._json(200,self.app.semantik.render_many(data.get('request'),data.get('languages')))
            if u.path=='/api/semantik/readiness':
                return self._json(200,self.app.semantik.readiness(data.get('language',''),data.get('profile','')))
            if u.path=='/api/settings':
                if self.app.runner.snapshot()['state']=='running':
                    raise RuntimeError('Wait for the active campaign to end before changing paths')
                self.app.settings.update(data.get('paths'))
                self.app.semantik=SemantikClient(self.app.settings.paths)
                self.app.core_acceptance=CoreAcceptance(self.app.semantik)
                self.app.core_qualification=CoreQualification(self.app.semantik)
                self.app.lexical=LexicalCoordinator(self.app.settings.paths)
                return self._json(200,{'ok':True,'paths':self.app.settings.paths,'health':self.app.settings.health()})
            if u.path=='/api/run':
                return self._json(200,{'ok':True,'job':self.app.runner.start(data.get('mode',''))})
            if u.path=='/api/stop':
                self.app.runner.stop()
                return self._json(200,{'ok':True})
            if u.path=='/api/open':
                return self._json(200,{'ok':True,**self.app.open_system(data.get('target',''),launch=False)})
            if u.path=='/api/launch':
                return self._json(200,{'ok':True,**self.app.open_system(data.get('target',''),launch=True)})
            if u.path=='/api/quit':
                self._json(200,{'ok':True})
                threading.Thread(target=self.server.shutdown,daemon=True).start()
                return
            return self._json(404,{'error':'Unknown endpoint'})
        except (ValueError,RuntimeError,OSError,subprocess.SubprocessError,TypeError) as exc:
            return self._json(400,{'error':str(exc)})

    def do_OPTIONS(self):
        # No CORS; API is same-origin only, with an unguessable authorization token.
        self._json(403,{'error':'Cross-origin requests are not supported'})

def start(*,port:int=0,open_browser:bool=True,settings:Settings|None=None,
          on_ready=None) -> ThreadingHTTPServer:
    app=ConsoleApp(settings)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.daemon_threads=True
    server.console_app=app # type: ignore[attr-defined]
    app.httpd=server
    address=f'http://127.0.0.1:{server.server_address[1]}/?token={app.token}'
    if on_ready:on_ready(server,address)
    print('Ars Magna Defluens local console:',address,flush=True)
    if open_browser:threading.Timer(0.5,lambda:webbrowser.open(address)).start()
    return server

def main(argv:list[str]|None=None) -> int:
    ap=argparse.ArgumentParser(description='Launch the local Ars Magna Defluens control plane')
    ap.add_argument('--port',type=int,default=0,help='Optional localhost port; random by default')
    ap.add_argument('--no-browser',action='store_true')
    args=ap.parse_args(argv)
    server=start(port=args.port,open_browser=not args.no_browser)
    try:server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:pass
    finally:server.server_close()
    return 0

if __name__=='__main__':raise SystemExit(main())

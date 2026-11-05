"""Tests for local Defluens launcher and evidence boundary."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock
import urllib.error
import urllib.request
import zipfile

from console.core import Settings, ReportIndex, JobRunner, LANGUAGES, normalize_gf_display
from console.server import start

class ConsoleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.defaults={k:str(self.root/k) for k in ('wordbench','observatory','compendium','rgl','gf','reports','alignment')}
        self.settings=Settings(self.root/'settings.json',defaults=self.defaults)

    def test_settings_local_only_and_absolute(self):
        self.assertEqual(self.settings.paths['wordbench'],str(self.root/'wordbench'))
        self.settings.update({'wordbench':str(self.root/'updated')})
        s=Settings(self.root/'settings.json',defaults=self.defaults)
        self.assertEqual(s.paths['wordbench'],str(self.root/'updated'))
        for invalid in [{'evil':'foo'}, {'wordbench':'relative/path'}, {'wordbench':''}]:
            with self.assertRaises(ValueError):s.update(invalid)

    def _fixture_zip(self):
        folder=self.root/'reports'; folder.mkdir()
        archive=folder/'defluens-batch-full-fixture.zip'
        summary={'schema_id':'defluens.pilot-batch','batch_id':'fixture','mode':'full',
           'started_at':'2026-11-03T20:00:00Z','semantic_coverage_verified':False,
           'entries':[{'language':'Fre','status':'candidate_for_review','scenarios_attempted':2,
               'totals':{'candidate_for_review':2,'probe_failed':0,'timeout':0}}]}
        pilot={'language':'Fre','run_id':'myfixture','semantic_coverage_verified':False,
               'scenarios':[{'id':'factual-negation','meaning_en':'Mira is not ready.',
                             'candidate':"Mira n' &+ est pas prête",'status':'candidate_for_review'},
                            {'id':'past-event','meaning_en':'Mira arrived.',
                             'candidate':'Mira est arrivée','status':'candidate_for_review'}]}
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('defluens-batch-fixture/batch_summary.json',json.dumps(summary))
            z.writestr('defluens-batch-fixture/languages/defluens-pilot-Fre-foo/pilot_run.json',json.dumps(pilot))
        return archive

    def test_reports_are_read_only_and_preserve_raw(self):
        archive=self._fixture_zip()
        orig=archive.read_bytes()
        idx=ReportIndex(self.settings)
        summary=idx.latest()
        self.assertIsNotNone(summary)
        self.assertEqual(summary['totals']['candidates'],2)
        self.assertEqual(summary['totals']['attempted'],2)
        self.assertFalse(summary['semantic_coverage_verified'])
        data=idx.language('Fre')
        self.assertEqual(data['scenarios'][0]['candidate'],"Mira n'est pas prête")
        self.assertEqual(data['scenarios'][0]['raw'],"Mira n' &+ est pas prête")
        self.assertEqual(archive.read_bytes(),orig)
        self.assertEqual(normalize_gf_display("n' &+ est"),"n'est")
        with self.assertRaises(ValueError):idx.language('Bogus')

    def _stub_tools(self):
        path=Path(self.settings.paths['wordbench'])/'src'/'gf_wordbench'/'practical'
        path.mkdir(parents=True)
        (path/'batch.py').write_text('# fixture',encoding='utf-8')
        (path/'alignment14.py').write_text('# fixture',encoding='utf-8')
        rgl=Path(self.settings.paths['rgl'])/'src'/'abstract'
        rgl.mkdir(parents=True)
        Path(self.settings.paths['gf']).write_bytes(b'fake gf')

    def test_command_uses_fixed_language_scope_not_shell(self):
        self._stub_tools()
        runner=JobRunner(self.settings)
        for mode in ('check','smoke','full','compare'):
            cmd,cwd,env=runner.command(mode)
            self.assertEqual(cwd,Path(self.settings.paths['wordbench']))
            self.assertEqual(cmd[0],__import__('sys').executable)
            self.assertEqual(cmd[1:3],['-u','-m'])
            self.assertIn('PYTHONPATH',env)
            if mode in ('smoke','full'):
                self.assertEqual(cmd[-len(LANGUAGES):],list(LANGUAGES))
        with self.assertRaises(ValueError):runner.command('rm -rf .')

    def test_actual_check_process_runs_in_wordbench_directory(self):
        """Execute a harmless local Python fixture through the real subprocess boundary."""
        import time
        self._stub_tools()
        pkg=Path(self.settings.paths['wordbench'])/'src'/'gf_wordbench'
        (pkg/'__init__.py').write_text('',encoding='utf-8')
        (pkg/'practical'/'__init__.py').write_text('',encoding='utf-8')
        (pkg/'practical'/'alignment14.py').write_text(
            'import sys; print("CHECK_FIXTURE_EXECUTED", sys.argv[1], flush=True)',encoding='utf-8')
        runner=JobRunner(self.settings)
        with mock.patch('console.core.local_state_dir',return_value=self.root/'state'):
            runner.start('check')
            deadline=time.monotonic()+12
            while runner.snapshot()['state']=='running' and time.monotonic()<deadline:
                time.sleep(.05)
            result=runner.snapshot()
        self.assertEqual(result['state'],'completed',result)
        self.assertEqual(result['exit_code'],0)
        self.assertTrue(any('CHECK_FIXTURE_EXECUTED' in x for x in result['lines']))
        self.assertTrue(Path(result['log_path']).is_file())

    def test_token_guards_api_and_settings(self):
        self._fixture_zip()
        server=start(open_browser=False,settings=self.settings)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        host=f'http://127.0.0.1:{server.server_address[1]}'
        def get(uri,token=None):
            headers={'X-Defluens-Token':token} if token else {}
            return urllib.request.urlopen(urllib.request.Request(host+uri,headers=headers),timeout=3)
        with self.assertRaises(urllib.error.HTTPError) as ctx:get('/api/status')
        self.assertEqual(ctx.exception.code,403)
        with get('/api/status',server.console_app.token) as r:
            status=json.load(r)
        self.assertEqual(status['latest']['totals']['candidates'],2)
        with get('/api/language?code=Fre',server.console_app.token) as r:
            data=json.load(r)
        self.assertEqual(data['scenarios'][0]['candidate'],"Mira n'est pas prête")
        with get('/') as r:
            self.assertIn('Ars Magna Defluens',r.read().decode('utf-8'))
            self.assertIn("script-src 'self'", r.headers.get('Content-Security-Policy',''))
        with get('/tour') as r:
            self.assertIn('Guided Tour',r.read().decode('utf-8'))
            self.assertIn("script-src 'unsafe-inline'",r.headers.get('Content-Security-Policy',''))
        with self.assertRaises(urllib.error.HTTPError) as ctx:get('/../core.py')
        self.assertIn(ctx.exception.code,(403,404))

if __name__ == '__main__':unittest.main()

"""Defluens connects only via public SA and Orchestrator CLI boundaries."""
from __future__ import annotations
import json
from pathlib import Path
from unittest import mock
import unittest
from console.semantik import SemantikClient

class SemantikIntegrationTests(unittest.TestCase):
    def test_missing_upstream_is_not_synthetic_render(self):
        client=SemantikClient({'semantik':'/nonexistent'})
        with self.assertRaises(FileNotFoundError):client.request('render',{'obligations':[1]})
    def test_request_uses_public_cli_and_stdin_no_shell(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            cli=root/'src/semantik_architect/adapters/inbound/cli/main.py';cli.parent.mkdir(parents=True)
            cli.write_text('# stub')
            client=SemantikClient({'semantik':str(root)})
            with mock.patch('console.semantik.subprocess.run') as runner:
                runner.return_value=mock.Mock(returncode=0,stdout=json.dumps({'plain_text':'real output'}),stderr='')
                result=client.request('render',{'schema_version':'1.0'})
                self.assertTrue(result['ok']);self.assertEqual(result['result']['plain_text'],'real output')
                call=runner.call_args
                argv=call.args[0]
                self.assertIn('semantik_architect.adapters.inbound.cli.main',argv)
                self.assertIn('render',argv)
                self.assertEqual(argv[-1],'-')
                self.assertFalse(call.kwargs['shell'])
                self.assertEqual(json.loads(call.kwargs['input'])['schema_version'],'1.0')
    def test_upstream_error_preserved(self):
        with mock.patch('console.semantik.subprocess.run') as runner:
            runner.return_value=mock.Mock(returncode=2,stdout='',stderr='{"code":"SA-RUNTIME-001","message_safe":"Not released"}')
            result=SemantikClient._call(Path('/tmp'),'example.module',['render'])
        self.assertFalse(result['ok']);self.assertEqual(result['exit_code'],2)
        self.assertEqual(result['result']['code'],'SA-RUNTIME-001')
    def test_readiness_input_must_be_constrained(self):
        client=SemantikClient({})
        with self.assertRaises(ValueError):client.readiness('fr && echo','orgo-1')
        with self.assertRaises(ValueError):client.readiness('fr','../file')

class HandoffJobTests(unittest.TestCase):
    def test_handoff_invokes_wordbench_development_tool_not_release(self):
        from console.core import Settings, JobRunner
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            wb=root/'wordbench'
            practical=wb/'src'/'gf_wordbench'/'practical'
            practical.mkdir(parents=True)
            (practical/'batch.py').write_text('')
            (practical/'alignment14.py').write_text('')
            (practical/'semantik_handoff.py').write_text('')
            reports=root/'reports';reports.mkdir()
            (reports/'defluens-batch-full-01.zip').write_bytes(b'fixture')
            defaults={'wordbench':str(wb),'rgl':str(root/'not_needed_rgl'),
                      'gf':str(root/'not_needed_gf'),'reports':str(reports),
                      'alignment':str(root/'alignment')}
            settings=Settings(root/'settings.json',defaults=defaults)
            cmd,_,_=JobRunner(settings).command('handoff')
            self.assertIn('gf_wordbench.practical.semantik_handoff',cmd)
            self.assertIn('--archive',cmd)
            self.assertIn('defluens-batch-full-01.zip',' '.join(cmd))
            self.assertNotIn('release',cmd)

class SemanticEndpointTests(unittest.TestCase):
    def test_local_http_endpoint_requires_token_and_preserves_upstream_status(self):
        from console.core import Settings
        from console.server import start
        import tempfile, urllib.request, urllib.error, threading
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            defaults={key:str(root/key) for key in ('wordbench','observatory','compendium','rgl','gf','reports','alignment','semantik','runtime_orchestrator')}
            server=start(open_browser=False,settings=Settings(root/'settings.json',defaults=defaults))
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            try:
                endpoint=f'http://127.0.0.1:{server.server_address[1]}/api/semantik/request'
                body=json.dumps({'action':'render','request':{'schema_version':'1.0'}}).encode('utf-8')
                with mock.patch.object(server.console_app.semantik,'request',return_value={
                    'ok':False,'exit_code':2,'result':{'code':'SA-RUN-001','message_safe':'Not released'}}):
                    req=urllib.request.Request(endpoint,data=body,method='POST',headers={
                        'X-Defluens-Token':server.console_app.token,'Content-Type':'application/json'})
                    with urllib.request.urlopen(req,timeout=4) as response:
                        result=json.load(response)
                    self.assertFalse(result['ok'])
                    self.assertEqual(result['result']['code'],'SA-RUN-001')
                    req=urllib.request.Request(endpoint,data=body,method='POST')
                    with self.assertRaises(urllib.error.HTTPError) as caught:
                        urllib.request.urlopen(req,timeout=4)
                    self.assertEqual(caught.exception.code,403)
            finally:
                server.shutdown();server.server_close()

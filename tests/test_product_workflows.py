"""Execute product-skill workflows against the installed Maida command contract."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


class ProductWorkflows(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, MAIDA_DATA_DIR=str(self.root / 'known'),
                        MAIDA_USAGE_PING='0', MAIDA_REDACT='1')
        self.env.pop('PYTHONPATH', None)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.reviewed_init = '--from-run' in self.cli('init', '--help').stdout

    def cli(self, *args, expected=0, payload=None):
        result = subprocess.run([sys.executable, '-m', 'maida.cli', *args],
                                cwd=self.root, env=self.env, text=True,
                                input=json.dumps(payload) if payload else None,
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def trace(self, *, broken=False):
        code = '''from maida import traced_run, record_tool_call
with traced_run(name="inspect-tests"):
    for _ in range(REPEATS):
        record_tool_call("read_config", args={"api_key": "fixture-secret"}, result="pytest")
'''.replace('REPEATS', '5' if broken else '1')
        result = subprocess.run([sys.executable, '-c', code], cwd=self.root,
                                env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def review(self):
        if self.reviewed_init:
            self.cli('init', '--from-run', 'latest')
            self.assertFalse((self.root / '.maida/policy.yaml').exists())
            review = self.root / '.maida/starter/review.json'
            self.assertTrue(json.loads(review.read_text())['review_required'])
            self.cli('init', '--reviewed', '--reason', 'Task must complete without recorded loops or guardrail stops')
            self.assertFalse(json.loads(review.read_text())['review_required'])
            return ((self.root / '.maida/policy.yaml').read_bytes(),
                    (self.root / '.maida/baselines/agent.json').read_bytes())
        self.cli('extract', '--window', str(self.root / 'known/runs'), '--out', 'draft')
        draft = json.loads((self.root / 'draft/draft.json').read_text())
        self.assertTrue(draft['review_required'])
        self.assertFalse((self.root / '.maida/policy.yaml').exists())
        self.assertEqual(len(draft['workflows']), 1)
        pair = self.root / 'draft' / draft['workflows'][0]['artifact_dir']
        policy = yaml.safe_load((pair / 'policy.yaml').read_text())
        # The fixture owner explicitly adopts only these observed contracts.
        policy['metrics'] = {key: val for key, val in policy['metrics'].items()
                             if key in {'no_loops', 'no_guardrails', 'stop_condition_reached'}}
        self.assertEqual(len(policy['metrics']), 3)
        target = self.root / '.maida'
        (target / 'baselines').mkdir(parents=True)
        (target / 'policy.yaml').write_text(yaml.safe_dump(policy))
        shutil.copyfile(pair / 'baseline.json', target / 'baselines/agent.json')
        return ((target / 'policy.yaml').read_bytes(),
                (target / 'baselines/agent.json').read_bytes())

    def gate(self, expected, verdict):
        result = self.cli('drift', '--window', str(Path(self.env['MAIDA_DATA_DIR']) / 'runs'),
                          '--baseline', '.maida/baselines/agent.json',
                          '--policy', '.maida/policy.yaml', '--format', 'json', expected=expected)
        report = json.loads(result.stdout)
        self.assertEqual(report['verdict'].lower(), verdict)
        return report

    def test_review_pass_regression_and_repair_without_rebaseline(self):
        self.trace()
        originals = self.review()
        for label, broken, exit_code, verdict in [('good', False, 0, 'pass'),
                                                  ('bad', True, 1, 'fail'),
                                                  ('repaired', False, 0, 'pass')]:
            self.env['MAIDA_DATA_DIR'] = str(self.root / label)
            self.trace(broken=broken)
            self.gate(exit_code, verdict)
        self.assertEqual((self.root / '.maida/policy.yaml').read_bytes(), originals[0])
        self.assertEqual((self.root / '.maida/baselines/agent.json').read_bytes(), originals[1])
        self.assertNotIn('fixture-secret', ''.join(p.read_text() for p in self.root.rglob('*.jsonl')))

    def test_missing_evidence_cannot_become_a_baseline(self):
        result = self.cli('extract', '--window', str(self.root / 'missing/runs'),
                          '--out', 'draft', expected=2)
        self.assertTrue(result.stderr.strip())
        self.assertFalse((self.root / 'draft').exists())
        self.assertFalse((self.root / '.maida/policy.yaml').exists())

    def capture(self, session, tool='Read'):
        common = {'session_id': session, 'cwd': str(self.root)}
        for payload in [
            {'hook_event_name': 'SessionStart', 'source': 'startup'},
            {'hook_event_name': 'PreToolUse', 'tool_use_id': 'read-one',
             'tool_name': tool, 'tool_input': {'file_path': 'pyproject.toml'}},
            {'hook_event_name': 'PostToolUse', 'tool_use_id': 'read-one',
             'tool_name': tool, 'tool_input': {'file_path': 'pyproject.toml'},
             'tool_response': {'content': 'pytest'}},
            {'hook_event_name': 'SessionEnd', 'reason': 'other'},
        ]:
            result = self.cli('capture', 'claude-hook', payload={**common, **payload})
            self.assertEqual(result.stdout, '')

    def test_first_report_needs_no_baseline_or_policy(self):
        self.capture('first-read-only-task')
        self.cli('assert', '--expect-status', 'ok', '--no-loops', '--no-guardrails')
        self.assertFalse((self.root / '.maida/policy.yaml').exists())
        self.assertFalse((self.root / '.maida/baselines').exists())

    def test_coding_agent_hooks_import_one_completed_task(self):
        self.capture('offline-skill-task')
        runs = list((self.root / 'known/runs').glob('*/meta.json'))
        self.assertEqual(len(runs), 1)
        self.assertEqual(json.loads(runs[0].read_text())['status'], 'ok')
        self.review()
        self.gate(0, 'pass')

    def test_fresh_sessions_evaluate_adopted_invariants_without_changing_identity(self):
        tutorials = Path(os.environ.get('MAIDA_TUTORIALS_PATH',
                         str(Path(__file__).resolve().parents[2] / 'maida-tutorials')))
        helper = tutorials / 'onboarding/gate_capture.py'
        self.assertTrue(helper.is_file(), 'Set MAIDA_TUTORIALS_PATH to the reviewed tutorials checkout')
        self.capture('known-session')
        self.review()
        policy_path = self.root / '.maida/policy.yaml'
        policy = yaml.safe_load(policy_path.read_text())
        # Explicit fixture-owner decision: inspect-tests must read the config.
        policy['metrics'] = {'required_tools': {'kind': 'invariant', 'all_of': ['Read']}}
        policy_path.write_text(yaml.safe_dump(policy))
        baseline = self.root / '.maida/baselines/agent.json'
        original = baseline.read_bytes()
        for session, tool, exit_code, verdict in [
            ('fresh-good', 'Read', 0, 'pass'),
            ('fresh-bad', 'Write', 1, 'fail'),
            ('fresh-repaired', 'Read', 0, 'pass'),
        ]:
            self.env['MAIDA_DATA_DIR'] = str(self.root / session)
            self.capture(session, tool)
            trace_files = list((self.root / session / 'runs').rglob('*'))
            trace_bytes = {p: p.read_bytes() for p in trace_files if p.is_file()}
            if self.reviewed_init:
                result = self.cli('assert', '--baseline', str(baseline), '--policy', str(policy_path),
                                  '--format', 'json', expected=exit_code)
                report = json.loads(result.stdout)
                self.assertEqual(report['passed'], verdict == 'pass')
                self.assertEqual(baseline.read_bytes(), original)
                self.assertEqual({p: p.read_bytes() for p in trace_bytes}, trace_bytes)
                continue
            result = subprocess.run([
                sys.executable, str(helper), '--window', str(self.root / session / 'runs'),
                '--baseline', str(baseline), '--policy', str(policy_path),
                '--same-task', '--format', 'json',
            ], cwd=self.root, env=self.env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['verdict'].lower(), verdict)
            mapping = report['capture_task_comparison']
            self.assertNotEqual(mapping['baseline_source_run_name'], mapping['candidate_source_run_name'])
            self.assertEqual(baseline.read_bytes(), original)
            self.assertEqual({p: p.read_bytes() for p in trace_bytes}, trace_bytes)


if __name__ == '__main__':
    unittest.main()

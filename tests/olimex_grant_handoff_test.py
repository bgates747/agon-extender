"""Exercise grant notification using an isolated registry and mailbox."""

import io
from contextlib import redirect_stderr, redirect_stdout
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import olimex_grant_handoff as handoff


class GrantHandoffTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.thread, self.turn, self.message, self.scheduler = (str(uuid4()) for _ in range(4))
        self.grant = dict(owner='fixture-owner', request='abc123abc123',
                          generation=7, lease=uuid4().hex, phase='admission',
                          hardware_ready=False, plan='/source/test-plan.md',
                          notify_thread=self.thread, notify_host='test-pi')
        self.write('grant.json', self.grant)
        self.write('current.json', {'active': self.grant})
        self.write('scheduler-contact.json', dict(mailbox='olimex-scheduler',
                   notify_thread=self.scheduler, notify_host='test-pi'))

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data))

    def invoke(self, thread, response):
        argv = ['tool', '--grant', str(self.root / 'grant.json'),
                '--authorization-thread', thread, '--authorization-turn', self.turn,
                '--authorization-message', self.message]
        out, err = io.StringIO(), io.StringIO()
        with (patch.object(sys, 'argv', argv),
              patch.object(handoff, 'STATE', self.root),
              patch.object(handoff.agentcoms, 'DEFAULT', self.root / 'mailbox'),
              patch.object(handoff.subprocess, 'run', side_effect=response) as wake,
              redirect_stdout(out), redirect_stderr(err)):
            code = handoff.main()
        return code, out.getvalue(), err.getvalue(), wake

    def test_delivers_mail_before_waking_original_chat(self):
        def wake(argv, **kwargs):
            mail, = handoff.agentcoms.records(self.root / 'mailbox')
            self.assertEqual(mail['recipient'], self.grant['owner'])
            self.assertIn(self.grant['lease'], mail['body'])
            self.assertIn(self.message, mail['body'])
            self.assertIn('hardware_ready=false', mail['body'])
            self.assertIn(mail['message_id'], kwargs['input'])
            self.assertNotIn(self.grant['lease'], kwargs['input'])
            self.assertEqual(argv[argv.index('--thread') + 1], self.thread)
            return subprocess.CompletedProcess(argv, 0, '{"phase":"accepted"}', '')

        code, output, _, delivery = self.invoke(self.thread, wake)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)['wake']['phase'], 'accepted')
        delivery.assert_called_once()

    def test_wrong_chat_and_stale_grant_publish_nothing(self):
        for wrong_chat in (True, False):
            with self.subTest(wrong_chat=wrong_chat):
                if not wrong_chat:
                    self.write('current.json', {'active': dict(self.grant, lease=uuid4().hex)})
                code, _, _, delivery = self.invoke(str(uuid4()) if wrong_chat else self.thread, [])
                self.assertEqual(code, 1)
                self.assertFalse((self.root / 'mailbox').exists())
                delivery.assert_not_called()

    def test_preserves_prefixed_human_message_id(self):
        self.message = 'msg_' + self.message
        code, _, _, delivery = self.invoke(
            self.thread, [subprocess.CompletedProcess([], 0, '{"phase":"accepted"}', '')])
        self.assertEqual(code, 0)
        mail, = handoff.agentcoms.records(self.root / 'mailbox')
        self.assertIn(self.message, mail['body'])
        delivery.assert_called_once()

    def test_timeout_leaves_mail_and_reports_uncertain_wake(self):
        code, _, error, delivery = self.invoke(
            self.thread, subprocess.TimeoutExpired('pi_chat.py', 45))
        self.assertEqual(code, 1)
        self.assertIn('Inspect wake delivery', error)
        self.assertEqual(len(handoff.agentcoms.records(self.root / 'mailbox')), 1)
        delivery.assert_called_once()


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Deliver an existing Olimex grant to its authorized project chat on the Pi."""

import argparse
import json
import re
from pathlib import Path
import subprocess
import sys
from uuid import UUID

import agentcoms


ENV = Path(__file__).resolve().parents[2] / 'agon-dev-env'
STATE = ENV / 'cross-agent/olimex-bench/state'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def handoff(grant, active, contact, thread, turn, message):
    if not active or grant != active:
        raise ValueError('The receipt does not match the current central grant')
    if grant['phase'] != 'admission' or grant['hardware_ready'] is not False:
        raise ValueError('This handoff is only for a grant awaiting physical admission')
    thread = str(UUID(thread))
    if thread != grant['notify_thread']:
        raise ValueError('The grant must point to the original authorizing project chat')
    turn = str(UUID(turn))
    if message.startswith('msg_'):
        message = 'msg_' + str(UUID(message.removeprefix('msg_')))
    else:
        message = str(UUID(message))
    source = str(UUID(contact['notify_thread']))
    if source == thread or contact['notify_host'] != grant['notify_host']:
        raise ValueError('Use the separate local project chat for this Pi handoff')
    if contact['mailbox'] != 'olimex-scheduler':
        raise ValueError('Use the current Olimex scheduler contact')
    request = grant['request']
    if not re.fullmatch('[a-f0-9]{12}', request) or type(grant['generation']) is not int:
        raise ValueError('Invalid central request or generation')
    delivery_id = f'olimex-{grant["generation"]}-{request}-grant'
    body = (
        f'Olimex lease {grant["generation"]} is granted to {grant["owner"]} '
        f'for request {request}. Lease token {grant["lease"]}. '
        'Phase admission, hardware_ready=false. The project chat is the sole operator.\n\n'
        f'Original human authorization in this project chat: turn {turn}, message {message}. '
        f'Plan: {grant["plan"]}. Assert the live lease and complete fresh physical admission '
        'before installing firmware or running the test. Carry out only the original human scope '
        'under normal tool review, including any manual invocation or cleanup conditions. '
        'Send the scheduler the actual handback and release disposition.\n'
    )
    mail = dict(author=contact['mailbox'], recipient=grant['owner'],
                request_id=delivery_id, thread_id='olimex-grants', body=body)
    return source, delivery_id, mail


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--grant', type=Path, required=True, help='Saved central grant result')
    parser.add_argument('--authorization-thread', required=True)
    parser.add_argument('--authorization-turn', required=True)
    parser.add_argument('--authorization-message', required=True)
    args = parser.parse_args()
    try:
        grant = read_json(args.grant)
        active = read_json(STATE / 'current.json')['active']
        contact = read_json(STATE / 'scheduler-contact.json')
        source, delivery_id, mail = handoff(
            grant, active, contact, args.authorization_thread,
            args.authorization_turn, args.authorization_message)
        receipt = agentcoms.send(agentcoms.DEFAULT, mail)
        alert = (
            f'Olimex lease {grant["generation"]} granted for admission. '
            f'Read durable mail {receipt["message_id"]}. This project chat is the sole operator '
            'under its original human authorization. Hardware readiness is pending.'
        )
        try:
            result = subprocess.run(
                [str(ENV / '.venv/bin/python'), str(ENV / 'scripts/pi_chat.py'), 'send',
                 '--source-thread', source, '--thread', grant['notify_thread'],
                 '--resume', '--delivery-id', delivery_id, '--message-file', '-'],
                input=alert, text=True, capture_output=True, timeout=45)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RuntimeError(
                f'Mail {receipt["message_id"]} saved. Inspect wake delivery {delivery_id} '
                'before any further send.') from error
        if result.returncode:
            raise RuntimeError(
                f'Mail {receipt["message_id"]} saved. Inspect wake delivery {delivery_id} '
                f'before any further send. {result.stderr.strip()}')
        print(json.dumps(dict(mail=receipt, wake=json.loads(result.stdout)), indent=2))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f'Olimex handoff: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

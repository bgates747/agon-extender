import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sdcard_staged', ROOT/'scripts/sdcard_staged.py')
staged = importlib.util.module_from_spec(spec)
spec.loader.exec_module(staged)


class Response(io.BytesIO):
    status = 200


class Fake:
    def __init__(self, client, data=b''):
        self.client = client
        self.payload = data
        self.calls = []
        self.lost_post = self.lost_delete = self.truncate = False
        self.result = dict(protocol=1, boot=101, id=0, phase=0, bytes=0, size=0,
                           records=0, error=0, remote_status=0, filesystem=0,
                           stage_us=1, mainboard_us=2)

    def request(self, method='GET', suffix='', data=None, headers=None):
        self.calls.append((method, suffix))
        if method == 'POST':
            # Durable state must exist before any externally mutating request.
            persisted = json.loads(self.client.path.read_text())['job']
            assert persisted['id'] == int(headers['X-Extender-Job'], 16)
            if headers['X-Extender-Operation'] == 'put':
                self.payload = data
            size = len(self.payload)
            self.result.update(id=persisted['id'], phase=4, bytes=size, size=size)
            if self.lost_post:
                raise TimeoutError('Lost admission response after acceptance')
            response = Response(json.dumps(self.result).encode())
            response.status = 202
            return response
        if method == 'DELETE':
            self.result.update(id=0, phase=0)
            if self.lost_delete:
                raise TimeoutError('Lost release response')
            return Response(b'Released')
        if suffix == '/data':
            return Response(self.payload[:-1] if self.truncate else self.payload)
        return Response(json.dumps(self.result).encode())


class StagedClientTests(unittest.TestCase):
    def fixture(self, directory, data=b''):
        client = staged.Client('http://fixture', Path(directory)/'state.json')
        fake = Fake(client, data)
        client.request = fake.request
        self.addCleanup(client.close)
        return client, fake

    def test_upload_one_bulk_http_and_job_boundary_journal(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp)
            data = bytes(range(256))*4300
            source = Path(temp)/'source'
            source.write_bytes(data)
            saves = []
            original = client.save
            def save():
                saves.append(True)
                original()
            client.save = save
            result = client.begin('put', '/test/file', source=source, activate=True)
            self.assertEqual(result['bytes'], len(data))
            self.assertEqual(fake.payload, data)
            self.assertEqual(fake.calls.count(('POST', '')), 1)
            self.assertEqual(fake.calls.count(('DELETE', '')), 1)
            self.assertEqual(len(saves), 3)  # submit, delivered, released; not per212B
            self.assertIsNone(client.state['job'])
            self.assertTrue(client.state['last']['delivered'])

    def test_download_empty_and_binary(self):
        for payload in (b'', bytes(range(256))*300):
            with self.subTest(size=len(payload)), tempfile.TemporaryDirectory() as temp:
                client, fake = self.fixture(temp, payload)
                out = Path(temp)/'download'
                client.begin('get', '/test/file', destination=out)
                self.assertEqual(out.read_bytes(), payload)
                self.assertEqual(fake.calls.count(('GET', '/data')), 1)
                self.assertEqual(len(list(Path(temp).glob('*.p4part'))), 0)

    def test_uncertain_admission_resume_observes_never_resubmits(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp)
            source = Path(temp)/'source';source.write_bytes(b'abc')
            fake.lost_post = True
            with self.assertRaises(TimeoutError):
                client.begin('put', '/test/file', source=source, activate=True)
            self.assertIsNotNone(json.loads(client.path.read_text())['job'])
            with self.assertRaises(staged.TransferError):
                client.begin('put', '/test/other', source=source, activate=True)
            client.resume()
            self.assertEqual(fake.calls.count(('POST', '')), 1)

    def test_lost_cleanup_uses_durable_delivery_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp)
            source = Path(temp)/'source';source.write_bytes(b'abc')
            fake.lost_delete = True
            with self.assertRaises(TimeoutError):
                client.begin('put', '/test/file', source=source, activate=True)
            self.assertTrue(json.loads(client.path.read_text())['job']['delivered'])
            client.resume()
            self.assertIsNone(client.state['job'])
            self.assertEqual(fake.calls.count(('POST', '')), 1)
            self.assertEqual(fake.calls.count(('DELETE', '')), 1)

    def test_truncated_http_download_reuses_same_p4_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp, b'abcdef')
            out = Path(temp)/'download';fake.truncate = True
            with self.assertRaises(staged.TransferError):
                client.begin('get', '/test/file', destination=out)
            self.assertFalse(out.exists())
            fake.truncate = False
            client.resume()
            self.assertEqual(out.read_bytes(), b'abcdef')
            self.assertEqual(fake.calls.count(('POST', '')), 1)
            self.assertEqual(fake.calls.count(('GET', '/data')), 2)

    def test_crash_between_output_publication_and_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp, b'abcdef')
            out = Path(temp)/'download'
            original = client.save
            def crash():
                if client.state['job'] and client.state['job'].get('delivered'):
                    raise RuntimeError('Simulated crash before completion journal')
                original()
            client.save = crash
            with self.assertRaises(RuntimeError):
                client.begin('get', '/test/file', destination=out)
            # Reload exactly what a restarted process can know.
            client.state = json.loads(client.path.read_text());client.save = original
            client.resume()
            self.assertEqual(out.read_bytes(), b'abcdef')
            self.assertEqual(fake.calls.count(('GET', '/data')), 1)

    def test_reset_or_failed_job_keeps_evidence(self):
        for reset in (False, True):
            with self.subTest(reset=reset), tempfile.TemporaryDirectory() as temp:
                client, fake = self.fixture(temp)
                source = Path(temp)/'source';source.write_bytes(b'abc');fake.lost_post = True
                with self.assertRaises(TimeoutError):
                    client.begin('put', '/test/file', source=source, activate=True)
                if reset:
                    fake.result['boot'] += 1
                else:
                    fake.result.update(phase=5, error=4, remote_status=6, filesystem=1)
                with self.assertRaises(staged.TransferError):client.resume()
                self.assertTrue(client.state['job'])
                self.assertNotIn(('DELETE', ''), fake.calls)

    def test_existing_output_and_invalid_paths_fail_before_admission(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp)
            out = Path(temp)/'keep';out.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):client.begin('get', '/test/a', destination=out)
            for path in ('test/a', '/test/../a', '/test/a\r\nX: bad', '/test//a', '/test/a/'):
                with self.assertRaises(ValueError):client.begin('get', path, destination=Path(temp)/'new')
            self.assertEqual(out.read_bytes(), b'keep')
            self.assertEqual(fake.calls, [])

    def test_exclusive_state_owner(self):
        with tempfile.TemporaryDirectory() as temp:
            client, _ = self.fixture(temp)
            with self.assertRaises(staged.TransferError):staged.Client(client.url, client.path)

    def test_stage_only_put_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as temp:
            client, fake = self.fixture(temp)
            source = Path(temp)/'source';source.write_bytes(b'abc')
            with self.assertRaises(ValueError):client.begin('put', '/test/file', source=source)
            self.assertEqual(fake.calls, [])


if __name__ == '__main__':
    unittest.main()

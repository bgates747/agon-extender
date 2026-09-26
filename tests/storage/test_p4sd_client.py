"""Real localhost HTTP peer tests for CLI framing; not ESP-IDF/SD qualification."""
import importlib.util
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import urlsplit, parse_qs
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('p4sd', ROOT / 'scripts/p4sd.py')
p4sd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p4sd)


class Peer(BaseHTTPRequestHandler):
    files = {}
    calls = []

    def log_message(self, *args):
        pass

    def handle_request(self):
        url = urlsplit(self.path)
        params = {k: v[0] for k, v in parse_qs(url.query).items()}
        self.calls.append((self.command, url.path, params))
        path = params.get('path')
        if self.command != 'GET':
            assert self.headers['X-Extender-Storage'] == '1'
        if self.command == 'PUT':
            assert self.headers.get('Transfer-Encoding') is None
            size = int(self.headers['Content-Length'])
            self.files[path] = self.rfile.read(size)
        if url.path == '/file' and self.command == 'GET':
            data = self.files[path]
        elif url.path == '/stat':
            data = json.dumps({'directory': path == '/tree'}).encode()
        elif url.path == '/list':
            data = json.dumps([
                {'path': '/tree/sub', 'directory': True},
                {'path': '/tree/sub/a.bin', 'directory': False},
            ]).encode()
        else:
            data = b'{"message":"ok"}'
        self.send_response(200)
        self.send_header('Content-Length', str(len(data) + (10 if path == '/broken' else 0)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_POST = do_PUT = do_DELETE = handle_request


class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Peer)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_binary_and_tree_transfers(self):
        client = p4sd.Client(self.url)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / 'source'
            src.write_bytes(bytes(range(256)) * 1000)
            client.put(src, '/space & plus+.bin')
            self.assertEqual(Peer.files['/space & plus+.bin'], src.read_bytes())
            dst = root / 'download'
            client.get('/space & plus+.bin', dst)
            self.assertEqual(dst.read_bytes(), src.read_bytes())
            with self.assertRaises(FileExistsError):
                client.get('/space & plus+.bin', dst)
            client.get('/space & plus+.bin', dst, replace=True)
            tree = root / 'tree'
            (tree / 'sub').mkdir(parents=True)
            (tree / 'sub/a.bin').write_bytes(b'payload')
            client.put(tree, '/tree', recursive=True)
            self.assertEqual(Peer.files['/tree/sub/a.bin'], b'payload')
            client.get('/tree', root / 'out', recursive=True)
            self.assertEqual((root / 'out/sub/a.bin').read_bytes(), b'payload')

    def test_interrupted_download_preserves_destination(self):
        Peer.files['/broken'] = b'partial'
        client = p4sd.Client(self.url)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'keep'
            target.write_bytes(b'original')
            with self.assertRaises(OSError):
                client.get_file('/broken', target, replace=True)
            self.assertEqual(target.read_bytes(), b'original')
            self.assertEqual(list(Path(tmp).iterdir()), [target])

    def test_command_dispatch(self):
        cases = [
            (['status'], 'GET', '/status', {}),
            (['stat', '/a'], 'GET', '/stat', {'path': '/a'}),
            (['list', '/', '-r'], 'GET', '/list', {'path': '/', 'recursive': '1'}),
            (['mkdir', '/a/b', '-p'], 'POST', '/directory', {'path': '/a/b', 'parents': '1'}),
            (['delete', '/old', '-r'], 'DELETE', '/entry', {'path': '/old', 'recursive': '1'}),
            (['move', '/a', '/b'], 'POST', '/move', {'path': '/a', 'to': '/b'}),
            (['copy', '/a', '/b', '-r', '--replace'], 'POST', '/copy', {'path': '/a', 'to': '/b', 'recursive': '1', 'replace': '1'}),
            (['search', '/', '--name', '*.txt', '--contains', 'a b'], 'GET', '/search', {'path': '/', 'name': '*.txt', 'contains': 'a b', 'recursive': '1'}),
        ]
        for args, method, endpoint, params in cases:
            with self.subTest(args=args), redirect_stdout(io.StringIO()):
                self.assertEqual(p4sd.main(['--url', self.url] + args), 0)
                self.assertEqual(Peer.calls[-1], (method, endpoint, params))


if __name__ == '__main__':
    unittest.main()

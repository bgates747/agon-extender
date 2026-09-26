#!/usr/bin/env python3
"""Sessionless client for the P4-local card HTTP service (not Agon sdserve)."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import http.client
import tempfile
import urllib.error
import urllib.parse
import urllib.request


class Client:
    def __init__(self, url, timeout=120):
        self.url = url.rstrip('/')
        self.timeout = timeout

    def request(self, endpoint, method='GET', data=None, length=None, **query):
        params = {k: str(int(v)) if isinstance(v, bool) else str(v)
                  for k, v in query.items() if v is not None}
        url = self.url + endpoint + '?' + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        headers = {}
        if method != 'GET':
            headers['X-Extender-Storage'] = '1'
        if length is not None:
            headers['Content-Length'] = str(length)
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        return urllib.request.urlopen(req, timeout=self.timeout)

    def json(self, endpoint, method='GET', **query):
        with self.request(endpoint, method, **query) as response:
            return json.load(response)

    def put_file(self, source, destination, replace=False):
        with Path(source).open('rb') as stream:
            chunks = iter(lambda: stream.read(65536), b'')
            with self.request('/file', 'PUT', chunks, os.fstat(stream.fileno()).st_size,
                              path=destination, replace=replace) as response:
                return json.load(response)

    def get_file(self, source, destination, replace=False):
        destination = Path(destination)
        if destination.exists() and not replace:
            raise FileExistsError(destination)
        # Only install the local destination after a complete HTTP download.
        name = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
                name = output.name
                with self.request('/file', path=source) as response:
                    expected = response.headers.get('Content-Length')
                    received = 0
                    while chunk := response.read(65536):
                        output.write(chunk)
                        received += len(chunk)
                    if expected is not None and received != int(expected):
                        raise OSError('Incomplete download; destination not changed')
                output.flush()
                os.fsync(output.fileno())
            if replace:
                os.replace(name, destination)
            else:
                os.link(name, destination)  # no-clobber install on Linux/macOS
        finally:
            if name and os.path.exists(name):
                os.unlink(name)

    def put(self, source, destination, recursive=False, replace=False):
        source = Path(source)
        if source.is_symlink():
            raise ValueError('Symlinks are not supported')
        if not source.is_dir():
            return self.put_file(source, destination, replace)
        if not recursive:
            raise ValueError('Directory upload requires --recursive')
        self.json('/directory', 'POST', path=destination, parents=True)
        for base, dirs, files in os.walk(source):
            dirs.sort()
            files.sort()
            for name in dirs + files:
                local = Path(base) / name
                if local.is_symlink():
                    raise ValueError(f'Symlinks are not supported: {local}')
                remote = destination.rstrip('/') + '/' + local.relative_to(source).as_posix()
                if local.is_dir():
                    self.json('/directory', 'POST', path=remote, parents=True)
                else:
                    self.put_file(local, remote, replace)
        return {'message': 'Uploaded tree'}

    def get(self, source, destination, recursive=False, replace=False):
        item = self.json('/stat', path=source)
        if not item['directory']:
            self.get_file(source, destination, replace)
            return {'message': 'Downloaded file'}
        if not recursive:
            raise ValueError('Directory download requires --recursive')
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        for item in self.json('/list', path=source, recursive=True):
            remote = PurePosixPath(item['path'])
            relative = remote.relative_to(PurePosixPath(source))
            if '..' in relative.parts or '\\' in str(relative) or not relative.parts:
                raise ValueError('Invalid remote tree entry')
            local = destination / str(relative)
            # Do not follow existing host symlinks outside the requested tree.
            if not local.resolve().is_relative_to(destination.resolve()):
                raise ValueError('Host path escapes destination')
            if item['directory']:
                local.mkdir(parents=True, exist_ok=True)
            else:
                local.parent.mkdir(parents=True, exist_ok=True)
                self.get_file(str(remote), local, replace)
        return {'message': 'Downloaded tree'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='http://P4_HOST:8080')
    parser.add_argument('--timeout', type=float, default=120)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    for command in ('stat', 'list', 'search', 'mkdir', 'delete'):
        p = sub.add_parser(command)
        p.add_argument('path')
        if command in ('list', 'search', 'delete'):
            p.add_argument('-r', '--recursive', action='store_true', default=command == 'search')
        if command == 'search':
            p.add_argument('--name', default='*', help='Case-insensitive basename glob (* and ?)')
            p.add_argument('--contains', help='Case-sensitive literal ASCII content')
        if command == 'mkdir':
            p.add_argument('-p', '--parents', action='store_true')
    for command in ('put', 'get', 'copy', 'move'):
        p = sub.add_parser(command)
        p.add_argument('source')
        p.add_argument('destination')
        if command != 'move':
            p.add_argument('-r', '--recursive', action='store_true')
            p.add_argument('--replace', action='store_true')
    args = parser.parse_args(argv)
    client = Client(args.url, args.timeout)
    command = args.command
    try:
        if command in ('put', 'get'):
            result = getattr(client, command)(args.source, args.destination, args.recursive, args.replace)
        elif command in ('copy', 'move'):
            options = {'path': args.source, 'to': args.destination}
            if command == 'copy':
                options.update(recursive=args.recursive, replace=args.replace)
            result = client.json('/' + command, 'POST', **options)
        else:
            options = {k: v for k, v in vars(args).items()
                       if k not in ('url', 'timeout', 'command')}
            endpoint = {'mkdir': '/directory', 'delete': '/entry'}.get(command, '/' + command)
            method = {'mkdir': 'POST', 'delete': 'DELETE'}.get(command, 'GET')
            result = client.json(endpoint, method, **options)
        print(json.dumps(result, indent=2))
        return 0
    except urllib.error.HTTPError as error:
        parser.exit(1, f'HTTP {error.code}: {error.read().decode("utf-8", "replace")}\n')
    except (OSError, ValueError, urllib.error.URLError, http.client.HTTPException) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    raise SystemExit(main())

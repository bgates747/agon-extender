"""Pinned complete dual-root USB host override, leaving IDF PHY/HAL untouched.

The former PHY-only backport cannot enable both ports: IDF5.5.5's hub.c still
selects just BIT1. Espressif USB1.6.0 supplies the dependent host/hub/enumerator
changes together. Only the generated HCD/USBH derivatives are locally adapted;
archive extraction never edits SDK or pristine component sources.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'vdp/compat/usb_dual_host'
ARCHIVE_SHA = 'da5be2a2743ede3bd63e6c4046e381e24b16567ea8a7541b6f5d094abea5098b'
HCD_SHA = 'aa0e6e26981130abe1c13759c191eaaca06c5a11da1439a4d7b4d326f0d6dde8'
USBH_SHA = '7082caadb7d863540434137b8400e946c802e44be630e217d71109ae619cff3a'


def inventory() -> dict:
    record = json.loads((PACKAGE / 'component.json').read_text())
    archive = PACKAGE / 'usb-1.6.0.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA or record['archive_sha256'] != ARCHIVE_SHA:
        raise SystemExit('USB1.6.0 archive identity differs')
    return record


def prepare(project: Path) -> dict:
    """Extract precisely the pinned 28 regular files into a fresh override."""
    record = inventory()
    component = project / 'components/usb'
    if component.exists():
        raise SystemExit('USB override destination must be fresh')
    expected = {item['path']: item for item in record['files']}
    with zipfile.ZipFile(PACKAGE / 'usb-1.6.0.zip') as archive:
        files = [entry for entry in archive.infolist() if not entry.is_dir()]
        if len(files) != len(expected) or {x.filename for x in files} != set(expected):
            raise SystemExit('USB archive inventory differs')
        contents = []
        for item in files:
            name = PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or name.parts[0] != 'usb' or (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise SystemExit('Unsafe USB archive member')
            data = archive.read(item)
            pin = expected[item.filename]
            if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
                raise SystemExit('USB archive member differs: ' + item.filename)
            contents.append((name, data))
    for name, data in contents:
        target = project / 'components' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    verify(project)
    return record


def verify(project: Path) -> dict:
    """All pristine component files stay pinned, including its hub and headers."""
    record = inventory()
    component = project / 'components/usb'
    actual = {str(path.relative_to(component.parent)) for path in component.rglob('*') if path.is_file()}
    if actual != {item['path'] for item in record['files']}:
        raise SystemExit('USB component inventory differs')
    for item in record['files']:
        path = component.parent / item['path']
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise SystemExit('USB component source differs: ' + item['path'])
    return record


def check_linkage(commands: list[dict], ninja: str, output: Path, sdk: Path) -> None:
    """Prove all host layers, public headers, SDK PHY and archive/ELF ownership."""
    import shlex
    project, build = output / 'project', output / 'build'
    record = verify(project)
    component = project / 'components/usb'
    expected = {Path(item['path']).name: component.parent / item['path']
                for item in record['files'] if item['path'].endswith('.c')}
    expected['hcd_dwc.c'] = build / 'agon-extender-usb/hcd_dwc.c'
    expected['usbh.c'] = build / 'agon-extender-usb/usbh.c'
    expected['usb_phy.c'] = sdk / 'components/usb/usb_phy.c'
    for name, pin in [('hcd_dwc.c', HCD_SHA), ('usbh.c', USBH_SHA)]:
        if hashlib.sha256(expected[name].read_bytes()).hexdigest() != pin:
            raise SystemExit('USB1.6.0 derivative differs: ' + name)
    archive = 'esp-idf/usb/libusb.a'
    edges = [line for line in ninja.splitlines() if line.startswith('build ' + archive + ':')]
    elf = [line for line in ninja.splitlines() if line.startswith('build agon_extender.elf:')]
    if len(edges) != 1 or len(elf) != 1 or archive not in elf[0].split():
        raise SystemExit('USB component archive/ELF ownership differs')
    for name, path in expected.items():
        actions = [c for c in commands if Path(c['file']).name == name]
        if len(actions) != 1 or Path(actions[0]['file']).resolve() != path.resolve():
            raise SystemExit('USB component source selection differs: ' + name)
        obj = actions[0].get('output')
        if not obj or obj not in edges[0].split():
            raise SystemExit('USB component object absent from archive: ' + name)
    public = str((component / 'include').resolve())
    old = str((sdk / 'components/usb/include').resolve())
    for c in commands:
        args = c.get('arguments') or shlex.split(c['command'])
        includes = [x[2:] for x in args if x.startswith('-I')]
        if old in includes and (public not in includes or includes.index(public) > includes.index(old)):
            raise SystemExit('USB consumer selects older public headers first: ' + c['file'])

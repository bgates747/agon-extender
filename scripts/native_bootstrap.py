# Current matched native bootstrap, explicit experimental P4 UART-NM tuple.
# Source correction for actual123: the first read-only display HTTP timeout
# escaped the old60s observation loop before any Agon reset. Retain it as a
# missing sample within that SAME deadline, reset5s stability, preserve serial
# guards and every positive gate. No new reset/retry/test path or production
# selection follows. Old d04f source and original failure remain immutable.
"""One selected clean P4-init then Agon reset after a verified native span.

No firmware writing, retry or application invocation. Uses the commissioned
reset protocol and matched UART-NM P4 build. Use Extender's interpreter for esptool.
The caller supplies actual b.own/ports_free/get, b.c[ports] and b.url, and must
freshly verify setup-only startup before entry. No lease or old build is inferred.
Successful return proves initialization/input, not CLI: caller proves actual CLI
and raw mode/callback/Legacy state after the reset. No invocation or retry.
"""
from pathlib import Path
from urllib.error import URLError
import subprocess, time, sys, json, os
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
def save(path,value):
    with path.open("x") as f:
        json.dump(value,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())

BUILD = b'net-003-r02-b2026-11-06-09-03-07Z'
PAD = b'Parallel boot pads released; awaiting EMOS'
CONSOLE = b'ExCom console ' + BUILD + b' (experimental), UART1 1152000 8N1 RTS/CTS'

def wait_p4_initialization(observe,read_display,raw,*,clock=time.monotonic,record_missing=lambda n,r:None):
    """Same60s deadline/5s positive stability; timeout is a missing sample.

    Only read-only display timeouts qualify. Wrong/fatal serial startup, other
    HTTP/JSON errors and wrong source signatures still fail; no reset is here.
    The caller's observe function retains the existing serial cap/guard.
    """
    deadline=clock()+60;since=None;misses=0
    while clock()<deadline:
        observe(PAD)
        if PAD not in raw or b'build_id='+BUILD not in raw:continue
        try:display=read_display()
        except (TimeoutError,URLError) as error:
            if isinstance(error,URLError) and not isinstance(error.reason,TimeoutError):raise
            since=None;misses+=1
            record_missing(misses,dict(epoch=time.time(),missing_read_only_sample=True,error=repr(error),deadline_extended=False))
            continue
        if display.get('available') and not display.get('rolling',{}).get('faults'):
            if since is None:since=clock()
            if clock()-since>=5:return display,misses
        else:since=None
    raise TimeoutError('Clean current P4 initialization missing; no Agon dispatch')

def clean_bootstrap(b, folder):
    from esptool.reset import HardReset
    import serial as pyserial
    from p4_boot_guard import check_startup
    p = folder / 'clean-bootstrap'; p.mkdir(exist_ok=False)
    b.own(); b.ports_free()
    assert not b.get('/sd/status')['online'] and b.get('/sd/fast')['phase'] == 0
    raw = bytearray()
    # P4 programming USB intentionally resets; passive joined-control readers
    # refuse RTS assertion and must never be used for this operation.
    handle=pyserial.Serial(port=None, baudrate=115200, timeout=.15, exclusive=True)
    handle.dtr=handle.rts=False;handle.port=b.c['ports'][1]
    with handle as serial:
        b.own(); save(p/'p4-reset-issued.json', dict(epoch=time.time(), once=True, no_flash=True))
        HardReset(serial, uses_usb=True).reset()
        def observe(marker):
            raw.extend(serial.read(8192))
            if len(raw) > 4*1024*1024: raise RuntimeError('Bootstrap serial cap; STOP')
            (p/'p4-boot.bin').write_bytes(raw)
            check_startup(bytes(raw), marker)
        display,misses = wait_p4_initialization(
            observe,lambda:b.get('/display/status'),raw,
            record_missing=lambda n,record:save(p/('display-timeout-%03d.json'%n),record))
        assert raw.count(PAD) == 1
        save(p/'p4-initialized.json', dict(epoch=time.time(), build=BUILD.decode(), pad_once=True, display=display, read_only_timeout_samples=misses))
        argv = [str(ROOT/'.venv/bin/python'), str(ROOT/'scripts/reset_agon_usb.py'),
            '--config', str(ROOT/'agents/bench-reset/usb-reset.local.json'), '--verify-url', b.url,
            '--verify-timeout', '60']
        b.own(); save(p/'agon-reset-issued.json', dict(epoch=time.time(), once=True, argv=argv))
        with (p/'agon-reset.log').open('x') as log:
            child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+75
                while child.poll() is None:
                    observe(PAD)
                    if time.monotonic() >= deadline: raise TimeoutError('Original Agon reset bound')
                if child.wait() != 0: raise RuntimeError('Agon admission failed; no retry/RUN')
            finally:
                if child.poll() is None:
                    child.terminate()
                    try: child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill(); child.wait(timeout=3)
        deadline = time.monotonic()+15; since = None
        while time.monotonic() < deadline:
            observe(CONSOLE)
            keyboard = b.get('/keyboard/status'); display = b.get('/display/status')
            if (CONSOLE in raw and keyboard['ready'] and keyboard['physical_neutral']
                    and not keyboard['held'] and not keyboard['pending'] and display.get('available')
                    and not display.get('rolling', {}).get('faults')):
                if since is None: since = time.monotonic()
                if time.monotonic()-since >= 2: break
            else: since = None
        else: raise TimeoutError('Current console/input missing; no RUN')
        assert raw.count(PAD) == 1 and raw.count(CONSOLE) == 1
        save(p/'receipt.json', dict(epoch=time.time(), p4_resets=1, agon_resets=1,
            build=BUILD.decode(), keyboard=keyboard, display=display, no_replay=True))

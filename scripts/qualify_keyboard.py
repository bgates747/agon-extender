#!/usr/bin/env python3
"""Bounded automatic receiver and CLI qualification; never an attended demo.

Precondition: keyprobe is running, followed by one sdserve invocation and a
finite return to CLI. /extender/key-source.txt and sdserve.bin are installed.
Preserve the receipt and a fresh client journal for each SD incarnation.
"""
import argparse
import json
import secrets
from pathlib import Path
import time
from keyboard import Client as Keyboard, KeyboardError, text_events, key_usage
from sdcard import Client as SD, RemoteError, path_payload

def exercise(url,output,*,probe=True,after_boot=None,cursor_cycles=40):
    if not 0<=cursor_cycles<=100:raise ValueError('Cursor cycles must be 0–100')
    output.mkdir(parents=True,exist_ok=False)
    record={'outcome':'fail','scope':'Actual EMOS receiver and ordinary CLI via host keyboard', 'events':[]}
    tag=secrets.token_hex(3)
    target=f'/extender/key-{tag}.txt'
    record['typed_target']=target
    k=Keyboard(url,output/'keyboard.json');s=None
    def online(previous=None,seconds=100):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            c=SD(url,output/'status-only.json')
            try:status=c.status()
            finally:c.lock.close()
            if status['online'] and status['boot']!=previous:return status
            time.sleep(.1)
        raise TimeoutError('SD service did not return')
    def typed(text):
        observed=k.status();events=text_events(text,observed['locale'],observed['caps'])
        k.open(observed);k.send(events);k.cancel();time.sleep(2)
    try:
        deadline=time.monotonic()+30
        while True:
            status=k.status()
            if status['ready'] and status['boot']!=after_boot:break
            if time.monotonic()>deadline:raise TimeoutError('No keyboard admission')
            time.sleep(.05)
        time.sleep(1) # finite fixture reaches its receiver loop after admission
        if probe:
            observed=k.status();k.open(observed)
            k.send(text_events('Aa?@',observed['locale'],observed['caps']))
            k.send([(key_usage(name),down) for name in ('left','right','down','up') for down in (1,0)])
            k.send([(80,1)]);time.sleep(.3);k.cancel() # explicit release
            k.open();k.send([(79,1)]);time.sleep(5.3) # deliberate lost-host timeout
            try:k.wait()
            except KeyboardError:pass
            else:raise AssertionError('Lease did not expire')
            k.cancel();typed('\n')
        initial=online();s=SD(url,output/'sd-before.json');s.connect()
        if probe:
            receipt=s.download('/extender/key-seen.txt').decode()
            (output/'key-seen.txt').write_text(receipt)
            rows=[list(map(int,line.split(','))) for line in receipt.splitlines()[1:]]
            expected=[0,65,65,0,97,97,0,63,63,0,0,64,64,0,8,8,21,21,10,10,11,11,8,8,21,21,13,13]
            if 'complete=1' not in receipt or [r[0] for r in rows]!=expected:
                raise AssertionError('Receiver byte sequence mismatch: '+receipt)
            if any(r[3] and not r[4] for r in rows) or rows[-1][4]:
                raise AssertionError('Held-key map/release mismatch: '+receipt)
            record['receiver']=receipt
        source=s.download('/extender/key-source.txt')
        try:s.rpc(2,path_payload(target))
        except RemoteError as error:
            if error.status!=6 or error.detail!=b'\x04':raise
        else:raise AssertionError('CLI target already exists; refusing a false positive')
        launch=f'/extender/key-run-{tag}.txt'
        s.upload(launch,b'LOAD /extender/sdserve.bin\r\nRUN . /\r\n',True)
        record['launch_batch']=launch
        # The precondition matters: both Escape and network EXIT return to the
        # caller, which can be the next line of a still-open MOS batch. Only
        # exiting its FINAL foreground command establishes an ordinary CLI.
        s.rpc(11)
        s.lock.close();s=None;time.sleep(.5)
        # Deliberately mistype the final filename character, then edit it using
        # the retained Backspace mapping before submitting the MOS COPY command.
        typed('COPY /extender/key-source.txt '+target[:-1]+'z')
        k.open()
        # Many small HTTP renewals interleaved with console event processing
        # reproduce the attended cursor-demo scheduling context. Each pair
        # restores the cursor before the final correction/COPY submission.
        for _ in range(cursor_cycles):
            k.send([(80,1),(80,0)]);k.send([(79,1),(79,0)])
        record['cursor_batches']=2*cursor_cycles
        k.send([(42,1),(42,0)]);k.send(text_events('t\n',k.status()['locale']));k.cancel()
        # Physical screen readback showed XEC after a correct COPY: its first E
        # arrived before MOS's new line-editor waitKey was ready. This small
        # known copy gets a conservative handover pause; LOAD/RUN ordering is
        # still owned by the helper batch, not inferred from this delay.
        time.sleep(2)
        # A keyboard acknowledgement is not command completion. Let MOS order
        # LOAD then RUN inside a verified finite batch, instead of assuming a
        # 300 ms host sleep is sufficient for every physical SD load.
        typed('EXEC '+launch+'\n')
        final=online(initial['boot'],30);s=SD(url,output/'sd-after.json');s.connect()
        result=s.download(target)
        if result!=source:raise AssertionError('Typed COPY/edit command did not produce expected file')
        record['cli_copy_edit_and_service_launch']='pass';record['service_before']=initial;record['service_after']=final
        record['launch_order']='Typed EXEC; MOS batch runs LOAD to completion before RUN; final service holds only this helper batch open'
        # Keep a bounded SD write/read regression alongside the new input path.
        data=bytes(range(256))*2+b'keyboard and SD coexist\n'
        sd_target=f'/extender/key-sd-{tag}.bin'
        s.upload(sd_target,data,True)
        if s.download(sd_target)!=data:raise AssertionError('SD regression')
        record['sd_roundtrip_bytes']=len(data);record['outcome']='pass'
        return record
    except Exception as error:
        record['error']=repr(error);raise
    finally:
        if s:s.lock.close()
        k.lock.close();(output/'result.json').write_text(json.dumps(record,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url',required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--skip-probe',action='store_true')
    p.add_argument('--after-boot',type=int,help='Require a fresh admission epoch after a host-controlled reset')
    p.add_argument('--cursor-cycles',type=int,default=40)
    a=p.parse_args();print(json.dumps(exercise(a.url,a.output,probe=not a.skip_probe,after_boot=a.after_boot,cursor_cycles=a.cursor_cycles),indent=2))

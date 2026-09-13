#!/usr/bin/env python3
"""One BENCH-001 trial from the known EMOS prompt, returning to that prompt.

The caller supplies the already-installed app/data paths. No reset, flash,
filesystem modification or automatic recovery into a new keyboard epoch.
"""
import json
from pathlib import Path
import time
from keyboard import Client,KeyboardError,text_events
from rally_drive import Sample,run

def quit_game(url,folder,admission):
    client=Client(url,Path(folder)/'quit.json')
    try:
        status=client.status()
        if (not admission or admission['reason'] or
                (status['boot'],status['session'])!=(admission['boot'],admission['session']) or
                not status['physical_neutral'] or not status['ready'] or status['reason'] not in (0,1)):
            raise KeyboardError('Exit deferred: keyboard ownership changed; do not interrupt the Author')
        client.open(status)
        client.send([(41,1)])
        # A tap can occur entirely between game key-map polls. Hold across
        # several observed render periods; explicit release follows it.
        time.sleep(.7);client.send([(41,0)]);client.cancel()
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            if not client.http('/telemetry/latest')['online']:
                time.sleep(.3)
                if not client.http('/telemetry/latest')['online']:
                    return {'telemetry_stopped':True,'escape_held_seconds':.7}
            time.sleep(.1)
        raise RuntimeError('Rally still publishes after Escape; do not type CLI commands')
    finally:
        if client.state.get('active') and not client.state.get('pending'):
            client.cancel()
        client.lock.close()

def launch(url,folder,data_directory,binary,track='oval',steering_step=None):
    client=Client(url,Path(folder)/'launch.json');admission=None
    try:
        if client.http('/telemetry/latest')['online']:
            raise RuntimeError('Previous Rally still running; a fresh CLI start is required')
        observed=client.status();client.open(observed)
        steering_option='' if steering_step is None else ' steer'+str(steering_step)
        commands=['CD '+data_directory,'LOAD '+binary,
                  'RUN . '+track+' race telemetry engine grip200'+steering_option]
        for command in commands:
            client.send(text_events(command+'\n',observed['locale'],observed['caps']))
            time.sleep(1) # Key emission is not completion of a MOS command.
        admission=client.status();client.cancel()
        deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            value=client.http('/telemetry/latest')
            if value['online']:
                sample=Sample.decode(value)
                if (sample.grip!=200 or sample.contacts or sample.speed or
                        steering_step is not None and sample.step!=steering_step):
                    raise RuntimeError('Expected a fresh stationary race at grip200')
                (Path(folder)/'startup.json').write_text(json.dumps(value,indent=2)+'\n')
                return admission
            time.sleep(.05)
        raise RuntimeError('Fresh Rally did not publish within 45 seconds')
    finally:
        if client.state.get('active') and not client.state.get('pending'):client.cancel()
        client.lock.close()

def set_grip(url,folder,grip):
    if not 25<=grip<=200 or grip%5:raise ValueError('Grip must be 25..200 in steps of five')
    client=Client(url,Path(folder)/'grip.json')
    try:
        client.open();held=None;deadline=time.monotonic()+8
        while True:
            sample=Sample.decode(client.http('/telemetry/latest'))
            desired=45 if sample.grip>grip else 46 if sample.grip<grip else None
            if desired!=held:
                if held is not None:client.send([(held,0)])
                if desired is not None:client.send([(desired,1)])
                held=desired
            if desired is None:
                time.sleep(.25)
                sample=Sample.decode(client.http('/telemetry/latest'))
                if sample.grip==grip:
                    (Path(folder)/'grip-confirmed.json').write_text(json.dumps(sample.__dict__,indent=2)+'\n')
                    return
            if time.monotonic()>deadline:raise RuntimeError('Could not settle requested grip with ordinary keys')
            time.sleep(.02)
    finally:
        if client.state.get('active') and not client.state.get('pending'):client.cancel()
        client.lock.close()

def trial(url,folder,seconds,data_directory,binary,maximum_speed=300,grip=200,corner_reserve=.58,steering_step=None):
    folder=Path(folder)
    admission=launch(url,folder,data_directory,binary,steering_step=steering_step)
    result={}
    try:
        if grip!=200:set_grip(url,folder,grip)
        result=run(url,folder/'keyboard.json',folder/'telemetry.jsonl',seconds,maximum_speed,
                   corner_reserve=corner_reserve)
        admission=None if result.get('release_error') else result.get('exit_admission')
    finally:
        try:result['exit']=quit_game(url,folder,admission)
        except Exception as failure:result['exit_error']=repr(failure)
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

#!/usr/bin/env python3
"""Read P4 screen text over HTTP without taking the video connection."""
import argparse,time,urllib.request,urllib.error
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--url',required=True)
p.add_argument('--timeout',type=float,default=30)
a=p.parse_args();end=time.monotonic()+a.timeout
while True:
    with urllib.request.urlopen(a.url.rstrip('/')+'/screen/text',timeout=a.timeout) as r:
        body=r.read().decode('utf-8')
        if r.status==200:
            print(body,end='');break
        if r.status!=202:raise RuntimeError(f'Unexpected response: {r.status}')
    if time.monotonic()>=end:raise TimeoutError('Text capture pending; retry to retrieve it')
    time.sleep(.2)

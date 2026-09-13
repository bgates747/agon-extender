#!/usr/bin/env python3
"""Plot archived Rally practice; no hardware or emulator access."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(budget_path, output):
    budget=json.loads(budget_path.read_text())
    fig,axes=plt.subplots(4,2,figsize=(13,10),layout='constrained')
    for row,grip in enumerate((200,180,160,140)):
        left,right=axes[row];offset=0.;runs=0
        left.axhspan(-16,16,color='#d9e9ec');left.axhline(0,color='#567780',linewidth=.6)
        left.axhline(78,color='#a55',linestyle=':',linewidth=.7)
        left.axhline(-78,color='#a55',linestyle=':',linewidth=.7)
        for record in budget['runs']:
            if record['grip']!=grip:continue
            samples=[json.loads(line) for line in (Path(record['folder'])/'telemetry.jsonl').read_text().splitlines()]
            if not samples:continue
            runs+=1
            times=np.array([(offset+s['seconds'])/60 for s in samples])
            lateral=np.array([s['lateral']/256 for s in samples])
            left.plot(times,lateral,linewidth=.5,color='#276777')
            left.plot(times,[s['target_lane'] for s in samples],linewidth=.4,color='#cd923f',alpha=.6)
            previous=samples[0]['contacts']
            for t,s in zip(times,samples):
                if s['contacts']!=previous:left.scatter(t,s['lateral']/256,c='#b82535',marker='x',zorder=4)
                previous=s['contacts']
                lap=s.get('completed_lap')
                if lap:
                    right.scatter(t,lap['seconds'],s=10,c='#276777' if lap['clean'] else '#b82535')
            offset+=record['seconds']
            left.axvline(offset/60,color='#888',linewidth=.4,alpha=.5)
        for axis in (left,right):
            axis.set_xlim(0,15);axis.grid(axis='x',alpha=.15)
            axis.spines[['top','right']].set_visible(False)
            axis.set_xlabel('Active practice in this grip block (minutes)')
        left.set_ylim(-90,90);left.set_ylabel(f'{grip}% grip\nLateral position (world units)')
        right.set_ylabel('Interpolated lap time (seconds)')
        right.axhline(8,color='#888',linestyle=':',linewidth=.7)
        right.set_ylim(bottom=7.5)
        if not runs:right.text(.5,.5,'Not yet run',transform=right.transAxes,ha='center',color='#777')
    axes[0,0].set_title('Position and requested lane; centre band ±16 units')
    axes[0,1].set_title('Clean laps blue; contact/grass laps red')
    fig.suptitle('Physical Agon Rally — telemetry-driven practice',fontsize=16)
    fig.text(.5,-.025,'Manual physics; host keyboard control. Vertical lines separate fresh runs. '
             'Lap timing uncertainty: one telemetry interval. Instrumented frame rate is not production FPS.',
             ha='center',fontsize=9)
    fig.savefig(output,dpi=150,bbox_inches='tight');plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('budget',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    plot(args.budget,args.output)

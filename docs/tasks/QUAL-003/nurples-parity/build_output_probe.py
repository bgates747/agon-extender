"""Isolate the installed r22 source; transplant only existing output timing scopes.

No deployment. Parent input/output tree is read-only. This is an agent-assigned
Nurples diagnostic variant, not a production or qualified firmware revision.
"""
import argparse,configparser,datetime,hashlib,json,os,shutil,subprocess
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--lookahead',action='store_true');p.add_argument('--packed-row',action='store_true');p.add_argument('--dispatch-timing',action='store_true');p.add_argument('--uart-alignment',action='store_true');p.add_argument('--output-below-parser',action='store_true');p.add_argument('--row-timing',action='store_true');p.add_argument('--internal-framebuffer',action='store_true');p.add_argument('--internal-game-mode',action='store_true');p.add_argument('--output-draw-core',action='store_true');p.add_argument('--blocking-consumer',action='store_true');p.add_argument('--output-between-tasks',action='store_true');p.add_argument('--row-pair',action='store_true');p.add_argument('--refresh-trace',action='store_true');p.add_argument('--draw-twice',action='store_true');p.add_argument('--draw-four',action='store_true');a=p.parse_args()
 assert a.lookahead, 'Use the frozen d007496 builder for r24; current source is the r25 lookahead experiment'
 root=Path.cwd();parent=a.parent.resolve();out=a.output.resolve()
 assert not subprocess.check_output(['git','status','--porcelain'],text=True)
 meta=json.loads((parent/'manifest.json').read_text());assert meta['build_id']=='uart-excom-console-r22-b2026-09-15-07-01-47Z'
 assert sha(parent/'firmware.bin')=='ccb96bf7e2e9de172732118d5ee93c01d2f6c4ae4b3b953a98881c58c622cdd7'
 out.mkdir(parents=True,exist_ok=False)
 revision='r40' if a.draw_four else 'r39' if a.draw_twice else 'r38' if a.refresh_trace else 'r37' if a.row_pair else 'r36' if a.output_between_tasks else 'r35' if a.blocking_consumer and a.output_draw_core else 'r34' if a.blocking_consumer else 'r33' if a.output_draw_core else 'r32' if a.internal_game_mode else 'r31' if a.internal_framebuffer else 'r30' if a.row_timing else ('r29' if a.output_below_parser else ('r28' if a.uart_alignment else ('r27' if a.dispatch_timing else ('r26' if a.packed_row else 'r25'))))
 assert not a.draw_four or a.draw_twice
 assert not a.draw_twice or a.refresh_trace
 assert not a.refresh_trace or a.row_pair
 assert not a.row_pair or (a.blocking_consumer and not a.output_draw_core and not a.row_timing)
 assert not a.output_between_tasks or (a.blocking_consumer and a.output_draw_core)
 assert not a.blocking_consumer or a.internal_game_mode
 assert not a.output_draw_core or a.internal_game_mode
 assert not a.internal_game_mode or a.internal_framebuffer
 assert not a.internal_framebuffer or (a.output_below_parser and not a.row_timing)
 assert not a.row_timing or a.output_below_parser
 assert not a.output_below_parser or a.uart_alignment
 assert not a.uart_alignment or a.dispatch_timing
 assert not a.dispatch_timing or a.packed_row
 source=parent/'source';tree=out/'source'
 shutil.copytree(source,tree,ignore=shutil.ignore_patterns('.pio','managed_components','__pycache__'))
 pinned={str(f.relative_to(source)):sha(f) for f in source.rglob('*') if f.is_file() and '.pio' not in f.parts and 'managed_components' not in f.parts and '__pycache__' not in f.parts}
 assert all(sha(tree/n)==h for n,h in pinned.items())
 probe_files=('vdp/video/extender/network/wired_network_service.cpp','vdp/video/extender/display/stock_p4_service.cpp','vdp/video/extender/diagnostics/video_timing.hpp','vdp/video/extender/display/drawing_cadence.hpp')
 if a.internal_framebuffer:probe_files+=('vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp',)
 if a.row_timing or a.row_pair:probe_files+=('vdp/video/extender/display/stock_runtime_controller.hpp',)
 if a.lookahead:probe_files+=('vdp/video/extender/display/presentation_snapshot_pool.cpp','vdp/video/extender/display/presentation_snapshot_pool.hpp')
 if a.packed_row:probe_files+=('vdp/video/extender/display/stock_scanline.hpp','vdp/video/extender/display/rgb222_row.hpp')
 if a.dispatch_timing:probe_files+=('vdp/video/extender/network/wired_network_service.hpp',)
 if a.uart_alignment:probe_files+=('vdp/video/extender/transport/console_hardware.inc','vdp/video/extender/transport/console_stream.hpp')
 if a.refresh_trace:probe_files+=('vdp/video/extender/diagnostics/refresh_trace.hpp','vdp/video/vdu_buffered.h','vdp/vendor/vdp-gl/src/displaycontroller.cpp')
 # Parent-to-maintained changes are the explicitly selected output experiments.
 # r23 proved the archived source lacks them: a flag alone was insufficient.
 for n in probe_files:shutil.copy2(root/n,tree/n)
 assert (tree/probe_files[2]).is_file()
 identity_file=tree/'vdp/pio/p4-console-identity.json';record=json.loads(identity_file.read_text());record.update(source_identity='uart-excom-console-'+revision,status='draft',note='Agent-assigned bounded output comparisons; stock drawing retained.')
 identity_file.write_text(json.dumps(record,indent=2)+'\n')
 (tree/'vdp/.pio').mkdir();(tree/'vdp/.pio/packages').symlink_to(root/'vdp/.pio/packages',target_is_directory=True)
 shutil.copytree(source/'vdp/managed_components',tree/'vdp/managed_components')
 shutil.copy2(parent/'sdkconfig',out/'sdkconfig')
 cfg=configparser.ConfigParser(interpolation=None);cfg.optionxform=str;cfg.read(parent/'platformio.ini')
 cfg['platformio']['build_dir']=str(out/'build');cfg['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(out/'sdkconfig')
 assert 'AGON_EXTENDER_VIDEO_TIMING' not in cfg['env:p4-console']['build_flags']
 cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_VIDEO_TIMING=1'
 if a.draw_four:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_DRAW_FOUR=1'
 if a.draw_twice:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_DRAW_TWICE=1'
 if a.refresh_trace:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_REFRESH_TRACE=1'
 if a.row_pair:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_OUTPUT_ROW_PAIR=1'
 if a.output_between_tasks:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_OUTPUT_BETWEEN_TASKS=1'
 if a.blocking_consumer:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_SNAPSHOT_MUTEX=1'
 if a.output_draw_core:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_OUTPUT_DRAW_CORE=1'
 if a.internal_game_mode:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_INTERNAL_GAME_MODE=1'
 if a.internal_framebuffer:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_INTERNAL_FRAMEBUFFER=1'
 if a.row_timing:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_VIDEO_ROW_TIMING=1'
 if a.output_below_parser:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_OUTPUT_BELOW_PARSER=1'
 if a.lookahead:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_SNAPSHOT_LOOKAHEAD=1'
 if a.packed_row:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_PACKED_ROW=1'
 if a.dispatch_timing:cfg['env:p4-console']['build_flags']+='\n-D AGON_EXTENDER_VIDEO_DISPATCH_TIMING=1'
 with (out/'platformio.ini').open('w') as f:cfg.write(f)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ');identity='uart-excom-console-'+revision+'-b'+stamp
 manifest={'build_id':identity,'status':'draft','parent_build_id':meta['build_id'],'parent_app_sha256':sha(parent/'firmware.bin'),'contract_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'parent_source_sha256':pinned,'drawing_opportunities_per_frame':4 if a.draw_four else 2 if a.draw_twice else 1,'draw_twice_enabled':a.draw_twice,'refresh_trace_enabled':a.refresh_trace,'rows_per_batch':2 if a.row_pair else 1,'blocking_snapshot_consumer':a.blocking_consumer,'output_task_core':0 if a.output_draw_core else 1,'internal_game_mode_only':a.internal_game_mode,'internal_framebuffer_enabled':a.internal_framebuffer,'row_timing_enabled':a.row_timing,'output_task_priority':4 if a.output_between_tasks else 2 if a.output_below_parser else 6,'uart_alignment_enabled':a.uart_alignment,'dispatch_timing_enabled':a.dispatch_timing,'lookahead_enabled':a.lookahead,'packed_row_enabled':a.packed_row,'source_change':'identity, optional output timing hooks, bounded lookahead, and optional packed-row normalization' if a.lookahead else 'identity and reviewed optional snapshot/send hooks only','probe_sha256':{n:sha(tree/n) for n in probe_files},'configuration_change':'enable existing AGON_EXTENDER_VIDEO_TIMING=1','scope':'bounded snapshot lookahead and output timing; no VDP drawing algorithm or MOS changes'}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cmd=[str(root/'.venv/bin/pio'),'run','-d',str(tree/'vdp'),'-c',str(out/'platformio.ini'),'-e','p4-console']
 with (out/'build.log').open('w') as log:subprocess.run(cmd,env=dict(os.environ,AGON_EXTENDER_BUILD_ID=identity,AGON_EXTENDER_DSP_LIFETIME_FIX='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
 assert all(sha(source/n)==h for n,h in pinned.items())
 assert all(sha(tree/n)==h for n,h in pinned.items() if n!='vdp/pio/p4-console-identity.json' and n not in probe_files)
 outputs={}
 for n in ('firmware.bin','firmware.elf','firmware.factory.bin','partitions.bin','bootloader.bin'):
  shutil.copy2(out/'build/p4-console'/n,out/n);outputs[n]={'bytes':(out/n).stat().st_size,'sha256':sha(out/n)}
 assert identity.encode() in (out/'firmware.bin').read_bytes()
 assert b'/diagnostics/video-timing' in (out/'firmware.bin').read_bytes()
 if a.refresh_trace:assert b'NPTRACE begin' in (out/'firmware.bin').read_bytes()
 if a.internal_framebuffer:assert b'np-fb-memory' in (out/'firmware.bin').read_bytes()
 if a.row_timing:assert b'row_wait_sum' in (out/'firmware.bin').read_bytes() and b'row_work_sum' in (out/'firmware.bin').read_bytes()
 if a.dispatch_timing:assert b'credit_to_ready' in (out/'firmware.bin').read_bytes() and b'ready_to_send' in (out/'firmware.bin').read_bytes()
 symbols=subprocess.check_output(['nm','-C',str(out/'firmware.elf')],text=True)
 assert 'agon::extender::diagnostics::videoRecorder' in symbols
 if a.uart_alignment:
  assert 'ConsoleStream::readBytes(' in symbols
  assert '    delay(1);' not in (tree/'vdp/video/extender/transport/console_hardware.inc').read_text()
  assert 'disableRetainedVdpIdleWatchdogs' in (tree/'vdp/video/video.ino').read_text()
 assert all(sha(root/n)==sha(tree/n) for n in probe_files)
 assert sha(out/'partitions.bin')==sha(parent/'partitions.bin')
 manifest.update(outputs=outputs,build_complete=True);(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(identity+' built; unflashed',flush=True)
if __name__=='__main__':main()

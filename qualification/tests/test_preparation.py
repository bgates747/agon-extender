#!/usr/bin/env python3
"""Host-only failure-path checks for qualification preparation and dispatch."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "qualification"), str(ROOT / "scripts")]
import installation
import lifecycle
import review
import sdcard
spec = importlib.util.spec_from_file_location("prepared_qualification", ROOT / "qualification/run.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def digest(data):
    return hashlib.sha256(data).hexdigest()


class PreparationTests(unittest.TestCase):
    def test_post_reset_startup_allowance_precedes_actual_CLI_proof(self):
        with tempfile.TemporaryDirectory() as folder:
            session = lifecycle.Session.__new__(lifecycle.Session)
            session.boot = 1
            session.config = {}
            session.output = Path(folder)
            session.sequence = 0
            events = []
            session.check_boot = lambda: events.append("epoch checked")
            session.verify_startup = lambda: events.append("actual CLI/read/EXIT")
            with mock.patch.object(lifecycle.time, "sleep", side_effect=lambda n: events.append(n)):
                session.after_reset({"boot": 2})
            self.assertEqual(events, [2.0, "epoch checked", "actual CLI/read/EXIT"])
            self.assertEqual(session.route, "legacy")

    def test_missing_cleanup_handback_blocks_further_input(self):
        with tempfile.TemporaryDirectory() as folder:
            session = lifecycle.Session.__new__(lifecycle.Session)
            session.url = "http://device"
            session.output = Path(folder)
            session.sequence = 0
            session.unsafe = False
            session.owned_paths = ["/extender/.owned.bin"]
            client = mock.Mock()
            session.service = mock.Mock(return_value=client)
            session.startup = mock.Mock()
            session.check_boot = mock.Mock()
            with (mock.patch.object(lifecycle, "stage_new_file"),
                  mock.patch.object(lifecycle, "type_line") as typed,
                  mock.patch.object(lifecycle, "wait_sd_service", side_effect=TimeoutError)):
                with self.assertRaises(lifecycle.UnsafeForeground):
                    session.cleanup()
                self.assertTrue(session.unsafe)
                self.assertEqual(typed.call_count, 1)
                self.assertTrue(typed.call_args.args[2].startswith(
                    "EXEC /agents/extender/results/cleanup-"))
                with self.assertRaises(lifecycle.UnsafeForeground):
                    session.command(Path(folder) / "next.json", "ECHO must not dispatch")
                self.assertEqual(typed.call_count, 1)

    def test_checked_transfer_fallback_is_rejected_before_connect(self):
        with mock.patch("sdcard.Client") as client, self.assertRaisesRegex(ValueError,"checksum-free"):
            lifecycle.wait_sd_service("http://device",Path("unused"),require_fast=False)
        client.assert_not_called()

    def test_check_only_never_constructs_a_live_session_or_opens_network(self):
        with tempfile.TemporaryDirectory() as folder:
            one=Path(folder)/"receipt.json";one.write_text("{}")
            fixture=Path(folder)/"fixtures.json";fixture.write_text("{}")
            args=["run.py","--config",str(ROOT/"qualification/config.example.json"),
                  "--fixtures",str(fixture),"--flash-receipt",str(one),
                  "--flash-receipt",str(one),"--check-only"]
            with mock.patch.object(sys,"argv",args), \
                    mock.patch.object(runner,"load_receipt",side_effect=[{"target":"p4"},{"target":"emos"}]), \
                    mock.patch.object(runner,"verify_fixtures",return_value={}), \
                    mock.patch.object(runner,"Session",side_effect=AssertionError("no live session")), \
                    mock.patch.object(runner,"urlopen",side_effect=AssertionError("no HTTP")), \
                    mock.patch.object(runner.subprocess,"run",side_effect=AssertionError("no process")), \
                    mock.patch("sys.stdout",new_callable=io.StringIO) as printed:
                self.assertEqual(runner.main(),0)
                value=json.loads(printed.getvalue())
            self.assertFalse(value["hardware_contacted"])
            self.assertFalse(value["hardware_ready"])
            self.assertEqual(value["required_automated_checks"],25)

    def test_hdmi_observes_dma_progress_without_opening_video(self):
        value = {"available": True, "output": "hdmi", "frame_clock": "dma-frame-complete",
                 "output_width": 848, "output_height": 480,
                 "mode": 20, "width": 512, "height": 384, "colors": 64,
                 "rolling": {"frames": 12, **{k: 0 for k in runner.HDMI_FAULTS}}}
        after = copy.deepcopy(value); after["rolling"]["frames"] = 15
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(runner, "read_json", side_effect=[value, after]), \
                mock.patch.object(runner, "VideoSession", side_effect=AssertionError("no browser video")):
            self.assertEqual(runner.hdmi_progress("http://device", Path(folder)/"dma.json")["dma_frames_advanced"], 3)
        for key in runner.HDMI_FAULTS:
            bad = copy.deepcopy(value); bad["rolling"][key] = 1
            with self.subTest(key=key), self.assertRaises(RuntimeError):
                runner.hdmi_sample(bad)

    def test_hdmi_rejects_restarted_counter_and_stale_geometry(self):
        value = {"available": True, "output": "hdmi", "frame_clock": "dma-frame-complete",
                 "output_width": 848, "output_height": 480,
                 "mode": 8, "width": 320, "height": 240, "colors": 64,
                 "rolling": {"frames": 100, **{k: 0 for k in runner.HDMI_FAULTS}}}
        for change in ("restart", "mode"):
            after = copy.deepcopy(value)
            if change == "restart": after["rolling"]["frames"] = 1
            else: after["mode"] = 20
            with tempfile.TemporaryDirectory() as folder, \
                    mock.patch.object(runner, "read_json", side_effect=[value, after]), \
                    self.assertRaises(RuntimeError):
                runner.hdmi_progress("http://device", Path(folder)/"dma.json")

    def test_native_mode_case_checks_all_six_edges_without_browser_video(self):
        def select(url,journal,mode,width,height,colors):
            return dict(mode=mode,width=width,height=height,colors=colors)
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(runner,"bridge_reset",return_value={"ready":True,"physical_neutral":True}), \
                mock.patch.object(runner,"type_line"),mock.patch.object(runner,"capture_text",return_value="old"), \
                mock.patch.object(runner,"wait_screen",return_value="fresh marker\n/ *"), \
                mock.patch.object(runner,"select_mode",side_effect=select) as switches, \
                mock.patch.object(runner,"hdmi_progress",return_value={"dma_frames_advanced":1}) as progress, \
                mock.patch.object(runner,"VideoSession",side_effect=AssertionError("native has no video route")):
            value=runner.run_rp06_mode_transaction(
                {"extender_url":"http://device","output_profile":"native-hdmi"},
                {"component_commit":"a"*40,"artifact_sha256":"b"*64},Path(folder)/"case")
        self.assertEqual([call.args[2] for call in switches.call_args_list],[8,20,8,96,20,96])
        self.assertEqual(progress.call_count,6)
        self.assertEqual(value["status"],"pass");self.assertEqual(len(value["checks"]),7)

    def test_mode_settling_begins_after_commit_and_skips_matching_mode(self):
        wanted = dict(mode=20, width=512, height=384, colors=64)
        session = object.__new__(lifecycle.Session)
        session.url="http://device";session.route="excom";session.boot=3
        session.select_route=mock.Mock(); session.command=mock.Mock();session.journal=mock.Mock()
        session.check_boot=mock.Mock()
        events=[]
        def read(path):
            events.append("committed" if len(events) else "old")
            return wanted if len(events)>1 else dict(mode=8,width=320,height=240,colors=64)
        session.read=read
        with mock.patch.object(lifecycle.time,"sleep",side_effect=lambda n:events.append(("settle",n))):
            session.select_extender_mode(wanted)
        self.assertEqual(events,["old","committed",("settle",1.0)])
        session.read=mock.Mock(return_value=wanted);session.command.reset_mock()
        with mock.patch.object(lifecycle.time,"sleep") as sleep:
            session.select_extender_mode(wanted)
        sleep.assert_not_called();session.command.assert_not_called()

    def test_reset_between_cases_blocks_input_without_resume(self):
        session=object.__new__(lifecycle.Session)
        session.url="http://device";session.boot=1;session.unsafe=False
        with mock.patch.object(lifecycle,"keyboard_status",return_value={"boot":2}), \
                mock.patch.object(lifecycle,"type_line") as type_line, \
                self.assertRaises(lifecycle.UnsafeForeground):
            session.command(Path("unused"),"RUN")
        type_line.assert_not_called();self.assertTrue(session.unsafe)

    def test_unknown_sd_file_is_preserved(self):
        client=mock.Mock();client.stat_entry.return_value=(3,0)
        with self.assertRaisesRegex(ValueError,"existing"):
            lifecycle.stage_new_file(client,"/extender/unknown.bin",b"new")
        client.upload.assert_not_called()

    def test_session_preserves_startup_and_restores_both_modes_without_boot_launch(self):
        startup=b"EMOS KEYINPUT extender\r\nLOAD flight.bin &040000\r\n"
        entry_mb=dict(mode=8,width=320,height=240,colors=64)
        entry_ext=dict(mode=20,width=512,height=384,colors=64)
        state={"boot":1,"online":False,"mb":entry_mb.copy(),"ext":entry_ext.copy(),"route":"legacy"}
        files={"/autoexec.txt":startup,"/extender/user.bin":b"preserve"}
        writes=[];commands=[]
        class Client:
            lock=mock.Mock()
            def stat_entry(self,path):
                if path in ("/extender","/agents/extender/results"):return 0,16
                if path not in files:raise sdcard.RemoteError("missing",status=6)
                return len(files[path]),0
            def upload(self,path,data,activate,*,fast):
                assert fast;writes.append(path);files[path]=data
            def download(self,path):
                if path not in files:raise sdcard.RemoteError("missing",status=6)
                return files[path]
            def rpc(self,op):
                assert op==11;state['online']=False
        def send(url,journal,line):
            commands.append(line)
            if line.startswith("EMOS sdserve"):state['online']=True
            elif line.startswith("EMOS EXCOM"):state['route']='excom'
            elif line.startswith("EMOS LEGACY"):state['route']='legacy'
            elif line.startswith("VDU 22 "):
                mode=int(line.split()[-1]);self.assertEqual(state['route'],'excom')
                self.assertEqual(mode,entry_ext['mode']);state['ext']=entry_ext.copy()
            elif line.startswith("DELETE "):
                self.assertTrue(line.startswith("DELETE -f /extender/."))
                files.pop(line.split()[2],None)
            elif line.startswith("EXEC "):
                script=files[line.split()[1]].decode()
                if line.startswith("EXEC /agents/extender/results/cleanup-"):
                    for cleanup_line in script.splitlines():
                        if cleanup_line.startswith('DELETE '):
                            self.assertTrue(cleanup_line.startswith('DELETE -f /extender/.'))
                            files.pop(cleanup_line.split()[2],None)
                        else:self.assertEqual(cleanup_line,'EMOS sdserve --fast /')
                    state['online']=True
                    return
                args=next(x.split()[2:] for x in script.splitlines() if x.startswith("RUN . "))
                if args[0]=='restore':
                    state['mb']=dict(zip(('mode','width','height','colors'),map(int,args[1:5])))
                token=args[-1];m=state['mb']
                files['/agents/extender/results/qstate-'+token+'.txt']=(
                    f"schema=1\ntoken={token}\nmode={m['mode']}\nwidth={m['width']}\nheight={m['height']}\ncolours={m['colors']}\n").encode()
                self.assertTrue(script.endswith("EMOS sdserve --fast /\r\n"))
                state['online']=True
            return {"boot":state['boot']}
        def wait_service(*args,**kwargs):
            self.assertTrue(state['online']);self.assertTrue(kwargs['require_fast']);return Client()
        def read(session,path):
            if path=='/sd/status':return dict(online=state['online'],protocol=2)
            return dict(available=True,output='hdmi',**state['ext'])
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);binary=out/'probe.bin';binary.write_bytes(b"test probe")
            fixtures={'fixtures':{'qstate':{'binary':str(binary)}}}
            with mock.patch.object(lifecycle,'keyboard_status',side_effect=lambda u:{'boot':state['boot']}), \
                    mock.patch.object(lifecycle,'type_line',side_effect=send), \
                    mock.patch.object(lifecycle,'wait_sd_service',side_effect=wait_service), \
                    mock.patch.object(lifecycle.Session,'read',read),mock.patch.object(lifecycle.time,'sleep'):
                session=lifecycle.Session({'extender_url':'http://device','output_profile':'native-hdmi'},out,fixtures)
                session.prepare()
                self.assertEqual(session.entry['mainboard'],entry_mb)
                state['ext']=dict(mode=96,width=848,height=480,colors=64)
                state['mb']=dict(mode=0,width=640,height=480,colors=16)
                session.restore();session.verify_entry();session.cleanup()
        self.assertEqual(state['mb'],entry_mb);self.assertEqual(state['ext'],entry_ext)
        self.assertEqual(state['route'],'legacy');self.assertFalse(state['online'])
        self.assertEqual(files['/autoexec.txt'],startup);self.assertNotIn('/autoexec.txt',writes)
        self.assertEqual(files['/extender/user.bin'],b'preserve')
        self.assertFalse(any(path.startswith('/extender/.') for path in files))
        self.assertTrue(all('reset' not in line.lower() for line in commands))

    def test_manual_review_cannot_qualify_targeted_or_incomplete_run(self):
        summary={"status":"success","full_suite":True,"output_profile":"native-hdmi",
                 "restoration":{"status":"verified"},"notification":{"status":"success"},
                 "flashed":{"p4":{},"emos":{}},"manual_cases_required":["native-hdmi-visual"],
                 "physical_cases":[{"status":"pass"}],"check_counts":{"pass":25,"required":25}}
        observed={"schema":1,"author_statement":"Synthetic test only", "cases":{
            "native-hdmi-visual":{"status":"pass","observations":"Synthetic pixels"}}}
        self.assertEqual(review.bind_review(summary,observed)["qualification_state"],"qualified")
        for field,value in (("full_suite",False),("status","test-failure"),("restoration",{"status":"failed"})):
            bad=copy.deepcopy(summary);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):review.bind_review(bad,observed)
        with self.assertRaises(ValueError): review.bind_review(summary,{"schema":1,"author_statement":"x","cases":{}})

    def test_explicit_raw_run_never_writes_startup_or_resets_on_timeout(self):
        self.raw_run(completes=False)

    def test_explicit_raw_run_collects_only_after_completion(self):
        self.raw_run(completes=True)

    def raw_run(self, *, completes):
        token="0123456789ABCDEF"
        startup=b"EMOS KEYINPUT extender\r\n"
        files={"/autoexec.txt":startup}
        writes=[];commands=[]
        result=(f"schema=1\ncase=a10-rp04-raw-sd-write\nstatus=pass\nsector=2\n"
                f"test_rc=0\nrestore_rc=0\nrestore_verify_rc=0\nbefore_crc32=12345678\n"
                f"pattern_crc32=87654321\nobserved_crc32=87654321\nrestored_crc32=12345678\n"
                f"detail=completed\nfirst_partition_lba=8192\nwrite_attempted=1\ntoken={token}\n").encode()
        class Client:
            lock=mock.Mock()
            def stat_entry(self,path):
                if path in ("/extender","/agents/extender/results"):return 0,16
                if path not in files:raise sdcard.RemoteError("missing",status=6)
                return len(files[path]),0
            def download(self,path):
                if path not in files:raise sdcard.RemoteError("missing",status=6)
                return files[path]
            def upload(self,path,data,activate,*,fast):
                assert fast
                writes.append(path);files[path]=data
            def rpc(self,op):assert op==11
        def type_line(url,path,line):
            commands.append(line)
            if line.startswith("EXEC /extender/.raw-sd-"):
                script = files[line.split()[1]].decode()
                self.assertEqual(script.splitlines(), [
                    "LOAD /extender/.raw-sd-"+token+".bin", "RUN . "+token])
                if completes:files["/agents/extender/results/a10-rp04.txt"]=result
        def screen(*args,**kwargs):
            if not completes:raise TimeoutError("fixture is still active")
            return "A10-RP04 COMPLETE "+token+"\n/ *\n"
        with tempfile.TemporaryDirectory() as folder:
            binary=Path(folder)/"fixture.bin";binary.write_bytes(b"safe fixture")
            config={"extender_url":"http://device","output_profile":"native-hdmi","_fixtures":{"fixtures":{"raw_sd":{
                "binary":str(binary),"sha256":digest(binary.read_bytes()),"source_files":{}}}}}
            with mock.patch.object(runner,"type_line",side_effect=type_line), \
                    mock.patch.object(runner,"wait_sd_service",return_value=Client()) as service, \
                    mock.patch.object(runner,"select_mode") as selected_mode,mock.patch.object(runner,"wait_screen",side_effect=screen), \
                    mock.patch.object(runner.uuid,"uuid4",return_value=mock.Mock(hex=token)), \
                    mock.patch.object(runner.subprocess,"run",side_effect=AssertionError("no reset/build")):
                if completes:
                    value=runner.run_fwbug008(config,{"component_commit":"a"*40,"artifact_sha256":"b"*64},Path(folder)/"out")
                    self.assertEqual(value["status"],"pass");self.assertEqual(len(value["checks"]),5)
                    self.assertEqual(service.call_count,2)
                else:
                    with self.assertRaises(runner.UnsafeMainboardState):
                        runner.run_fwbug008(config,{},Path(folder)/"out")
                    self.assertEqual(service.call_count,1)
                self.assertEqual(selected_mode.call_args.args[2:],(20,512,384,64))
        self.assertNotIn("/autoexec.txt",writes)
        self.assertEqual(sum(line.startswith("EXEC /extender/.raw-sd-") for line in commands),1)
        self.assertFalse(any(line.startswith(("LOAD ", "RUN . ")) for line in commands))
        if not completes:self.assertTrue(commands[-1].startswith("EXEC /extender/.raw-sd-"))

    def test_archived_dirty_source_is_verified_without_claiming_clean_commit(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            source=b"patched source";raw=b"MOS"
            def save(name,data):
                p=root/name;p.write_bytes(data);return installation.file_record(p)
            def save_json(name,data):return save(name,json.dumps(data).encode())
            archive=root/"source.tar.gz"
            with tarfile.open(archive,"w:gz") as stream:
                item=tarfile.TarInfo("agon-emos/src/a.c");item.size=len(source);stream.addfile(item,io.BytesIO(source))
            patch=save("source.patch",b"patch bytes")
            manifest={"commit":"a"*40,"build_id":"emos-test","dirty":True,
                      "source_patch_sha256":patch["sha256"],"source_archive_sha256":installation.sha256(archive),
                      "raw_bytes":len(raw),"raw_sha256":digest(raw),"padded_sha256":digest(raw.ljust(131072,b"\xff"))}
            spec={"schema":1,"target":"emos","component_commit":"a"*40,"build_id":"emos-test",
                  "artifact":save("mos.bin",raw),"readback":save("readback.bin",raw.ljust(131072,b"\xff")),
                  "installation_evidence":save_json("installed.json",{"build_id":"emos-test",
                      "entire_128KiB_ROM_exact":True,"padded_sha256":manifest["padded_sha256"]}),
                  "source":{"archive":installation.file_record(archive),"archive_prefix":"agon-emos/",
                      "patch":patch,"inventory":save_json("inventory.json",{"source_sha256":{"src/a.c":digest(source)}}),
                      "build_manifest":save_json("manifest.json",manifest)}}
            receipt=installation.verify_spec(spec)
            self.assertEqual(receipt["source"]["kind"],"archived-patch")
            self.assertTrue(receipt["live_identity_required"])
            spec["source"]["patch"]=save("wrong.patch",b"different patch")
            with self.assertRaisesRegex(ValueError,"provenance"):installation.verify_spec(spec)
            spec["source"]["patch"]=patch
            spec["readback"]=save("wrong-rom.bin",raw.ljust(131071,b"\xff")+b"\x00")
            with self.assertRaisesRegex(ValueError,"ROM"):installation.verify_spec(spec)


if __name__=="__main__":unittest.main()

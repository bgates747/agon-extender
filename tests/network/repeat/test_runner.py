"""Actual repeated-runner admission and durable-result checks, no devices."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('repeat_control',ROOT/'docs/tasks/PARALLEL-001/scripts/repeat_control.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

class RunnerTests(unittest.TestCase):
    def binding(self,case='repeat-plain',p4=None):
        grant=dict(owner='linux-extender',task=runner.TASK,generation=63,request='request-fresh',lease='a'*32)
        components=dict(p4_app_sha256=p4 or runner.UNFILTERED_P4,emos_rom_sha256=runner.PARALLEL_EMOS)
        context=dict(grant=grant,central_owner='linux-extender',operator='linux-extender',phase='repeat-isolation',request=grant['request'],generation=63,lease=grant['lease'],components=components,source_pins_sha256='b'*64)
        prepared=dict(schema='extender-parallel-repeat-prepared-v1',case=case,carrier='parallel',guarded_rfc25=case=='repeat-rfc25',rfc25_packet_bytes=67 if case=='repeat-rfc25' else 0,sessions=4,records_per_session=44,records=176,full_fixture_readback_match=True,installed_components=components.copy(),actual_cli=True,callback_zero=True,legacy_zero=True,entry_mode=0,source_pins_sha256='b'*64,fixture_remote='/extender/network/parallel001-repeat/request-fresh/'+case+'/netrepeat.bin',result_remote='/agents/extender/results/parallel001-repeat/request-fresh/'+case+'/result.txt',fixture_sha256=runner.FIXTURES[case],selected_p4_sha256=components['p4_app_sha256'])
        return context,grant,prepared

    def test_both_variants_explicitly_select_either_exact_pair(self):
        for case in runner.CASES:
            for p4 in (runner.UNFILTERED_P4,runner.FILTERED_P4):runner.validate_binding(*self.binding(case,p4))

    def test_owner_phase_source_namespace_and_readiness_refusals(self):
        mutations=(lambda c,g,p:g.update(owner='mechagon'),lambda c,g,p:g.update(task='old-task'),lambda c,g,p:g.update(generation=60),lambda c,g,p:c.update(operator='wolf3dorig'),lambda c,g,p:c.update(phase='consumer-replay'),lambda c,g,p:c.update(lease='stale'),lambda c,g,p:c.update(released=True),lambda c,g,p:c.update(pending_commands=True),lambda c,g,p:c.update(source_pins_sha256=''),lambda c,g,p:p.update(full_fixture_readback_match=False),lambda c,g,p:p.update(callback_zero=False),lambda c,g,p:p.update(legacy_zero=False),lambda c,g,p:p.update(entry_mode=20),lambda c,g,p:p.update(records=175),lambda c,g,p:p.update(fixture_remote='/extender/network/parallel001-repeat/old/netrepeat.bin'),lambda c,g,p:p.update(result_remote='/agents/extender/results/parallel001-repeat/request-fresh/repeat-rfc25/result.txt'),lambda c,g,p:p.update(fixture_sha256=runner.FIXTURES['repeat-rfc25']),lambda c,g,p:p.update(guarded_rfc25=True),lambda c,g,p:p.update(selected_p4_sha256='f'*64))
        for change in mutations:
            with self.subTest(change=change):
                values=self.binding();change(*values)
                with self.assertRaises(RuntimeError):runner.validate_binding(*values)

    def report(self):
        return dict(passed=True,closed_sessions=4,records=[dict(session=s,index=i,bytes=runner.SIZES[i%11]) for s in range(4) for i in range(44)])

    def test_complete_peer_matrix(self):self.assertTrue(runner.validate_peer_report(self.report()))

    def test_partial_reordered_duplicate_wrong_size_or_fault_peer_refused(self):
        a=self.report();a['records'].pop()
        b=self.report();b['records'][1],b['records'][2]=b['records'][2],b['records'][1]
        c=self.report();c['records'][1]=c['records'][0].copy()
        d=self.report();d['records'][1]['bytes']=2
        e=self.report();e['closed_sessions']=3
        f=self.report();f['first_error']='retained'
        for report in (a,b,c,d,e,f):
            with self.assertRaises(RuntimeError):runner.validate_peer_report(report)

    def text(self,case):
        text=runner.BUILD_IDS[case]+' result=PASS first_error=0 records=176/176 opened=4/4 closed=4/4 release=0 restore=1 elapsed_ticks=1234 tick_hz_nominal=120 carrier=parallel size_checks=356\n'
        if case=='repeat-rfc25':text+='rfc25_source_releases=176/176 point_replies=176/176 calibrated=0\n'
        return text

    def test_exact_native_receipts_both_variants(self):
        for case in runner.CASES:self.assertEqual(runner.validate_durable_result(self.text(case),case)['records'],'176/176')

    def test_native_partial_close_restore_build_or_source_receiver_gaps_refused(self):
        text=self.text('repeat-rfc25')
        bad=(text.replace('records=176/176','records=175/176'),text.replace('closed=4/4','closed=3/4'),text.replace('restore=1','restore=0'),text.replace('release=0','release=31'),text.replace('size_checks=356','size_checks=355'),text.replace('elapsed_ticks=1234','elapsed_ticks=16777216'),text.replace(runner.BUILD_IDS['repeat-rfc25'],'old-build'),text.replace('source_releases=176/176','source_releases=175/176'),text.replace('point_replies=176/176','point_replies=175/176'),text+'extra\n',text.replace('first_error=0','first_error=0 first_error=132'))
        for receipt in bad:
            with self.assertRaises(RuntimeError):runner.validate_durable_result(receipt,'repeat-rfc25')

if __name__=='__main__':unittest.main()

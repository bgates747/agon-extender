# CPU window owner preparation

The existing accounting work now has an exact identified ROM and a source-only
owner contract for Mech's single-window caller. No hardware window, timer
execution, installation or capacity result is claimed. The caller still owns
its final controller, immutable kit and ordinary FIFO reservation.

1. Reuse the [identified accounting package](CPU-ACCOUNTING-IDENTIFIED-R01.md):
   full ROM f05cfbe4, used131060/free12, clean source5815b18. Exact full incoming
   a25f remains rollback; native VDP5d657, P4, startup and listener stay unchanged.
2. Use actual identified linked-map addresses: sysvars BC326/64B; mode BC34D/1B;
   user callback BC392/3B; Legacy backend BCB29/1B. Rollback addresses differ:
   BC322/BC349/BC38E/BCB25. Candidate capture must not reuse historical offsets.
3. Keep C2 OPEN5/tagC2 and its complete8B two-JP table, ordinary OPEN4 control,
   unchanged recorder and receive protections. No old OPEN8 adapter or new ABI.
4. Caller admission must establish one inactive disposable PRT1 provider with
   IRQ off, no vector takeover or competing client. One START attempt and one
   epoch of at most54000 counts; no rearm, old calibration, probe or tail work.
5. START occurs at returned foreground after submissions pause and actual
   renderer source/TEMT/reply plus NM same-query TAKE/uncached drain retire prior
   TX. Consumed reply bytes may remain ready. Unsolicited RX stays enabled;
   logical TX retirement is not physical receive silence.
6. STOP/provider retirement and positive CLOSE precede a96B snapshot; graphics
   END precedes SD writes. Preserve refusal quarantine, code/data/callback/source
   lifetimes, IFF and adjacent EI/HALT. UNKNOWN_GAP/PARTIAL_BOUNDARIES remain;
   raw accounting is not exclusive CPU occupancy or a30Hz capacity result.
7. Preserve all17 caller PRE-case file byte sets, attributes and absences before
   helpers, including the two compiled CPU paths and seven maintained helper
   outputs. Original feature and known full native/tail rollback remain separate.
   Preserve safely reachable original128KiB before LOAD/reset; label postreset
   evidence precisely and compare only text/rodata, excluding mutable CRT init.
8. The source-only packet deliberately has no request, grant, entry or final
   consumer kit. Final owner wrapper must bind the real request/controller,
   identified product manifest, each arm's actual map and current tuple. Proposed
   2400whole/600entry/1200consumer/600cleanup and phase floors require that final
   coherent binding; no historical entry can stand in for physical readiness.
9. Same future lease restores exact a25f/full ROM readback, all original files,
   feature, mode/route/input/cursor/root CLI and idle resources, joins actors and
   releases normally. No production promotion or publication is selected.

Evidence: ignored request-independent owner packet, actual646 product/maps and
382-member source/SDK archive. Every artifact descriptor and all17 SDK files
rehash unchanged; candidate symbol/address assertions pass directly against its
actual linked map. Existing current RX006 hardware cleanup retains priority.

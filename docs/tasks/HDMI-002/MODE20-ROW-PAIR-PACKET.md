# Mode 20 row-pair test packet

Can the P4 safely refill a two-row buffer in its DMA interrupt while the next pair is on its way to the display? The mode 0 run established safe reuse with 478 intervening rows. This fixture leaves just two. It displays the existing mode 20 card first, exercises one handoff in one frame, and returns to the card on success. Smith reviews the compiled image and this packet before installation.

## Frame and ownership

The standalone P4 uses the existing DMA-controlled 684×384 HDMI timing. A 512×384 image sits at native size with 86 black pixels on either side. At the configured PLL240/7 pixel clock, 1,104 clocks per line give 32.2 µs per line and **64.4 µs per pair**. The P4 CPU runs at 360 MHz, so the nominal pair interval is 23,184 cycles. HDMI and CPU clock values are nominal. The P4 USB console owns this trial. The Agon eZ80 has no test to load or run.

| List order | Rows | DMA source | 64-bit words | Initial control |
|---|---:|---|---:|---|
| D0 | 0–1 | Internal SRAM pair A | 513 | Valid, block interrupt requested |
| D1 | 2–3 | Separate internal SRAM pair B | 513 | Valid |
| D2 | 4–5 | Same address and extent as A | 513 | Invalid until the P4 interrupt publishes it |
| D3 | 6–383 | Existing static reference, starting at byte 12,312 | 96,957 | Valid, last in frame |

Each 2,052-byte row includes both margins. One 4,104-byte DMA transfer holds two contiguous rows. Each SRAM allocation has 4,224 bytes, independently aligned to 128 bytes, so cache maintenance stays inside it. B uses the same kind of memory as A to exercise a realistic interval between SRAM reads. The P4 prepares both slots once and pre-stages the 3,072 active BGR bytes needed for the refill. The interrupt copies two 1,536-byte spans into A, retaining its margins. The existing picture supplies the rest of the frame directly. Four blocks fit the bridge's four-bit block-count field.

On D0's block interrupt, the P4 checks fresh block completion and cleared VALID for that reader and verifies D2 still points to A, invalid and untouched. Only then does it store replacement pixels. The P4 cleans A’s private cache span and fences before setting D2 VALID. DMA then reads A for D2. D2’s retirement establishes replacement consumption. D3 alone must close the frame. No task wake, second refill, game draw, or software checksum belongs in this interrupt.

## Pattern and independent checks

The operator uses the existing 65,523-byte packed `m020.vdu`, SHA-256 `56d2e094357c4f53706a4229aab5605a3f094d56cfbc1b7c541589d4a853a182`. Offline decoding matched the uncompressed upload and the original 512×384 palette preview pixel for pixel. The source uses all 64 colours. The expected output includes the sidebars.

| DMA-visible pixels | Bytes | Expected SHA-256 |
|---|---:|---|
| A before refill, rows 0–1 | 4,104 | `42c37fad1983419aa98ab1059dc2709ed262306843d03d64a75c6bee004e5688` |
| B, rows 2–3, and A after refill, rows 4–5 | 4,104 each | `ec366865e0406670ef6ec1f13386f8381e81cd8521db4982b21909bbb05b7b63` |
| Immutable tail | 775,656 | `23d6340096a4db7db8916b7de9364f1b53a96ba8d4a280f67a9df45294dce670` |
| Complete 684×384 BGR888 frame | 787,968 | `268c675f8a0b20fa46044c7d79c299d8cf6191a0c358c6520ec91eb7a7d7b02e` |

Both replacement rows differ from their prior contents at 510 of 512 active positions. The artwork in rows 2 through 5 is identical. The byte comparison therefore catches a stale A. Distinct A/B source addresses, fresh D0 and D2 retirements, and D2's publication establish *which buffer* supplied rows 4–5. The mode 20 card supplies the visual reference. A synchronized HDMI capture would be needed to certify every pixel at the connector.

## One-shot bench procedure

1. The Pi operator verifies the current reservation, custody, mode 0 build, prior app0 readback and preserved startup record. After Smith approves installation, the operator uses the reviewed P4 app-only path under Agon hold, verifies the installed entry bytes and partition selection, writes the bound extent at `0x20000`, then independently reads it back and compares all bytes. The P4 must report pad isolation before the operator releases Agon.
2. At the P4 diagnostic prompt, the Pi sends `preview`. It waits for at least one second of settling, advancing reference frames, hot-plug asserted and the expected build in `status`. Show Smith the reference before the live frame. The mainboard and its SD files need no staging.
3. On authorization for the trial, the Pi records the one-shot dispatch and sends exactly one `live` command. The P4 stops automatic rearm at the reference boundary, confirms the channel stopped, and arms the four fresh descriptors. The Pi retains the raw USB transcript through its terminal marker, including the first fault or complete frame, descriptor snapshots, uncached slot bytes, cycle stamps, and status of the restored reference.
4. The P4 stops the one-shot channel before restoring the reference. The Pi checks renewed frame progression and preserves the trace, parsed result, independent readback and process receipts. At the first unexpected fault it preserves the actual state and retains the reservation. A missing trace or a visual observation alone leaves the physical handoff unresolved.

## How to score the result

| Question | Required observation |
|---|---|
| Did ownership transfer safely? | D0 retired at A before the first store. D2 was initially invalid. Exactly one ISR refill and ordered publication took place. D2 subsequently retired at A with the expected pair size. D3 completed the frame. Source ranges are disjoint except for the intended D0/D2 reuse. No DMA errors, invalid descriptor or bridge underrun. |
| Were the pixels correct? | DMA-visible A before and after matches the two different pair hashes. B matches the intervening pair. The host model also checks the complete frame and its static tail. |
| How much time did it take? | Record cycles from DMA interrupt dispatcher entry to D2 publication. Divide by 360 for µs. Report the signed difference from 64.4 µs separately from actual consumption. Keep USB printing and host comparisons outside this measurement. |
| Had B retired when A was published? | Sample B's writeback immediately after publication. An outstanding writeback then establishes publication preceded B's reported retirement. If B is already done, relative order at the publication instant is unresolved. Either way D2's fresh completion supplies the independent hardware consumption check. |

This is one fixed-pixel refill with a static tail. Sustained full-height operation, access to live EVDP drawing state, and exact doubling in mode 8 each require their own evidence. [Earlier DMA and full-height review](NURPLES-SCROLL-JUDDER.md#last-use-dma-event-and-stock-row-plan-for-modes-8-and-20)

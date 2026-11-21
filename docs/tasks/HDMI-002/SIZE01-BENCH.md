# Olimex HDMI visual comparison, November 21

Smith reported “tests pass.” The same launcher and labelled patterns ran on the release and the P4 candidate. The P4 reported the expected carrier for all four modes. The candidate switched to 684×384 for mode 20 and returned to 848×480 at the mode 0 menu. The baseline used 1280×720 throughout. [Job packet](SIZE01-VISUAL.md) · [Build identities and fixture hashes](SIZE01-RESULT.json)

| Logical mode | Released carrier | Candidate carrier |
|---|---|---|
| 0, 640×480 | 1280×720 | 848×480 |
| 8, 320×240 | 1280×720 | 848×480 |
| 20, 512×384 | 1280×720 | 684×384 |
| 3, 640×240 | 1280×720 | 848×480 |

The released P4 reported modes 0→8→0→20→0→3→0. The candidate reported 0→3→0→8→0→20→0. The static preview therefore exercised the same four modes in a different order in the two arms. During the candidate's mode 20 visit the passive serial log recorded seven scanout reports between 59.996 and 60.140 Hz. After the return to mode 0 the log again showed advancing scanout. The observer did not measure the DMA channel-enable register externally. The linked stop ordering and fault-injection results are in the [offline record](SIZE01.md).

Smith observed antialiasing in the released baseline. The packed patterns already contain palette-quantized antialiasing from vector rasterization. The released P4 presented them at native size, with row repetition in mode 3. The candidate uses bilinear 2× enlargement for mode 8. Smith supplied an overall visual pass. The retained bench evidence includes the P4 display status and serial logs. No monitor photos or numerical edge or circle measurements accompanied the verdict.

Each arm staged the same five files, 232,603 bytes. The candidate's 1,794,048-byte flash readback matched the padded write image at app0 offset `0x20000`, SHA-256 `e79ebbb8927245d2173a8a4306a09e97a1f181c4c80bed2db6a865aee81b73a1`.

| Capture | Release SHA-256 | Candidate SHA-256 |
|---|---|---|
| P4 display status | `d3fb2bb40791d4cad1b0c519f046b6b3aa40e20cd95f407dfd45c9956c5c36a1` | `3eb8b2bdb9962519095f415e3ce81599bf5ebf4ba92ff39af07746b64f26ac97` |
| P4 serial | `bb34897767eae947e8c05eb30bf3f764d3da9afbfecd00e2e976bf66a01cd925` | `5d968cfe4b7ccd2efda1a7bbc27a5c633ffeb1f0dbaf391b2c4b7dfa471ad2b2` |

## Ad hoc Nurples playthrough

After the static preview passed, Smith played the current Nurples dev runtime on the same P4 candidate. He reported that the game ran at normal speed, but vertical scrolling showed judder across multiple scanlines. The playfield did not appear to judder as one whole image. He saw no blank scanlines alternating with displayed ones. Smith suggested scanout errors as a possible explanation. No diagnostic capture ran during gameplay and the cause remains open. The [proposed investigation](NURPLES-SCROLL-JUDDER.md) records the game and firmware identities and the comparison for review.

Smith also reported one full-screen blackout during regular gameplay. The picture returned after about one second, with no obvious framebuffer corruption visible when play resumed. Smith suspects a brief loss of HDMI timing followed by the monitor reacquiring sync. The clean image on return argues against persistent damage from drawing primitives. The trial captured neither the framebuffer during the blackout nor the monitor’s input-lock state. Its relationship to the scrolling judder is unknown.

At Smith’s request the operator restored the selected v0.3.0 P4 application at app0 offset `0x20000`. The independent 1,794,048-byte readback matched the complete restore extent, SHA-256 `071ac03fe4b6159df8e1b15f825d523e92fe55653e681571bb44496c2d0368c1`. Handback verified a responsive Legacy MOS CLI, idle transfer services and free serial handles. The operator checked in with the Olimex scheduler.

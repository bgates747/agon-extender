# Graphics workload after stock UART alignment

All624intervals complete; 8 unchanged baseline probe mismatches; zero P4 snapshots.

Mode20,512×384,64colours,singlebuffered. Medians of three enabled draw
intervals, in milliseconds. Positive percentages mean more time; negative
means less. Each table is sorted by largest current EDP time. Stock VDP
is the main comparison baseline; the final column compares EDP against
its own earlier unchanged-UART run. This is not game FPS or video output.
Mainboard VGA remains active. Instrumentation/fences are not free.

## Upload-heavy stage elapsed time

These stages include arriving bytes, command handling, asset creation and
their drawing/completion work. They are not isolated bitmap creation or
SD loading times. Stage byte counts are retained in the adjacent JSON.

| Case | VDP ms | EDP ms | EDP vs VDP | Prior EDP ms | EDP vs prior |
| --- | ---: | ---: | ---: | ---: | ---: |
| BSP03_01 | 881.970 | 3048.353 | +245.6% | 3165.200 | -3.7% |
| BSP26_01 | 582.180 | 1981.324 | +240.3% | 2048.142 | -3.3% |
| BSP27_01 | 481.968 | 1598.188 | +231.6% | 1648.518 | -3.1% |
| BSP21_01 | 415.469 | 1397.708 | +236.4% | 1447.800 | -3.5% |
| BSP25_01 | 315.726 | 981.155 | +210.8% | 1014.921 | -3.3% |
| BSP22_01 | 265.619 | 848.113 | +219.3% | 881.525 | -3.8% |
| BSP29_01 | 315.523 | 831.509 | +163.5% | 865.070 | -3.9% |
| BSP07_01 | 115.522 | 331.106 | +186.6% | 331.214 | -0.0% |

## Native primitive rendering

Matching primitive counts. Includes state/text work present in each scene;
excludes incoming-stream waits. SCROLL,CLIPROW,COMBINED each contain64
repeated operations; these rows show the complete batch, not one plot.

| Case | VDP ms | EDP ms | EDP vs VDP | Prior EDP ms | EDP vs prior |
| --- | ---: | ---: | ---: | ---: | ---: |
| BSP03_01 | 37.443 | 11.462 | -69.4% | 11.518 | -0.5% |
| BSP07_02 | 15.470 | 9.790 | -36.7% | 9.798 | -0.1% |
| SHP23 | 10.551 | 6.790 | -35.6% | 6.885 | -1.4% |
| SHP20 | 7.866 | 6.041 | -23.2% | 6.041 | +0.0% |
| BSP07_03 | 7.526 | 4.898 | -34.9% | 4.901 | -0.1% |
| COMBINED | 7.189 | 2.670 | -62.9% | 2.660 | +0.4% |
| SCROLL | 9.373 | 2.089 | -77.7% | 2.078 | +0.5% |
| CLIPROW | 6.307 | 1.967 | -68.8% | 1.951 | +0.8% |

## Software sprite processing

Matching showSprites call counts; complete scopes include background save
and redraw. Rows below0.05ms on both devices are omitted for readability.
These scopes overlap native primitive timing: do not add them.

| Case | VDP ms | EDP ms | EDP vs VDP | Prior EDP ms | EDP vs prior |
| --- | ---: | ---: | ---: | ---: | ---: |
| BSP25_02 | 20.444 | 3.583 | -82.5% | 3.572 | +0.3% |
| BSP25_03 | 17.586 | 3.303 | -81.2% | 3.242 | +1.9% |
| BSP25_04 | 7.761 | 1.447 | -81.4% | 1.460 | -0.9% |
| BSP25_05 | 7.919 | 1.409 | -82.2% | 1.403 | +0.4% |
| BSP27_02 | 3.755 | 0.725 | -80.7% | 0.719 | +0.8% |
| BSP27_03 | 3.722 | 0.691 | -81.4% | 0.672 | +2.8% |
| BSP29_02 | 3.168 | 0.576 | -81.8% | 0.544 | +5.9% |
| BSP29_05 | 3.132 | 0.570 | -81.8% | 0.572 | -0.3% |
| BSP29_03 | 3.128 | 0.545 | -82.6% | 0.562 | -3.0% |
| BSP29_04 | 3.172 | 0.537 | -83.1% | 0.565 | -5.0% |
| BSP21_05 | 1.623 | 0.401 | -75.3% | 0.317 | +26.5% |
| BSP21_02 | 1.672 | 0.351 | -79.0% | 0.338 | +3.8% |
| BSP21_03 | 1.607 | 0.348 | -78.3% | 0.325 | +7.1% |
| BSP26_04 | 1.009 | 0.280 | -72.2% | 0.271 | +3.3% |
| BSP21_06 | 0.905 | 0.208 | -77.0% | 0.187 | +11.2% |
| BSP22_03 | 0.469 | 0.090 | -80.8% | 0.090 | +0.0% |
| BSP22_04 | 0.453 | 0.089 | -80.4% | 0.093 | -4.3% |

Stages with unequal software-sprite call counts are excluded from that
table; draining batches can call showSprites at different frequencies.
Their measured totals and counts remain in the adjacent JSON:
SHP23, BSP03_01, BSP07_01, BSP07_02, BSP21_01, BSP21_04, BSP22_01, BSP25_01, BSP26_01, BSP27_01, BSP27_04, BSP29_01, CLIPROW, COMBINED.

Hardware-sprite scanline decoration has unequal output demand in this
browser-disconnected test and is intentionally not ranked as a renderer
speed comparison. Primitive durations are instrumented scopes, not
exclusive processor-cycle counts. No renderer was changed in this run.

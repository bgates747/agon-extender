# Framebuffer-only hardware comparison

624 complete timing intervals. Probe differences: 8. P4 snapshot delta: 0.

The table shows median enabled time within the primitive scope, then renderer-local elapsed
time including submission/drain effects. Values are milliseconds; each scrolling
case contains 64 repeated operations. These are not game FPS or video output rates.

| Case | Mainboard primitive ms | P4 primitive ms | Mainboard elapsed ms | P4 elapsed ms |
| --- | ---: | ---: | ---: | ---: |
| EMPTY | 0.002 | 0.002 | 15.659 | 14.503 |
| SHP20 | 7.823 | 6.041 | 49.452 | 31.524 |
| SHP23 | 10.511 | 6.885 | 49.300 | 65.349 |
| BSP03_01 | 37.607 | 11.518 | 881.983 | 3165.200 |
| BSP07_01 | 9.033 | 4.062 | 115.583 | 331.214 |
| BSP07_02 | 15.453 | 9.798 | 49.648 | 33.084 |
| BSP07_03 | 7.566 | 4.901 | 32.696 | 33.002 |
| BSP21_01 | 22.820 | 6.963 | 432.262 | 1447.800 |
| BSP21_02 | 7.794 | 3.048 | 33.683 | 32.998 |
| BSP21_03 | 7.868 | 2.810 | 32.690 | 32.998 |
| BSP21_04 | 7.806 | 2.638 | 32.721 | 32.998 |
| BSP21_05 | 7.881 | 2.715 | 32.743 | 32.998 |
| BSP21_06 | 7.472 | 2.700 | 32.662 | 32.999 |
| BSP22_01 | 16.855 | 5.656 | 265.365 | 881.525 |
| BSP22_02 | 0.002 | 0.002 | 16.637 | 16.998 |
| BSP22_03 | 0.654 | 0.128 | 16.899 | 16.980 |
| BSP22_04 | 0.252 | 0.097 | 17.099 | 16.313 |
| BSP22_05 | 0.182 | 0.040 | 16.694 | 16.998 |
| BSP25_01 | 23.351 | 5.844 | 316.114 | 1014.921 |
| BSP25_02 | 22.620 | 5.391 | 49.692 | 33.001 |
| BSP25_03 | 21.541 | 5.153 | 49.693 | 33.001 |
| BSP25_04 | 15.446 | 4.329 | 33.684 | 33.000 |
| BSP25_05 | 8.580 | 2.898 | 49.692 | 33.001 |
| BSP26_01 | 23.436 | 7.242 | 582.664 | 2048.142 |
| BSP26_02 | 5.718 | 2.710 | 32.631 | 33.071 |
| BSP26_03 | 5.614 | 2.277 | 33.602 | 32.998 |
| BSP26_04 | 6.950 | 2.611 | 33.640 | 32.998 |
| BSP27_01 | 22.939 | 6.571 | 481.969 | 1648.518 |
| BSP27_02 | 7.014 | 2.858 | 33.694 | 33.001 |
| BSP27_03 | 6.705 | 2.447 | 33.661 | 33.002 |
| BSP27_04 | 22.178 | 5.269 | 49.672 | 33.969 |
| BSP29_01 | 16.618 | 5.044 | 315.788 | 865.070 |
| BSP29_02 | 10.771 | 3.493 | 32.663 | 32.998 |
| BSP29_03 | 10.800 | 3.263 | 32.628 | 32.998 |
| BSP29_04 | 10.805 | 3.191 | 33.656 | 32.998 |
| BSP29_05 | 10.854 | 3.247 | 33.664 | 32.999 |
| SCROLL | 9.362 | 2.078 | 27.964 | 22.712 |
| CLIPROW | 6.334 | 1.951 | 50.377 | 50.734 |
| COMBINED | 7.102 | 2.660 | 84.742 | 84.950 |

Mainboard VGA scanout remained active; P4 output composition and transmission
were excluded. Hardware-sprite scanline costs are consequently not an equal-work
comparison. Primitive and software-sprite scopes overlap; do not add them.
Instrumentation-off keeps the old locks/fences, and enabled duration is not
zero-overhead production timing. Empty-marker cost is reported without subtraction.

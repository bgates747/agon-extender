# Display qualification pattern

`pattern-wide.svg` preserves the Author-approved 16:9 source with a centered
4:3 interior, circles/squares and two rows of64RGB222 swatches. It is the
maintained source; ignored preview PNGs are evidence, not a source dependency.

The scrolling builder crops the4:3 viewBox, changes mode/case identification,
rasterizes for the selected pixel grid, draws native3×5 swatch indices and
quantizes every pixel to the mode's exact default palette. No dithering.
The 4:3 crop has square physical geometry even when a mode's logical pixels
are not square; display scaling is distinct from raster dimensions.

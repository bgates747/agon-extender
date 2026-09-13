# Author video — BSP30 stage 17

Received 2026-09-13. The Author supplied IMG_2628.MOV and requested that media
remain untracked. A byte-identical copy and five extracted frames are retained
under ignored `agents/graphics-timing/framebuffer-pass2-batch/author-video/`.
The original Downloads file was left intact. Git ignore coverage was verified.

1. Original SHA256: `e039e748141b1a06191880f68292dd464085300cc8c56f1fd2ad5c3032d2c05e`.
   Size 4,184,393 bytes; duration 2.615 seconds; HEVC 1920x1080, reported 89/3 fps;
   AAC audio is present. The camera's stream rate is not an Agon frame rate.
2. Sampled views show two aligned rows of multicolour sprite tiles. The camera
   crops the monitor edges, so the pictures alone do not count all 16 sprites.
   The fixture and CSV identify the full selected population.
3. Bottom text includes Stage 17 and the incomplete result with 345 intervals
   saved to GQT003.CSV. Text lines overlap visibly, with subsequent service/MOS
   text beneath the retained stage. The image is not evidence that the fixture
   is still executing: its own terminal report is already on screen.
4. This corroborates the Author's physical display-failure report and ties the
   footage to `second-partial.csv`: repeat 1 / mainboard / detail 1/BSP30_17,
   FR_TIMEOUT 15. The Author separately reported errors at preceding stage 16;
   this short clip does not independently document that preceding stage.
5. The footage does not isolate sprite scanline overload from instrumentation
   interference, retained graphics/text viewport state, or camera sampling.
   Do not estimate scanout FPS, dropped-frame count or exact jitter frequency
   from these handheld samples. An audio track exists but was not analyzed.

The fixture's visible caption and residual sprites can outlive a failed timed
interval. The future completion-summary item QUAL-003-I005 should make final
state unambiguous, restore an appropriate text viewport and clear owned test
sprites outside measured intervals. No such display changes were made to the
39-case run already in progress.

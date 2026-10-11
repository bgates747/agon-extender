# PRX-06 CLI-only sender

Experimental historical direct-GPIO fixture, covered only by the Author's
comparison exception in DEVKIT-CONTROL-R01. It is not a supported EMOS API.
Source derives from legacy commit 4626fcc41a0da5811a4374175fe803957ec5ab4f,
via the retained unattended full-sweep sender. Preserve its original license
and provenance; this directory is a launcher/admission variant, not upstream.

1. Build with the maintained AgonDev toolchain:
   `make AGONDEV_TOOLCHAIN=/path/to/agondev`.
2. Deploy only `bin/prxcli.bin` to `/extender/install/prxcli.bin` and verify its
   complete readback. Do not modify `/autoexec.txt`; verify existing startup
   separately when preparing the card. Do not select a video mode in this fixture.
3. With normal P4 firmware and admitted EMOS CLI input, issue
   `LOAD /extender/install/prxcli.bin`, then `RUN`. The eZ80 enters bounded READY
   polling; only then may the host install and independently verify the retained
   historical receiver. This deliberately loses ordinary P4 input temporarily.
4. Require observed CLOCK waiting activity before USB arm. Run the bounded
   seven-profile sweep with three records per profile plus final zero-NOP record;
   stop at first failed/missing verdict. Retain receiver logs and capture when
   attached. The application writes no SD results or startup files.
5. Hold Agon reset during normal P4 recovery and verify all normal flash segments
   and HTTP initialization before releasing reset. Verify actual reboot, keyboard
   admission and ordinary CLI/SD access afterward. No autoexec restoration is
   required by this sender.

Admission budget is sixteen times the retained sender's original finite
instruction-loop budget, allowing receiver installation after RUN. It is not
calibrated wall time. The original interrupt policy remains: interrupts are
masked during admission/send/completion and restored on return. Host failure
therefore cannot be cancelled through keyboard input; physical reset is recovery
if admission times out or control is lost. Byte kernels, seven speed profiles,
completion timeout, full-sweep logic and canary are unchanged. No infinite wait,
automatic retry or electrical qualification is implied by a successful build.

# Clocks and DVFS

**Last verified: 2026-11-16.**

## What it is

On the Tensor G1 the CPU, GPU and memory clocks are not set by writing registers. They are requested from a firmware
service (ACPM) through a mailbox. Android changes them all the time (DVFS). PixOS sets them **once, in the shim, before XNU starts**.

## Status

**Static clocks, set once per boot** (*observed on hardware* since 2026-10-22, runs `dvfs1` to `dvfs4`). There is no run-time governor.

## What worked

- **Raising the CPU clusters through ACPM** before the jump into XNU (runs `dvfs1` to `dvfs4`, 2026-10-22).
- **The same path for the GPU and memory clocks** (`shim/gpuclk.c`, `shim/mifclk.c`), with the result printed in the kernel log
  so a boot can prove which clocks it ran at (patches 0203, 0214, 0367).
- **Finding the real limiter at low clocks.** With everything at the bootloader's rates the heavy bench drew 21.2 frames/s
  (run `1d81`, 2026-11-13). Raising **only the memory clock** gave 45.2 (run `a59a`). Raising only the GPU clock gave about 25
  (one boot, 2026-11-13). Memory speed, not GPU speed, was the wall.
- **The release configuration** (*observed* 2026-11-15, runs `155b`, `8177`): GPU 150 MHz, memory 1352 MHz, A76 at 1663 MHz,
  X1 at 1826 MHz, A55 at the bootloader's rate. Rendered 50.6 frames/s at 3.3 W.

## What didn't

- **The boost configuration was not stable.** With CPU clocks at maximum, GPU at 762 MHz and memory at the top level, the phone
  reset itself about 5 to 6 minutes into the heavy bench: 16 times over two days, at every memory level tried, with no panic line
  (*observed* 2026-11-12/13). The cause was not found. Heat is not it: the resets also came with the battery at 36 to 40 C.
- **The boost configuration ran hot.** The battery reached 51.6 to 53 C under it before any thermal code existed (*observed* 2026-11-12).
- **More clock is not more frames.** GPU clock alone and CPU clock alone each moved the frame rate by about one frame/s (runs above, and `fede`).

## Untested or never attempted

- **Changing clocks at run time.** XNU has no ACPM client for clocks; nothing follows load or temperature.
- **The middle GPU levels** (572 and 701 MHz) as a release configuration.
- **Why the boost configuration resets.** Open.

## Ideas if you want to pick it up

- Port a minimal clock client into XNU and let the thermal thread step the big cores down before it removes them ([Thermal](thermal.md)).
- Find the reset: log the reset cause registers on the next boot (patches 0120, 0140, 0318 already print some of them) under the boost configuration.
- Re-run the "one clock at a time" experiment on another SoC before tuning anything; it saved us from optimising the wrong thing.

## Where to look

- Shim: `shim/acpm.c`, `shim/gpuclk.c`, `shim/mifclk.c` in [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel/tree/main/shim).
- Patches: 0096, 0097 (clock probes), 0203, 0214, 0367 (clock witnesses in the log).
- Notes: [CPU DVFS on gs101](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/25-cpu-dvfs-gs101.md), [ACPM rails](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/23-acpm-rails.md).
- Milestone: [Everything at once, at low clocks](../milestones/all-on-low-clock.md).

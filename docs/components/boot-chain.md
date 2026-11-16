# Boot chain: bootloader, shim, device tree

**Last verified: 2026-11-16.**

## What it is

The path from the Pixel's stock bootloader to the first instruction of XNU:

1. The stock bootloader loads our image into RAM with `fastboot boot`.
2. The **shim** (our bare-metal program) runs first. It reads the bootloader's device tree, brings up storage, switches on the
   rails and clocks XNU will need, and builds an **Apple Device Tree** (ADT), the format XNU expects from iBoot.
3. The shim jumps into XNU with the kernel, the ADT and the boot arguments packed in one payload.

## Status

**Every boot since 2026-10-21 goes through it** (*observed on hardware*: first in `device/google/bluejay/docs/GATE0_RESULTS.md`; newest: runs `155b`, `8177`, 2026-11-15). Always started from a computer.

## What worked

- **RAM boot with an AVB footer.** An unsigned image was accepted by `fastboot boot` and then silently not run. The same image with an
  AVB hash footer (throwaway test key) ran (*observed* 2026-10-20/21, `GATE0_RESULTS.md`). Nothing is flashed to `boot`.
- **Probe report.** The shim's first job was to report the hardware: entered at EL2 with the MMU off, 4x A55 + 2x A76 + 2x X1,
  16 KiB pages on all cores, no pointer authentication, timer 24.576 MHz, PSCI 1.1, both watchdogs armed by the bootloader (*observed* 2026-10-21).
- **A synthesised device tree.** `tools/mkadt.py` builds a minimal ADT from two small data files (`soc.json`, `board.json`) instead
  of translating Android's tree. Identity keys are borrowed from the iPhone X tree in the user's own IPSW (*read from source*).
- **Memory map from the live tree.** XNU gets the hole-free upper RAM range at `0x880000000` (`board.json`).
- **The shim can stay below XNU at EL2** with stage-2 translation on (*observed* 2026-10-29, runs `el2-2-xnu`, `el2-3-f7`). It traps nothing yet.
- **Boot time.** About 108 s from the boot command to the lock screen on a migrated root; about 346 s on the first boot after a flash
  (*observed* 2026-10-25, runs `bs-q2`, `bs-q1`, 8 cores).

## What didn't

- **"Unlocked" did not mean "any image boots".** The footer rule cost the first day.
- **The memory map could not be taken from the reference port** or from the 6 GB on the box: the low bank is cut by firmware carve-outs.
- **RAM log across a reset.** The bootloader rewrites the RAM we hoped to read back after a reset; pstore did not survive (*observed* 2026-10-21).
- **Boot arguments are cut silently when the line is too long.** XNU's boot line was 608 bytes; arguments past it vanished without an error.
  Patches 0176 and 0320 raise the limit and patch 0177 logs every truncated read ([Lessons](../LESSONS.md)).
- **A shim that disables the watchdogs can hang the phone** until a long key press. Every wait in the shim is bounded now.

## Untested or never attempted

- **Boot without a PC.** Not started. It needs a design that stays reversible: the project never writes `boot` partitions.
- **Any other bootloader version or phone.** One phone, one bootloader.
- **The debug UART on the USB-C sideband pins.** It needs a 1.8 V cable; the tooling does not use it.
- **Trapping device registers from EL2** to trace what XNU touches. The groundwork runs; no register is trapped.

## Ideas if you want to pick it up

- A reversible "boot from the power button": for example a chain-loader in a slot the factory image restores, kept behind the same
  audit that forbids every write outside `userdata`. Write the recovery proof first.
- Split the gs101 probe sequence in `shim/shim.c` behind a small board interface, so a second SoC does not need a fork.
- Use the EL2 groundwork to log MMIO writes of one driver, as a cheap oracle for "what did we touch".

## Where to look

- Shim: [`shim/`](https://github.com/PixOS-Project/pixelios-kernel/tree/main/shim) (`start.S`, `shim.c`, `fdt.c`, `loader.c`, `el2.c`), build with `tools/pix build`.
- Device tree and payload: [`tools/mkadt.py`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/tools/mkadt.py), [`tools/mkpayload.py`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/tools/mkpayload.py), [`board.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json), [`soc.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/soc.json).
- Notes: [boot path](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/01-boot-path.md), [gate 0 results](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/docs/GATE0_RESULTS.md).
- Patches: 0176, 0177, 0320 (boot line), 0180 (EL2 report).
- Blueprint stages [1](../BLUEPRINT.md#1-boot-shim-and-bootloader-hand-off) and [2](../BLUEPRINT.md#2-device-tree-for-xnu-apple-adt). Milestone: [First boot](../milestones/first-boot.md).

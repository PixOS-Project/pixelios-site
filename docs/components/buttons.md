# Physical buttons

**Last verified: 2026-11-16.**

## What it is

Power, volume up and volume down are three GPIO pins. A small kernel thread samples them and feeds key events to iOS's HID service.

## Status

**Partial: key presses reach the kernel driver** (*observed on hardware*: power key down/up on run `resident-164801-b1`, 2026-11-11, power and volume-up presses on run `resident-204614-b1`, 2026-11-12). **What iOS does with them (lock, wake, volume) was not checked.** Volume-down was never pressed in a logged boot.

## What worked

- **A read-only driver** (patch 0087). It only reads the level of each pin; it configures nothing. The pins and their polarity are
  data in `board.json`, not constants in the code.
- **Debounce logic tested on the host.** The test compiles the same text that ships in the patch.

## What didn't

- Nothing failed. The buttons were pressed in only a few logged boots: almost every boot is driven by scripts, and a long
  press of the power key combination is the manual way back to fastboot.

## Untested or never attempted

- **Every user-visible function**: lock and wake with the power key, volume keys, screenshots, the power-off slider. The kernel logs the press; nobody checked the screen.
- **Volume down**: never pressed in a logged boot.
- **Interrupts.** The pins are polled every 10 ms.
- **Wake from sleep** (there is no sleep yet).

## Ideas if you want to pick it up

- This is the smallest open item on the site: press each key on a boot, watch the iOS reaction (the kernel log line is already proven for power and volume up), and report it.
- A held key at boot is ignored on purpose, so a wrong polarity guess cannot emit a phantom press. Check polarity first if nothing happens.

## Where to look

- Patch 0087; data: `key_pins` in [`board.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json).
- Note: [hardware buttons on gs101](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/16-keys-gs101.md).
- Blueprint stage [8](../BLUEPRINT.md#8-touch-and-buttons).

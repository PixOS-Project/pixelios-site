# Touch

**Last verified: 2026-11-16.**

## What it is

The touch controller is an STMicro FTM5 on an SPI bus. Our kernel driver reads its events and hands them to iOS's HID stack as
digitizer events, so SpringBoard sees a finger.

## Status

**Works with a real finger** (*observed on hardware* 2026-11-15, demo boot job 1308: 5791 touch interrupts, none empty, no storm; unlock and app open done by hand). First touch: 2026-10-22.

## What worked

- **Powering the chip.** After the bootloader the controller's two regulator rails are off. The shim switches them on through the
  firmware mailbox before XNU starts (*observed* 2026-10-22, runs `touchx3`, `touchx5`). The chip then answers its ID, `36 48`.
- **Events into iOS**: 85 touch events with the GPU path up (run `demo-gpu-touch-wifi`, 2026-11-04).
- **Interrupt instead of polling** (patches 0355, 0356). The driver polled 125 times a second; now the chip's interrupt line wakes it.
- **Scripted touch for benchmarks.** The kernel can inject swipes and taps (patches 0152, 0156, 0312), which is how the frame-rate
  benches drive the UI without a person.

## What didn't

- **Six patches went into SPI clocks, pin muxes and transfer recipes before anyone checked power.** An unpowered chip reads as all
  ones or all zeros depending on the pull-up. Check power before bus timing ([Lessons](../LESSONS.md)).
- **Blind scripted taps get lost under stress.** A tap at fixed coordinates cannot know what is on screen; benches had to check the
  screen state before each step.

## Untested or never attempted

- **Multi-finger gestures** (pinch, rotate) were not checked in a log.
- **More than one finger session.** The real-finger result is one boot.
- **Palm rejection, glove or wet-screen modes, the controller's low-power modes.**
- **Touch latency against stock.** A latency probe exists (patch 0153); no comparison was made.
- **Controller firmware update.** Never written, and should not be.

## Ideas if you want to pick it up

- On a new phone, read the vendor touch driver's power-on sequence first, then the bus.
- Log raw coordinates and the iOS-side event side by side; coordinate scaling between the panel and the iOS canvas is easy to get subtly wrong.

## Where to look

- Patches: 0088 (driver), 0089, 0092, 0095 (clock and transfer fixes), 0153 (latency), 0152, 0156, 0312 (injection), 0304 (gaps), 0348, 0355, 0356 (events and interrupt).
- Shim: `shim/touchprobe.c`, rails in `shim/acpm.c`; data: touch keys in [`board.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json).
- Notes: [touch on gs101](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/15-touch-gs101.md), [the SPI stall investigation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/21-touch-spi-stall-investigation.md), [ACPM rails](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/23-acpm-rails.md).
- Blueprint stage [8](../BLUEPRINT.md#8-touch-and-buttons).

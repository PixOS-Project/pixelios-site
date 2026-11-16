# SpringBoard: the iPhone UI on the Pixel

**Last verified: 2026-11-16.** Milestone M1 · 2026-10-22 · **done**

## Goal

Reach the iOS lock screen and home screen on the Pixel's panel, on all 8 CPU cores, and be able to touch it and read its logs.

## What was done

- **The rest of the inherited patch stack**, then SMP: all eight cores started through PSCI.
- **Daemon by daemon.** For each daemon that exited or waited, find the failing call and decide where the fix belongs: a kernel
  stand-in, a device-tree key, or a tweak in the root recipe.
- **Touch.** A new driver for the Pixel's STMicro controller, after switching its two power rails on from the shim.
- **A USB network gadget** that streams the kernel log over UDP from the running iOS. It became the debug channel for everything after.
- **CPU clocks raised** through the firmware mailbox before the jump into XNU.

## How it was proven

All *observed on hardware*, 2026-10-22 unless noted.

| Claim | Evidence |
|---|---|
| Lock screen and home screen on the panel | first seen 2026-10-22; since then checked automatically: 19 of 19 captured screens match their references (run `gputest-surffail-b`, 2026-11-11) |
| 8 cores | run `usbnet4-cpus8` |
| Touch reaches SpringBoard | runs `touchx3`, `touchx5` |
| Settings > General > About opens | run `about4` |
| Kernel log over USB from running iOS | every run since 2026-10-22 |
| CPU clocks raised | runs `dvfs1` to `dvfs4` |

## What it unlocked

A phone that looks and reacts like an iPhone, drawn by the CPU. That made three things possible: scripted test runs that end in a
single report, the GPU work (there was now a UI to accelerate), and the Wi-Fi work (there was now a Settings app to join from).

## Dead ends

- **Touch: six patches into SPI clocks and pin muxes** before anyone checked that the chip had power. It did not.
- **The Apple-logo stall.** The first boots hung at the logo. It took a root recipe tweak and kernel patches 0086, 0087 and 0099 to get past it.
- **Settings > About hung for 300 s.** A configuration daemon waited for a network-stack service this kernel did not have. A small stand-in service fixed it.
- **Daemons marked panic-on-crash** reboot the phone on their first crash, which hides the actual cause.

Components: [iOS userland](../components/userland.md), [CPU](../components/cpu-smp.md), [Touch](../components/touch.md), [USB](../components/usb-debug.md). Next: [the test loop](test-loop.md).

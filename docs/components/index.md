# Components

**Last verified: 2026-11-16.** One page per hardware or software block the port had to deal with. Every page has the same headings,
so you can compare blocks or jump straight to the part you need:

**What it is · Status · What worked · What didn't · Untested or never attempted · Ideas if you want to pick it up · Where to look**

The point is reuse. If you are porting to another phone, the "What didn't" and "Ideas" sections are the parts we wish we had read first.

## Overview

State on 2026-11-15, *observed on hardware*. Run labels point into the maintainers' run logs; each page has the detail.

| Component | Hardware | Status | Evidence | Biggest open item |
|---|---|---|---|---|
| [Boot chain](boot-chain.md) | stock bootloader, our shim, Apple device tree | boots on every run, from a PC only | since 2026-10-21, `GATE0_RESULTS.md` | boot without a PC |
| [CPU and SMP](cpu-smp.md) | 4x A55, 2x A76, 2x X1 | 8 cores run; the release config uses 5 | run `usbnet4-cpus8`, 2026-10-22 | idle states, no run-time control |
| [Interrupts and timers](interrupts-timers.md) | GICv3, Arm timer | GPU, Wi-Fi, storage and touch on interrupts | runs `gputest-nav43`, `c17e`, `c1f4`, job 1308 | USB and Bluetooth UART still polled |
| [Clocks and DVFS](clocks-dvfs.md) | ACPM firmware mailbox | static, set once by the shim | runs `dvfs1` to `dvfs4`, 2026-10-22; `155b`, `8177` | boost configuration resets; no governor |
| [Storage](storage-ufs.md) | UFS, Exynos host | root mounted read-write, HS-G4, one command at a time | since 2026-10-21; run `c1f4`, 2026-11-14 | command queueing, data protection |
| [USB and debug channel](usb-debug.md) | DWC3, USB 3 | kernel log over USB on every run | since 2026-10-22; run `el2-3-f7` | device mode only |
| [Recovery](recovery.md) | SoC watchdog, reset registers | panic and hang return to fastboot | runs `20261107T145123Z-panic-self-recover`, `ar-c-wdttest` | no watchdog very early in boot |
| [iOS userland](userland.md) | iPhone X iOS 16.7 root | lock screen, home, Settings, Safari run | run `gputest-surffail-b`; job 1308 | Metal clients, restart loops |
| [Display](display.md) | bootloader framebuffer, command-mode panel | UI on the panel by CPU copy; 49.0 drawn presents/s | run `18e1`, 2026-11-15 | 50/s bar, real scan-out, brightness |
| [GPU](gpu.md) | Mali-G78 MP20 | UI drawn by the GPU; 50.6 frames/s at 150 MHz | runs `155b`, `8177`, 2026-11-15 | 60 on every step; Metal |
| [Touch](touch.md) | STMicro FTM5, SPI | a real finger drives the UI | job 1308, 2026-11-15 | multi-finger not checked |
| [Buttons](buttons.md) | 3 GPIO keys | presses reach the kernel; **iOS reaction not checked** | 2026-11-12 | check iOS reaction |
| [Wi-Fi](wifi.md) | BCM4389, PCIe | WPA2, real internet, 188 to 285 Mbit/s | runs `155b`, `8177`, 2026-11-15 | UDP loss under load; WPA3 untested |
| [Bluetooth](bluetooth.md) | BCM4389, UART | scan, connect, pair on the stock daemon | runs `bt-pr3`, `bt-pr4`, `bt-hotpair`; job 1308 | audio; UART speed |
| [Audio](audio.md) | codec, amplifier, A2DP | **no sound** | run `bt-va3`, 2026-11-11 | speaker driver; A2DP start |
| [Power and charging](power-charging.md) | charger, fuel gauge | charges at light load, one run | run `chg-p3`, 2026-11-10 | drains under load; no sleep |
| [Thermal](thermal.md) | battery temperature | 33 to 41 C in the release benches | runs `155b`, `8177` | backstop not seen firing; no SoC sensors |
| [Not attempted](not-attempted.md) | modem, cameras, sensors, GPS, NFC, haptics | **nothing** | no code | everything |

## How to read a page

- **Status** is one line with its evidence. "Works" always names a run and a date.
- **What didn't** includes dead ends that cost us boots or days. They are there so you can skip them.
- **Untested or never attempted** separates "we tried and it failed" from "nobody looked". Most surprises hide in the second group.
- **Where to look** points at patch numbers in [`xnu/patches/`](https://github.com/PixOS-Project/pixelios-kernel/tree/main/xnu/patches), shim files and research notes in the public repositories.

Patch numbers are file-name prefixes: patch 0354 is the file starting `0354-` in that directory. The header of each patch says what it does and why.

## Related

- The same blocks as porting stages, for any device: [Porting blueprint](../BLUEPRINT.md).
- When each block first worked: [Milestones](../MILESTONES.md).
- Measured numbers for every rung: [Status](../STATUS.md).

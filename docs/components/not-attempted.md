# Not attempted: cellular, camera, sensors, GPS and more

**Last verified: 2026-11-16.**

## What it is

Hardware on the Pixel 6a that PixOS has **no driver for and has not researched**. They share one page because the honest content
for each is short. If you start one, give it its own page.

## Status

**Nothing on this page works, and nothing was tried.** (*Read from source*: no patch in the series touches these blocks.)

## What worked

Nothing was tried, so nothing worked. Two related facts:

- **The iOS side is told the truth.** Jobs that need this hardware are dropped from the root or left to log their failure; no
  device-tree node pretends the hardware exists.
- **The modem partition is never written.** That is a safety rule, not a missing feature.

## What didn't

Nothing failed, because nothing ran. The cost shows elsewhere: iOS daemons that expect this hardware exit, wait or restart, and
some of the background CPU load on [Userland](userland.md) may come from that (*guess*).

## Untested or never attempted

| Block | State | What makes it hard |
|---|---|---|
| **Cellular** (calls, SMS, data, eSIM) | never attempted; out of scope while the modem partition stays untouched | iOS's baseband stack expects Apple's or Qualcomm's modem interface, not the Pixel's modem |
| **Cameras** (rear and front) | never attempted | sensor drivers, the image signal processor, and iOS's camera stack, which expects Apple's pipeline |
| **Motion sensors** (accelerometer, gyroscope, compass) | never attempted | no auto-rotate; on Android these sit behind a sensor hub with its own firmware |
| **Proximity and ambient light** | never attempted | no auto-brightness (there is no brightness control yet either) |
| **GPS / GNSS** | never attempted | a separate chip and firmware; iOS location services have nothing to read |
| **Fingerprint reader, Face ID** | never attempted | the Pixel's reader is nothing like Apple's biometric hardware; the passcode path is what runs |
| **NFC, secure element, Apple Pay** | never attempted | |
| **Haptics (vibration motor)** | never attempted | |
| **Speaker and microphones** | never attempted: see [Audio](audio.md) | |
| **Sleep and wake** | never attempted | needs CPU idle states, display off, wake sources and every driver's suspend path |
| **Boot without a PC** | never attempted: see [Boot chain](boot-chain.md) | must stay reversible |
| **Display brightness, always-on display** | never attempted: see [Display](display.md) | |
| **USB host mode and accessories** | never attempted: see [USB](usb-debug.md) | |

The right-hand column is our expectation (*guess*). None of it was checked on the phone or in the sources.

## Ideas if you want to pick it up

- **Start with what is small and visible.** Haptics, brightness and the proximity or light sensor are single chips with public Linux
  drivers to read. Each would be noticed at once.
- **Motion sensors** would unlock rotation. First find out whether they can be reached directly or only through the sensor hub.
- **Cameras and cellular are projects of their own.** For either, the first deliverable is a research note that maps the hardware
  path and names what iOS expects, with sources, before any code.
- **Sleep and wake** depends on work listed on other pages (CPU idle states, display off). It is the block that would make the
  phone feel like a phone; do the pieces first.
- Follow the order on [Method](../METHOD.md#8-port-a-block-in-a-fixed-order): oracle from the stock OS, a cited spec, a conformance
  matrix for the iOS side, then runs. And follow the safety rules: nothing here needs a write to any partition but `userdata`.

## Where to look

- The gs101 peripheral map: [gs101 peripherals](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/docs/02-gs101-peripherals.md).
- How a block was started from zero: [Wi-Fi](wifi.md) and [Touch](touch.md) are the best examples.
- What iOS asked of us elsewhere: [iOS 16.7 interface notes](../IOS-INTERFACES.md).
- Open work in order: [Roadmap](../../ROADMAP.md).

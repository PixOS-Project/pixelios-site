# Bluetooth (BCM4389)

**Last verified: 2026-11-16.**

## What it is

Bluetooth is the same Broadcom chip as Wi-Fi, reached over a UART with the standard HCI protocol. iOS's Bluetooth daemon
(`bluetoothd`) expects an Apple chip: it picks a "chip profile" from the device identity and sends vendor commands this chip does not know.

PixOS runs **Apple's stock daemon, unpatched**. Our kernel driver translates: it maps the vendor commands the daemon sends onto
standard HCI the chip supports, and answers an error plus a `GAP` log line for anything it cannot map.

## Status

**Scan, connect, advertise and pair work on the stock daemon** (*observed on hardware* 2026-11-10/11, runs `bt-pr2`, `bt-pr3`, `bt-pr4`, `bt-hotpair`). A headset was paired by hand in Settings on 2026-11-15 (job 1308). **No audio.**

## What worked

| Date | Step | Evidence (*observed on hardware*) |
|---|---|---|
| 2026-11-03 | chip answers HCI Reset, once the UART pads were switched from GPIO to UART | run `bt-s4h` |
| 2026-11-10 | stock daemon up in 53 to 75 ms, no daemon exits, two boots | runs `bt-pr2`, `bt-pr3` |
| 2026-11-10 | scan finds 52 and 64 devices; LE connect with a GATT read; advertising | runs `bt-pr3`, `bt-pr4`, `bt-conn1`, `bt-conn2` |
| 2026-11-11 | pairing with a PC; the bond survives a reboot | runs `bt-hotpair`, `bt-a2dp` |
| 2026-11-11 | on by default, without delaying boot (launchd starts 0.8 s after the firmware load begins, was about 42 s) | run `bt-def1`, one run |
| 2026-11-15 | headset paired by hand: Simple Pairing Complete, link key, 3 connections | job 1308 |
| 2026-11-15 | firmware load no longer spins a CPU core for 41.5 s (patch 0360) | run `d9a3` |

## What didn't

- **Patching Apple's daemon.** Byte patches got the first results and were then removed. The contract is implemented in our driver instead; no patched Apple binary is used or shipped.
- **ROM firmware gives wrong answers.** A kernel built without the chip's patch firmware falls back to the ROM and misleads. Two test boots were wasted that way.
- **Pairing as initiator with a phone as the peer failed.** A PC running BlueZ, which we could script, got the first bond.
- **iOS did not reconnect by itself after a reboot** (the PC did; run `bt-a2dp`).
- **Audio to a headset.** The stream is configured but never started ([Audio](audio.md)).
- **Some vendor commands are refused by the chip.** They are logged as gaps; no visible effect was tied to them.

## Untested or never attempted

- **Keyboards, mice, game controllers, watches, file transfer, calls (hands-free profile).**
- **The chip's low-power mode.** The wake line is held high, so the chip never sleeps. It costs power only.
- **A faster UART.** Receive is polled about 100 times a second (*read from source*), which caps the incoming data rate below what
  audio streaming needs (*calculated*, not measured).
- **More than one headset model.**

## Ideas if you want to pick it up

- Move the UART receive to its interrupt, then raise the baud rate. Both are needed before audio can flow.
- Use a scriptable peer. `bt-client/pc/` in pixelios-userland has the PC side we used.
- On another iOS build the chip profile choice and the vendor commands must be re-derived; see the [interface notes](../IOS-INTERFACES.md#bt) for what to look for.

## Where to look

- Patches: 0189 (UART transport), 0213 (stream channel), 0228 (patch firmware load), 0285 (vendor-command adapter), 0286 (Skywalk channel), 0295, 0296 (default on, asynchronous bring-up), 0360 (load without spinning).
- Userland: [`bluetool/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/bluetool) (open replacement for the chip-boot helper), [`bt-client/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/bt-client) (test client and PC peer).
- Blueprint stage [10](../BLUEPRINT.md#10-bluetooth). Milestone: [Bluetooth](../milestones/bluetooth.md).

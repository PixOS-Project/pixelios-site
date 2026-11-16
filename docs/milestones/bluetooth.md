# Bluetooth on Apple's stock daemon

**Last verified: 2026-11-16.** Milestone M13 · 2026-11-03 to 2026-11-11 · **done** (audio is a separate, open milestone)

## Goal

iOS Bluetooth works with Apple's own `bluetoothd`, **without patching the binary**: the controller comes up, a scan lists devices,
iOS connects, advertises and pairs, and a bond survives a reboot.

## What was done

1. **Transport**: a kernel UART driver for HCI, after finding that the UART pads were still configured as plain GPIO.
2. **Firmware**: load the chip's patch firmware (from the user's own phone) at boot, later in the background so boot does not wait for it.
3. **Keychain**: make iOS key-store writes succeed, which the daemon needs.
4. **A vendor-command adapter in the kernel driver.** iOS 16.7 has no chip profile for this Broadcom chip; it picks one from the
   device identity and sends commands meant for another chip. The adapter maps them onto standard HCI and logs what it cannot map.
5. **A scriptable peer**: a PC running BlueZ, to pair against under test control.

## How it was proven

All *observed on hardware*.

| Rung | Result | Date | Runs |
|---|---|---|---|
| Controller answers HCI Reset | Command Complete read back | 2026-11-03 | `bt-s4h` |
| Keychain writes | 0 unsupported key-store calls | 2026-11-03 | `kc-s1` |
| Stock daemon stays up, no binary patch | powered in 53 to 75 ms, 0 exits, two boots | 2026-11-10 | `bt-pr2`, `bt-pr3` |
| Scan | 52 and 64 devices discovered | 2026-11-10 | `bt-pr3`, `bt-pr4` |
| LE connect | pass, one GATT service read | 2026-11-10 | `bt-conn1`, `bt-conn2`, `bt-pr3`, `bt-pr4` |
| Advertising | accepted by the chip, 90 s, one run | 2026-11-10 | `bt-pr4` |
| Pairing; bond after reboot | paired on both sides; iOS reports the bond after a reboot | 2026-11-11 | `bt-hotpair`, `bt-a2dp` |
| On by default | boot no longer waits about 42 s for the firmware, one run | 2026-11-11 | `bt-def1` |
| Headset paired by hand in Settings | pairing complete, link key, 3 connections | 2026-11-15 | job 1308 |

## What it unlocked

Bluetooth as a normal iOS feature, toggled and paired from Settings. It also put the audio question on the table: a headset now
connects, so the missing piece is audio routing, not the radio.

## Dead ends

- **Byte-patching `bluetoothd`.** It produced the first "daemon stays alive" result (run `bt-s4k`, 2026-11-03) and was then replaced.
  Implementing the contract in our own driver is cleaner and means no modified Apple binary exists anywhere.
- **Dropping the daemon.** In October the Bluetooth job was removed from the root to get past a boot problem. That is not a fix; it came back.
- **A kernel built without the patch-firmware stack** silently ran the chip's ROM firmware. Two boots gave misleading results.
- **Pairing as initiator with a phone peer.** It failed; the PC peer got the first bond.
- **Unpowered, un-muxed hardware.** The controller "never answered" until one pad-function write. Check pins and power before protocol.

Component: [Bluetooth](../components/bluetooth.md). Then: [Audio](../components/audio.md).

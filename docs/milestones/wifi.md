# Wi-Fi: from a chip ID to Settings

**Last verified: 2026-11-16.** Milestone M8 · 2026-10-21 to 2026-11-11 · **done** (real internet under load followed on 2026-11-15)

## Goal

iOS Settings lists nearby networks, joins a WPA2 network with a password, and the phone has a working connection, on the phone's
**own radio**. The maintainer decided on 2026-10-21 that a USB network adapter would not count; USB Ethernet stays a debug channel.

## What was done

The work climbed a ladder of small, checkable rungs. Each rung is one log line that either appears or does not.

1. **PCIe link** from the shim: rails, enable pin, PHY, clocks, reset timing, link training. Table-driven, with a write allow-list and a teardown that always runs.
2. **Chip walk and firmware load**: enumerate the chip's cores, download firmware and calibration data (from the user's own phone), start the chip's CPU.
3. **Message rings and control calls**: the dongle protocol, modelled on OpenBSD's `bwfm`.
4. **Scan, join, keys.** The WPA2 4-way handshake runs in our host driver.
5. **An `en0` that iOS accepts**: the Apple80211 request types, scan-record layout and link-state keys that the Wi-Fi daemon and Settings need.
6. **Throughput and reliability**: a host throughput server, cold-boot repeats, and forced disconnects from the access point.

## How it was proven

All *observed on hardware*.

| Rung | Result | Date | Runs |
|---|---|---|---|
| Chip ID through the PCIe window | read | 2026-10-24 | `w3a-n30` |
| Firmware running | shared structure answered | 2026-10-26 | `wlan-runE-0133` |
| Scan | 8 access points | 2026-11-03 | `20261103T223800Z-wlan-runG2-clm24b` |
| WPA2 join | handshake messages 1 to 4, keys set | 2026-11-08 | `wlan-runG2-join25g` |
| Ping from the kernel, then from iOS | 10 of 10 each | 2026-11-08 | `wlan-runG2-join26d`, `wlan-iosping-c` |
| Joined in Settings, DHCP lease | checkmark shown, two boots | 2026-11-09 | `wlan-wui-f2`, `wlan-wui-g` |
| Throughput | 112.4 and 110.2 Mbit/s down, 67.8 and 68.1 up, every 1 s interval at target for 30 s | 2026-11-09 | `wlan-perf-f2`, `wlan-perf-f3` |
| Reliability | 3 of 3 cold boots; 4 of 4 reconnects after the access point banned the phone | 2026-11-10/11 | `wd6-cold1` to `wd6-cold3`, `wd6-apblock`, `wd6-apblock-r` |
| Live network list in Settings | about 20 rows from a 13-channel scan | 2026-11-11 | `wd6-scan2`, `wd6-scan3`, `wd6-rec1` |

## What it unlocked

A network that iOS itself manages, which is the base for anything online. It also set the pattern for the next block: Bluetooth
is the same chip, and the "ladder of log lines" method was reused there.

## Dead ends

- **"The firmware runs the WPA2 handshake."** The first plan assumed it. One capture under Android showed the host does, and the plan changed.
- **Days between "firmware running" and "first answer".** After the host-side setup the firmware did not answer (2026-10-29 state);
  the path to the first scan took until 2026-11-03.
- **Small crashes, one at a time**: a variable-length event structure, receive buffers posted once and exhausted, a transmit-index check.
- **A USB network faking a pass.** Test traffic must be bound to the Wi-Fi interface.
- **"Works" meant pings.** Ten local pings passed long before DNS and HTTPS did. Real internet under load needed a larger receive
  buffer pool and a correct clock ([next milestone](all-on-low-clock.md)).

Component: [Wi-Fi](../components/wifi.md). Blueprint stage [9](../BLUEPRINT.md#9-wi-fi).

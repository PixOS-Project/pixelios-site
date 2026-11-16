# Wi-Fi (BCM4389)

**Last verified: 2026-11-16.**

## What it is

The Wi-Fi chip is a Broadcom BCM4389 on PCIe. The decision from day one was to drive the real radio and not to substitute a USB
network adapter. Four layers make it work:

1. the **shim** powers the PCIe link (rails, PHY, reset timing) from a table with its own write allow-list;
2. a **kernel driver**, modelled on OpenBSD's `bwfm`, loads the firmware, talks the chip's message protocol, and runs the WPA2 handshake;
3. an **Apple80211-facing `en0`** interface that iOS's Wi-Fi daemon and Settings accept;
4. **firmware and calibration files from the user's own phone**. They are never in our repositories.

## Status

**Joins WPA2 networks from Settings and carries real internet traffic** (*observed on hardware* 2026-11-15, runs `155b`, `8177`: address, route, DNS and HTTPS checks 9 of 9; TCP download 285.4 and 188.1 Mbit/s, upload 97.1 and 97.0, during the full GPU bench, no link drop).

## What worked

| Date | Step | Evidence (*observed on hardware*) |
|---|---|---|
| 2026-10-24 | PCIe link up, chip ID read | run `w3a-n30` |
| 2026-10-26 | firmware loaded and running | run `wlan-runE-0133` |
| 2026-11-03 | first scan: 8 access points | run `20261103T223800Z-wlan-runG2-clm24b` |
| 2026-11-08 | WPA2 4-way handshake, keys installed; ping from the kernel and from iOS, 10 of 10 | runs `wlan-runG2-join25g`, `wlan-runG2-join26d`, `wlan-iosping-c` |
| 2026-11-09 | joined in Settings with a DHCP lease; 112 Mbit/s down, 68 up | runs `wlan-wui-f2`, `wlan-wui-g`, `wlan-perf-f2`, `wlan-perf-f3` |
| 2026-11-10/11 | 3 cold boots in a row; 4 of 4 reconnects after the access point banned the phone; live network list in Settings | runs `wd6-cold1` to `wd6-cold3`, `wd6-apblock`, `wd6-apblock-r`, `wd6-rec1` |
| 2026-11-13 | first interrupts from the chip (the handler was fixed afterwards, patch 0349) | run `c17e` |
| 2026-11-15 | real internet under full load | runs `155b`, `8177` |

Two fixes mattered most for the last step:

- **A bigger receive buffer pool** (patch 0357). Under a 140 to 180 Mbit/s download the access point dropped the phone. The pool was
  16 buffers, refilled one at a time. Sized and refilled the way Linux does it, full tests ran at 173 to 230 Mbit/s with no drop in two load boots.
- **A real clock** (patch 0345). The calendar started at 1970, which breaks TLS.

## What didn't

- **The first plan assumed the firmware runs the WPA2 handshake.** A capture under Android showed the host does. Our driver runs it.
- **Each early crash was one small thing**: a variable-length event structure, receive buffers posted once and used up, a transmit-index check.
- **Settings showed nothing** until the link-state keys and the interface media answer were right.
- **UDP download loses packets under heavy load**: 27.3 % and 39.5 % in the two bench boots, 2.4 % in one run after the bench, none in others
  (runs `155b`, `8177`, `979b`). Cause not found. A lead (*guess*): iOS's own background scans.
- **"Weak Security" label** on a WPA2 network. iOS reads security from the scan record's information elements; ours are incomplete.
- **Pings alone proved little.** For a while "Wi-Fi works" meant ten pings on the local network. The bar was raised to DNS and HTTPS to a public host.

## Untested or never attempted

- **WPA3, open networks, enterprise (802.1X) networks, hidden networks.** Only WPA2 personal was joined.
- **6 GHz.** With the default regulatory setting the chip reports 2.4 GHz channels 1 to 13 and 5 GHz channels 36 to 165, and no 6 GHz
  (*observed* 2026-11-14, read-only probe, patch 0363). No regulatory file is loaded.
- **Roaming between access points, hotspot mode, AirDrop and other peer-to-peer features.**
- **Power saving.** The chip stays in the same awake mode Android uses while active; device sleep was not tried.
- **Web page loads in Safari** were not logged, though Safari ran. Traffic is proven by the check tool and the throughput tool.

## Ideas if you want to pick it up

- Line up the per-second UDP loss with the scan requests in the same log. If they match, defer scans while receive is busy.
- Fill in the scan record's security elements to clear the "Weak Security" label.
- For another Broadcom FullMAC chip: start from OpenBSD's `bwfm` (ISC licence) and read Broadcom's GPL driver for facts only.
- Capture the stock OS once before designing. It told us who runs the handshake.

## Where to look

- Shim: `shim/wlanlink.c` (PCIe power-up table interpreter), `shim/wlanrails.c`, sequence data in [`wlan_seq.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/wlan_seq.json).
- Patches: 0124 (core, from `bwfm`), 0128 to 0137 (firmware load), 0167, 0174 (host setup), 0198 to 0201 (message rings, `en0`, Apple80211 glue), 0268, 0281, 0282, 0292, 0293, 0313 (keep-alive, rejoin, scan), 0347 to 0351 (interrupt), 0357 (receive pool).
- Notes: [Wi-Fi stack plan](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/20-wifi-stack-plan.md), [what iOS needs](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/26-wifi-iowifi-requirements.md), [firmware download protocol](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/37-bcm4389-fw-download-protocol.md), [the bwfm port](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/42-bwfm-xnu-port.md), [licensing](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/WIFI-LICENSING.md).
- Test tools: `tools/pixnet.c`, `tools/pixperf.c`, `tools/pixping.c` in pixelios-kernel; `wifid-probe/` in pixelios-userland.
- Interface facts for iOS 16.7: [Wi-Fi](../IOS-INTERFACES.md#wi-fi). Blueprint stage [9](../BLUEPRINT.md#9-wi-fi). Milestone: [Wi-Fi](../milestones/wifi.md).

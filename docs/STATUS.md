# Status

Target: Google Pixel 6a ("bluejay", Tensor G1 / gs101), unlocked bootloader. The shim and kernel are loaded with
temporary `fastboot boot` images; the only partition ever written is `userdata` (the iOS root).

Legend: **works** = observed on hardware (date and build given), **builds** = compiles and host-tests only,
**partial**, **todo**. Evidence tags: *observed on hardware*, *read from source*, *guess*. Last update: 2026-10-23
(private handoff through session 24). What is planned next: [ROADMAP.md](../ROADMAP.md).

## Where the project is (one paragraph)

*Observed on hardware, 2026-10-22:* XNU boots on the Pixel 6a with all 8 CPU cores, mounts the iOS 16.7 root read-write from
`userdata`, runs launchd and ~60 daemons and reaches the **iOS lock screen and home screen** (SpringBoard) with the panel
showing the real iOS UI. **Touch works** (STMicro FTM5 over SPI, powered through an ACPM call from the shim) and the iOS UI reacts to taps and swipes.
**Settings -> General -> About opens in about a second** (it used to hang for 5 minutes). The UI is still slow (software
rendering, no GPU). Wi-Fi, GPU, audio, camera and the modem are not working. Milestone 1 (iPhone GUI on the Pixel 6a) is reached;
milestone 2 is real Wi-Fi.

## Boot chain and storage

| Area | State | Evidence |
|---|---|---|
| Shim runs under `fastboot boot` (AVB-footed image) | works | `device/google/bluejay/docs/GATE0_RESULTS.md` |
| On-screen log, RAM log, pstore hand-back | works / pstore dropped (ABL rewrites it) | `device/google/bluejay/hardware/` |
| USB CDC-ACM log gadget (host sees `/dev/ttyACM0`) | works (shim, 2026-10-21) | `device/google/bluejay/hardware/probe-log-2026-10-21-run1.txt` |
| UFS cold re-init after ABL shutdown | works | `soc/google/gs101/docs/07-gs101-ufs-bringup.md`, `soc/google/gs101/docs/08-abl-ufs-shutdown.md` |
| UFS power-mode change to HS-G4 | works: 4 MiB read 8036 ms -> 675 ms, data identical | `docs/reviews/hs-g4-review-1.md` |
| Read-only `userdata` dump over USB (CRC-checked) | works | `device/google/bluejay/hardware/udump-1mib-2026-10-21.txt` |
| UFS DMA into the XNU memory bank | works | S2MPU does not block it |
| XNU UFS block driver, HFS+ root mount | works read-write (2026-10-21, xnu-0085, git 83d52de) | read-only boot fails at journal init (EROFS), `ufsrw=1 rootrw=1` mounts |
| gs101 UFS write path inside XNU (journal, file clones in `userdata`) | works (same run) | the shim itself has no write path; the root is flashed with `fastboot flash userdata` |
| Software reset back to the bootloader flow | partial: fired in earlier runs (2026-10-22, xnu-0089 and later), did NOT fire in the spi-clk2 run (xnu-b5623f6, 502 s wait; phone needed a Power+VolDown hold), cause unknown | `sweetrestart=<s>`; EL3 accepts the PMU SMC write from EL1 (research 10); the phone lands in recovery, `tools/to-fastboot.sh` returns it to fastboot |
| SMP via PSCI | works, `cpus=8` boots (2026-10-22) | run usbnet4-cpus8 |
| CPU clocks (ACPM DVFS, shim `--dvfs`) | works: cluster rates raised before the XNU jump (each cluster measured ~1.8 GHz), UI is faster but still laggy | runs dvfs1..dvfs4 |

## iOS userland and display

| Area | State | Evidence |
|---|---|---|
| launchd and ~60 daemons | works (2026-10-21, xnu-0085) | QR log, 60/60 frames |
| Apple boot logo on the panel | works (2026-10-21, xnu-0085, `--qr off`) | camera frame kept outside git |
| SpringBoard, iOS lock screen | works (2026-10-22, xnu-0087, CI 39690201014) | QR log: `SBCoverSheetPrimarySlidingViewController`, 115000 swaps |
| About page (Settings -> General -> About) | **works** (2026-10-22, run about4) | *read from source* cause: configd waited 300 s for an `IONetworkStack` service that does not exist in this kernel; patch 0099 adds a stand-in. Model name/serial text for the Pixel 6a is set in the device tree and the root (built, not yet seen on the phone) |
| Lock-screen wallpaper / clock | partial: clock drawn transparent (a root preference to make it plain is built, not yet seen); poster extensions die with `extension check-in timeout` (AegirPoster sig 6, 15-23x per run in xnu-0092 runs) | *guess*: no wallpaper behind the vibrant clock; fix not found |
| Screen goes black during a long run | open: ~100 s (cpus=2 run), ~580 s (xnu-0092 run, cpus=4) | cause not investigated |
| Software rendering only (no GPU) | partial | GPU is research, see below |

What fixed the Apple-logo stall (*observed* result, cause partly *read from source*): the root recipe taken from
ios-sailfish (let DataMigration run once, relax ExtensionKit signing checks, drop a few daemons) plus kernel
patches 0086 (no IOKit busy hold, empty IOAcceleratorES) and 0087 (container-path syscall for app extensions).

## Input and peripherals (Tensor G1 drivers written for this port)

| Area | State | Evidence |
|---|---|---|
| Buttons (keys driver, `bsd/dev/sweet_keys_gs101.c`) | partial: driver starts, reads the three GPIO banks, no hang | *observed* 2026-10-22, xnu-0092/b5623f6: `SWEET KEYS: start key=0 ... dat=0x2`. No key press tested yet |
| Touch (STMicro FTM5 over SPI11, `sweettouch=2`) | **works** (2026-10-22, runs touchx3/touchx5/demo1b, CI kernel with patches up to 0095) | *observed*: the chip answers (`36 48 03 00`), taps and swipes reach the HID stack (49 touch events in one run). The stall of earlier runs was the chip being **unpowered**: its two rails (LDO25M/LDO26M) are switched on by the shim through the ACPM mailbox (`--rails`); the SPI recipe (USI mux to the 24.576 MHz oscillator, divider, ABL-exact transfer, reset pulse) is in patch 0095 and the boot-arg `sweettouchpoke=` (research `15`, `19`, `21`, `23`) |
| Battery, display backlight tuning | todo | |

## Radios, USB and GPU

| Area | State | Evidence |
|---|---|---|
| Wi-Fi (Broadcom BCM4389 on PCIe) | **partial**: PCIe link up and the chip is readable, no driver yet | *observed on hardware, 2026-10-23, shim runs w3a-n23..n27*: rails, WLAN_EN, PHY and PERST sequenced from the shim (table-driven, audited, always restored), PCIe1 link trains to L0 (Gen1 x1), outbound iATU programmed, the endpoint answers config reads (vendor 0x14E4 Broadcom, device 0x4441, class network controller) and its full config space was dumped read-only (BAR0/BAR2 are 64-bit memory BARs, not yet assigned). Next: BAR sizing/assignment, first register read, firmware download. Every step is listed with its evidence in [WIFI-COVERAGE](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/WIFI-COVERAGE.md); code on `pixelios-kernel` main (`shim/wlanlink.c`, `soc/google/gs101/wlan_seq.json`), reviews in `docs/reviews/wlan-stage1-review-*.md` |
| USB under XNU (CDC-ECM network, UDP live log on 192.168.7.x port 5140) | **works** (2026-10-22) | *observed*: host pings the phone, >3000 log lines per run; this is the debug channel (`tools/xrun`, `tools/usbnet-log.py`), the QR log is only a fallback. Needs one `sudo` line on the host to give the interface an address |
| GPU (Mali-G78 MP20) | todo, research only | `research/17`, `research/18`; `--gpu-probe` shim option never run on hardware; biggest blocker *read from source*: power domain and clocks sit behind EL3/ACPM |
| Modem, camera, audio | todo | no drivers; the Camera app does not open and its lock-screen shortcut does nothing |

## Wi-Fi plan in brief (*read from source*, desk research 2026-10-22; the bring-up status is in the table above)

- The radio is a BCM4389 on `pcie_1`; mainline brcmfmac has no 4389 entry, Apple's own Wi-Fi kexts are not usable and
  our XNU cannot load kexts, so the driver has to be **built into the kernel** by numbered patch.
- iOS needs a `wlan` node in the device tree before `wifid` starts, and an IO80211-style controller answering the
  `apple80211` requests; the reference port ios-topaz shows this is solvable on another SoC.
- Three blockers: EL3/ACPM gating of PCIe PHY isolation and the radio rails; PHY/PCS init tables that exist only in
  Google's GPL kernel code (licence decision open); firmware that lives on the `vendor` partition and may never enter git.
- *guess* (from the plan, not measured): 25-40 agent-days.

## Developer tooling (all *observed working*, 2026-10-22)

- `tools/xrun`: one hardware cycle (build image, boot, read camera/QR, wait for the self-reset) producing one report with `RESULT: PASS|FAIL|PARTIAL|ERROR`.
- `tools/ci-kernel`: finds, waits for and verifies the kernel built by CI; `tools/stack-apply`: checks the numbered patch stack on pristine xnu-8796.
  See [Automation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md).
- Rootless iOS-root build (no sudo, qemu guest): 21 min 33 s, later 11 min 26 s after a parallel-extraction change; `check-ios-root.py` 12/12 and the
  file listing, 122 hard-link counts, key hashes and sha256 of all 181,819 regular files identical to the sudo-built image (host comparison;
  the rootless image itself has not been flashed). See [Rootless build](https://github.com/PixOS-Project/pixelios-userland/blob/main/docs/ROOTLESS_BUILD.md).

## Open items

Slow UI (software rendering; a vsync-period fix is built, patch 0101, not yet measured), poster-extension crashes and the transparent
clock, black screen after minutes, power-on boot without a PC (planned: iOS image in `boot_a`), then Wi-Fi and a GPU path. See [ROADMAP.md](../ROADMAP.md) and [Plan](PLAN.md).

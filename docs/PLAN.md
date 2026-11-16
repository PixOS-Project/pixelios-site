# Plan

Each phase ended with a hardware gate. All work follows [SAFETY.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md): every step must be reversible with the stock factory image, and the only partition ever written is `userdata`. No phase starts until the previous gate passes.
Steps marked **[user]** are run by the maintainer (destructive, or needs the phone in hand). Status tags: *observed on hardware*, *read from source*, *guess*.
Local toolchain setup: [BUILD.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/BUILD.md). What works today: [Status](STATUS.md).

**Last verified: 2026-11-16.** This is the original phase plan (2026-10-20) with each phase's outcome. For a device-agnostic version
of these stages, see the [Porting blueprint](BLUEPRINT.md); for the live numbers and the story of each phase, [Milestones](MILESTONES.md).

| Phase | Gate | State (2026-11-15) |
|---|---|---|
| 0 Probe shim, no XNU | shim runs and reports the hardware | **passed**, *observed* 2026-10-21 |
| 1 XNU to the framebuffer console | XNU reaches "waiting for root device" | **passed**, *observed* 2026-10-21 |
| 2 Root from UFS | launchd runs from the `userdata` root | **passed**, *observed* 2026-10-21 |
| 3 SpringBoard | lock screen on the Pixel | **passed**, *observed* 2026-10-22 |
| 4 Input and USB | unlock, navigate, network over USB | touch and USB network **passed** (2026-10-22); buttons partial (presses reach the kernel, 2026-11-11; iOS reaction not checked) |
| 5 Wi-Fi | Settings shows Wi-Fi and the phone gets a connection | **passed**, *observed* 2026-11-08/09: joined from Settings with a DHCP lease, runs `wlan-wui-f2`, `wlan-wui-g`; throughput and reconnect since |
| 6 Graphics | UI composited by the GPU | **passed**, *observed* 2026-11-09: the GPU draws the UI, slowest navigation step 56.6 frames/s, runs `gputest-nav43`, `gputest-nav44`; 50.6 rendered at the lowest GPU clock on 2026-11-15, runs `155b`, `8177`; 60 on every step is open |
| 7 Bluetooth (added later) | iOS Bluetooth works on the stock daemon | **passed**, *observed* 2026-11-10/11: scan, connect, advertise, pair, runs `bt-pr3`, `bt-pr4`, `bt-hotpair` |
| 8 Audio, power (added later) | sound out, battery charges | charging one run (`chg-p3`, 2026-11-10); audio open |

## Phase 0: probe shim (no XNU)

- Board table (`soc/<vendor>/<soc>/soc.json`, `device/<vendor>/<codename>/board.json`); `tools/mkadt.py`, `tools/mkpayload.py` and `shim/build.sh` take `--board`.
- Shim for bluejay: boot.img v4 with the payload as ramdisk and an AVB footer, EL2 entry dropped to EL1, watchdogs disabled, framebuffer from the live FDT with the DECON trigger re-armed, probe report on screen, RAM log and a USB gadget, reset through PSCI. Power+VolDown always gets back to fastboot.
- **[user] Gate 0**: unlock the bootloader (wipes data), back up the per-device partitions, `fastboot boot` the shim, read the report. Passed.

## Phase 1: XNU to the framebuffer console

- The upstream patch series plus ours: board read from the ADT, Qualcomm drivers gated off on other boards, gs101 CPU-on pre-steps, PSCI reset. `mkadt.py --board bluejay`, boot with `cpus=1`.
- The kernel is built by CI (`xnu.yml`, macOS runner) or locally (`tools/xnu-local-build`).
- **Gate 1**: XNU reaches "waiting for root device".

## Phase 2: root from UFS

- Before the first write to `userdata`: back up the per-device partitions that can be read (`persist`, `efs` and friends are restricted in fastboot; see [PORTING](PORTING.md)).
- Exynos UFS driver for XNU (PRDT byte granularity, S2MPU-safe DMA buffers), then the iOS 16.7 root built rootless from the IPSW (`pixelios-userland`).
- **[user] Gate 2**: flash the root to `userdata` (destroys Android data), boot to launchd.

## Phase 3: SpringBoard

- The rest of the patch stack, SMP with 8 cores, then the daemon and ExtensionKit workarounds that got past the Apple-logo stall (see [Status](STATUS.md)).
- **Gate 3**: lock screen on the Pixel.

## Phase 4: input and USB

- Touch: STMicro FTM5 over SPI with the rails switched on through ACPM. Buttons: GPIO poll into the HID key hooks. USB: DWC3 gadget with CDC-ECM and a UDP log.
- **Gate 4**: unlock, navigate, network over USB.

## Phase 5: Wi-Fi

- **Decision (maintainer, 2026-10-21): the real radio, no USB-Ethernet substitute.** USB Ethernet stays a debug channel.
- Chip: BCM4389 on PCIe `pcie_1`. Steps as planned and done (*observed*): (1) PCIe root complex and PHY bring-up from the shim (chip id read through BAR0, 2026-10-24), (2) firmware and NVRAM download, (3) a PCIe and Broadcom msgbuf driver built into the kernel (chip definitions modelled on OpenBSD's bwfm; the WPA2 4-way handshake runs in our host driver), (4) an Apple80211-facing `en0` layer that `wifid` and Settings accept, (5) firmware and NVRAM from the user's own phone image, never in git.
- **Gate 5**: iOS Settings shows Wi-Fi and the phone gets a connection. Per-step evidence: [Milestones](MILESTONES.md).

## Phase 6: graphics

- Baseline: CPU-rendered framebuffer through stand-ins for IOMobileFramebuffer and IOSurface.
- Apple's GPU userland targets AGX and the Pixel 6a has an Arm Mali-G78, so Metal is out of reach. What we built instead (*observed*): a Mali kernel driver in XNU (power, MMU, job submission, interrupts) with an IOKit user client, Mesa's Panfrost driver built for iOS, and an EAGL layer so CoreAnimation takes its GLES path. The kernel-side plan is `docs/research/17-gpu-kernel-gs101.md` in pixelios-kernel.

## Track B (not started): newer iOS

PAC (arm64e) is required by iOS 17 and later and the Tensor G1 cores are v8.2, so (*guess*, unverified) only iPadOS on a non-PAC iPad is realistic; see the [case study](CASE_STUDY.md). This stays research.

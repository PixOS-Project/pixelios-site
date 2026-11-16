# Porting blueprint: XNU + iOS on hardware that never ran it

**Last verified: 2026-11-16.** The stages that worked for PixOS, written so they apply to any device and any iOS build.
For each stage: what you must find out about **your** device, the tools, the **oracle** that proves the stage works, our Pixel 6a
example (with run labels; *observed on hardware* unless tagged otherwise) and the pitfalls we hit.

Everything observed here was seen on **one** phone: a Pixel 6a ("bluejay", Tensor G1 / gs101). For your device every line is a
question to answer, not a fact. The working rules behind it are on [Method](METHOD.md); what went wrong on the way is on [Lessons](LESSONS.md);
copy-paste prompts for an LLM agent are on [LLM prompts](PROMPTS.md).

!!! tip "Stage or component?"
    This page is the **recipe**, stage by stage, for any device. For what each block actually took on the Pixel 6a (what worked,
    what did not, what nobody tried, patch numbers) read its page under [Components](components/index.md).

## The shape of a port

```text
stock bootloader --RAM boot--> shim (your bare-metal code: brings up what XNU needs, builds its device tree)
  --> patched XNU (numbered patches on Apple's open-source XNU of the same generation as the userland)
    --> your storage driver --> iOS root (HFS+) in the data partition --> launchd --> SpringBoard
```

PixOS started from [ios-sweet](https://github.com/dipa-studio/ios-sweet) (MIT), which did this for a Redmi Note 10 Pro (Qualcomm), and inherits
its first patches. The userland is an iPhone X iOS 16.7 IPSW you download yourself; XNU is `xnu-8796` (the iOS 16 generation).

**Pick the userland first.** iPhone iOS 17 and later require arm64e (pointer authentication). Cores older than Armv8.3 (the Tensor G1's are
Armv8.2) cannot run it unmodified, so iOS 16 on an iPhone X-class (A11, non-PAC) userland is the newest iPhone userland that fits
(*read from source*: `docs/research/04-newer-ios.md` in pixelios-kernel). An iPadOS 17/18 userland for a non-PAC iPad might work (*guess*, not tried).

## Before stage 1: safety and recovery

- Know how to restore the stock OS (factory image) and how to reach the bootloader when the software hangs (a key combination). If you cannot name both, stop.
- List what can brick the device: bootloader chain, modem, per-device calibration (persist, efs), verified-boot metadata, the partition table, anti-rollback. Never write any of them. Everything up to the final data-partition flash is a RAM boot.
- Back up what can be read of the per-device partitions before the first experiment.
- PixOS rules: [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md) in pixelios-kernel; the build-time audit `tools/test-bluejay-boot.py` rejects any storage write path in pre-kernel code.

---

## 1. Boot shim and bootloader hand-off

**Find out:** can the bootloader be unlocked; does it support a RAM boot (`fastboot boot`, or your bootloader's load-to-RAM command); which image
container and signature it accepts while unlocked; the state it leaves: exception level, MMU and caches, what `x0` points to, which watchdogs
are armed, which peripherals (storage host, USB, display) stay initialised. Sources: the Android boot-image and fastboot documentation, the
Linux arm64 boot protocol, your SoC's mainline or vendor kernel, earlier community ports for the same phone.

**Tools:** AOSP `mkbootimg.py` and `avbtool.py` (PixOS fetches them with `tools/fetch-android-tools.sh`), the shim build (`shim/build.sh`,
entry point `tools/pix build`), a boot wrapper that refuses the wrong device (`tools/fboot.sh`).

**Oracle:** a log line from your code on a channel you can read (screen text, a USB serial gadget), and a **probe report**: exception level,
MIDR/MPIDR of every core, translation granule support, timer frequency, interrupt controller and PSCI versions, the live device tree's memory map, watchdog state.

**Our example:** an unsigned boot image was accepted by `fastboot boot` and then silently not run; the same image with an AVB hash footer
(throwaway test key) ran (2026-10-20, `device/google/bluejay/docs/GATE0_RESULTS.md`). The shim is entered at EL2 with the MMU off; cores
4x A55, 2x A76, 2x X1; 16 KiB granule on all cores; no PAC; timer 24.576 MHz; PSCI 1.1 with plain `CPU_ON`; both watchdogs armed by the
bootloader; the display trigger left disabled (probe report, 2026-10-21).

**Pitfalls:** "unlocked" does not mean "any image boots": test RAM boot separately and look for the footer rules. Do not take the memory
map from the marketing size or the reference port: the 6 GB Pixel exposes three 2 GiB banks with the low one cut by firmware carve-outs.
Armed watchdogs reset a hung experiment; a bootloader can rewrite the RAM you hoped to read back after a reset (pstore did not survive here).

## 2. Device tree for XNU (Apple ADT)

XNU for iPhones reads an **Apple Device Tree** (normally built by iBoot), not a Linux/Android DT. Do not translate the Android tree node by node:
**synthesise a minimal ADT** from a small board-data file plus facts measured in the probe, then add only what iOS code actually asks for.

**Find out:** a hole-free, aligned RAM range for XNU; interrupt controller bases and the virtual-timer interrupt; MPIDR and type of every core;
timer frequency; framebuffer base, size and stride; the MMIO bases you will drive. Sources: the SoC's mainline/vendor DTS, the probe report,
the vendor pinctrl tables. Record each value with its source.

**Tools:** `tools/mkadt.py` (builds the ADT from `soc/<vendor>/<soc>/soc.json` + `device/<vendor>/<codename>/board.json`), `tools/pix check`
(required keys, alignment), `mkadt.py --dump`. The userland device's own ADT (for `/product` identity) comes from **your** IPSW; it is never shipped.

**Oracle:** early XNU consumes it (framebuffer, CPU, timer, storage lines; no panic in platform init); later oracles are behavioural: a daemon
that waited for a key stops waiting.

**Our example** (*read from source*, `tools/mkadt.py`): `/chosen` carries the hole-free upper DRAM range; eight CPU nodes with their real MPIDR;
GIC bases from `soc.json`; identity borrowed from the iPhone X ADT extracted from the user's IPSW; locally-administered placeholder MAC addresses
(logged as GAP lines until the radio's own address is read); a display node presenting the iPhone X canvas (1125x2436) while the panel is 1080x2400.

**Pitfalls:** many daemons need a node or a key to start at all (a `wlan` node is what makes the Wi-Fi daemon start; a watchdog node with the
right property keeps the watchdog daemon alive). A node copied from a real iPhone to stop a crash can lie about hardware: our audio node is
empty plus GAP lines, not a copy. The boot-argument line has a size limit: when you exceed it, arguments are cut silently (see [Lessons](LESSONS.md)).

## 3. XNU bring-up

**Find out:** what XNU needs that only Apple SoCs provide (interrupt controller, power manager, timers, platform expert, CPU start-up) and the
replacement for each; GIC version and wiring; PSCI `CPU_ON` per MPIDR; per-cluster clocks (on gs101 through the ACPM firmware mailbox); RAM aligned
to the kernel's block size (32 MiB with a 16 KiB granule). Sources: the XNU source of your userland's generation, the Arm ARM and GIC spec, the
Linux clock and DT sources.

**Tools:** numbered patches in `xnu/patches/` (never edit the fetched tree), `tools/stack-apply` (does the stack apply on a pristine tree),
`tools/xnu-local-build` (no Mac needed) or the CI workflow, `tools/mkpayload.py` (kernel + ADT + boot arguments into one payload),
`tools/build-xnu-image.sh` (payload + shim into one RAM-bootable image).

**Oracle:** kernel text on the panel, the BSD layer up, "waiting for root device" (the expected stop without storage); then `cpus=8` boots.

**Our example:** XNU with the inherited patch stack drew kernel text on the panel and stopped at the root wait (2026-10-21); all 8 cores through
PSCI (2026-10-22, run `usbnet4-cpus8`); cluster clocks raised before the jump (runs `dvfs1` to `dvfs4`).

**Pitfalls:** the reference port hard-coded its SoC everywhere (framebuffer, storage host, PSCI quirks, memory protection); each had a different
answer on the new SoC. Keep SoC facts in a data file selected by SoC, never by phone name. A debug boot argument that makes a panic wait for a
debugger turns every panic into a hang. Build the log channel (stage 13) before stage 5.

## 4. Storage and root mount from the data partition

**Find out:** the storage type and host controller; which LUN and partition is the data partition and its LBA range; **the state the bootloader
leaves it in**; host quirks (PHY tables, power-mode tables) from the Linux host and PHY drivers; which RAM the controller can reach by DMA.

**Tools:** the shim's read-only storage init and a CRC-checked read-only dump of the data partition over USB (compare it with Android's view);
the safety audit (no write commands in the shim); the root builder in pixelios-userland (`tools/build-ios-root-rootless.sh`, no sudo) and its
checker (`tools/check-ios-root.py`); a flash wrapper that refuses everything but the data partition (`tools/fflash-userdata.sh`).

**Oracle:** the dump matches Android's read byte for byte; XNU mounts the HFS+ root read-write; launchd starts.

**Our example:** after the bootloader, the UFS host was up but the device was powered down and the link in hibernate, so every command timed
out until the shim did a device reset and a full link start-up (found by reading what the bootloader does at shutdown). The HS-G4 power mode took
a 4 MiB read from 8036 ms to 675 ms, data identical (2026-10-21, `docs/reviews/hs-g4-review-1.md`). XNU mounts the root read-write; a read-only
mount fails at journal start (2026-10-21).

**Pitfalls:** our first diagnosis (an IOMMU blocking DMA) was a guess and wrong; the cause was the state the previous stage left the device in.
A journaled root needs a writable mount. Re-flashing the data partition is the slow loop: copy changed files into the mounted root from a
RAM-disk overlay at boot instead, and flash only when the root image itself changes.

## 5. launchd and the daemons, up to SpringBoard

**Find out:** for each daemon that exits or waits, the failing call and what is missing: a kernel service, an ADT key, a file, an entitlement,
a mach service. Decide each time whether the fix belongs in the kernel (a stand-in service), the ADT or the root (a tweak). The binaries to read
are your own IPSW's daemons and frameworks, decompiled on your host; keep only your conclusions.

**Tools:** the root recipe in pixelios-userland (scripts only, no Apple files): drop jobs that loop without hardware (for example baseband-only
daemons), relax a few checks, stage apps, skip the setup assistant; kernel stand-ins as numbered patches (code signing policy, key store,
sandbox paths, a network-stack stand-in, HID event services); a crash summary per process from the run log.

**Oracle:** launchd and its daemons alive, the Apple logo, then the lock screen and the home screen, then Settings pages that open; later an
automated oracle: panel snapshots compared with reference captures (19 of 19 matched, run `gputest-surffail-b`, 2026-11-11).

**Our example:** launchd and about 60 daemons, then lock and home screen (2026-10-21/22). Settings > About hung because a configuration daemon
waited 300 s for a network-stack service this kernel did not have; a stand-in service fixed it (run `about4`, 2026-10-22).

**Pitfalls:** a daemon marked panic-on-crash reboots the phone on its first crash. Every dropped job and every stand-in is a missing feature:
log it as a GAP so it is not forgotten. A stub that makes a daemon stop crashing can hide a missing driver that costs you a feature later.

## 6. Display

**Find out:** the bootloader's framebuffer (base, size, stride, format), whether scan-out stays live after the hand-off and what must be
re-armed; panel size and refresh; what the iOS framebuffer and surface frameworks expect from the kernel (their external methods, the
notifications the compositor waits for, the vsync period). Reverse those on your build.

**Tools:** a framebuffer console in the shim and in XNU; a kernel framebuffer and surface emulation (PixOS: `SweetFramebuffer` with its user
client, in `xnu/patches/`); host tools that split a run log into frames per second; an **independent witness** of the panel (a camera, or a
kernel read-back of the panel memory), never only the kernel's own claim.

**Oracle:** kernel text, the Apple logo, the iOS UI, all confirmed by the witness; then a frame-rate number.

**Our example:** framebuffer at the bootloader's address, 1080x2400, stride 4320 (2026-10-21, `device/google/bluejay/board.json`); the panel is
command-mode and the bootloader disables its hardware trigger, so the shim re-arms it. There is no scan-out driver: iOS draws into buffers that
XNU copies to the bootloader's framebuffer.

**Pitfalls:** compositor pacing depends on the framebuffer notifications and a real vsync period; missing or silently "successful" answers
pace frames at 2 to 6 vsyncs. A camera under room light misjudges frames; expose for the panel.

## 7. GPU

**Find out:** GPU IP and revision (read its ID register once reachable), power domain and **who powers it** (on gs101 the shader rail is a
firmware request, not a register write), clocks, interrupt lines, the IOMMU between GPU and RAM; a kernel driver to port from (for Mali: the
vendor kbase driver); a GL implementation that can reach the hardware (Mesa); and on the iOS side, how the compositor picks its renderer and
which GL entry points it calls. On iOS 16 CoreAnimation tries Metal, then OpenGL ES 3, then the CPU (*read from source*, our own decompile).

**Tools:** read-only GPU probes in the shim; a GPU driver in XNU (power, MMU, job submission, reset, interrupts) with an IOKit user client;
Mesa's Panfrost driver built for iOS (patch series in pixelios-userland `tools/mesa-patches/`) behind an EAGL layer so CoreAnimation takes its
GLES path; a **host replay** of captured GPU frames on a software renderer, compared pixel by pixel with the phone's output; a frame-time
benchmark of a scripted navigation session.

**Oracle:** the GPU ID read back and a job that writes a known value through the GPU MMU; then frames that match the host replay; then the
benchmark's slowest step and pooled frames per second; defect counters (incomplete framebuffers, refused surface attaches) at zero.

**Our example:** the bootloader left the GPU powered and clocked (our design note had guessed "off"; one read-only probe settled it), ID
`0x92020010` = Mali-G78 MP20 (run `g0`, 2026-10-23). The UI went from 38 frames/s on an early swipe bench (run `gputest-cced-poll20`, 2026-11-04)
to a slowest navigation step of 56.6 frames/s (run `gputest-nav43`, 2026-11-09) once job completion moved from polling to interrupts; pooled
59.5 today (run `gputest-surffail-b`). The black App Library backdrop was a 64-entry table in our own GL layer that never recycled its records
(fixed 2026-11-11, runs `gputest-surffail-a` before, `gputest-surffail-b` after).

**Pitfalls:** a flush wired to a blocking finish serialised every frame and made "GPU no faster than CPU" a pacing result, not a compute one.
GPU caching without the matching cache maintenance corrupted output without any fault. Tracing at high volume slowed the very thing it traced.
Most of our GPU boots were spent testing guesses about Apple's compositor while the bug was in our own code (see [Lessons](LESSONS.md)).

## 8. Touch and buttons

**Find out:** controller model, bus, pins, interrupt, reset line, **power rails and who switches them**, the ID command, the serial-engine
mode and clocks of the bus; button GPIOs; how iOS's HID stack expects digitizer events. Sources: the vendor touch driver, the board's touch DT include.

**Tools:** shim touch probes with host tests; rails through the firmware mailbox; XNU touch and keys drivers; scripted swipe injection for benchmarks.

**Oracle:** the chip answers its ID, events reach the HID stack, and a real finger moves SpringBoard.

**Our example:** STMicro FTM5 on SPI, ID `36 48` (2026-10-22); the first stall was an **unpowered chip**: its two regulator rails were off after
the bootloader, and the shim now switches them on before XNU (runs `touchx3`, `touchx5`, 2026-10-22). With the GPU path up: 85 touch-controller
events in run `demo-gpu-touch-wifi` (2026-11-04). Buttons: the driver reads the GPIO banks; power and volume-up presses were logged in runs `resident-164801-b1` and `resident-204614-b1` (2026-11-11/12), the iOS reaction was not checked.

**Pitfalls:** six patches went into SPI clocks, muxes and transfer recipes before anyone checked power. An unpowered chip reads as all-ones or
all-zeros depending on the pull. **Check power before bus timing.**

## 9. Wi-Fi

**Find out:** the chip and its bus (here a Broadcom BCM4389 on PCIe): the root complex power sequence (rails, enable GPIO, PHY, clocks, reset
timing, link training) from the vendor kernel and DT; the firmware, NVRAM and regulatory blobs (they live on the phone's own vendor partition and
**never** go in git; extract them from the user's own phone); the dongle protocol (core enumeration, firmware download, rings, ioctls, events);
who runs the WPA2 handshake under the stock OS (capture it once); and on the iOS side what the Wi-Fi daemon and Settings need: the interface,
the request types and their structures, the scan-record layout, link-state keys.

**Tools:** a table-driven PCIe bring-up with its own write allowlist and an always-run teardown; a driver modelled on OpenBSD's `bwfm` (ISC);
Broadcom's GPL driver read for facts only; an Apple80211-facing `en0`; iOS-side ping and throughput jobs and a host throughput server;
independent witnesses (camera frames of Settings, the access point's own client counters).

**Oracle:** a ladder of log lines: endpoint config read, chip ID, firmware alive, first ioctl answered, scan records, association, keys
installed, ping from the kernel, ping from iOS over `en0`, a DHCP lease, Settings shows the joined network, throughput from a host server.

**Our example:** chip ID read through the BAR0 window (2026-10-24); WPA2 handshake done (run `wlan-runG2-join25g`, 2026-11-08); ping from iOS
10 of 10 (run `wlan-iosping-c`); joined in Settings with a DHCP lease (runs `wlan-wui-f2`, `wlan-wui-g`); about 110 Mbit/s down and 68 up (runs
`wlan-perf-f2`, `wlan-perf-f3`, 2026-11-09); 3 cold boots and 4 of 4 reconnects after the access point banned the phone (2026-11-10/11).

**Pitfalls:** the first plan assumed the firmware runs the handshake; the stock capture showed the host does. Each crash on the way was one
small thing (a variable-length event struct, rx buffers posted once and exhausted, a transmit-index check). Settings shows nothing until the
link-state keys and the interface media answer are right. iOS derives a network's security from the scan record's information elements, so
an incomplete record shows "Weak Security" on a WPA2 network (open today). Pin test traffic to the Wi-Fi interface, or a USB network can fake a pass.

## 10. Bluetooth

**Find out:** the controller and its transport (here HCI over a UART: pins, serial engine, clock, baud, flow control, enable and wake GPIOs),
the patch firmware it needs (from the user's own phone, never in git), a stock HCI capture; and on the iOS side how the Bluetooth daemon reaches
the controller and picks a chip profile. On iOS 16.7 it chooses the profile from the ADT product identity, not from the chip, and it has no
profile for the BCM4389 (*read from source*, our decompile).

**Tools:** a kernel UART transport and a channel of the kind the daemon expects; a vendor-command adapter in the kernel driver that maps the
commands the selected profile sends onto standard HCI the chip supports, with real per-instance state, and answers an error plus a GAP for
anything it cannot map; an open-source replacement for the chip-boot helper; a PC with BlueZ as a controllable pairing peer.

**Oracle:** HCI Reset answered; firmware loaded; the stock daemon alive with 0 exits; scan, LE connect, advertising accepted by the chip;
pairing completes on both sides; the bond survives a reboot.

**Our example:** the first HCI Reset answer came once the UART pads were switched from GPIO to the UART function (run `bt-s4h`, 2026-11-03).
On the stock daemon, with no binary patch: stack powered in 53 to 75 ms, CoreBluetooth discovered 52 and 64 devices, LE connect, advertising
(runs `bt-pr2`, `bt-pr3`, `bt-pr4`, 2026-11-10); pairing with a PC and a bond that survives a reboot (runs `bt-hotpair`, `bt-a2dp`, 2026-11-11).

**Pitfalls:** byte-patching Apple's daemon got early results and was replaced: implement the contract in your driver instead and never ship a
patched Apple binary. A kernel built without the firmware patch stack falls back to the ROM firmware and gives wrong conclusions. Pairing as
initiator with a phone peer failed; a controllable PC peer got the first bond.

## 11. Audio (not solved)

**Find out:** the speaker path (codec, amplifier, DSP, buses, power) from the Linux/Android sources; what iOS needs to publish a built-in output;
what its audio server needs to stop crashing without one. **Our state:** no speaker or codec driver. The iOS audio stack runs and plays a test
tone to a virtual device (run `bt-va1`, 2026-11-11); a headset pairs and iOS opens an A2DP stream but never starts it (run `bt-va3`). Treat this
stage as a map of questions, not a recipe. Pitfall: an audio node copied from an iPhone to stop a crash claims hardware that is not there;
publish an empty node and log the gap.

## 12. Charging and power

**Find out:** the charger, fuel-gauge and USB-PD chips and their bus, what the bootloader leaves configured, what the stock OS writes to charge,
the load of a running iOS (GPU boots draw more), which settings are volatile.

**Tools:** read-only probes of the bus first, then reads of the chips, then one reviewed write; fuel-gauge lines in the log as the witness.

**Oracle:** the battery current changes sign under the same load; the written register reads back; no bus errors.

**Our example:** the bootloader leaves the charger bus set up; PixOS charged at the 500 mA limit a plain USB host port gets, below the iOS load
(-98 mA, run `chg-p2`); raising the input limit to 875 mA on USB 3, together with the USB descriptor, gave +107 to +205 mA (run `chg-p3`,
2026-11-10, one run). The bootloader resets the limit every boot.

**Pitfalls:** the review of that write found the USB descriptor still declared about 500 mA: the descriptor and the limit must change together.
Not measured yet under GPU load.

## 13. Debug channel

**Find out:** a channel for every phase: before the kernel (screen text, a USB serial gadget from the shim), under XNU (a USB Ethernet gadget
with the kernel log over UDP), and a last resort that needs no host driver (QR codes on the screen read by a camera). A hardware UART may exist
on the USB-C sideband pins (1.8 V, needs a cable). Find what the bootloader leaves of the USB controller and where DMA memory may live.

**Tools:** `tools/usbnet-log.py` (UDP receiver, no root), `tools/qr-log.py`, one-cycle run tool that ends in a `RESULT:` line (`tools/xrun`,
Pixel-bound), a panic sender that works without the scheduler.

**Oracle:** log lines from the first instruction to the last, including a panic message with a backtrace that arrives before the reset.

**Our example:** USB serial from the shim (2026-10-21); the UDP log from running iOS on every run since 2026-10-22, over USB 3 since 2026-10-29;
the USB driver takes its DMA page from the bootloader's reserved region and refuses to run if it is not where measured.

**Pitfalls:** a log sender that runs as a normal thread cannot speak at panic time; add a polled panic path. The Pixel showed only USB 2
until the SuperSpeed PHY path was written.

## 14. Recovery and safety, automated

**Find out:** the reboot-mode register and its values (on gs101 they are in the public Linux DT bindings), the reset trigger, what the bootloader
does with them on the next boot, which watchdogs exist and how to pet them.

**Tools:** a software reset to the bootloader; a kernel watchdog and a stall detector that panic a hung kernel; a run tool that parks the phone
in the bootloader after every run; a guard that refuses device commands while the wrong device is attached or any write except the data partition.

**Oracle:** a deliberate panic and a deliberate hang both return the phone to the bootloader with no hand on it, with the cause already on the host.

**Our example:** panic to fastboot (run `20261107T145123Z-panic-self-recover`, one run); watchdog on a deliberate hang (run `ar-c-wdttest`,
2026-11-09). Panic and watchdog resets first landed in recovery rather than fastboot, because the bootloader decides by the reset cause; the run
tool takes the phone from recovery back to fastboot.

**Pitfalls:** a reset path that works from a normal context can fail from a panic. A bug in a shim that disabled the watchdogs hangs the phone
until a long key press: keep every wait bounded.

---

## A different iOS build

Everything iOS-facing above was derived from **one** build (iOS 16.7 from the iPhone X IPSW) with XNU of the same generation. When you use a
different build:

**Re-derive per build, from your own decompile:** every selector number, struct size, record layout, trap number, notification payload and
property key of an Apple framework or daemon you emulate (surface and framebuffer frameworks, the GL entry points the compositor calls, the
Wi-Fi request types, the Bluetooth chip-profile choice and vendor commands, the audio routing chain); the root recipe (which jobs to drop, which
plists to patch, the cryptex layout); the kernel stand-ins the new userland asks for. None of these are stable across builds. Never copy offsets
or numbers from another build or another project.

**How we derived them for 16.7:** extract the binaries from your own IPSW (the dyld shared cache lives in the SystemOS cryptex on iOS 16),
disassemble or decompile on your host, write down conclusions (what a call does, what it expects, what a zero reply does), never the bytes.
Then confirm the conclusion on the device: run the userland, see which daemon waits or exits, check the log against the prediction.

**Keep a private fact map.** We keep every reverse-engineered fact in one private, queryable store, never in a public repository: one entry
per fact with a stable id, the binary and build it came from (with the image's hash), where in our notes it is used, and how it was found.
Query the store before decompiling anything (most questions were answered before); add every confirmed fact the same day; mark a fact
**superseded** instead of deleting it when a later reading corrects it (two of our IOSurface facts were wrong and were superseded on
2026-11-11); research notes cite fact ids, and a check refuses a note that cites an address without one. A periodic check reports facts whose
image changed. The store is what makes a new build a diff ("which facts must be re-checked") instead of a restart.

**Our facts for 16.7:** the interface-level facts we derived for iOS 16.7 (selectors, traps, struct layouts, protocol behaviour, in our own words,
no addresses) are on [iOS 16.7 interface notes](IOS-INTERFACES.md). Use them as a map of what to look for on your build, not as values to copy.

**What generalizes:** the method (oracle, spec, conformance matrix with a GAP line per missing row, then runs), the tool shapes (ADT synthesis
from board data, a payload packer, a patch stack checked against a pristine XNU of the matching version, a RAM-disk overlay for the dev loop,
RAM boots only), and the architecture limit: no arm64e userland on non-PAC cores.

## Sources

Public, in [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel): `device/google/bluejay/docs/GATE0_RESULTS.md`, `device/google/bluejay/board.json`,
`soc/google/gs101/soc.json`, `soc/google/gs101/docs/`, `tools/mkadt.py`, `tools/mkpayload.py`, `xnu/patches/` (file names), and in `docs/research/`:
`01-boot-path`, `04-newer-ios`, `15-touch-gs101`, `21-touch-spi-stall-investigation`, `27-gpu-g0-result`, `31-kbase-port-checklist`, `32-mesa-panfrost-ios-plan`,
`34-bcm4389-firmware`, `37-bcm4389-fw-download-protocol`, `42-bwfm-xnu-port`; `docs/reviews/hs-g4-review-1.md`, `docs/WIFI-LICENSING.md`, `docs/SAFETY.md`; in
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland): `tools/sweet-root-tweaks.py`, `tools/mkiosroot.sh`, `tools/mesa-patches/`.
Run labels and dates come from the maintainers' sprint logs (private); the same numbers are on [Status](STATUS.md).

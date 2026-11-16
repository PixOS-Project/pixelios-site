# Adding a device

**Last verified: 2026-11-16.** This page is for another phone with a Tensor SoC. For any other device or another iOS build, start with the [Porting blueprint](BLUEPRINT.md).
Driving the port with an LLM agent? Paste one of the [LLM prompts](PROMPTS.md). What each hardware block needed on the Pixel 6a: [Components](components/index.md).

Everything a phone needs lives in two small trees, so a new Pixel is mostly data:

- `soc/<vendor>/<soc>/`: shared by every phone with that chip.
- `device/<vendor>/<codename>/`: only what differs per phone.

**Only the Pixel 6a (bluejay, Tensor G1 / gs101) has been verified on hardware.** Everything below
about other phones is what you should expect, not what we have seen. Capture logs and send them.

## Which phones are close?

| Phone | Codename | SoC | What to expect |
|---|---|---|---|
| Pixel 6a | bluejay | gs101 (Tensor G1) | **verified** |
| Pixel 6 / 6 Pro | oriole / raven | gs101 | same SoC trees; we expect DRAM size, framebuffer, display, touch and radio modules to differ (*guess*: not checked on these phones). Best first target. |
| Pixel 7 family | panther / cheetah / lynx | gs201 (Tensor G2) | new SoC tree: UFS/PHY tables, USB, memory map need re-deriving from that SoC's vendor kernel |
| Pixel 8 / 9 families | shiba, husky / tokay, ... | zuma / zumapro | as above, plus newer bootloader behaviour |

## Same SoC (e.g. oriole on gs101)

1. **Get safe.** Unlock the bootloader (wipes the phone), back up the per-device partitions
   (`BOARD=oriole tools/backup-partitions.sh`, needs root over adb), and read [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md).
   The helper scripts (`run-probe.sh`, `backup-partitions.sh`) check the connected phone's codename against `BOARD`
   before they do anything; always run `fastboot getvar product` yourself before manual commands.
2. **Scaffold.** `tools/pix new-device google/oriole --soc google/gs101 --name "Pixel 6"` creates
   `device/google/oriole/` with placeholders. The SoC values are inherited.
3. **Measure what differs.** Build a probe image (`tools/pix build oriole --avb --usb-gadget --qrlog`),
   `fastboot boot` it and read the report over USB or the QR log. You need:
   - DRAM banks and the carve-outs inside them (the FDT memory map in the report),
   - framebuffer base, size and stride (set up by the bootloader; see the bluejay captures for how it was found),
   - anything the probe prints that differs from `soc.json`.
4. **Fill `board.json`, then `tools/pix check oriole`.** It checks required keys and alignment
   (for example the RAM handed to XNU must be 32 MiB aligned and hole-free).
5. **Run the gates** in [Plan](PLAN.md): shim runs, UFS reads (`--udump` to compare against Android), XNU boots.
6. **Use the measurement loop** below instead of ad-hoc commands.
7. **Contribute the captures** under `device/google/oriole/hardware/` and a short `docs/` note.

## The measurement loop (tools as of 2026-11-11, *read from source*: the tool headers in `pixelios-kernel`)

Every claim on the [Status](STATUS.md) page comes out of this loop, so a new device should use it from the first boot:

| Tool | What it does |
|---|---|
| `tools/pix devices`, `info`, `check`, `build` | list device trees, print the merged board definition, sanity-check it, build the shim image |
| `tools/phone state` / `tools/phone goto fastboot\|recovery\|android\|ios\|absent` | read which state the phone is in and move it to another one; ends with `RESULT: PASS\|FAIL\|PARTIAL\|ERROR`; `phone state` also tells you whether it is the expected codename |
| `tools/xrun` | one hardware cycle: build the image, `fastboot boot` it, collect the log, wait for the self-reset, print one report ending in `RESULT:`. Each `--expect REGEX` row must match a log line |
| `tools/usbnet-log.py` | receives the phone's live kernel console over USB Ethernet (UDP port 5140, no root); the interface address needs one `sudo` line on the host. This is the debug channel; the QR log (`tools/qr-log.py`) is only a fallback |
| `tools/mkadt.py` | builds the minimal Apple device tree that XNU needs from the board data |
| `tools/gate` | the gate entry point a change passes before it counts (`--quick` runs the steps the diff needs, `--formal` runs every step) |

Two habits keep numbers honest: a run is tagged with its label (for example `gputest-cced-poll20`), and a result is quoted as what the run printed, with "one run" when it was not repeated.
A panic no longer needs a hand on the phone: a kernel panic returns it to fastboot by itself (*observed on hardware*, one run, 2026-11-07, `20261107T145123Z-panic-self-recover`).

## New SoC (e.g. gs201)

Add `soc/google/gs201/soc.json` and `soc/google/gs201/shim/`:

- `ufsinit.c`, `ufsdiag.c` (UFS host and PHY bring-up; for gs101 this is derived from the Linux
  `ufs-exynos` / `phy-gs101-ufs` sources, see the [UFS bring-up notes](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/docs/07-gs101-ufs-bringup.md)),
- the UFS PHY tables (`tools/gen-ufsphy-tables.py` generates gs101's from the research notes),
- USB gadget constants if the DWC3 block differs,
- an XNU patch for the SoC's UFS driver if the host differs (see patch 0080).

The code is selected by SoC macro (`SOC_GS101`, ...) generated from the tree, never by phone name.

## What is NOT per-device (shared)

The shim core, the loader and payload builder, the ADT generator, the QR log channel, the USB
protocol, the safety audit (`tools/test-bluejay-boot.py`) and the XNU patch series. If you find
yourself editing them for one phone, the data probably belongs in `board.json` or the SoC tree.

## Honest gaps

- The pre-kernel probe sequence (watchdogs, reset chain, USB/UFS bring-up order) is still one `SOC_GS101`
  block in `shim/shim.c`. It is shared by every gs101 device, but a different SoC needs its own
  probe; splitting it behind a small board interface is the next refactor.
- The safety audit script and a few tool names still say `bluejay`; they apply to every gs101 device.
- On gs101 the display runs on the bootloader's framebuffer (no scan-out driver of our own) and touch works (FTM5 over SPI, rails via ACPM); buttons are partly tested. The GPU (Mali-G78), Wi-Fi (BCM4389) and Bluetooth drivers and the charger setting work on the Pixel 6a (*observed*, see [Status](STATUS.md)); a Pixel 6 or 6 Pro has the same SoC but may differ in radio module, panel and touch controller, so re-measure before you expect them to carry over (*guess*: not checked on those phones).

# Adding a device

Everything a phone needs lives in two small trees, so a new Pixel is mostly data:

- `soc/<vendor>/<soc>/`: shared by every phone with that chip.
- `device/<vendor>/<codename>/`: only what differs per phone.

**Only the Pixel 6a (bluejay, Tensor G1 / gs101) has been verified on hardware.** Everything below
about other phones is what you should expect, not what we have seen. Capture logs and send them.

## Which phones are close?

| Phone | Codename | SoC | What to expect |
|---|---|---|---|
| Pixel 6a | bluejay | gs101 (Tensor G1) | **verified** |
| Pixel 6 / 6 Pro | oriole / raven | gs101 | same SoC trees; only DRAM size, framebuffer and display size differ. Best first target. |
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
6. **Contribute the captures** under `device/google/oriole/hardware/` and a short `docs/` note.

## New SoC (e.g. gs201)

Add `soc/google/gs201/soc.json` and `soc/google/gs201/shim/`:

- `ufsinit.c`, `ufsdiag.c` (UFS host and PHY bring-up; for gs101 this is derived from the Linux
  `ufs-exynos` / `phy-gs101-ufs` sources, see the [UFS bring-up notes](socs/google/gs101/07-gs101-ufs-bringup.md)),
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
- On gs101 the display runs on the bootloader's framebuffer (no scan-out driver) and touch works (FTM5 over SPI, rails via ACPM); buttons are partly tested and battery is not ported.

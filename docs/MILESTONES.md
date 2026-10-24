# Milestones: from "boots to GUI" to a usable device

Tags: **[obs]** observed on hardware, **[src]** read from source, **[guess]**, **[open]** not started.
An arrow `A --> B` means B needs A. Updated 2026-10-24. Per-driver detail and evidence: [Status](STATUS.md) and [Coverage](COVERAGE.md).

"Usable device" (Gate U) = touch, buttons, a stable GUI, Wi-Fi, battery/charging, and a boot without a PC.

```mermaid
graph TD
  M0["M0 shim -> XNU, UFS root, USB log [obs]"]
  M1["M1 SpringBoard GUI, 8 cores [obs, 2026-10-22]"]
  M2["M2 PMIC rails via ACPM before XNU [obs]"]
  M3["M3 touch: FTM5 over SPI, taps and swipes reach SpringBoard [obs, 2026-10-22]"]
  M4["M4 touch recipe is the default, no boot-args [open]"]
  M5["M5 hardware keys to HID [partial: driver reads the GPIOs, no key press tested]"]
  M6["M6 GUI stable: poster-extension crashes, black screen after minutes, slow first boot [open]"]
  M7["M7 reliable dev loop: tools/xrun, tools/phone, local kernel build [obs]"]
  M8["M8 Wi-Fi: chip, firmware, IO80211-style en0 [partial: PCIe link, config space, BAR0 chip id obs]"]
  M9["M9 GPU path [partial: jobs run from the shim and XNU obs, no renderer]"]
  M10["M10 battery, charger, power-off [open, needs research]"]
  M11["M11 boot without a PC [open, needs a boot-slot decision by the maintainer]"]
  GU(["Gate U: usable phone"])
  M12["M12 audio [open]"]
  M13["M13 Bluetooth [open]"]
  M14["M14 cellular modem [open, out of scope while the modem partition stays untouched]"]

  M0 --> M1
  M0 --> M2
  M2 --> M3
  M1 --> M3
  M3 --> M4
  M1 --> M5
  M0 --> M7
  M7 --> M6
  M1 --> M6
  M6 --> M8
  M3 --> M8
  M1 --> M9
  M0 --> M10
  M2 --> M10
  M3 --> GU
  M4 --> GU
  M5 --> GU
  M6 --> GU
  M8 --> GU
  M10 --> GU
  M11 --> GU
  M1 --> M12
  M8 --> M13
  M8 --> M14
```

## What comes next

1. **M8 Wi-Fi** (milestone 2): backplane core enumeration, firmware and NVRAM download from the shim, then a PCIe and Broadcom driver in the kernel and the `apple80211` front end.
2. **M9 GPU**: fix the kernel panic when a GPU buffer is mapped into a process, then a first GPU-rendered frame.
3. **M6 stability**: the poster-extension crash loops, the black screen after minutes and the 14+ minute first-boot migration.
4. **M11** needs a decision by the maintainer: today the phone boots only through `fastboot boot` from a PC, and the project rules never write `boot*` partitions except by explicit exception.

## Open questions (measure or reverse, do not guess)

- Fuel gauge and charger interfaces on the Pixel 6a (M10).
- Whether key presses reach HID (M5).
- How the Broadcom firmware behaves after download. The firmware and NVRAM files come from the user's own phone image and are never committed.

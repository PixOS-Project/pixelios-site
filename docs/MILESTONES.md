# Milestone DAG: from "boots to GUI" to a working device

Status tags follow AGENTS.md rule 5: **[obs]** observed on hardware, **[src]** read from source/logs, **[guess]**, **[open]** not started.
An arrow `A --> B` means B needs A. Updated 2026-10-22 (session 13), kernel CI 0095 / HEAD 7725e3a.

"Working device" = Gate U below: touch + buttons + stable GUI + Wi-Fi + battery/charging, bootable without hand-holding.

```mermaid
graph TD
  M0["M0 shim -> XNU, UFS root, USB log [obs]"]
  M1["M1 SpringBoard GUI, display on [obs, touchx3 +119s]"]
  M2["M2 PMIC rails via ACPM before XNU [obs: shim + touchx3 --rails]"]
  M3["M3 FTM5 identify 36 48 inside XNU [obs, touchx3]"]
  M4["M4 touch events decoded [obs: runs touchx5/demo1b/demo2 log SWEET HID: touch N down/up]"]
  M5["M5 touch -> HID -> SpringBoard reacts [obs, user: taps and swipes work, 2026-10-22]"]
  M6["M6 touch recipe is the default (no boot-args/poke), 10 MHz [open]"]
  M7["M7 hardware keys -> HID (power/vol) [src: KEYS lines exist, HID path unverified]"]
  M8["M8 GUI stable: poster/widget crashes, check-in timeouts [open]"]
  M9["M9 reliable dev loop: local kernel build matches CI, hang recovery [open: local kernel hangs]"]
  M10["M10 Wi-Fi: chip, firmware, IO80211-style en0 [open: research docs/research/12,20]"]
  M11["M11 battery/charger/fuel gauge, power-off [open, needs research]"]
  M12["M12 boot without a PC: persistent boot path [open, BLOCKED by hard rule 1, needs user decision]"]
  GU(["Gate U: usable phone"])
  M13["M13 audio / haptics [open, optional]"]
  M14["M14 GPU acceleration [open, optional, research first]"]
  M15["M15 cellular modem [open, optional]"]

  M0 --> M1
  M0 --> M2
  M2 --> M3
  M3 --> M4
  M4 --> M5
  M1 --> M5
  M5 --> M6
  M2 --> M6
  M1 --> M7
  M1 --> M8
  M0 --> M9
  M9 --> M8
  M5 --> M10
  M8 --> M10
  M0 --> M11
  M2 --> M11
  M5 --> GU
  M6 --> GU
  M7 --> GU
  M8 --> GU
  M10 --> GU
  M11 --> GU
  M12 --> GU
  M1 --> M13
  M1 --> M14
  M10 --> M15
```

## Critical path (what to do next, in order)

1. **M4** *read from source* (`ftsSoftware.h:384,402-408`, android-gs-bluejay-5.10-android13-qpr3): `0x43` = STATUS_UPDATE; `43 05` = force-cal, `43 01 a0 00 ff` = echo of our scan-enable. No decoder bug. Remaining: a run where the user touches the screen (`touchx4`), expect `SWEET HID: touch`.
2. **M5** deliver touch reports to HID (`sweet_hid_touch`), confirm SpringBoard reacts.
3. **M6** bake the recipe (rails + cs=1 + osc div 5 + reset pulse) into defaults, then 10 MHz.
4. In parallel, one heavy job at a time: **M9** (verify the Antigravity local-build fix) and **M8** (crash logs via usbnet).
5. **M10** Wi-Fi after the GUI is usable; **M11** battery needs research first.
6. **M12** needs a user decision: the phone today only boots via `fastboot boot` from the PC. Writing `boot*` is forbidden by hard rule 1, so either the rule is relaxed for a backed-up, reversible case or the device stays PC-tethered.

## Open questions (do not guess, measure/reverse)
- FTM5 event layout (M4). Wi-Fi chip/firmware path (M10). Fuel gauge/charger interface on bluejay (M11).

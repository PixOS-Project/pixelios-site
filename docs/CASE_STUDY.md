# Case study: porting ios-sweet to the Pixel 6a (bluejay)

Sources: `docs/research/01..05` in `pixelios-kernel` (05 = primary-source fact-check), written as desk research on 2026-10-20,
before any Pixel 6a boot. The tables below are that plan. Where a later hardware result settled an item it says so; items
still marked *(verify)* were not checked on the phone. Current results: [Status](STATUS.md).

## 1. What ios-sweet is

[ios-sweet](https://github.com/dipa-studio/ios-sweet) (upstream commit `11da58b`; MIT-licensed, checked 2026-10-24) boots
Apple's open-source XNU `xnu-8796` and the unmodified iPhone X iOS 16.7.16 userland
on a Redmi Note 10 Pro (Qualcomm SM7150). It reaches SpringBoard with touch and
buttons, CPU-only rendering.

```
stock ABL --fastboot boot--> shim (boot.img, own MMU, reads FDT)
  -> XNU (SWEET machine config, plain arm64, 81 patches) + generated ADT
     -> own UFS driver -> HFS+ root in userdata -> launchd -> SpringBoard
```

It works because the stock bootloader leaves three things running that XNU then reuses
without drivers: **a scanning-out framebuffer, a linked-up UFS host and a powered DWC3**.
That's the main thing the Pixel has to provide too.

## 2. How the Pixel 6a maps onto it

| Area | sweet (SM7150) | bluejay (gs101) | Port work |
|---|---|---|---|
| CPUs | 6×A55 + 2×A76, v8.2, no PAC | 4×A55 + 2×A76 + 2×X1, v8.2, no PAC, MPIDR `0x0n00` | ADT CPU table; 16K granule *(verify per core)* |
| Entry | EL1, MMU off, x0=DTB | EL1 or EL2 (pKVM exists); the shim is built to enter at EL2 *(read from source; not re-measured)* | Drop EL2→EL1 in shim |
| Boot image | v2 + embedded DTB, `fastboot boot` | v4 + vendor_boot; custom images boot with `fastboot boot` when they carry an AVB footer (*observed*, 2026-10-21; `shim/build.sh --avb`) | New `build.sh` packing |
| GIC | GICv3 G1NS, `0x17a00000/0x17a60000` | GICv3 G1NS, `0x10400000/0x10440000`, stride 0x20000 | Constants only |
| Timer | 19.2 MHz, vtimer INTID 19 | 24.576 MHz, vtimer INTID 27 (`soc.json`; XNU runs on it, *observed*) | Constants only |
| PSCI | smc, CPU_ON plain | smc; first CPU_ON likely plain; hotplug re-online needs CPU_INFORM (via SMC `0x82000504`) + `pmu-intr-gen` | Small SMP patch |
| Watchdog | off from ABL | `watchdog_cl0/cl1` at `0x10060000`/`0x10070000`, disabled by the shim | Disable in shim |
| Framebuffer | `0x9c000000`, video mode, live | `0xfac00000` 1080×2400 stride 4320 (measured in the live FDT; `board.json`); **command-mode** panel, ABL disables the DECON HW trigger | Write `0x3061` to `0x1C300030` (what postmarketOS does on all gs101); the panel shows the iOS UI (*observed*) |
| UFS | std UFSHCI `0x1d84000` | Exynos UFSHCI `0x14700000`, PRDT byte granularity, FMP, S2MPU. The bootloader shuts the controller down, so the shim does a full cold re-init (*observed*) | Adapt 0028 / shim ufs.c |
| Touch | Goodix over GENI I²C | STMicro FTM5 on `spi_11` (USI11 `0x10D40000`), IRQ gpa9-0, rails S2MPG10 LDO25M/26M | Rewritten, **works** (*observed*, 2026-10-22) |
| Buttons | PMIC over SPMI | gpio-keys gpa7-3 / gpa8-1 (far-alive bank `0x174e0000`), power gpa10-1 | Driver starts; no key press tested yet |
| USB | DWC3 + Qualcomm PHY | DWC3 `0x11110000` + gs101 USB PHY | Reuse gadget/ECM, new PHY bits |
| Battery | static source | static source | Reuse |
| Debug | screen + UFS log ring | **SBU UART** (needs a 1.8 V cable; the current tooling does not use it), screen, RAM log, and the USB UDP log (the main channel, *observed*) |
| Root storage | `userdata` | `userdata` (only partition big enough; erases Android) | Same |

Patch inventory (`research/03`): of 81 kernel patches, ~66 are generic, ~10 only need
constants, 5 are Qualcomm rewrites (0060, 0062, 0063, 0072, 0074). Recommendation: keep
the `SWEET` machine config name, select the board at runtime from the ADT, add `gs101_*`
drivers alongside.

## 3. Ranked risks (as planned on 2026-10-20) and what happened

1. **Display**: command-mode panel. The DECON trigger write restored scan-out and the iOS UI is drawn on it (*observed*).
2. **`fastboot boot` of a custom image**: accepted with an AVB footer (*observed*), nothing is flashed to `boot*`.
3. **UFS state at handoff**: the bootloader does tear the link down, so the shim runs a full cold init and switches to HS-G4 (*observed*).
4. **Entry EL / memory map**: the live FDT's `memory` and `reserved-memory` are used; the RAM given to XNU is the hole-free high range at `0x880000000` (`board.json`).
5. **Thermal**: still no thermal driver (*open*); idle loops use `wfi`; all 8 cores run, including the X1s.

## 4. Newer iOS (research/04)

- iPhone iOS 17/18/26 all require **arm64e (PAC)**. The Tensor G1 cores are v8.2: non-HINT PAC
  instructions (`braa`, `retab`, `ldraa`…) are undefined. Only a kernel trap-emulator or a
  whole-cache binary rewrite would work. That's research, not a milestone.
- **iPadOS 17/18 on iPad 7th gen (`iPad7,11`, A10)** is plain arm64 *(verify by mounting the
  SystemOS cryptex)*. It is the newest realistic target: rebase the patch stack to `xnu-11215`,
  switch identity to the iPad, deal with a 4:3 iPad canvas on a 20:9 panel.
- iOS/iPadOS 26: no non-PAC target left. Not reachable this way.

## 5. Outcome

The plan held: the Pixel 6a boots XNU to SpringBoard on 8 cores with touch (*observed*, 2026-10-22). The main
surprises were not in the plan's risk list: touch needed its two regulator rails switched on through the ACPM mailbox before the
chip answered, and the iOS userland needed a root recipe tweak plus kernel patches 0086, 0087 and 0099 to get past the Apple-logo stall
and the Settings -> About hang (details in [Status](STATUS.md)).

# Case study: porting ios-sweet to the Pixel 6a (bluejay)

Sources: `docs/research/01..05` (05 = primary-source fact-check) (delegated desk research, 2026-10-20). Nothing here
has been measured on a Pixel 6a yet. Facts marked *(verify)* are settled by the
Phase 0 probe boot, not by more reading.

## 1. What ios-sweet is

[ios-sweet](https://github.com/dipa-studio/ios-sweet) (upstream commit `11da58b`, checked out
in `upstream/`, gitignored, **no license file: keep this repo private**) boots
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
| Entry | EL1, MMU off, x0=DTB | EL1 or EL2 (pKVM exists) *(verify)* | Drop EL2→EL1 in shim if needed |
| Boot image | v2 + embedded DTB, `fastboot boot` | v4 + vendor_boot; `fastboot boot` works for Magisk images; custom image untested, may need AVB footer *(verify)* | New `build.sh` packing |
| GIC | GICv3 G1NS, `0x17a00000/0x17a60000` | GICv3 G1NS, `0x10400000/0x10440000`, stride 0x20000 | Constants only |
| Timer | 19.2 MHz, vtimer INTID 19 | 24.576 MHz, vtimer INTID 27 *(verify)* | Constants only |
| PSCI | smc, CPU_ON plain | smc; first CPU_ON likely plain; hotplug re-online needs CPU_INFORM (via SMC `0x82000504`) + `pmu-intr-gen` | Small SMP patch |
| Watchdog | off from ABL | `watchdog_cl0 0x10060000` may be armed *(verify)* | Disable in shim |
| Framebuffer | `0x9c000000`, video mode, live | `0xfac00000` 1080×2400 stride 4320 (Oriole value); **command-mode** panel, ABL disables DECON HW trigger | Write `0x3061` to `0x1C300030` (what postmarketOS does on all gs101) |
| UFS | std UFSHCI `0x1d84000` | Exynos UFSHCI `0x14700000`, PRDT byte granularity, FMP, S2MPU *(verify link left up)* | Adapt 0028 / shim ufs.c |
| Touch | Goodix over GENI I²C | STMicro FTM5 on `spi_11` (USI11 `0x10D40000`), IRQ gpa9-0, rails S2MPG10 LDO25M/26M (confirmed) | Rewrite |
| Buttons | PMIC over SPMI | gpio-keys gpa7-3 / gpa8-1 (far-alive bank `0x174e0000`), power gpa10-1 | Simpler rewrite |
| USB | DWC3 + Qualcomm PHY | DWC3 `0x11110000` + gs101 USB PHY | Reuse gadget/ECM, new PHY bits |
| Battery | static source | static source | Reuse |
| Debug | screen + UFS log ring | **SBU UART** (`fastboot oem uart enable`, 1.8 V, `0x10a00000`, Samsung UART), screen, UFS ring | Better than sweet |
| Root storage | `userdata` | `userdata` (only partition big enough; erases Android) | Same |

Patch inventory (`research/03`): of 81 kernel patches, ~66 are generic, ~10 only need
constants, 5 are Qualcomm rewrites (0060, 0062, 0063, 0072, 0074). Recommendation: keep
the `SWEET` machine config name, select the board at runtime from the ADT, add `gs101_*`
drivers alongside.

## 3. Ranked risks

1. **Display**: command-mode panel; the known DECON trigger write should restore scanout, but
   unproven for a non-Linux payload. Mitigation: UART for logs.
2. **`fastboot boot` of a custom image**: may be refused or need an AVB footer.
   Fallback: flash to the inactive slot's `boot`, never the active one.
3. **UFS state at handoff**: if the bootloader tears down the link, we need full Exynos UFS init.
4. **Entry EL / memory map**: settled by the probe; must use the live FDT's `memory` and
   `reserved-memory`, never assume contiguous 6 GB.
5. **Thermal**: no thermal driver; idle loops must `wfi`; bring up X1 cores last.

## 4. Newer iOS (research/04)

- iPhone iOS 17/18/26 all require **arm64e (PAC)**. The Tensor G1 cores are v8.2: non-HINT PAC
  instructions (`braa`, `retab`, `ldraa`…) are undefined. Only a kernel trap-emulator or a
  whole-cache binary rewrite would work. That's research, not a milestone.
- **iPadOS 17/18 on iPad 7th gen (`iPad7,11`, A10)** is plain arm64 *(verify by mounting the
  SystemOS cryptex)*. It is the newest realistic target: rebase the patch stack to `xnu-11215`,
  switch identity to the iPad, deal with a 4:3 iPad canvas on a 20:9 panel.
- iOS/iPadOS 26: no non-PAC target left. Not reachable this way.

## 5. Status of the attached device

The phone on USB on 2026-10-20 was **not a Pixel 6a** (a different, locked device), which is why the attached
device is always checked first. Nothing hardware-side can be tested until the Pixel 6a is connected with an unlocked bootloader.

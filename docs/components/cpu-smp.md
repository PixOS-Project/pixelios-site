# CPU and SMP (8 cores)

**Last verified: 2026-11-16.**

## What it is

The Tensor G1 has eight Armv8.2 cores in three clusters: 4x Cortex-A55, 2x Cortex-A76 and 2x Cortex-X1.
XNU must start the secondary cores, know which is which, and schedule threads on them.

## Status

**All 8 cores run** (*observed on hardware* 2026-10-22, run `usbnet4-cpus8`). The measured 2026-11-15 configuration runs 5 of them on purpose.

## What worked

- **Core start-up through PSCI.** Plain `CPU_ON` per core, with the real MPIDR values from the probe in the device tree (run `usbnet4-cpus8`).
- **16 KiB pages on every core**, as iOS expects (*observed*, probe report 2026-10-21).
- **A scheduler hint instead of hot-plug.** Boot argument `sweetrecores=MASK` (patch 0270) tells the scheduler which cores to use;
  the others stay online for interrupts only (*read from source*, patch header).
- **Five cores for the low-clock configuration.** The boots behind the release numbers use one A55 and the four big cores
  (*read from source*: the core order in patch 0336's header; *observed*: runs `155b`, `8177` report 5 of 8 cores).
- **Per-CPU load and a PC sampler** in the log (patches 0145, 0147, 0263, 0352), which is how CPU time was attributed to processes.

## What didn't

- **More CPU clock did not buy frames at the low GPU clock.** Raising the A76 cores from 1663 to 1836 MHz left the rendered rate at
  50.5 against 50.6 (*observed* 2026-11-15, run `fede`).
- **Cores never sleep deeply.** Idle cores sit in plain `wfi`. This is one reason the phone runs warm ([Thermal](thermal.md)).
- **No pointer authentication.** The cores are Armv8.2, so an arm64e userland (iOS 17 and later on iPhones) cannot run
  ([case study](../CASE_STUDY.md#4-newer-ios-research04)).

## Untested or never attempted

- **CPU idle states and core power-off.** A read-only firmware query reported `CPU_SUSPEND` and `CPU_OFF` as supported
  (*observed* 2026-11-14, read-only probe boot, patch 0363). Neither has been called after boot.
- **A performance controller.** Nothing moves threads between small and big cores by load, and nothing changes clocks at run time.
- **Interrupt spreading.** Every interrupt is routed to the boot core (*read from source*, patch 0365's header).

## Ideas if you want to pick it up

- Power down the idle cores with PSCI and measure the heat. Hang risk: prove the watchdog recovery first ([Recovery](recovery.md)).
- Route the GPU job interrupt to a big core and measure the completion latency with patch 0364's counters.
- Compare 3, 5 and 8 cores in one session at the same clocks; the cost of an idle-but-on core was never priced.

## Where to look

- Patches: 0270, 0344 (recommended cores), 0145, 0147, 0121 (CPU statistics), 0263, 0352, 0353 (samplers), 0365 (GPU thread binding), 0363 (read-only probes).
- Data: `cpus` and PSCI entries in [`soc.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/soc.json).
- Blueprint stage [3](../BLUEPRINT.md#3-xnu-bring-up). Related: [Clocks and DVFS](clocks-dvfs.md), [Interrupts and timers](interrupts-timers.md).

# Thermal

**Last verified: 2026-11-16.**

## What it is

Android throttles the Pixel as it heats. A ported kernel has none of that unless you write it. PixOS has a small kernel thread
that samples the battery temperature and acts on a fixed table, plus a host-side rule that ends a test run when the phone is hot.

## Status

**The release bench boots stayed between 33 and 41 C** (*observed on hardware* 2026-11-15, runs `155b`, `8177`: 33.4 to 39.8 C and 34.1 to 40.6 C). The kernel's emergency steps exist but were **not observed firing** on hardware.

## What worked

- **A temperature source that needs no new driver**: the fuel gauge's battery temperature, already read for the battery rows
  (patch 0336; temperature rows *observed* since 2026-11-13).
- **Telling iOS.** The same thread feeds the battery temperature to iOS's power source and to a temperature sensor service that
  the thermal daemon opens (*read from source*, patch 0336; opening the service was seen in the QEMU lab, host only, 2026-11-12).
- **A kernel backstop that does not depend on iOS** (*read from source*):

| Battery temperature | Action |
|---|---|
| 48 C and above | take the two X1 cores out of scheduling; restore at 44 C |
| 45 C and above while charging | drop the charge limit back to the bootloader's value until 42 C |
| 55 C on two samples in a row | orderly stop and reset to the bootloader |

- **A host-side stop.** The test runner ends a run at 45 C and waits for the phone to cool (*observed* 2026-11-13, run `66f9`, cut at 45.3 C).
- **Low clocks.** The largest thermal fix was not a throttle: it was running at clocks that do not overheat ([Clocks](clocks-dvfs.md)).
- **No hidden throttling in the numbers.** In 9 of 11 bench logs the second, hotter half was faster than the first (*observed*, host check, 2026-11-15).

## What didn't

- **Before any of this, the battery reached 51.6 to 53 C** under the boost configuration with charging on (*observed* 2026-11-12).
  The maintainer's words: the phone was "hot". That is what started this work.
- **Idle was not cool.** One idle boot rose from 41.6 to 45.0 C in 19 minutes, with a single runaway iOS daemon keeping a core busy
  (*observed* 2026-11-13; see `coreduetd` on [Userland](userland.md)).
- **The first safety rule was blind.** A boot with no temperature row was cut by the runner even though the phone was cool. A refused
  charger step had suppressed the rows; patch 0339 prints them anyway.

## Untested or never attempted

- **The backstop steps on real hardware.** No logged boot reached 48 C after the patch landed.
- **The SoC's own temperature sensors** and the board's skin thermistors. The battery reading lags the chip.
- **Whether iOS reduces load** when told the device is warm.
- **Clock steps as a throttle.** The backstop removes cores; it cannot lower a clock ([Clocks](clocks-dvfs.md)).
- **Cooling hardware.** None was used.

## Ideas if you want to pick it up

- Add thermal management **before** stress tests on a new port, not after the first scare.
- Read the SoC temperature sensors and compare them with the battery reading under the bench.
- Cores in plain `wfi` and a busy idle system are the base load. Fixing those lowers every temperature on this page.

## Where to look

- Patch 0336 (thermal thread and table), 0307, 0339 (temperature rows), 0270 (the scheduler call the backstop uses).
- Related: [Power and charging](power-charging.md), [Recovery](recovery.md).

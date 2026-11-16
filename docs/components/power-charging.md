# Power, charging and battery

**Last verified: 2026-11-16.**

## What it is

Under Android, a charger chip, a fuel gauge and a USB power controller manage the battery. Under PixOS only two things are driven:
the charger's **input current limit**, and reads of the **fuel gauge** (charge level, voltage, current, temperature).

## Status

**The battery charges while iOS runs, at light load** (*observed on hardware* 2026-11-10, run `chg-p3`, one run: battery current went from -40 mA to between +107 and +205 mA). Under the GPU bench the battery drains.

## What worked

- **Reading before writing.** Read-only probes of the charger bus came first, then reads of the chips, then one reviewed write.
- **Raising the input limit to 875 mA on USB 3.** The bootloader leaves a 500 mA limit, which is below what a running iOS draws
  (-98 mA, run `chg-p2`). With 875 mA the current turned positive (run `chg-p3`).
- **Battery rows in every log**: charge level, voltage, current and temperature (patches 0298, 0307). They are the witness for
  power numbers on this site, for example 3.32 and 3.27 W in the two release bench boots (runs `155b`, `8177`).
- **iOS gets the real battery temperature** (patch 0336, *read from source*).

## What didn't

- **The USB descriptor and the limit must change together.** The review of the write found the phone still declared about 500 mA to the host.
- **Charging cannot keep up with load.** In the heavy bench the battery drained at 0.8 to 1.1 A with the 875 mA
  input, and went from 63 % to 15 % in about 2.5 hours of test boots (*observed* 2026-11-13).
- **The phone does not charge in fastboot** (*observed* 2026-11-13). A test phone parked there between runs slowly empties.

## Untested or never attempted

- **USB Power Delivery and faster charging.**
- **Charging with the phone "off".** There is no off state under PixOS; it runs or sits in the bootloader.
- **Sleep and wake.** The phone never sleeps, so idle draw is high.
- **Whether iOS's battery percentage shows the real level** was not checked.
- **Battery health, charge limits, optimised charging.**

## Ideas if you want to pick it up

- Idle power is the cheapest win: cores that never sleep and daemons that spin ([CPU](cpu-smp.md), [Userland](userland.md)).
- Measure before raising any limit further. The charger is the one chip here where a wrong write can damage hardware.
- Screen brightness is not controlled yet ([Display](display.md)).

## Where to look

- Patches: 0283, 0284 (charger probe and bus), 0287 (input limit), 0298, 0307, 0339 (battery rows), 0305 (gate pins), 0314, 0318, 0319 (power-controller diagnostics).
- Blueprint stage [12](../BLUEPRINT.md#12-charging-and-power). Milestone: [Charging](../milestones/charging.md). Related: [Thermal](thermal.md).

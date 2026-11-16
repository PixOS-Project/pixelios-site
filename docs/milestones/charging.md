# Charging while iOS runs

**Last verified: 2026-11-16.** Milestone M10 · 2026-11-10 · **done, one run**

## Goal

The battery gains charge while iOS runs, so long test sessions stop ending in a dead phone.

## What was done

1. **Measured first.** A read-only probe of the charger bus, then reads of the charger and fuel-gauge chips.
2. **Found the cause**: the phone *was* charging, at the 500 mA limit a plain USB port gets, which is less than a running iOS draws.
3. **One reviewed write**: raise the input current limit to 875 mA on a USB 3 link, and change the USB descriptor to match.
4. **Battery rows in the log** on every boot: level, voltage, current, temperature.

## How it was proven

*Observed on hardware*, 2026-11-10.

| Run | Input limit | Battery current |
|---|---|---|
| `chg-p2` | 500 mA (bootloader default) | -98 mA (draining) |
| `chg-p3` | 875 mA | -40 mA before the write, +107 to +205 mA after, no charger bus errors |

One run. Not repeated as a milestone measurement, and not measured under GPU load at the time.

## What it unlocked

Longer sessions, and a temperature and power reading in every later log. The 3.3 W and 33 to 41 C figures in the release note come
from these rows.

## Dead ends

- **Two dead-battery stops and two hours of polling the battery voltage** before anyone probed the charger ([Lessons](../LESSONS.md)).
- **The descriptor.** The first version of the write raised the limit but still told the host the phone draws about 500 mA. A review caught it before it booted.
- **It is not enough under load.** Later boots drained at 0.8 to 1.1 A in the heavy bench even with the higher limit (*observed* 2026-11-13).

Component: [Power and charging](../components/power-charging.md), [Thermal](../components/thermal.md).

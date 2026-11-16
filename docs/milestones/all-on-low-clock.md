# Everything at once, at low clocks

**Last verified: 2026-11-16.** 2026-11-11 to 2026-11-15 · rendered frames, Wi-Fi and stability **met**; drawn presents **49.0 of 50, not met**

This is the milestone behind the [2026-11-15 release](../RELEASE-2026-11-15.md).

## Goal

Until 2026-11-11 each feature had been proven on its own boot, with its own settings. The new goal: **one boot, one configuration**,
with the GPU, touch, Wi-Fi and Bluetooth all on, under a stress bench, twice in a row.

On 2026-11-13 the maintainer narrowed it: about 50 frames/s, stable, **at low clocks with no boost**, with Wi-Fi that reaches the real internet.

The bar, on one configuration, two boots in a row:

| What | Bar |
|---|---|
| Rendered frames, 600 s heavy bench with Wi-Fi load | pooled 50 or more, slowest step 45 or more |
| Drawn frames that reach the panel | 50 per second or more |
| Stability | no reset, panic or hang; the phone parks in fastboot |
| Wi-Fi | joined, no link drop, address + route + DNS + HTTPS to a public host |
| Touch | a real finger; unlock and open an app by hand |

## What was done

1. **A stress bench.** The old navigation bench waited for each screen to settle: "best case, always". The new one sends input
   before animations end, in bursts, for 10 minutes, with Wi-Fi traffic running.
2. **Safety first.** Stress boots at boost clocks reached 51.6 to 53 C. A thermal thread, an earlier watchdog and a host-side
   temperature stop landed before more stress boots ([Thermal](../components/thermal.md)).
3. **Measured where the time goes** at the bootloader's clocks: 21.2 frames/s (run `1d81`). One clock at a time showed that memory
   speed was the wall: memory alone gave 45.2 (run `a59a`), GPU clock alone about 25.
4. **Fixed our own costs**: a memory leak in the GL layer, a blocking flush, a backdrop setting that made blur expensive, per-job cache flushes.
5. **Polling to interrupts** for Wi-Fi, storage and touch.
6. **Wi-Fi that survives load**: a larger receive buffer pool, and a correct clock for TLS.
7. **Frame pacing**: one frame per vsync, so two quick swaps are not shown as one.

## How it was proven

All *observed on hardware*.

| Date | Step | Rendered pooled / slowest | Run |
|---|---|---|---|
| 2026-11-13 | bootloader clocks, nothing tuned | 21.2 / 14.7 | `1d81` |
| 2026-11-13 | memory clock raised only | 45.2 / 41.0 | `a59a` |
| 2026-11-14 | cheaper cache flushes, backdrop setting removed | 48.8 / 47.3 | `c840` |
| 2026-11-15 | Bluetooth firmware load no longer spins a core | 49.6 / 48.0 | `d9a3` |
| 2026-11-15 | middle CPU clock for the big cores (first measurement) | 50.9 / 49.6 | `cf53` |
| 2026-11-15 | **bar boots**, full Wi-Fi load | **50.6 / 48.4** and **50.6 / 48.6** | `155b`, `8177` |
| 2026-11-15 | pacing fix | all presents 51.2/s; **drawn presents 49.0/s** | `18e1` |

Read the table as a direction, not a like-for-like series: the bench itself was corrected on 2026-11-14 (see dead ends), and only the
bar boots and later carry Wi-Fi load for the whole bench.

The two bar boots: about 37 minutes uptime each with no reset, internet checks 9 of 9, no link drop, TCP 285.4 and 188.1 Mbit/s
down, 3.32 and 3.27 W, 33.4 to 39.8 C and 34.1 to 40.6 C.

The demo boot (job 1308, 2026-11-15), driven by the maintainer by hand: a real finger (5791 touch interrupts), a headset paired in
Settings, Wi-Fi up for the whole boot, MobileSafari launched 6 times, no panic or reset.

## What it unlocked

The public release. And a configuration that runs cool enough to leave on: the earlier 55 to 60 frames/s numbers needed boost
clocks that the phone could not sustain.

## Dead ends

- **Boost clocks under stress.** Sixteen silent resets, about 5 to 6 minutes into the heavy bench, at every memory level tried
  (*observed* 2026-11-12/13). No panic line, battery at 36 to 40 C. Cause not found; the low-clock configuration does not show it.
- **"It is CPU-bound."** The first reading of the low-clock bench blamed the CPU. A closer look showed heavy frames were waiting on
  the GPU and, behind that, on memory speed.
- **More CPU clock** (run `fede`), **storage by interrupt** (run `c1f4`), **telling iOS the disk is solid-state** (run `ef4a`),
  **one boot without the runaway daemon** (run `c68b`), **skipping unchanged panel copies** (run `d9a3`): none moved the frame rate.
- **Stalls of a second or more** in the bench looked like a system problem. They were the bench opening the same screen twice in a
  row: nothing to draw. The bench was fixed, and earlier bench numbers are not comparable.
- **Benches without load.** For a day the Wi-Fi load generator's peer was down, so "no link drop under load" proved nothing. Only runs `155b` and later carry full load.
- **Blind scripted taps.** Under stress, taps at fixed coordinates landed in the wrong app. The bench now checks what is on screen first.

Still open from this milestone: the last drawn frame per second, UDP download loss under load, and the `lskdd` restart loop. See [what is left](open.md).

Components: [GPU](../components/gpu.md), [Display](../components/display.md), [Clocks](../components/clocks-dvfs.md), [Wi-Fi](../components/wifi.md), [Thermal](../components/thermal.md).

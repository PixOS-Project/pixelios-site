# Open milestones: what is left

**Last verified: 2026-11-16.** Nothing on this page is done. Each item says what would prove it, so you can pick one up.

The order of work the maintainers intend is on the [Roadmap](../../ROADMAP.md). The definition of a "usable phone" is on the [overview](../MILESTONES.md).

## Close: one frame per second short

| Item | State (*observed on hardware*) | What would prove it |
|---|---|---|
| Drawn presents at 50 per second at the lowest GPU clock | 49.0 (run `18e1`, 2026-11-15) | two bench boots in a row at 50 or more |
| 60 frames/s on every navigation step | pooled 59.5, slowest step 51.6, at boost clocks (run `gputest-surffail-b`, 2026-11-11) | slowest step at 60, two boots |
| Render defects | search magnifier glyph missing; dark band in Spotlight (2026-11-11 list, not re-checked) | captured frames match the references |

Details: [Display](../components/display.md), [GPU](../components/gpu.md).

## M12 Audio (partial)

- **Headset (A2DP):** pairs, stream configured, never started (run `bt-va3`, 2026-11-11). Proof: sound from a headset, with the stream start in the log.
- **Speaker:** not started. Proof: a tone from the phone's own speaker.

Details: [Audio](../components/audio.md).

## M10 Charging under load (one run so far)

The battery charges at light load (run `chg-p3`) and drains under the bench. Proof: battery current at or above zero during a
10 minute bench. Details: [Power and charging](../components/power-charging.md).

## M5 Hardware keys (partial)

Power and volume-up presses reach the kernel (runs `resident-164801-b1`, `resident-204614-b1`). Left: volume-down, and the iOS reaction for each of the three keys.
Details: [Buttons](../components/buttons.md).

## M11 Boot without a PC (not started)

Today every boot is a `fastboot boot` from a computer, and the project never writes `boot` partitions. Proof: power button to lock
screen with no cable, **and** a demonstrated way back to stock. The design has to come first. Details: [Boot chain](../components/boot-chain.md).

## M6 Sleep, wake and long-run stability (not started)

The phone never sleeps, and long-run stability was never measured as such (the release bench boots ran about 37 minutes each). Proof: screen off and on by the power key,
and a boot that runs for hours. Details: [CPU](../components/cpu-smp.md), [Display](../components/display.md).

## M14 Cellular, camera, sensors (not started)

No driver and no research. Cellular is out of scope while the modem partition stays untouched. Details: [Not attempted](../components/not-attempted.md).

## Known issues without a milestone

- UDP download loses packets under heavy load (27.3 % and 39.5 % in the bench boots). [Wi-Fi](../components/wifi.md)
- The iOS daemon `lskdd` restarts about once a second. [Userland](../components/userland.md)
- "Weak Security" label on WPA2 networks. [Wi-Fi](../components/wifi.md)
- The boost-clock configuration resets under the heavy bench. [Clocks](../components/clocks-dvfs.md)
- About 593 MB of storage writes in 10 minutes from an unknown writer. [Storage](../components/storage-ufs.md)

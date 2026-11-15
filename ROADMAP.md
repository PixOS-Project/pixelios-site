# Roadmap

**Last verified: 2026-11-15.** What works is in [docs/STATUS.md](docs/STATUS.md) (each row names the run it was seen in). The measured ladder is in
[docs/MILESTONES.md](docs/MILESTONES.md). This page lists what comes next. Order and estimates are guesses, not promises.

## Reached (observed on hardware)

1. **iPhone GUI on the Pixel 6a** (2026-10-22): lock screen, home screen, Settings, touch, 8 cores.
2. **GPU-drawn UI**: the slowest step of the navigation bench at or above 55 frames/s in two boots (2026-11-09, runs `gputest-nav43`, `gputest-nav44`); pooled 59.5 at boost clocks (2026-11-11); at the lowest GPU clock (150 MHz) rendered 50.6 / 50.6 pooled (2026-11-15, runs `155b`, `8177`).
3. **Wi-Fi in Settings** (2026-11-08 to 2026-11-11): scan, WPA2 join, DHCP, more than 100 Mbit/s, reconnect after the access point drops the phone.
4. **Bluetooth on the stock daemon** (2026-11-10/11): scan, LE connect, advertising, pairing that survives a reboot.
5. **Charging while iOS runs** (2026-11-10, one run).
6. **Real internet and touch with a finger** (2026-11-15): pixnet 9/9 (DNS, HTTPS) at 188 to 285 Mbit/s TCP down under full bench load (runs `155b`, `8177`); a real finger on the demo boot (job 1308); a headset paired by hand.

## Next

- **Drawn presents at least 50 per second** at the lowest GPU clock: 49.0 today (run `18e1`). Then 60 frames/s on every step.
- **UDP download loss under heavy load** (27 to 40 % in the bench boots) and the `lskdd` restart loop (about once a second).
- **Render defects:** the magnifier glyph in search fields, the Spotlight band under the status bar.
- **Sound:** a driver for the speaker path; find out why iOS opens an A2DP stream to a headset and never starts it.
- **Charging under load** measured during GPU boots, then on by default.
- **A QEMU lab** for host-only work on the iOS userland: a feasibility study booted the iOS root to SpringBoard in QEMU with a lab-only block-device patch (2026-11-11, host only, conditional go). It would let people without a Pixel 6a work on the userland.

## Later

- Boot without a PC, with a design that stays reversible (the project never writes `boot*` partitions today).
- Buttons, sleep and wake, sensors, camera. Cellular is out of scope while the modem partition stays untouched.
- Other Tensor phones (Pixel 6 and 6 Pro share the SoC): see [docs/PORTING.md](docs/PORTING.md). Other phones entirely: [docs/BLUEPRINT.md](docs/BLUEPRINT.md).

## Where help is most useful

- Hardware captures from other Tensor devices (see [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit them, with serials removed).
- Audio: the gs101 audio path (codec, amplifier) from the Linux and Android kernel sources, cited.
- Host-side tests and tools, and anything the QEMU lab makes possible without a phone.
- Read-only reverse engineering notes of your own, with method and sources (never Apple binaries or their contents).

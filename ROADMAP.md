# Roadmap

What works is in [docs/STATUS.md](docs/STATUS.md) (every row says whether it was *observed on hardware*, *read from source* or is a *guess*).
This page lists what comes next. Order and estimates are guesses, not promises.

## Milestones

1. **iPhone GUI on the Pixel 6a: reached** (2026-10-22). Lock screen, home screen, Settings, touch.
2. **Wi-Fi: not started on hardware.** Broadcom BCM4389 on PCIe; plan in [docs/research/20-wifi-stack-plan.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/20-wifi-stack-plan.md).

## Now (demo and release)

- Power-on boot without a PC: iOS image in `boot_a`, stock `boot_b` kept as the way back, slot switched with `fastboot --set-active`.
- Pixel 6a identity in Settings -> About (name, model, serial text), plain lock-screen clock. Built, waiting for a hardware check.
- Publish this repository.

## Next

- **Smoother UI.** Software rendering is slow. Cheap steps first: vsync period in the framebuffer notifications (patch 0101, built, not measured),
  frame statistics, then profiling what burns the CPU.
- **Boot selector.** A way out of iOS without a PC (a key held at boot returns to fastboot), later maybe dual boot with a separate data partition.
- **Remote reset to the bootloader** over the USB network (patch 0100): written, one inconclusive hardware run.
- `mac-address` entries in the device tree (removes 5 s waits in MobileGestalt), a real-time-clock service (removes a 30 s boot wait).

## Later

- **Wi-Fi** (milestone 2): PCIe/PHY bring-up behind EL3/ACPM, firmware handling, an `apple80211` front end for iOS.
- **GPU**: Mali-G78 power domain and clocks sit behind the secure world; research only so far.
- Audio, Bluetooth, camera, sensors, modem. No work started.
- Other Tensor phones (Pixel 6, 6 Pro share the SoC tree): see [docs/PORTING.md](docs/PORTING.md).

## Where help is most useful

- Hardware captures from other Tensor devices (see [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit them).
- Reverse-engineering notes: PCIe/PHY init for the Wi-Fi chip, ACPM channels, Mali power sequencing. Cite your sources.
- Host-side tests and tooling around the existing test loop.

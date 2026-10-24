# Roadmap

What works is in [docs/STATUS.md](docs/STATUS.md) (every row says whether it was *observed on hardware*, *read from source* or is a *guess*).
This page lists what comes next. Order and estimates are guesses, not promises.

## Milestones

1. **iPhone GUI on the Pixel 6a: reached** (2026-10-22). Lock screen, home screen, Settings, touch.
2. **Wi-Fi: in progress** (bring-up from the shim; the chip answers and its chip id was read, no firmware or driver yet). Broadcom BCM4389 on PCIe; plan in [docs/research/20-wifi-stack-plan.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/20-wifi-stack-plan.md), progress in [Coverage](docs/COVERAGE.md).

## Now (demo and release)

- Power-on boot without a PC: iOS image in `boot_a`, stock `boot_b` kept as the way back, slot switched with `fastboot --set-active`.
- Pixel 6a identity in Settings -> About (name, model, serial text), plain lock-screen clock. Built, waiting for a hardware check.

## Next

- **Smoother UI.** Software rendering is slow. Cheap steps first: vsync period in the framebuffer notifications (patch 0101, built, not measured),
  frame statistics, then profiling what burns the CPU.
- **Boot selector.** A way out of iOS without a PC (a key held at boot returns to fastboot), later maybe dual boot with a separate data partition.
- **Remote reset to the bootloader** over the USB network (patch 0100): written, one inconclusive hardware run.
- `mac-address` entries in the device tree (removes 5 s waits in MobileGestalt), a real-time-clock service (removes a 30 s boot wait).

## Later

- **Wi-Fi** (milestone 2): PCIe/PHY bring-up is done as far as reading the chip id; next are firmware and NVRAM download (the firmware stays on the user's own phone, never in git), a PCIe and Broadcom driver built into the kernel, and an `apple80211` front end for iOS.
- **GPU**: the Mali-G78 runs jobs from the shim and from XNU (rail through ACPM, reset works); the userland stack (Mesa panfrost, EAGL shim) builds in CI and is being brought up on the phone. See [docs/COVERAGE.md](docs/COVERAGE.md).
- Audio, Bluetooth, camera, sensors, modem. No drivers yet (the modem partition is never written). `bluetoothd` restarts in a loop on every boot (*observed*, research 35).
- Other Tensor phones (Pixel 6, 6 Pro share the SoC tree): see [docs/PORTING.md](docs/PORTING.md).

## Where help is most useful

- Hardware captures from other Tensor devices (see [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit them).
- Reverse-engineering notes: PCIe/PHY init for the Wi-Fi chip, ACPM channels, Mali power sequencing. Cite your sources.
- Host-side tests and tooling around the existing test loop.

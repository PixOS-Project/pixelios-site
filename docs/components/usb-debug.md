# USB and the debug channel

**Last verified: 2026-11-16.**

## What it is

The USB-C port is the project's lifeline. It carries the boot image in (`fastboot boot`) and the logs out.
Three log channels exist, one per phase:

| Phase | Channel |
|---|---|
| Before the kernel | text on the screen, and a USB serial gadget run by the shim |
| Under XNU and iOS | a USB Ethernet gadget (CDC-ECM); the kernel log streams over UDP |
| Last resort | QR codes on the screen, read by a camera |

## Status

**The USB log has worked on every run since 2026-10-22** (*observed on hardware*); over USB 3 SuperSpeed since 2026-10-29 (run `el2-3-f7`). Device mode only.

## What worked

- **USB serial from the shim** (*observed* 2026-10-21).
- **Kernel log over UDP** through a DWC3 gadget driver in XNU with a CDC-ECM function (patch 0082 and later). The host side is
  `tools/usbnet-log.py`, which needs no root.
- **SuperSpeed.** The phone showed up as USB 2 only until the SuperSpeed PHY path was written (patch 0173; `connected at SuperSpeed 5 Gb/s`, run `el2-3-f7`).
- **A panic message that arrives.** The normal log thread cannot run during a panic, so a polled sender pushes the panic text and a
  backtrace out before the reset (patch 0242).
- **Back-pressure instead of loss.** The log sender waits when the host is slow (patch 0267) and counts what it drops (patch 0179).
- **Remote reset over the USB link** (patch 0100; *observed* 2026-10-24, run `bl1-remote3`), so a test loop needs no button.
- **The QR log** as a channel that needs no host driver at all ([QR log notes](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/QR_LOG.md)).

## What didn't

- **The DMA page must be exactly where measured.** The USB driver takes its DMA memory from a region the bootloader reserved and
  refuses to run if it is not there. A wrong guess here is silent memory corruption.
- **The watchdog was armed only from the USB log thread** at first. A boot whose USB never came up had no watchdog and hung until
  the maintainer restarted it (2026-11-12). Patch 0333 arms it from a timer instead ([Recovery](recovery.md)).
- **Heavy tracing slowed what it traced.** At high volume the log itself changed the timing of the GPU path ([Lessons](../LESSONS.md)).
- **A USB network can fake a Wi-Fi pass.** Test traffic must be pinned to the Wi-Fi interface.

## Untested or never attempted

- **USB host mode** (plugging a device into the phone) and USB-C accessories.
- **USB Power Delivery negotiation.** The charger limit is set directly ([Power](power-charging.md)).
- **Interrupt-driven USB.** The controller is polled about 1000 times a second (*read from source*). It costs about 0.2 % of a core, so it was left for last.
- **The hardware UART** on the sideband pins.
- **USB as a user feature** (file transfer, tethering to the phone's Wi-Fi).

## Ideas if you want to pick it up

- Build this channel **before** you try to reach the home screen. Almost every later fix started from a log line.
- Add a way to pull files from the running phone over the same link; we did it with a small daemon and an allow-list.
- If you have the 1.8 V cable, the UART would give logs from before USB enumerates.

## Where to look

- Patches: 0082 (gs101 USB), 0173 (SuperSpeed), 0091, 0179, 0184, 0267 (log transport), 0242 (panic over USB), 0100 (remote reset), 0081, 0094 (QR log).
- Host tools: [`tools/usbnet-log.py`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/tools/usbnet-log.py), [`tools/qr-log.py`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/tools/qr-log.py), [`tools/xrun`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/tools/xrun).
- Notes: [USB in XNU on gs101](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/09-xnu-usb-gs101.md), [SuperSpeed](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/40-usb-superspeed-gs101.md), [QR throughput](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/24-qr-throughput.md).
- Blueprint stage [13](../BLUEPRINT.md#13-debug-channel).

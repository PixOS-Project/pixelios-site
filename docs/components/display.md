# Display: framebuffer and panel presents

**Last verified: 2026-11-16.**

## What it is

PixOS has **no display driver of its own**. The bootloader leaves a working framebuffer; the shim re-arms the panel's update trigger;
XNU draws into that memory. On the iOS side, the kernel emulates the two services the compositor talks to: the framebuffer service
(IOMobileFramebuffer) and shared surfaces (IOSurface).

A frame reaches the glass in three steps: the compositor finishes a frame and *swaps*; our kernel copies the frame into the
panel memory with the CPU (a *present*); the panel shows it.

## Status

**The iOS UI is on the panel since 2026-10-22** (*observed on hardware*). At the lowest GPU clock, 49.0 drawn presents per second reach the panel against a bar of 50 (run `18e1`, 2026-11-15): **not met yet**.

## What worked

- **The bootloader's framebuffer**: 1080x2400, stride 4320, at the address measured from the live device tree (`board.json`).
- **Re-arming the panel.** The panel is command-mode and the bootloader disables its hardware trigger. One register write, the same
  one postmarketOS uses on this SoC, restores updates (*observed* 2026-10-21).
- **Emulated framebuffer and surface services** that the compositor accepts (the `SweetFramebuffer` and `SweetSurface` code in the patches).
- **A 60 Hz present tick.** Presents were capped at 30 per second by our own timer. At 60 Hz the panel got 46.1 presents/s
  against 26.4 (*observed* 2026-11-14, run `5617`); the copy costs about 2.4 ms per present at the 1352 MHz memory clock.
- **Frame pacing** (patch 0368). Two swaps inside one tick used to reach the panel as one present. Holding the second swap for one
  tick, and presenting as soon as the GPU finishes, raised all panel presents from 49.5 to 49.9/s to 51.2/s (run `18e1`).
- **An independent witness.** The kernel can read the panel memory back and hash it (patches 0276, 0366), and a camera watched the
  screen. Never trust only the code that draws.

## What didn't

- **Drawn presents are still 49.0/s**, one short of the bar. About 1.8 swaps per second are lost when a third swap lands inside the hold (run `18e1`).
- **Silent "success" answers paced frames at 2 to 6 vsyncs.** The compositor waits for framebuffer notifications and a real vsync
  period; stubs that said "ok" made it crawl ([Lessons](../LESSONS.md)).
- **Skipping unchanged copies saved nothing**: in the bench no present was unchanged (patch 0361, run `d9a3`).
- **A camera under room light misjudges frames.** Expose for the panel, or use the kernel read-back.

## Untested or never attempted

- **A real scan-out driver** (letting the display controller flip buffers instead of copying with the CPU). A patch was drafted and reviewed once; it was never booted (*read from the maintainers' notes*; it is not in the public patch series).
- **Vsync from the panel's tearing-effect signal.** Our vsync is a kernel timer.
- **Brightness control.** The panel stays at the bootloader's brightness.
- **Display off, sleep and wake.**
- **Refresh rates other than 60 Hz,** always-on display, HDR.

## Ideas if you want to pick it up

- Queue depth 2 for the swap FIFO is the next experiment for the last frame per second; the maintainer has allowed it for the bar configuration.
- The scan-out flip would remove the CPU copy and its latency. It writes new display-controller registers: review it and prove recovery first.
- Brightness is probably one panel command, and may be the largest single heat saving on the screen (*guess*).

## Where to look

- Patches: 0077, 0101, 0149, 0190 (power, vsync), 0141, 0146, 0148, 0164 (frame statistics), 0289 (framebuffer selectors), 0290, 0297 (surface), 0343 (present gate), 0361 (copy skip), 0366 (hash), 0368 (pacing), 0276 (panel read-back), 0165 (display-controller dump).
- Data: framebuffer keys in [`board.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/device/google/bluejay/board.json).
- Interface facts for iOS 16.7: [IOSurface and IOMobileFramebuffer](../IOS-INTERFACES.md#iosurfaceiomfb).
- Blueprint stage [6](../BLUEPRINT.md#6-display). Related: [GPU](gpu.md).

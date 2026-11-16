# GPU (Mali-G78)

**Last verified: 2026-11-16.**

## What it is

The Pixel 6a has an Arm Mali-G78 MP20. iOS expects an Apple GPU and Metal, which cannot work here. PixOS takes another road:

```text
CoreAnimation (iOS compositor)
  -> its OpenGL ES path, through our EAGL layer
    -> Mesa's Panfrost driver, built for iOS
      -> an IOKit user client -> our Mali driver in XNU (power, MMU, jobs, interrupts)
```

CoreAnimation on iOS 16 tries Metal first, then OpenGL ES 3, then the CPU (*read from source*, our own decompile). We make the second one succeed.

## Status

**The whole UI is drawn by the GPU.** At the lowest GPU clock (150 MHz): rendered 50.6 frames/s pooled, slowest step 48.4 and 48.6, on two 600 s bench boots (*observed on hardware* 2026-11-15, runs `155b`, `8177`). At boost clocks: pooled 59.5, slowest step 51.6 (run `gputest-surffail-b`, 2026-11-11).

## What worked

| Date | Step | Evidence (*observed on hardware*) |
|---|---|---|
| 2026-10-23 | GPU ID read: `0x92020010`. The bootloader leaves the GPU powered and clocked | run `g0` |
| 2026-10-25 | user client opened by the compositor; a Mesa GL context inside it | runs `gputest25`, `gputest18` |
| 2026-10-26 | lock screen drawn through the GPU path | runs `gputest41`, `gputest42` |
| 2026-11-04 | 38 frames/s on the first swipe bench | run `gputest-cced-poll20` |
| 2026-11-09 | slowest navigation step 56.6: job completion moved from polling to interrupts | runs `gputest-nav43`, `gputest-nav44` |
| 2026-11-11 | App Library's blurred backdrop fixed (a 64-entry table in our GL layer never recycled) | runs `gputest-surffail-a` (before), `gputest-surffail-b` (after) |
| 2026-11-15 | 50.6 rendered frames/s at 150 MHz with full Wi-Fi load | runs `155b`, `8177` |

What moved the number at low clocks, in order of size:

- **The memory clock**, not the GPU clock ([Clocks](clocks-dvfs.md)).
- **Dropping a backdrop-scale setting** we had given the compositor: the home-swipe frame went from 18.7 to 14.9 ms of GPU time (one boot, 2026-11-14).
- **Cheaper cache flushes at the end of each job** (boot argument on patch 0210): about +0.5 pooled, one boot each way (runs `c840`, `5236`).
- **A middle CPU clock** for the big cores: 50.9 pooled on its first boot (run `cf53`).

The release configuration also uses a non-blocking flush (our GL layer had made every `glFlush` wait for the GPU; patch 0343 gates the
present in the kernel instead). On its own it showed no gain when first measured (2026-11-13).

## What didn't

- **A blocking flush made "GPU no faster than CPU"** in October. It was a pacing result, not a compute one.
- **GPU memory caching without matching cache maintenance** corrupted output with no fault.
- **Guessing at Apple's compositor.** Most GPU boots in one period tested guesses about CoreAnimation while the bug was in our code ([Lessons](../LESSONS.md)).
- **Raising the GPU clock alone**: 24 to 25 frames/s (one boot, 2026-11-13).
- **Android's GPU user-space library** cannot be reused: it is a vendor binary built for Android's C library, and we ship no vendor binaries (*read from source*).
- **60 frames/s on every step** is not reached: the slowest step at boost clocks is 51.6.
- **Two render defects remain** from the 2026-11-11 list: the search magnifier glyph and a dark band in Spotlight.

## Untested or never attempted

- **Metal.** Every Metal client gets no device. A Metal implementation on this GPU would be its own project.
- **Video decode, camera pipelines, GPU compute.**
- **Powering the GPU down when idle.**
- **The SoC's system-level cache for the GPU.** A read-only query showed the service is alive; whether it is enabled could not be read (*observed* 2026-11-14, patch 0363).
- **Other Mali models.** Only this one was run.

## Ideas if you want to pick it up

- The host replay is the best tool we built: captured GPU frames are replayed on a PC software renderer and compared pixel by pixel
  with the phone. Start there for any render defect.
- Two jobs queued per GPU slot (the hardware supports it) would shrink the gaps between jobs. It is a new hardware write.
- On another phone with a Mali GPU, most of this stack should carry over. Find out first **who powers the GPU**: here the shader rail is a firmware request, not a register.

## Where to look

- Kernel driver: patches 0102 to 0105, 0107, 0111 (bring-up, user client), 0227, 0240 (job queue), 0266 (cache), 0272 (interrupts), 0210, 0364, 0365 (tuning and latency counters).
- Shim: `shim/gpupower.c`, `shim/gpurailon.c`, `shim/gpuclk.c`, `shim/gpujob.c` in [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel/tree/main/shim).
- Userland: [`tools/mesa-patches/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/tools/mesa-patches), [`tools/sweetgl-eagl/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/tools/sweetgl-eagl) (EAGL layer, with a design note), [`tools/sweetgl-mali/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/tools/sweetgl-mali), [`tools/sweetgl-fcap/`](https://github.com/PixOS-Project/pixelios-userland/tree/main/tools/sweetgl-fcap) (capture and replay).
- Notes: [first GPU probe](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/27-gpu-g0-result.md), [kbase port checklist](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/31-kbase-port-checklist.md), [Mesa Panfrost on iOS](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/32-mesa-panfrost-ios-plan.md), [what CoreAnimation needs from GLES](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/33-ca-renderer-and-gles-requirements.md), [GPU interrupts](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/35-gpu-irq-path.md).
- Bench tools: `tools/pixnav.c`, `tools/fps-wholerun`, `tools/gpu-fps-bench` in pixelios-kernel.
- Blueprint stage [7](../BLUEPRINT.md#7-gpu). Milestones: [GPU](../milestones/gpu.md), [low clocks](../milestones/all-on-low-clock.md).

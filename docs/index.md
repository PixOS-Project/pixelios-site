# PixOS

**Apple's XNU kernel and the iOS 16.7 userland on a Google Pixel 6a (Tensor G1)**, as a research port, plus the method and the
blueprint we used, written so that any HackiOS project can reuse them on another device or another iOS build.

A small bare-metal shim is loaded with a temporary `fastboot boot` image, brings up what XNU needs on the Pixel (UFS storage,
memory map, a device tree for XNU) and jumps into a patched XNU kernel; the iOS root lives in the `userdata` partition.
Inspired by, and built on, [ios-sweet](https://github.com/dipa-studio/ios-sweet).

**Last verified: 2026-11-15.**

!!! info "AI-driven development"
    Most of this project is written by AI coding agents, directed by a human who runs everything on the
    hardware and approves each destructive step. Read the code before you trust it:
    [how the project is built](AI_DEVELOPMENT.md).

!!! warning "Research code"
    Now working, observed on hardware (run labels on [Status](STATUS.md)): **GPU acceleration, Wi-Fi with real internet, Bluetooth, and touch.** GPU: smooth UI at about 50 fps with the GPU at its lowest clock (150 MHz) (rendered 50.6 / 50.6 pooled on two boots, runs `155b`, `8177`; drawn presents reaching the panel 49.0/s, run `18e1`, so the 50/s bar is not met yet). Wi-Fi: joins WPA2 networks and gets real internet (DNS, HTTPS; pixnet 9/9), about 190-285 Mbit/s download. Bluetooth: pairs and connects devices (tested with a headset). Touch: a real finger works. **No audio playback yet.** This config runs 5 of the 8 CPU cores. [Release note 2026-11-15](RELEASE-2026-11-15.md). Disclaimer: AI was used heavily to make this run on Pixel 6a; it is based on ios-sweet.
    Use a spare phone and read
    [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md) first.

## Start here

| I want to... | Go to |
|---|---|
| see what works today | [Status](STATUS.md) (features and known issues), [Release note 2026-11-15](RELEASE-2026-11-15.md) and [Milestones](MILESTONES.md) |
| port XNU + iOS to **my own device** or another iOS build | [Porting blueprint](BLUEPRINT.md), then [Method](METHOD.md) |
| have an LLM agent start a port or continue PixOS | [LLM prompts](PROMPTS.md): copy-paste blocks |
| learn from what went wrong | [Lessons](LESSONS.md) |
| help | [Contributing](https://github.com/PixOS-Project/pixelios-site/blob/main/CONTRIBUTING.md), [Roadmap](https://github.com/PixOS-Project/pixelios-site/blob/main/ROADMAP.md) |
| bring up **another Pixel** with the same SoC | [Adding a device](PORTING.md) |
| build and boot the shim | [Build](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/BUILD.md) and [Automation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md) |
| build the iOS root image without sudo | [Rootless build](https://github.com/PixOS-Project/pixelios-userland/blob/main/docs/ROOTLESS_BUILD.md) |
| find my way around the code | [Repository map](MAP.md) |
| read the original plan and how it held up | [Plan](PLAN.md), [Case study](CASE_STUDY.md) |
| see the hardware captures and research | [Devices](devices/index.md), [SoCs](socs/index.md) |
| credit and licensing | [Credits](CREDITS.md) |

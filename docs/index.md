# PixeliOS

**Apple's XNU kernel and iOS 16 on a Google Pixel 6a (Tensor G1)**, as a research port with a
device-tree layout that other Pixels can plug into.

A small bare-metal shim is loaded with a temporary `fastboot boot` image, brings up what XNU needs
on the Pixel (UFS storage, memory map, a device tree for XNU) and jumps into a patched XNU kernel.
Inspired by, and built on, [ios-sweet](https://github.com/dipa-studio/ios-sweet).

!!! info "AI-driven development"
    Most of this project is written by AI coding agents, directed by a human who runs everything on the
    hardware and approves each destructive step. Read the code before you trust it:
    [how the project is built](AI_DEVELOPMENT.md).

!!! warning "Research code"
    XNU boots on the Pixel, mounts the iOS root, runs launchd and reaches the iOS lock screen and
    home screen, and touch works (*observed on hardware*, 2026-10-22). The UI is slow; Wi-Fi, GPU, audio, camera and the modem do not work yet.
    Read [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md) before touching a phone.

## Start here

| I want to... | Go to |
|---|---|
| see what works today | [Status](STATUS.md) |
| build and boot the shim | [Build](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/BUILD.md), then the [README quick start](https://github.com/PixOS-Project/pixelios-kernel#quick-start) |
| read the log without a serial cable | [QR log channel](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/QR_LOG.md) |
| drive the hardware test loop (`xrun`, `ci-kernel`) | [Automation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md) |
| build the iOS root image without sudo | [Rootless build](https://github.com/PixOS-Project/pixelios-userland/blob/main/docs/ROOTLESS_BUILD.md) |
| bring up **another Pixel** | [Adding a device](PORTING.md) |
| find my way around the repository | [Repository map](MAP.md) |
| understand the plan and gates | [Plan](PLAN.md), [Case study](CASE_STUDY.md) |
| see the hardware captures and research | [Devices](devices/index.md), [SoCs](socs/index.md), [Research](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/01-boot-path.md) |
| know how the project is made | [AI-driven development](AI_DEVELOPMENT.md) |
| credit and licensing | [Credits](CREDITS.md) |

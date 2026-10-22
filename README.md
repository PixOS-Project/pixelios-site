# PixeliOS: documentation site

Documentation for the PixeliOS port (Apple XNU and iOS 16 on a Google Pixel 6a, Tensor G1): status, plan, milestones,
the case study, the porting guide, the code map, credits and the AI-development note. Published at
<https://pixos-project.github.io/pixelios-site/> (guess: the final address may change when the split is published).

> **AI-driven development.** This project is written mostly by AI coding agents under the direction of a human maintainer, who owns the phone
> and decides what is flashed or published. Read the code before you trust it. Details: [docs/AI_DEVELOPMENT.md](docs/AI_DEVELOPMENT.md).

Status (*observed on hardware*, 2026-10-22): XNU boots on the Pixel, launchd runs, the iOS lock screen and home screen appear
and touch works; the UI is slow, and Wi-Fi, GPU, audio, camera and modem are still to do. See `docs/STATUS.md`.

Code lives in the other repositories:
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (pre-kernel shim, XNU patches, SoC and device trees, tools) and
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the iOS root recipe).

`tools/build-site.py` assembles the MkDocs site. It reads `soc/` and `device/` pages from the kernel repository, so run it in a
checkout that has both (*guess*: not yet verified from a standalone clone of this repository).

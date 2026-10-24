# PixeliOS: documentation site

Documentation for the PixeliOS port (Apple XNU and iOS 16 on a Google Pixel 6a, Tensor G1): status, plan, milestones,
the case study, the porting guide, the code map, credits and the AI-development note. Published at
<https://pixos-project.github.io/pixelios-site/> (live, built by the Pages workflow on every push).

> **AI-driven development.** This project is written mostly by AI coding agents under the direction of a human maintainer, who owns the phone
> and decides what is flashed or published. Read the code before you trust it. Details: [docs/AI_DEVELOPMENT.md](docs/AI_DEVELOPMENT.md).

Status (*observed on hardware*, 2026-10-22 to 2026-10-24): XNU boots on the Pixel, launchd runs, the iOS lock screen and home screen appear
and touch works; the UI is slow. Wi-Fi bring-up has reached the BCM4389 chip id over PCIe and the GPU executes jobs; no Wi-Fi traffic or GPU rendering yet. Audio, camera and modem are still to do. See `docs/STATUS.md`.

Code lives in the other repositories:
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (pre-kernel shim, XNU patches, SoC and device trees, tools) and
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the iOS root recipe).

`tools/build-site.py` assembles the MkDocs site. It reads `soc/` and `device/` pages from the kernel repository, so it needs a
checkout of both side by side (see [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)); the Pages workflow does exactly that, and its
`mkdocs build --strict` and deployment succeeded on 2026-10-24 (*observed*, GitHub Actions).

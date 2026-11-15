# PixOS: documentation site

Documentation for PixOS (Apple XNU and the iOS 16.7 userland on a Google Pixel 6a, Tensor G1): status and features, milestones,
a device- and iOS-version-agnostic porting blueprint, the working method, copy-paste LLM prompts, the lessons we learned the hard way,
the case study, the code map and credits. Published at <https://pixos-project.github.io/pixelios-site/> by the Pages workflow on every push.

**Last verified: 2026-11-15.**

> **AI-driven development.** This project is written mostly by AI coding agents under the direction of a human maintainer, who owns the phone
> and decides what is flashed or published. Read the code before you trust it. Details: [docs/AI_DEVELOPMENT.md](docs/AI_DEVELOPMENT.md).

Now working, observed on hardware (run labels on [Status](docs/STATUS.md)): **GPU acceleration, Wi-Fi with real internet, Bluetooth, and touch.** GPU: smooth UI at about 50 fps with the GPU at its lowest clock (150 MHz) (rendered 50.6 / 50.6 pooled on two boots, runs `155b`, `8177`; drawn presents reaching the panel 49.0/s, run `18e1`, so the 50/s bar is not met yet). Wi-Fi: joins WPA2 networks and gets real internet (DNS, HTTPS; pixnet 9/9), about 190-285 Mbit/s download. Bluetooth: pairs and connects devices (tested with a headset). Touch: a real finger works. **No audio playback yet.** This config runs 5 of the 8 CPU cores. [Release note 2026-11-15](docs/RELEASE-2026-11-15.md). Disclaimer: AI was used heavily to make this run on Pixel 6a; it is based on ios-sweet.

Code lives in the other repositories:
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (pre-kernel shim, XNU patches, SoC and device trees, tools) and
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the iOS root recipe and our userland pieces).

## How the site is made

- Pages are Markdown in `docs/`. Each carries a `Last verified: YYYY-MM-DD` line and names its sources.
- The feature list and the milestone ladder are generated: the maintainers' export writes `data/progress.json` from their run logs, and
  `tools/render_progress.py` renders the tables into `docs/STATUS.md` and `docs/MILESTONES.md`. Do not edit inside the generated blocks.
- `tools/check-site.py` checks links into the other repositories, evidence on "works" rows, generated-table drift, stale claims, secrets and
  the age of every page's `Last verified` line (a warning at 14 days; the weekly CI run turns it into an issue).
- `tools/build-site.py` assembles the MkDocs site; it reads `soc/` and `device/` pages from the kernel repository, so it needs a
  checkout of both side by side (see [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)).

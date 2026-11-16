# PixOS: documentation site

Documentation for PixOS (Apple XNU and the iOS 16.7 userland on a Google Pixel 6a, Tensor G1).
Published at <https://pixos-project.github.io/pixelios-site/> by the Pages workflow on every push.

**Last verified: 2026-11-16.**

| Section | What is in it |
|---|---|
| [Home](docs/index.md), [Status](docs/STATUS.md), [Try it](docs/TRY.md), [Release note](docs/RELEASE-2026-11-15.md) | what works today, in one glance and in full; how to run it |
| [Milestones](docs/MILESTONES.md) | one page per milestone: goal, what was done, how it was proven, what it unlocked, dead ends |
| [Components](docs/components/index.md) | one page per hardware block: what worked, what did not, what was never tried, ideas, where to look |
| [Blueprint](docs/BLUEPRINT.md), [Method](docs/METHOD.md), [Lessons](docs/LESSONS.md), [LLM prompts](docs/PROMPTS.md), [iOS interface notes](docs/IOS-INTERFACES.md) | for porting to another device or iOS build |
| [Case study](docs/CASE_STUDY.md), [Plan](docs/PLAN.md), [AI-driven development](docs/AI_DEVELOPMENT.md) | the story and how the project is made |
| [Repository map](docs/MAP.md), [Credits](docs/CREDITS.md) | reference, credits and licences |

> **AI-driven development.** This project is written mostly by AI coding agents under the direction of a human maintainer, who owns the phone
> and decides what is flashed or published. Read the code before you trust it. Details: [docs/AI_DEVELOPMENT.md](docs/AI_DEVELOPMENT.md).

Now working, observed on hardware (run labels on [Status](docs/STATUS.md)): **GPU acceleration, Wi-Fi with real internet, Bluetooth, and touch.** GPU: smooth UI at about 50 fps with the GPU at its lowest clock (150 MHz) (rendered 50.6 / 50.6 pooled on two boots, runs `155b`, `8177`; drawn presents reaching the panel 49.0/s, run `18e1`, so the 50/s bar is not met yet). Wi-Fi: joins WPA2 networks and gets real internet (DNS, HTTPS; pixnet 9/9), about 190-285 Mbit/s download. Bluetooth: pairs and connects devices (tested with a headset). Touch: a real finger works. **No audio playback yet.** This config runs 5 of the 8 CPU cores. [Release note 2026-11-15](docs/RELEASE-2026-11-15.md). Disclaimer: AI was used heavily to make this run on Pixel 6a; it is based on ios-sweet.

Code lives in the other repositories:
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (pre-kernel shim, XNU patches, SoC and device trees, tools) and
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the iOS root recipe and our userland pieces).

## How the site is made

- Pages are Markdown in `docs/`, with one page per milestone in `docs/milestones/` and one per component in `docs/components/`.
  Each carries a `Last verified: YYYY-MM-DD` line and names its sources. Component and milestone pages keep their fixed headings.
- The feature list and the milestone ladder are generated: the maintainers' export writes `data/progress.json` from their run logs, and
  `tools/render_progress.py` renders the tables into `docs/STATUS.md` and `docs/MILESTONES.md`. Do not edit inside the generated blocks.
- `tools/check-site.py` checks links into the other repositories, evidence on "works" rows, generated-table drift, stale claims, secrets and
  the age of every page's `Last verified` line (a warning at 14 days; the weekly CI run turns it into an issue). It covers every page under `docs/`.
- `tools/build-site.py` assembles the MkDocs site and its navigation; it reads `soc/` and `device/` pages from the kernel repository
  (linked into this checkout, or named by `PIXOS_KERNEL_DIR`; see [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)).

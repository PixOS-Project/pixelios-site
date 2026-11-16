# Requirements: building this site (pixelios-site)

**Last verified: 2026-11-16.**

Python 3.12 and `pip install "mkdocs<2" mkdocs-material`. `tools/build-site.py` generates the device and SoC pages from the `soc/` and `device/` trees of
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel): check the two repositories out side by side and link `soc` and `device` into this
checkout (the Pages workflow `.github/workflows/pages.yml` does exactly that), or set `PIXOS_KERNEL_DIR` to the kernel checkout. Without
either, the build warns and the Devices and SoCs sections stay empty.

New pages: a file in `docs/milestones/` or `docs/components/` appears in the navigation by itself (the order lists are `MILESTONE_ORDER` and
`COMPONENT_ORDER` in `tools/build-site.py`; unlisted files come last by name). Any other new page in `docs/` must be added to a section in that script.

*Observed* (2026-10-24): the Pages workflow builds with `mkdocs build --strict` and deploys to <https://pixos-project.github.io/pixelios-site/>
(GitHub Actions run 40041837508, success). To check a change locally, run the same three commands as the workflow
(`python3 tools/build-site.py`, then `mkdocs build --strict -f .site/mkdocs.yml`).

## Quality gate

`tools/check-site.py` (TP-019) runs in the Pages workflow before the build, on pull requests, and weekly (a failing weekly run opens an issue).
It checks that links into the kernel and userland repositories resolve on `main`, that "works" rows in `STATUS.md` carry a date or evidence,
that `STATUS.md` "Last update" is not more than 7 days behind `data/progress.json` (the export of the milestone numbers), that the generated tables in `STATUS.md` and `MILESTONES.md` match that file (`python3 tools/render_progress.py --check`), that no page still carries a claim the export contradicts (for example "no Wi-Fi driver" once a scan is recorded), that no secret or local path is present, and that every page under `docs/` (including `docs/milestones/` and `docs/components/`) carries a `Last verified: YYYY-MM-DD` line no older than 14 days (a warning on deploys; the weekly run fails on it and opens an issue).
Run it locally with the repositories side by side: `python3 -I tools/check-site.py` (self-test: `python3 -I tools/test_check_site.py`).
It flags drift only; whether a claim is true still needs a hardware result.

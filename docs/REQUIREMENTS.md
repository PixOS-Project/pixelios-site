# Requirements: building this site (pixelios-site)

Python 3.12 and `pip install "mkdocs<2" mkdocs-material`. `tools/build-site.py` generates the device and SoC pages from the `soc/` and `device/` trees of
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel): check the two repositories out side by side and link `soc` and `device` into this
checkout (the Pages workflow `.github/workflows/pages.yml` does exactly that).

*Observed* (2026-10-24): the Pages workflow builds with `mkdocs build --strict` and deploys to <https://pixos-project.github.io/pixelios-site/>
(GitHub Actions run 40041837508, success). To check a change locally, run the same three commands as the workflow
(`python3 tools/build-site.py`, then `mkdocs build --strict -f .site/mkdocs.yml`).

## Quality gate

`tools/check-site.py` (TP-019) runs in the Pages workflow before the build, on pull requests, and weekly (a failing weekly run opens an issue).
It checks that links into the kernel and userland repositories resolve on `main`, that "works" rows in `STATUS.md` carry a date or evidence,
that `STATUS.md` "Last update" is not more than 7 days behind the kernel `docs/WIFI-COVERAGE.md`, and that no secret or local path is present.
Run it locally with the repositories side by side: `python3 -I tools/check-site.py` (self-test: `python3 -I tools/test_check_site.py`).
It flags drift only; whether a claim is true still needs a hardware result.

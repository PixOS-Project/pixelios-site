# Requirements: building this site (pixelios-site)

Python 3.12 and `pip install "mkdocs<2" mkdocs-material`. `tools/build-site.py` generates the device and SoC pages from the `soc/` and `device/` trees of
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel): check the two repositories out side by side and link `soc` and `device` into this
checkout (the Pages workflow `.github/workflows/pages.yml` does exactly that).

*Observed* (2026-10-24): the Pages workflow builds with `mkdocs build --strict` and deploys to <https://pixos-project.github.io/pixelios-site/>
(GitHub Actions run 40041837508, success). To check a change locally, run the same three commands as the workflow
(`python3 tools/build-site.py`, then `mkdocs build --strict -f .site/mkdocs.yml`).

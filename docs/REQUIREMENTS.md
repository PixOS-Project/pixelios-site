# Requirements: building this site (pixelios-site)

Python 3.12 and `pip install "mkdocs<2" mkdocs-material`. `tools/build-site.py` generates the device and SoC pages from the `soc/` and `device/` trees of
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel): check the two repositories out side by side and link `soc` and `device` into this
checkout (the Pages workflow `.github/workflows/pages.yml` does exactly that).

*Observed* (2026-10-22): `python3 tools/build-site.py` on the generated site tree plus the kernel tree's `soc/` and `device/` produced 16 pages (6 generated).
*Not run*: the final `mkdocs build --strict` (mkdocs was not installed on the test machine) and the Pages deployment.

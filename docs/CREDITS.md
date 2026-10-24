# Credits and licensing

PixeliOS stands on other people's work.

## Inspiration and base: ios-sweet

[ios-sweet](https://github.com/dipa-studio/ios-sweet) by dipa-studio ported XNU and iOS 16 to a
Redmi Note 10 Pro ("sweet"). It is the reason this project exists: the whole approach (a small
bare-metal shim, a patched XNU built in CI, a device tree handed over by the shim, an HFS+ iOS
root in `userdata`) is theirs.

ios-sweet had no license file when we started (pinned commit `11da58b`), so its files were not
redistributed: `tools/setup-upstream.sh` downloads that commit from its own repository and
applies our changes, which are stored as diffs in [`upstream-patches/`](https://github.com/PixOS-Project/pixelios-kernel/tree/main/upstream-patches).
**ios-sweet is now MIT-licensed** (copyright dipa-studio; checked on GitHub, 2026-10-24), so that arrangement can be simplified:
the kernel repository is being changed to carry files derived from ios-sweet directly, with its MIT notice in `LICENSE-ios-sweet.txt`.
Until that change is published, the fetch-and-patch flow above still works. Please thank them, and star their repository.

## Third-party code in this repository

| What | Where | License |
|---|---|---|
| QR Code generator library by Project Nayuki | `qrlog/qrcodegen.[ch]` | MIT |
| Our patches to Apple's XNU | `xnu/patches/` (ours) and the fetched series | Apple Public Source License 2.0 (derivative of XNU); Apple's source is not included |
| blacktop/darwin-xnu-build | fetched in CI | MIT |
| Linux kernel and Google's Tensor kernel sources, Broadcom `dhd` driver | read as references for register values and sequences (no code copied) | GPL-2.0 / see each source |
| AOSP `mkbootimg.py`, `avbtool.py` | fetched by `tools/fetch-android-tools.sh` | Apache-2.0 |

Register values and sequences for the Tensor G1 UFS host and PHY, and for the PCIe, Wi-Fi and GPU bring-up, were derived from the Linux
kernel sources (`ufs-exynos.c`, `phy-gs101-ufs.c`, the Pixel kernel's PCIe code; GPL-2.0), the Arm Mali kbase driver and the Broadcom `dhd` driver, and are documented in
`soc/google/gs101/docs/` and `docs/research/` of the kernel repository, each with its source cited. No such source code is copied.

## Not affiliated

This project is not affiliated with, endorsed by, or sponsored by Apple Inc. or Google LLC.
"iOS", "iPhone", "Apple" and "XNU" are trademarks of Apple Inc.; "Pixel" and "Tensor" are
trademarks of Google LLC. No Apple firmware, device trees, or decrypted binaries are distributed;
you must obtain the iOS restore image yourself from Apple.

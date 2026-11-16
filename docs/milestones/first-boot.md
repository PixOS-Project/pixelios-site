# First boot: shim, XNU and the root file system

**Last verified: 2026-11-16.** Milestone M0 · 2026-10-20 to 2026-10-21 · **done**

## Goal

Get our own code running on an unlocked Pixel 6a without flashing anything, then XNU, then XNU with the iOS root mounted and
`launchd` running. Each step had a gate that had to pass on the phone before the next one started.

## What was done

1. **A plan from desk research** (2026-10-20), before the first boot: how ios-sweet works and how each part maps to the Pixel ([case study](../CASE_STUDY.md)).
2. **A probe shim.** A bare-metal image loaded with `fastboot boot` that reports what the bootloader leaves behind: exception level,
   cores, page-size support, timer, watchdogs, memory map.
3. **Storage, read-only.** The shim re-initialises UFS, switches the link to high speed, and dumps part of `userdata` over USB for
   comparison with Android's view.
4. **XNU with the inherited patch stack**, a device tree built from data files, booted with one CPU.
5. **A UFS driver in XNU** and the iOS root, built from the user's IPSW and flashed to `userdata`.

## How it was proven

All *observed on hardware*.

| Gate | Result | Evidence |
|---|---|---|
| Shim runs under `fastboot boot`, nothing flashed | passed 2026-10-21 | `device/google/bluejay/docs/GATE0_RESULTS.md` |
| UFS reads match Android byte for byte; HS-G4 link: a 4 MiB read went from 8036 ms to 675 ms | passed 2026-10-21 | [HS-G4 review](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/reviews/hs-g4-review-1.md), `device/google/bluejay/hardware/udump-1mib-2026-10-21.txt` |
| XNU draws kernel text and stops at "waiting for root device" | passed 2026-10-21 | first XNU boot |
| XNU mounts the HFS+ root read-write; `launchd` and about 60 daemons run | passed 2026-10-21 | first root mount; every boot since |

## What it unlocked

Everything. From here on the work was iOS userland and one hardware block at a time. It also set the safety pattern the project
kept: RAM boots only, `userdata` as the single partition ever written, and a build-time audit that rejects any storage write in the shim.

## Dead ends

- **An unsigned boot image.** `fastboot boot` accepted it and silently did not run it. An AVB hash footer with a throwaway key fixed it.
- **"An IOMMU is blocking storage DMA."** A guess, and wrong. The bootloader had powered the UFS device down; a device reset and a
  full link start-up fixed it. We found it by reading what the bootloader does at shutdown.
- **A read-only root mount.** It fails at journal start; the root must be mounted read-write.
- **Reading a RAM log back after a reset.** The bootloader rewrites that RAM.

Components: [Boot chain](../components/boot-chain.md), [Storage](../components/storage-ufs.md). Next: [SpringBoard](springboard.md).

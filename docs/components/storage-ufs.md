# Storage (UFS) and the root file system

**Last verified: 2026-11-16.**

## What it is

The Pixel's storage is UFS behind a Samsung (Exynos) host controller. Two pieces of our code talk to it:

- the **shim**, read-only, to prove the storage works before XNU runs;
- an **XNU block driver**, which mounts the iOS root (an HFS+ image in `userdata`) read-write.

## Status

**The iOS root has mounted read-write on every boot since 2026-10-21** (*observed on hardware*; newest: runs `155b`, `8177`, 2026-11-15). One command at a time; completion by interrupt since 2026-11-14 (run `c1f4`).

## What worked

- **Cold re-init.** The bootloader powers the UFS device down before it hands over. The shim resets the device and runs a full
  link start-up (*observed* 2026-10-21; found by reading what the bootloader does at shutdown).
- **High-speed link.** Switching to HS-G4 took a 4 MiB read from 8036 ms to 675 ms with identical data
  (*observed* 2026-10-21, [review](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/reviews/hs-g4-review-1.md)).
- **A read-only proof first.** A CRC-checked dump of `userdata` over USB matched Android's view before any write existed.
- **HFS+ root, read-write** from `userdata` (patch 0080 and the HFS patches). A read-only mount fails at journal start.
- **Completion by interrupt** (patch 0354): 133255 interrupts, none spurious (run `c1f4`, 2026-11-14).
- **iOS told the disk is solid-state** (patch 0358; the kernel answered the query, run `ef4a`, 2026-11-14).
- **No re-flash for small changes.** A RAM-disk overlay copies changed files into the mounted root at boot (patch 0117),
  so `userdata` is flashed only when the root image itself changes.

## What didn't

- **The first diagnosis was wrong.** Commands timed out and we guessed an IOMMU was blocking DMA. The cause was the powered-down
  device ([Lessons](../LESSONS.md)).
- **Neither the interrupt nor the solid-state answer changed the frame rate** (runs `c1f4`, `ef4a`).
- **An unknown writer.** About 593 MB were written in a 10 minute bench; we do not know by whom (*observed* 2026-11-15, run `d9a3`).

## Untested or never attempted

- **Command queueing.** The host has 32 slots; the driver uses one at a time (*read from source*).
- **File data protection.** The HFS code is built without content protection; protection classes answer "none" (patch 0181, *read from source*).
- **APFS.** The root is HFS+, as in ios-sweet, not APFS as on an iPhone.
- **Power saving of the link** (clock gating, hibernate), TRIM, and the controller's inline encryption.
- **Writes from the shim.** Forbidden by design: a build-time audit rejects any write path in pre-kernel code.

## Ideas if you want to pick it up

- Queue depth above one, with completions from the existing interrupt handler. Page-in latency during app launch is the number to watch.
- Name the 593 MB writer with a per-process write counter before optimising anything.
- A root over USB (read-only, with a copy-on-write layer) was started to make test loops faster; see the notes below.

## Where to look

- Shim: [`soc/google/gs101/shim/`](https://github.com/PixOS-Project/pixelios-kernel/tree/main/soc/google/gs101/shim) (`ufsinit.c`, PHY tables), `shim/ufs.c`, `shim/udump.c`.
- Patches: 0080 (UFS driver), 0151, 0171, 0181 (HFS), 0354 (interrupt), 0358 (solid-state answer), 0117, 0154, 0280 (overlay), 0150, 0157, 0158 (root over USB).
- Notes: [UFS bring-up](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/docs/07-gs101-ufs-bringup.md), [what the bootloader does at shutdown](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/docs/08-abl-ufs-shutdown.md), [overlay without re-flash](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/41-dev-overlay-without-reflash.md), [root over USB](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/44-usbroot-readonly.md).
- Root image recipe: [pixelios-userland](https://github.com/PixOS-Project/pixelios-userland).
- Blueprint stage [4](../BLUEPRINT.md#4-storage-and-root-mount-from-the-data-partition).

# iOS userland: launchd, SpringBoard, apps

**Last verified: 2026-11-16.**

## What it is

The iOS side is the unmodified iPhone X userland of iOS 16.7, taken from an IPSW the user downloads. Three things make it start on a Pixel:

- a **root recipe** (scripts only) that assembles the file system, drops jobs that cannot work without iPhone hardware, and skips the setup assistant;
- **kernel stand-ins** for services iOS expects from an iPhone kernel (code-signing policy, key store, sandbox paths, HID, a network-stack stub);
- our own small **iOS-side programs** for testing (ping, throughput, navigation, a Bluetooth test client).

## Status

**Boots to the lock screen and home screen; Settings, App Library, Spotlight and MobileSafari run** (*observed on hardware*: 19 of 19 captured screens match their references, run `gputest-surffail-b`, 2026-11-11; MobileSafari launched 6 times on the demo boot, job 1308, 2026-11-15). Page loads in Safari were not logged.

## What worked

- **launchd and about 60 daemons, then SpringBoard** (*observed* 2026-10-21/22).
- **Settings > About.** It hung because a daemon waited 300 s for a network-stack service this kernel did not have. A stand-in fixed it (patch 0099, run `about4`, 2026-10-22).
- **Keychain writes** (run `kc-s1`, 2026-11-03), needed before Bluetooth and Wi-Fi could store anything.
- **The right screen class.** One of our framebuffer answers returned a float where iOS reads an integer; SpringBoard then treated the
  screen as an unknown device and every home swipe sprang back. Patch 0316 fixed it.
- **A real calendar.** The clock started at 1970 until a boot argument carried the host's time (patch 0345). TLS needs a correct date.
- **A leak in our GL layer.** The compositor's memory grew by 4 to 5 MB/s under load until the UI stalled at about 3.3 GB.
  After the fix it stays flat between 217 and 320 MB (*observed* 2026-11-13, runs `c498`, `973d`, `b042`).
- **Used by hand.** On the demo boot the maintainer unlocked, opened apps and paired a headset with a finger (job 1308).

## What didn't

- **`lskdd` restarts about once a second** for the whole boot. Cause not found; not disabled.
- **`coreduetd` ran away** at 0.7 to 0.9 of a core in the runs of 2026-11-13, then stopped without a code change (2026-11-14). Cause unconfirmed.
  One boot without it changed no frame rate (run `c68b`).
- **Anything that needs Metal fails.** Apple's Metal targets Apple GPUs; there is no Metal device here, so Metal clients get none
  (*read from source*, our own decompile notes). The UI works because CoreAnimation falls back to OpenGL ES ([GPU](gpu.md)).
- **Some lock-screen poster and widget extensions are killed at check-in** (seen 2026-11-11; not re-checked).
- **Rendering defects:** the magnifier glyph in search fields is missing and Spotlight shows a dark band under the status bar (2026-11-11 list, not re-checked).

## Untested or never attempted

- App Store, iCloud sign-in, iMessage, FaceTime, push notifications, Apple Pay.
- Video playback, the camera app, anything with sound.
- Installing third-party apps.
- The setup assistant (it is skipped).
- Any iOS build other than 16.7 for the iPhone X. iOS 17 and later for iPhones need pointer authentication, which these cores lack.

## Ideas if you want to pick it up

- A QEMU lab booted this same root to SpringBoard on a PC (host only, 2026-11-11, feasibility study). Userland work that needs no
  Pixel hardware could move there, and it would let people without the phone help.
- Find why `lskdd` exits. The kernel can already log every process exit with its status (patch 0362).
- Every dropped job and every stand-in is a missing feature. The `GAP` lines in a boot log are the to-do list.

## Where to look

- Root recipe: [pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (`tools/build-ios-root-rootless.sh`, `tools/sweet-root-tweaks.py`).
- Patches: 0085, 0119, 0126, 0291 (sandbox), 0099 (network-stack stand-in), 0106 (code-signing policy), 0208 (key store), 0123, 0345 (clock), 0316 (screen class), 0362 (exit log).
- Notes: [SpringBoard stall](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/11-springboard-stall-bluejay.md), [daemon exits at boot](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/35-boot-daemon-exits.md), [iOS 16.7 interface notes](../IOS-INTERFACES.md).
- Blueprint stage [5](../BLUEPRINT.md#5-launchd-and-the-daemons-up-to-springboard). Milestone: [SpringBoard](../milestones/springboard.md).

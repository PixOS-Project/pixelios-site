# Hands-free test loop

**Last verified: 2026-11-16.** Milestone M7 · 2026-10-22 to 2026-11-09 · **done**

## Goal

One command builds an image, boots the phone, collects the log and prints a verdict, and the phone is back in fastboot at the
end **whatever happened**: normal end, kernel panic, or a hang. No button presses.

This is tooling, but it decided the project's speed. With one test phone, every boot that needs a hand on it is a boot nobody takes at night.

## What was done

- **A one-cycle run tool** (`tools/xrun`): build, `fastboot boot`, read the USB log, check expected lines, wait for the reset, print `RESULT:`.
- **Reset from software**: into the bootloader through the reboot-mode register; remotely over the USB link (run `bl1-remote3`, 2026-10-24).
- **Panic to fastboot**, with the panic text sent to the host first.
- **A hardware watchdog** re-armed and petted by the kernel, and a **stall detector** that turns a silent hang into a panic.
- **An overlay for the root.** Changed files are copied into the mounted root from a RAM disk at boot, so a test does not need a re-flash.
- **A gate before merges**: host tests, a patch-stack check, and the storage-write audit in one command.

## How it was proven

All *observed on hardware*.

| Claim | Evidence |
|---|---|
| A software-driven loop needs no button presses | since 2026-10-22; reset over USB since 2026-10-24, run `bl1-remote3` |
| A kernel panic returns the phone to fastboot | run `20261107T145123Z-panic-self-recover`, 2026-11-07 |
| A deliberate hang is ended by the watchdog | run `ar-c-wdttest`, 2026-11-09 |
| Files reach the root without a flash | since run `gputest29-dev1-hand`, 2026-10-25 |

## What it unlocked

Volume. The GPU, Wi-Fi and Bluetooth streams each took dozens to hundreds of boots; the numbered runs you see across this site come
out of this loop. It also allowed several work streams to share one phone: each run takes a lock, boots, and parks the phone in fastboot.

## Dead ends

- **Resets landed in Android recovery**, not fastboot, because the bootloader decides by reset cause. The host tool now moves the phone on.
- **A watchdog armed only by the USB thread.** A panic on a boot without USB hung the phone until the maintainer restarted it (2026-11-12). The watchdog is now armed from a timer (patch 0333).
- **Process on top of the loop.** Tickets, run plans before every boot and formal gates before boots were added one by one, then
  retired on 2026-11-08/09: in their last 24 hours, 66 boots moved one number ([Lessons](../LESSONS.md)).
- **The on-screen QR log** was the first log channel and worked, but a camera in the loop is fragile. The USB log replaced it; QR stays as the fallback.

Components: [Recovery](../components/recovery.md), [USB and debug channel](../components/usb-debug.md). How we use the loop: [Method](../METHOD.md).

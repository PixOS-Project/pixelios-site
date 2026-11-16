# Try it

**Last verified: 2026-11-16.** The path from a stock Pixel 6a to the iOS lock screen, in the order you would do it.
This page is a map; each step links to the document that has the exact commands.

!!! danger "What it costs"
    - Unlocking the bootloader **wipes the phone**.
    - Installing the iOS root **erases Android's data** (it replaces the `userdata` partition).
    - You can go back: Google's factory image restores the phone ([restore procedure](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md)).
    - Use a spare phone. This code runs at the highest privilege level.

!!! note "How far this has been tested"
    Everything here was *observed on hardware* on one phone, the maintainer's Pixel 6a. We have no report of a second phone yet.
    If you try it, please [send the log](../CONTRIBUTING.md), whatever the result.

## What you need

| Thing | Why |
|---|---|
| A Google Pixel 6a ("bluejay") whose bootloader can be unlocked | the only phone this runs on |
| A Linux computer with `adb`, `fastboot`, Python 3 and an AArch64 bare-metal GCC | builds the shim and boots the phone ([build setup](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/BUILD.md)) |
| A USB cable, ideally on a USB 3 port | every boot comes from the computer; the log comes back over USB |
| The iPhone X restore image (IPSW) for iOS 16.7, downloaded from Apple by you | the iOS userland; we distribute no Apple software |
| For Wi-Fi and Bluetooth: the firmware files from **your own** phone's Android image | they are never in our repositories ([Wi-Fi licensing](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/WIFI-LICENSING.md)) |

## The steps

### 1. Read the safety rules

[Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md) lists what must never be written (bootloader, modem, `persist`, `efs`, `vbmeta`, `boot`, the partition table)
and why a Pixel 6a can always be restored. The tools refuse to act on any phone that does not report `bluejay`.

### 2. Boot the shim alone (writes nothing)

```sh
git clone https://github.com/PixOS-Project/pixelios-kernel && cd pixelios-kernel
tools/fetch-android-tools.sh     # mkbootimg / avbtool from AOSP
tools/pix build bluejay --avb --qrlog
fastboot getvar product          # must say: bluejay
fastboot boot shim/out/shim-boot-avb.img
```

The shim runs from RAM and shows its log on the screen. If you see it, your phone accepts our boot image and nothing has been changed yet.
A long press of Power + Volume Down returns to fastboot.

### 3. Build the kernel

XNU is built by the repository's GitHub Actions workflow on a macOS runner, or locally without a Mac with `tools/xnu-local-build`
([local build](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/LOCAL-BUILD.md)). The patches in `xnu/patches/` are applied in order on Apple's open-source `xnu-8796`.

### 4. Build the iOS root image

In [pixelios-userland](https://github.com/PixOS-Project/pixelios-userland): `tools/build-ios-root-rootless.sh IPSW_DIR OUT.img` assembles the root from your IPSW without sudo
([rootless build](https://github.com/PixOS-Project/pixelios-userland/blob/main/docs/ROOTLESS_BUILD.md)). `tools/check-ios-root.py` checks the image before you flash it.

### 5. Flash the root to `userdata`

This is the only destructive step after the unlock. Back up what you can first (`tools/backup-partitions.sh`).
`tools/fflash-userdata.sh` refuses every partition except `userdata` and every phone except `bluejay`.

### 6. Boot iOS and read the log

`tools/xrun` does one full cycle: build the boot image, `fastboot boot` it, collect the kernel log over USB, wait for the phone to
return to fastboot, and print one report ([automation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md)).
The first boot after a flash is slow: about 346 s to the lock screen against about 108 s afterwards
(*observed on hardware*, runs `bs-q1`, `bs-q2`, 2026-10-25, 8 CPU cores).

### 7. Go back to Android

Flash Google's factory image for bluejay, as described under "Restore procedure" in [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md).

## What to expect when it runs

- The phone only boots while a computer starts it. There is no boot from the power button yet.
- Touch, the GPU-drawn UI, Wi-Fi and Bluetooth work; sound does not. See [Status](STATUS.md).
- The battery charges slowly or drains under load. See [Power and charging](components/power-charging.md).
- It gets warm. See [Thermal](components/thermal.md).

## If something goes wrong

| What you see | Where to look |
|---|---|
| `fastboot boot` is accepted but nothing runs | the image needs an AVB footer: [Boot chain](components/boot-chain.md) |
| No log on the computer | [USB and the debug channel](components/usb-debug.md); the on-screen QR log is the fallback |
| The phone hangs | a kernel panic or a watchdog returns it to fastboot by itself: [Recovery](components/recovery.md). Otherwise hold Power + Volume Down |
| A daemon or app misbehaves | every missing piece prints a `GAP` line in the log: [Method](METHOD.md) |

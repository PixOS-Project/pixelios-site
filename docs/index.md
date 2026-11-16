# PixOS

**Apple's XNU kernel and the iOS 16.7 userland, running on a Google Pixel 6a.**

PixOS is a research port. A small boot program (the *shim*) is loaded into RAM with `fastboot boot`, prepares the Pixel's
hardware, and starts a patched XNU kernel. iOS itself lives in the phone's `userdata` partition. Nothing else on the phone is written.

It is based on [ios-sweet](https://github.com/dipa-studio/ios-sweet), which did the same for a Redmi Note 10 Pro.

**Last verified: 2026-11-16.**

!!! info "AI was used heavily"
    AI was used heavily to make this run on Pixel 6a; it is based on ios-sweet. Most code and docs were written by AI coding
    agents, directed by a human who owns the phone. Read the code before you trust it:
    [how the project is built](AI_DEVELOPMENT.md).

!!! warning "Research code, not a daily driver"
    Use a spare phone. Unlocking the bootloader wipes it, and installing the iOS root erases Android's data.
    Read [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md) first.

## What works today

State on 2026-11-15, *observed on hardware*. Run labels (in `code`) point into the maintainers' run logs; every row is explained on its component page.

| Area | State | In short | More |
|---|---|---|---|
| Boot to the iOS home screen | :material-check: yes | lock screen, home screen, Settings, App Library (run `gputest-surffail-b`) | [Userland](components/userland.md) |
| Touch | :material-check: yes | a real finger: 5791 touch interrupts, none empty (demo boot, job 1308) | [Touch](components/touch.md) |
| GPU-drawn UI | :material-check: yes | 50.6 rendered frames/s at the GPU's lowest clock, two boots (runs `155b`, `8177`) | [GPU](components/gpu.md) |
| Frames reaching the panel | :material-alert: close | 49.0 drawn presents/s against a bar of 50 (run `18e1`) | [Display](components/display.md) |
| Wi-Fi | :material-check: yes | WPA2 join, real internet (DNS, HTTPS), 188 to 285 Mbit/s TCP download (runs `155b`, `8177`) | [Wi-Fi](components/wifi.md) |
| Bluetooth | :material-check: yes | scan, connect, pair; a headset paired by hand in Settings (job 1308) | [Bluetooth](components/bluetooth.md) |
| Charging | :material-alert: one run | battery current turned positive at 875 mA input (run `chg-p3`) | [Power](components/power-charging.md) |
| Audio | :material-close: no | no speaker driver; a headset pairs but no sound plays (run `bt-va3`) | [Audio](components/audio.md) |
| Buttons | :material-alert: partly | power and volume-up presses reach the kernel (runs `resident-164801-b1`, `resident-204614-b1`); the iOS reaction was not checked | [Buttons](components/buttons.md) |
| Boot without a PC | :material-close: no | every boot is a `fastboot boot` from a computer | [Boot chain](components/boot-chain.md) |
| Cellular, camera, sensors, GPS, sleep | :material-close: no | never attempted | [Not attempted](components/not-attempted.md) |

The numbers above come from one configuration: 5 of the 8 CPU cores, static CPU clocks, GPU at 150 MHz.
Full tables: [Status](STATUS.md). Known issues: [release note](RELEASE-2026-11-15.md#known-issues).

## Where to start

<div class="grid cards" markdown>

-   **Try it**

    ---

    What you need, what it costs you (your Android data), and the steps from a stock Pixel 6a to the iOS lock screen.

    [Try it](TRY.md)

-   **Read the story**

    ---

    How each milestone was reached, what proved it, and the dead ends on the way.

    [Milestones](MILESTONES.md) · [Case study](CASE_STUDY.md) · [Lessons](LESSONS.md)

-   **Look at one component**

    ---

    One page per hardware block: what worked, what did not, what nobody tried, and ideas if you want to pick it up.

    [Components](components/index.md)

-   **Port another device**

    ---

    The stages in order, written for any phone and any iOS build, plus the rules we work by.

    [Porting blueprint](BLUEPRINT.md) · [Method](METHOD.md) · [Another Pixel](PORTING.md)

-   **Contribute**

    ---

    Open work, how to send a hardware result, and how to work with an AI agent here.

    [Contributing](../CONTRIBUTING.md) · [Roadmap](../ROADMAP.md) · [LLM prompts](PROMPTS.md)

-   **Check the credits**

    ---

    ios-sweet, Mesa, OpenBSD's bwfm and the other work this stands on, with licences.

    [Credits](CREDITS.md)

</div>

## How it boots

```text
stock bootloader --fastboot boot--> shim (ours: storage, memory map, device tree for XNU)
  --> patched XNU kernel (numbered patches on Apple's open-source xnu-8796)
    --> our UFS driver --> iOS 16.7 root in userdata --> launchd --> SpringBoard
```

The code is in two repositories: [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (shim, XNU patches, tools)
and [pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the recipe that builds the iOS root, and our iOS-side code).
No Apple software is distributed; you download the iOS restore image yourself.

## How to read the claims

Every claim on this site is tagged:

- *observed on hardware*: seen on the Pixel 6a, with a run label and date;
- *read from source*: read in code or a document, not run;
- *guess*: not checked.

"Works" always comes with a run label. "One run" means it was not repeated.

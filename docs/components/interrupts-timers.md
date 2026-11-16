# Interrupts and timers

**Last verified: 2026-11-16.**

## What it is

XNU on an iPhone uses Apple's interrupt controller and timers. The Pixel has a standard Arm GICv3 and the Arm generic timer.
On top of that, each of our drivers must decide how it learns that hardware is done: by **interrupt** or by **polling**.

## Status

**XNU has run on the GIC and the Arm timer since its first boot** (*observed on hardware* 2026-10-21; every run since). The busiest drivers (GPU, Wi-Fi, storage, touch) now use interrupts; USB, the Bluetooth UART and the buttons still poll.

## What worked

- **GICv3 and the virtual timer** with constants only: bases, the timer interrupt and the 24.576 MHz frequency come from `soc.json`.
- **Polling to interrupts, one driver at a time.** Each conversion was measured:

| Driver | Before | After | Evidence (*observed on hardware*) |
|---|---|---|---|
| GPU job completion | polled | interrupt (patch 0272) | slowest navigation step rose to 56.6 frames/s, run `gputest-nav43`, 2026-11-09 |
| Wi-Fi (PCIe INTx doorbell) | 5 ms idle sleep | interrupt (patches 0347 to 0351) | 9138 interrupts in 157 s, none spurious, run `c17e`, 2026-11-13 |
| Storage (UFS completion) | polled | interrupt (patch 0354) | 133255 interrupts, none spurious, run `c1f4`, 2026-11-14 |
| Touch | 125 polls/s | interrupt (patches 0355, 0356) | 5791 interrupts, none empty, demo boot job 1308, 2026-11-15 |

## What didn't

- **The first Wi-Fi interrupt handler switched itself off.** It acknowledged in a loop and gave up when the status stayed set.
  Linux acknowledges once and lets the level-triggered line fire again; patch 0349 does the same.
- **Faster storage completion changed no frame rate** (run `c1f4`: 45.7 pooled, unchanged). It removed a poller, not a bottleneck.
- **Vsync is a kernel timer, not the panel's signal.** Frames are paced by our own 60 Hz tick ([Display](display.md)).

## Untested or never attempted

- **USB controller interrupt.** The USB gadget is polled about 1000 times a second (*read from source*).
- **Bluetooth UART interrupt.** Receive is polled about 100 times a second, which also limits its data rate ([Bluetooth](bluetooth.md)).
- **Button interrupts.** The key pins are sampled every 10 ms.
- **MSI for Wi-Fi.** The driver uses the legacy INTx line.
- **The panel's tearing-effect signal** as the vsync source.

## Ideas if you want to pick it up

- Convert the Bluetooth UART first: it is the one poller that blocks a feature (audio needs more bytes per second than the poll delivers).
- A rule that helped: a new interrupt handler first runs *next to* the poller and only counts. Switch over when the counts agree.

## Where to look

- Patches: 0109 (GIC probe), 0272, 0346 (interrupt plumbing), 0347 to 0351 (Wi-Fi), 0354 (UFS), 0355, 0356 (touch), 0101, 0149 (vsync timer).
- Notes: [GPU interrupt path](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/35-gpu-irq-path.md), [gs101 peripherals](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/docs/02-gs101-peripherals.md).
- Data: GIC and timer entries in [`soc.json`](https://github.com/PixOS-Project/pixelios-kernel/blob/main/soc/google/gs101/soc.json).

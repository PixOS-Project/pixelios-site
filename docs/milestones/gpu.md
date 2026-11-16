# GPU: from CPU drawing to 55 frames/s

**Last verified: 2026-11-16.** Milestones M9 and M9b · 2026-10-23 to 2026-11-11 · **done** (55 on the slowest step); 60 on every step **open**

## Goal

Draw the iOS UI with the Pixel's Mali GPU instead of the CPU, fast enough to feel like a phone: first 20 frames/s, then 40, then
the slowest step of a scripted navigation at 55 or more.

## What was done

1. **Reach the GPU.** Read its ID from the shim; learn who powers it (the shader rail is a firmware request); hand it to XNU.
2. **A Mali driver in XNU**: power, memory mapping, job submission, reset, later interrupts, with an IOKit user client.
3. **A GL stack for iOS**: Mesa's Panfrost driver built for iOS, behind an EAGL layer, so CoreAnimation takes its OpenGL ES path.
4. **Correctness, with a host replay.** Captured GPU frames are replayed on a PC software renderer and compared with the phone, pixel by pixel.
5. **Speed, with a frame-time bench.** A scripted session (unlock, home pages, Settings, Spotlight, app launch) with a per-step score.

## How it was proven

All *observed on hardware*. The benches changed as they were outgrown; old rungs are kept as history on the [ladder](../MILESTONES.md#measured-ladder-generated).

| Date | Result | Runs |
|---|---|---|
| 2026-10-23 | GPU ID `0x92020010` read | `g0` |
| 2026-10-26 | lock screen drawn through the GPU path; not yet faster than the CPU renderer | `gputest41`, `gputest42`, `gputest48` |
| 2026-11-04 | 38 frames/s median on the 240-swipe bench (target 20) | `gputest-cced-poll20` |
| 2026-11-07 | 41 with one swipe every 4 s (target 40), one run | `gputest-c21e-unmap` |
| 2026-11-09 | slowest navigation step 56.6 and 56.7, pooled 59.8; again from the trunk build at 55.2 and 55.1 | `gputest-nav43`, `gputest-nav44`, `gputest-trunk10`, `gputest-trunk11` |
| 2026-11-11 | App Library backdrop fixed; pooled 59.5, slowest step 51.6 | `gputest-surffail-a` (before), `gputest-surffail-b` (after) |

## What it unlocked

A UI that scrolls. It also produced the instruments later work depended on: the navigation bench, the frame-time witness, the host
replay, and the `GAP` rule (every stub logs loudly) that came out of its worst bug.

## Dead ends

- **A stub that said "success".** Our surface emulation ignored one creation key and handed out zeroed memory. Every check was green
  and the home-screen icons were missing. About two days of runs.
- **A blocking flush.** Every frame waited for the GPU to finish, so "the GPU is no faster than the CPU" was a pacing result.
- **Polling for job completion.** It capped the slowest step below 55 until the GPU's interrupts were wired (2026-11-09).
- **One guess per boot.** About 25 boots testing theories about CoreAnimation's internals fixed none of three defects. The bug
  (black App Library) was a 64-entry table in our own GL layer; an audit of our own code found it in two boots.
- **Instruments that disturb.** High-volume tracing pushed the frame rate to about 19 frames/s; those boots measured the tracer.
- **Benches that could not reach their target.** The swipe bench had idle gaps, so its 55 target was unreachable by construction
  (peak 52.9, run `gputest-splitlag`). It was replaced, and the page says so instead of deleting the number.
- **Metal.** Out of reach on this GPU; never attempted.

Component: [GPU](../components/gpu.md), [Display](../components/display.md). What happened next: [everything at once, at low clocks](all-on-low-clock.md).

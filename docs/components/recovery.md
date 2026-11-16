# Recovery: panic, watchdog and stall detector

**Last verified: 2026-11-16.**

## What it is

A test phone that hangs needs a human to press buttons. PixOS added three things so that it never does:

- a **panic path** that sends the panic text to the host and resets into fastboot;
- a **hardware watchdog** that resets a kernel which stops responding;
- a **stall detector** that turns a silent hang into a panic with a cause line.

## Status

**A panic and a deliberate hang both return the phone to fastboot with no hand on it** (*observed on hardware*: run `20261107T145123Z-panic-self-recover`, 2026-11-07; run `ar-c-wdttest`, 2026-11-09).

## What worked

- **Reset to the bootloader from software.** The reboot-mode register and its values are in the public Linux device-tree bindings
  for gs101 ([note](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/10-reboot-to-bootloader-gs101.md); patches 0083, 0100).
- **Panic to fastboot** (run `20261107T145123Z-panic-self-recover`), with the panic text and a backtrace on the host first (patch 0242).
- **The SoC watchdog, re-armed and petted by the kernel** (patch 0278; deliberate hang, run `ar-c-wdttest`).
- **A stall detector** (patch 0279): if the log thread has not run for 20 s, panic with the cause, so the panic path reports it.
- **Arming without USB** (patch 0333): a timer arms and pets the watchdog, so a boot whose USB never comes up is still covered.
- **A thermal emergency stop** that uses the same orderly reset ([Thermal](thermal.md)).

## What didn't

- **Resets first landed in Android recovery, not fastboot.** The bootloader decides by the reset cause. The host tool moves the phone from recovery to fastboot.
- **A reset path that works normally can fail during a panic.** On 2026-11-12 a panic with no USB link printed its registers, tried to
  reset, faulted again and hung until the maintainer restarted the phone. That boot had no watchdog, because only the USB thread armed it. Patch 0333 is the fix.
- **A missing panic-log region made stock XNU spin forever** on every panic. Patch 0182 skips the save when there is no region.
- **A debug boot argument that waits for a debugger** turns every panic into a hang.

## Untested or never attempted

- **A panic before the platform code starts.** There is no watchdog that early (*read from source*, patch 0333's header). The shim could arm one; that is a new hardware write and was not done.
- **Saving the panic log on the phone.** It only goes to the host.
- **Recovery when no computer is attached.** The phone parks in fastboot and waits.

## Ideas if you want to pick it up

- On a new device, prove this **before** the first risky experiment: a deliberate panic and a deliberate hang, both ending in the bootloader.
- Arm the watchdog in the shim, with a review of that one write, to close the early-boot gap.
- Keep a panic region in RAM and read it back after the reset, if your bootloader leaves RAM alone (ours does not).

## Where to look

- Patches: 0083, 0086, 0100, 0122 (reset paths), 0182, 0224, 0242 (panic), 0278, 0333 (watchdog), 0279 (stall detector), 0120, 0140 (reset cause), 0191, 0195 (test hooks).
- Notes: [reset to the bootloader on gs101](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/10-reboot-to-bootloader-gs101.md), [automation](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/AUTOMATION.md).
- Blueprint stage [14](../BLUEPRINT.md#14-recovery-and-safety-automated). Milestone: [Hands-free test loop](../milestones/test-loop.md).

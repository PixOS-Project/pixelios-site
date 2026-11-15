# Lessons: the mistakes we made, so you don't have to

**Last verified: 2026-11-15.** PixOS is built mostly by AI agents with one human and one test phone. These are the mistakes that cost us the most,
told plainly so other HackiOS projects can skip them. Each one says what happened, what it cost, how we found it and the rule we adopted
(the rules are collected on [Method](METHOD.md)). Costs are counted from the maintainers' sprint logs (private; one line per boot);
"not recorded" means we did not count it. No blame: most of these were made by agents following rules we had written ourselves.

## Debugging

### 1. A stub that returns "success" hides the real failure

**What happened.** Our kernel emulates parts of Apple's IOSurface and IOMobileFramebuffer services. Twice, an unimplemented piece answered
"success" with empty data and logged nothing. In October the surface emulation ignored one creation key and handed out zeroed memory; every GL call
succeeded, every checkpoint was green ("no black frames", "text legible"), and the home-screen icons were simply missing. In November a sweep
found that the framebuffer user client answered every selector it did not implement with success and zeroed outputs, and that the surface
service silently dropped every `SetValue` call (more than a thousand per boot from SpringBoard), so every process read back empty values.
**Cost.** About two days of GPU runs in October; the November sweep cost no boots, it removed blind spots. **How found.** A person looked at a
frame and a kernel scan showed the icon surfaces were all zero; later a read of our own patch source. **Rule.** No silent failures: every stub,
ignored key or unsupported selector prints one loud `GAP` line with a count, a stub never returns plain success, and every UI checkpoint checks
content, not just liveness. A lint step now flags silent returns in new code.

### 2. Two calls, one handler: wrong trap semantics

**What happened.** The IOSurface client uses two kernel traps when it releases a surface: one detaches the client, the next one releases it, and
the second one alone also undoes a failed client build. Our kernel handled both as "release", so the first call dropped the reference and the
second failed every time; a lookup by another thread between the two could even lose a fresh reference. Our own fact notes held the wrong reading.
**Cost.** Not recorded. It turned out not to be the cause of the defect we were chasing at the time (lesson 4). **How found.** A lead from a
similar project, confirmed by our own reading of the framework's release path, then compared with our patch. **Rule.** Never assume what an
interface does: confirm each call's meaning on your build. Mark a wrong fact *superseded* rather than deleting it, so the history of the mistake stays.

### 3. One guess per boot is trial and error

**What happened.** The GPU stream had three visual defects. For about a day it booted one hypothesis about CoreAnimation internals at a time
(recorder on or off, a decode step off, snapshot off, more tracing, texture-name quarantine). Several boots were unusable for unrelated reasons
(the navigation landed in the wrong app, a migration screen after a re-flash, a script mistake). **Cost.** About 25 boots and 0 of 3 defects
fixed; the thread was stopped by the maintainer. **How found.** The maintainer, not our own checks (lesson 12). **Rule.** Data first: before a
fix, name the observed error (run label and log line) and the data that shows its cause; if the data is missing, the next boot adds the capture,
not another guess. Two boots in a row without an explained result means the model is wrong: stop and rethink.

### 4. The bug was in our code while the boots probed Apple's

**What happened.** The App Library backdrop drew black because CoreAnimation drew into framebuffers whose colour texture had no storage. We had
built a theory about CoreAnimation's texture-name reuse and tested it; the defect stayed. Then an audit of our own GL layer for silent failures
added a log line to every path that could fail without a word. The first boot with it showed the cause at once: our attach table kept one record
per texture name, at most 64, and never removed one, so after 64 names every new attach was refused. **Cost.** Two boots from the audit to the
fix (runs `gputest-surffail-a` and `gputest-surffail-b`, 2026-11-11), after the 25 of lesson 3. **How found.** Reading our own source where the
evidence pointed, then counting failures by path. **Rule.** Audit your own code for silent failures before you reverse-engineer the vendor's.

### 5. Trusting a summary instead of the source

**What happened.** Several times a summary was believed over the data: a progress check accepted a thread's own report that it was "learning";
a fact store filled by automated extraction held two wrong facts; a notes file blamed the wrong component for leaked processes and corrected itself
later; delegated agents once hid what they changed, wrote a wrong address sheet and a safety check that could never fire. **Cost.** Not recorded.
**How found.** Re-reading the log or the source. **Rule.** Tag every claim (*observed* with a run label, *read from source* with file and line, or
*guess*). A summary, including an agent's own report, is a pointer to evidence, not evidence. Re-open the log before you repeat a claim.

### 6. Silent clamps: the setting was dropped without a word

**What happened.** The kernel command line has a size limit. Adding a few boot arguments pushed out the tokens that raise the memory clock;
nothing said so, and two GPU boots ran with the memory at its boot clock and measured 19 frames/s. Separately, a queue tool capped a wait at one
hour without telling the caller, the queue outlasted it and a Wi-Fi boot never ran. **Cost.** 2 invalid boots and 1 boot not run. **How found.**
Log lines that should have been there were missing; reading the tool's source. **Rule.** The same as lesson 1: any value that is cut, clamped
or ignored prints a GAP line.

### 7. The hardware was not powered or not muxed

**What happened.** The Bluetooth controller never answered: the bootloader leaves its UART pads configured as plain GPIO, and one pad-function
write fixed it. The touch controller never answered: its two regulator rails were off, and six patches had gone into SPI clocks, muxes and
transfer details before anyone checked power. Later, touch looked dead on GPU runs because the touch recipe was only in boot arguments the GPU
runs did not pass. **Cost.** For touch, six patches (time not recorded); for Bluetooth, 1 boot once the pads were read. **How found.**
Read-only witness lines of the pad and power state. **Rule.** Check power, clocks and pin functions before bus timing, and print them in the
same boot as the first attempt.

### 8. A test oracle that checks liveness passes the wrong picture

**What happened.** Our screen checker compared each snapshot with a reference by mean difference. When the navigation ended up in an unexpected
app that showed a mostly white welcome screen, 11 of 19 snapshots "matched" white Settings references. Earlier, a reference set made on a boot
that already had the black App Library defect made correct frames look wrong. **Cost.** At least 1 boot that answered nothing. **How found.**
A person looked at the snapshots. **Rule.** References come from a known-good boot; the run ends at once when an unexpected app starts; the
checker flags two different references that got identical snapshots.

### 9. An instrument that disturbs what it measures

**What happened.** High-volume text tracing through the kernel log and CoreAnimation's own logging each pushed the frame rate to about 19
frames/s, so those boots measured the tracer. The frame recorder was blamed for the black App Library until control boots with it off showed
the same black. **Cost.** At least 2 diagnostic boots with unusable numbers, and part of lesson 3. **Rule.** Measure the cost of an instrument
with a control boot before you trust what it shows; keep traces small or binary.

## Shared resources (one phone, several workers)

### 10. One shared root image, many owners

**What happened.** Every stream's boots assume the same iOS root on the phone. Streams re-flashed their own variants for one-file differences:
six flashes on one day, and on the next day one stream flipped between two roots four times in three hours to toggle one settings file. Each
flash holds the phone for 5 to 7 minutes and makes the next boots of every stream run the slow first-boot migration, so their timings are not
comparable. **Cost.** At least 2 GPU boots invalid because of a root change; the rest not recorded. **How found.** The phone lock's history
during an efficiency review, the second time it happened. **Rule.** One standard root, announced by hash and changed only when a file cannot be
overlaid; a per-run difference goes in a boot-time overlay. Since the second occurrence the flash tool refuses a non-standard root unless the
caller says why it cannot be an overlay. (General rule: the second occurrence of a mistake gets a tool guard.)

### 11. A fallback that quietly changed what was booted

**What happened.** The remote build host was unreachable, the build fell back to a local incremental build, and `make` linked old Wi-Fi code.
The boot looked like a protocol regression. In another stream, Bluetooth kernels built without the controller's firmware patch stack booted fine,
fell back to the ROM firmware, and measured nothing useful. **Cost.** One boot for Wi-Fi; for Bluetooth one 28-minute hold. **How found.**
Marker strings of the newest commit were missing from the kernel; a GAP line said the firmware stack was absent. **Rule.** Before a boot, check
the built image for a marker of the change under test; fallbacks build from clean.

### 12. Judging progress per time window instead of in total

**What happened.** A scheduled check every two hours was meant to catch a stuck stream before the maintainer did. It looked only at the boots
since the last check, accepted the stream's own "learning" verdict again and again, and never added up that 16 boot entries had fixed 0 of 3
defects with 7 invalid. **Cost.** The stuck period of lesson 3. **How found.** The maintainer asked why the check had not caught it. **Rule.**
Count per defect over the whole stream (boots, invalid boots, closed); hard stop triggers (six boots on one open defect, two invalid boots in a
window, no third "learning" in a row, evidence pointing at our code while the boots probe the vendor's); and read our own code for silent failures every time.

### 13. Editing a script while a run executes it

**What happened.** A boot script was edited while that boot's shell was still running it; the run ended with a syntax error after the data was
taken. A generated patch was regenerated with the wrong tool while a build used the tree, and the image build refused. **Cost.** 1 run status lost,
1 boot not run. **Rule.** Runs execute a copy of their script; no edits in a tree a running build or boot uses.

### 14. Serial host work left the phone idle

**What happened.** On one day the phone was held 11.6 of 17.2 hours: 54 real runs and 5.8 hours idle, in gaps that lined up with host work
done one step after each boot (analysis, a review, a rebuild). More workers would not have helped. **Cost.** 5.8 hours of idle phone in a day.
**Rule.** Prepare the next boot (review, build, analysis script) while the current one runs, and queue a ready boot before releasing the phone.

### 15. Timing tests that fail when the host is busy

**What happened.** Tests with fixed wall-clock bounds failed once on a loaded build host and passed alone, several times; a merge had to be run
with a pre-check skipped. **Cost.** Repeated gate runs; not counted. **Rule.** Assert what ran, not how long it took: record the calls, use a fake
clock, or give real slack.

## Process

### 16. Ceremony outweighed the work and was retired

**What happened.** Each safeguard was added after a real mistake: tickets and a work queue, a coordinator role and role threads, a written run
plan and a plan check before every boot, formal gates before boots, review rounds until no high finding was left, successor threads at context
limits, adversarially framed reviews, a two-hourly queue review. Together they took more effort than the mistakes they prevented: on one day,
66 boots in 24 hours moved one number. The maintainer stopped the process on 2026-11-08 and the docs were rewritten on 2026-11-09 for goal
threads without tickets. **Cost.** "66 boots, one number moved" in the last 24 hours before the change; hours not recorded. **What stayed:** the
hard safety rules, a goal per stream with a "what counts" line set by the maintainer, one log line per boot, one review for a new hardware
write, and a gate before a change lands on the main branch (ungated merges had broken the main branch twice). **Rule.** Keep the process as
small as the risk allows; when a rule is retired, sweep every document and tool that still prescribes it.

### 17. Very long agent threads lose detail

**What happened.** By the third day of a sprint, the GPU thread had about 2800 items and 116 runs. Repeated context compaction is our best guess
for several small slips of the kind in lessons 11 and 13 (*guess*: not proven). **Rule.** A fresh thread per stream with a short brief (goal,
what counts, state, last boot line, open items) when a thread gets very long; the old thread is closed, not continued in parallel.

## Power

### 18. The phone drained while it was "charging"

**What happened.** The phone died twice in long iOS sessions. A read-only probe and then reads of the charger chip showed it was charging, but at
the 500 mA input limit a plain USB host port gets, below the load of a running iOS: -98 mA on a black-screen boot, more with the GPU busy.
Nobody had raised that default, and the bootloader resets it on every boot. Meanwhile one stream polled the battery voltage every 10 minutes
for two hours, and three Bluetooth boots were not run because the battery was under the safety threshold. **Cost.** 2 dead-battery stops,
3 boots not run, 2 hours of polling. **How found.** Probing the charger read-only, then reading it. **Rule.** Measure power before you plan long
sessions; raising the input limit to 875 mA on USB 3 (together with the USB descriptor, which a review caught) made the phone charge
(run `chg-p3`, one run). The battery threshold stays: a safety value is not loosened to get a run in.

## Sources

The maintainers' sprint logs (one line per boot, private), their anti-pattern notes and retired-rules list, and the efficiency review of
2026-11-10. Public code that came out of these lessons: the GAP logging and the silent-return lint (`tools/lint-silent`), the flash tool's
standard-root guard (`tools/fflash-userdata.sh`) and the help-handler check for new tools, all in
[pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel).

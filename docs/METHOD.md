# Method: the working rules that made progress

**Last verified: 2026-11-16.** These are the rules PixOS works by today, written so another HackiOS project can adopt them without our tools.
Each rule says where it came from: most were adopted after a mistake that cost boots or days ([Lessons](LESSONS.md) has the stories).
Sources: the project's hard rules (`AGENTS.md` in [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel)), the maintainers' rule list and sprint logs (private, summarized here).

## 1. Safety comes first, and it is mechanical

- **Reversible only.** Never write the bootloader, modem, persist, efs, vbmeta, boot, dtbo partitions or the partition table. Never relock without the stock image, never flash an older bootloader (anti-rollback). `userdata` is the only partition the iOS root replaces.
- **RAM boots.** Every kernel and shim is started with `fastboot boot` (or your bootloader's load-to-RAM command), which writes nothing.
- **Prove recovery before you need it.** Before the first risky step, show on the phone that a hung boot gets back to the bootloader (a key combination, a watchdog, a panic handler). PixOS added a panic handler and a hardware watchdog that return the phone to fastboot without a hand on it (*observed*, runs `20261107T145123Z-panic-self-recover`, `ar-c-wdttest`).
- **Only the right phone.** Every hardware command first checks that the attached device reports the expected codename. Any other phone is never touched.
- **The human runs the phone.** Agents stage commands that need root on the host; the maintainer runs them. Flashing `userdata` and phone runs are pre-approved; anything else destructive is asked each time.
- **Nothing private in git.** No serials, IMEI, MAC addresses, network names, keys, partition dumps, firmware, Apple binaries or anything extracted from them. Private values live in a git-ignored `.env`; the repository only has `*.example` files. A pre-push guard scans for them.
- **A build-time audit** rejects any storage write path in code that runs before the kernel. Never loosen a safety check to make a change pass; fix the change.

## 2. Data first: name the error before the fix

Before any change, write down the observed error (run label and the log line) and the data that shows its cause. A change without a named
error is trial and error, and trial and error was our most expensive habit. When the data is missing, the first boot of a task adds the
capture that would show the cause, not a guess at a fix.

## 3. Never assume; check against a source

Every register, offset, struct layout, unit, flag or API is checked against a cited source before use: a Linux, BSD or vendor driver at a
commit, a decompile you made yourself, or a measurement. Cite file and line. "It probably works like X" is a guess and is labelled as one.

## 4. Cheapest evidence first

For any open question, use the cheapest source that can answer it:

1. existing logs from earlier runs,
2. source code (Linux, OpenBSD, vendor kernels, Apple's open-source XNU),
3. a decompile of the binary on your host,
4. a host test or a replay (for the GPU we replay captured frames on the host's software renderer and compare them pixel by pixel),
5. a capture from the stock OS on the same phone (RAM-booted, read-only),
6. a boot of your own code.

A boot is the most expensive question you can ask. Say which cheaper evidence you checked before you take one.

## 5. No silent failures

Every stub, ignored value, unsupported selector or refused call prints one loud `GAP` line (with a count) in the log, and the run summary
counts them. A stub never returns plain success. Our worst bugs were stubs that said "success" while doing nothing: the client then
failed somewhere else, much later, with no trace of why (see [Lessons](LESSONS.md)). A lint step checks new code for silent returns.

## 6. Tag every claim

Every sentence about the hardware or the software is one of: *observed on hardware* (with the run label), *read from source* (with file and
line), or *guess*. "Works" needs a run label. "One run" is said when it was not repeated. Summaries, including an agent's own report, are
not evidence: re-open the log or the source before you repeat a claim.

## 7. Make every boot count (one phone, several workers)

PixOS has one test phone and several parallel work streams (GPU, Wi-Fi, Bluetooth, tools). What kept the phone busy and the results comparable:

- **One lock for the phone.** Every run takes the lock, does flash and boot in one hold, and returns the phone to fastboot at the end. Never stop another worker's run; when the phone is busy, do host work.
- **Change one thing against a known baseline, or batch read-only checks.** A boot either flips one variable against a named earlier run, or answers several independent read-only questions at once.
- **A shared standard root image.** Everyone boots the same root; a worker who needs a variant uses an overlay applied at boot instead of re-flashing `userdata`, because a re-flash changes the next boot for everyone (a first boot after a flash runs a slow data migration).
- **Prepare the next boot while this one runs**: the review, the build and the analysis script, so the phone does not sit idle between holds.
- **Stop when the number does not move.** Two boots in a row that leave the metric inside run-to-run noise mean the model of the problem is wrong: stop, write down what the result rules out, then test a new model. A stream that has not moved its number in its last N boots is stuck, however busy it looks (judge it over the whole stream, not per time window).
- **A queued session**: the phone stays in iOS and runs queued jobs from several workers before it parks, which cuts boot overhead (in use since 2026-11-11; the 2026-11-15 bench boots ran this way).
- **A QEMU lab** booted the iOS root to SpringBoard in an emulator (host only, 2026-11-11, feasibility study): userland work that needs no Pixel hardware can move there.

## 8. Port a block in a fixed order

For each hardware block (display, GPU, Wi-Fi, Bluetooth, audio, charger, ...):

1. **Oracle:** how the block behaves under the stock OS (a capture or trace from Android on the same phone, or a cited reference driver).
2. **Spec:** the ordered sequence from power-on to the user-visible feature, every step cited, every unknown listed with what settles it.
3. **Conformance matrix** for the iOS-facing side: every selector, property, ioctl and key the iOS daemons ask of you, each marked implemented, partial or missing (missing = a GAP line).
4. **Build and run**, with each run's question and predicted log lines written down before the boot.

## 9. Reviews where they pay

A patch that writes new hardware registers, firmware commands or bus stores gets one independent read-only review before it boots,
with proof for every finding. Nothing else needs a review round. Review briefs say what to check, never what to expect.

## 10. Keep the process small

We tried tickets, a work queue, plan checks, run plans per boot, formal gates before every boot and review rounds. Each was added for a
good reason, and together they slowed the work more than the mistakes they prevented. They were retired on 2026-11-08/09. What stayed:
the hard safety rules, one goal per stream with a "what counts" line set by the maintainer, one log line per boot, and a gate before
merging to the main branch. A rule that is not enforced by a tool tends to be forgotten; a rule enforced by a tool tends to outlive its
purpose. Review both regularly.

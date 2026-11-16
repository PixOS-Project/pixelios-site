# Audio

**Last verified: 2026-11-16.**

## What it is

Two separate paths would make sound:

- the phone's **own speaker and microphones**, which need drivers for the codec and amplifier chips;
- a **Bluetooth headset** (A2DP), which needs no new hardware driver but needs iOS to route audio to it.

## Status

**No sound plays.** No speaker driver exists. A headset pairs and iOS opens an audio stream to it but never starts it (*observed on hardware* 2026-11-11, run `bt-va3`).

## What worked

- **The iOS audio stack itself runs.** A 60 s test tone plays to a virtual output device (run `bt-va1`, 2026-11-11).
- **The headset link.** Pairing completes and the A2DP stream is configured (SBC, 44.1 kHz; run `bt-va3`). Pairing by hand in
  Settings worked again on 2026-11-15 (job 1308).
- **An honest device tree.** Our audio node is empty and logs gaps. It does not copy an iPhone's node, which would claim hardware that is not there.

## What didn't

- **A2DP never starts.** After the stream opens, iOS does not send the Start command, so the headset stays silent. The public
  ladder says "cause not found". The lead is in iOS's audio routing: no route to the Bluetooth output gets selected
  (*read from our own decompile notes; not confirmed on hardware*).
- **An earlier workaround disabled the Bluetooth audio plug-in** to stop a reconnect loop that burned a core (October). It was
  temporary and is gone; the plug-in is back in the root.

## Untested or never attempted

- **Speaker, earpiece, microphones.** No driver, no research note, no register read.
- **Volume keys, ringer, haptics.**
- **Calls of any kind.**
- **USB audio.**

## Ideas if you want to pick it up

- **Speaker:** read the Pixel 6a's audio path (codec, amplifier, buses, power) from the Pixel kernel sources and write the map first.
  Then decide what iOS needs to publish a built-in output. This is the largest unstarted block that people would notice.
- **Headset:** the Bluetooth UART is too slow for audio today ([Bluetooth](bluetooth.md)). Fix the transport, then chase the routing.
- The [VirtualAudio interface notes](../IOS-INTERFACES.md#virtualaudio) list what we learned about the routing code.

## Where to look

- ADT audio node: `tools/mkadt.py` and its test `tools/test_mkadt_audio.py` in pixelios-kernel.
- Userland: `bt-client/bt_tone_ios.c` (the test tone) in pixelios-userland.
- Blueprint stage [11](../BLUEPRINT.md#11-audio-not-solved). Open milestones: [what is left](../milestones/open.md).

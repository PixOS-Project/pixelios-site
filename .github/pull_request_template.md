## What and why

## Hardware evidence
<!-- Device, date, build id, exact observed output. "Not tested on hardware" is a valid answer. -->

## Safety checklist
- [ ] No write outside `userdata`; no new UFS write path in the shim
- [ ] `tools/check-all.sh` prints `GATE PASS`
- [ ] No serials, dumps, keys, firmware or Apple artifacts in the diff
- [ ] Constants cite their source; claims are tagged observed / read / guess
- [ ] AI assistance: what was generated, what a human checked

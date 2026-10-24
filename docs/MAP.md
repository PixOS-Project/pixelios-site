# Repository map

The tree follows AOSP's idea: shared platform code in one place, then **SoC** trees (what every
device with a chip shares), then **device** trees (what one phone adds).

```
shim/                    shared bare-metal shim: start-up, MMU, FDT parser, loader, console, RAM log,
                         pstore, USB gadget protocol, userdata dump framing, host tests, build.sh
xnu/patches/             numbered patches to Apple's XNU, applied in order on xnu-8796 (fetched series + ours, e.g. 0080 gs101 UFS,
                         0095 touch, 0099 IONetworkStack stand-in)
qrlog/                   QR frame builder + encoder shared by shim and kernel
tools/                   ADT/payload builders, USB log + dump receivers, QR log reader, hardware test loop
                         (`xrun`, `probe-run`, `phone`, `phone-lock`, `ci-kernel`, `stack-apply`), quality gate
                         (`check-all.sh`), `pix` (device entry point)

soc/<vendor>/<soc>/      soc.json (GIC, timer, UFS base, watchdogs, CPUs, PSCI, boot header)
                         shim/  SoC code the shim compiles (e.g. gs101 UFS cold init, HS-G4, PHY tables)
                         docs/  datasheet-level research (e.g. gs101 UFS bring-up)

device/<vendor>/<codename>/   board.json (names its SoC; DRAM map, framebuffer, ...)
                              docs/ hardware/   gate results, raw captures from that phone

docs/                    safety, build, automation, research notes, reviews, Wi-Fi coverage
upstream-patches/        our diffs against ios-sweet, applied by tools/setup-upstream.sh (being retired, see Credits)
```

The project is three repositories: [pixelios-kernel](https://github.com/PixOS-Project/pixelios-kernel) (everything above),
[pixelios-userland](https://github.com/PixOS-Project/pixelios-userland) (the iOS root build: `tools/build-ios-root*.sh`, rootless guest scripts) and
[pixelios-site](https://github.com/PixOS-Project/pixelios-site) (this site; `tools/build-site.py` assembles it).

## Reading order

1. [AI-driven development](AI_DEVELOPMENT.md): how the project is made, and how to read it.
2. [Status](STATUS.md) and [Plan](PLAN.md): where the project is and why it is shaped this way.
3. [Safety](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md): the rules every change follows.
4. [Boot path](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/research/01-boot-path.md): how a Pixel reaches our code.
5. The device you care about under [Devices](devices/index.md), and its SoC under [SoCs](socs/index.md).

## Commands

```sh
tools/pix devices                 # list device trees
tools/pix info bluejay            # merged SoC + device values
tools/pix check bluejay           # sanity checks (alignment, required keys)
tools/pix build bluejay --avb     # build the shim for a device
tools/pix new-device google/oriole --soc google/gs101 --name "Pixel 6"
tools/pix probe ARGS...           # one shim probe cycle: build, boot, capture, verdict
```

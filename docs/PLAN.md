# Plan

Each phase ends with a hardware gate. All work follows [SAFETY.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/SAFETY.md): every step must be reversible with the stock factory image. No phase starts until the previous gate passes.
Device steps marked **[user]** are run by the user (destructive or needs the phone in hand).

For user-local compiler and Android image tool setup, see [BUILD.md](https://github.com/PixOS-Project/pixelios-kernel/blob/main/docs/BUILD.md).

## Phase 0: import + probe shim (no XNU)

1. Import upstream ios-sweet at `11da58b` into this repo unchanged (one commit), so every later
   change is a reviewable diff against it.
2. Board table: `tools/boards.py` with `sweet` and `bluejay` constants (DRAM, GIC, timer, FB, UFS,
   UART, watchdog, CPU MPIDRs). `mkadt.py`, `mkpayload.py`, `shim/build.sh` take `--board`.
3. Shim for bluejay (`shim/build.sh --board bluejay`):
   - boot.img **v4** (`mkbootimg --header_version 4`), payload as ramdisk, loader scans
     `[initrd-start, initrd-end)` for the payload magic; optional AVB footer via `avbtool`.
   - `start.S`: handle EL2 entry (set `VBAR_EL2`, drop to EL1).
   - Disable `watchdog_cl0/cl1`.
   - Framebuffer address/stride from the live FDT `simple-framebuffer`/`cont_splash` if present,
     else board table; re-arm the DECON hardware trigger.
   - Samsung UART output at `0x10a00000` in parallel with the screen.
   - Probe screen/UART dump: CurrentEL, MIDR/MPIDR/`ID_AA64MMFR0` per core (PSCI CPU_ON with the
     gs101 PMU pre-steps), CNTFRQ, GICD_TYPER/CTLR, PSCI version, FDT `memory` + `reserved-memory`,
     UFS HCE/HCS/CAP + READ CAPACITY on each LUN + GPT partition names.
   - Reset via PSCI `SYSTEM_RESET`; Power+VolDown always gets back to fastboot.
4. **[user] Gate 0**: unlock the bootloader (wipes data), back up partitions, `fastboot oem uart enable`
   if a UART cable is available, `fastboot boot shim-boot.img`, photograph the screen / capture the UART.

## Phase 1: XNU to the framebuffer console

- Patches 0001–0020 + one new patch: board from ADT, Qualcomm drivers gated off on non-sweet boards
  (`sweetusb=0 sweetkeys=0 sweettouch=0` as stopgap), `PE_halt_restart` → PSCI reset,
  gs101 CPU-on pre-steps in 0063. Optional: S5L UART console via ADT `uart0`.
- `mkadt.py --board bluejay`. Boot `cpus=1`.
- CI: fork-style GitHub Actions build (`xnu.yml`) in this repo.
- **Gate 1**: XNU reaches "waiting for root device".

## Phase 2: root from UFS

- **Before the first write to `userdata`: root-based backup of the per-device partitions.**
  `fastboot fetch` refuses `persist` and `efs` even when unlocked ("Fetching restricted partition",
  observed 2026-10-20). Plan: boot Android once (unlocked), enable USB debugging, `fastboot boot` a
  Magisk-patched copy of the factory `boot.img` (temporary, nothing flashed), then via adb root
  `dd` `persist`, `efs`, `efs_backup`, `modem_userdata`, `devinfo` to the PC (gitignored, off-device).
  Verify sizes against `partition-size:` from `getvar all`, record SHA-256s. Not writing any of those
  partitions remains the rule; the backup is insurance.
- Exynos UFS adaptation of 0028/0030/0034/0067 (PRDT byte granularity, base address, LUN choice,
  S2MPU-safe DMA buffers).
- Build the iOS 16.7.16 iPhone X root (`mkiosroot.sh` + `sweet-root-tweaks.py`, unchanged).
- **[user] Gate 2**: flash root to `userdata` (destroys Android data), boot to launchd.

## Phase 3: SpringBoard (current milestone: boot into the iOS GUI)

- Rest of the patch stack through 0079. SMP with all 8 cores (wfi idle, thermal watch).
- **Gate 3**: lock screen on the Pixel.

## Phase 5: Wi-Fi (milestone after the GUI)

- Research first (`docs/research/12-wifi-bluejay.md`): the Pixel 6a Wi-Fi chip and firmware and what iOS userland needs from the kernel
  (an IO80211 `en0` interface). **Decision (user, 2026-10-21): the real radio, no USB-Ethernet substitute.** USB Ethernet stays a debug channel.
  Write or reverse the driver as needed. Chip: BCM4389 on PCIe `pcie_1` (research 12). Steps: (1) read-only WLAN probe in the shim
  (`--wlan-probe`, Sonnet task), (2) PCIe RC + PHY bring-up in the shim as an experiment, (3) Broadcom msgbuf dongle driver in the kernel,
  (4) IO80211-compatible `en0` layer that wifid accepts (needs wifid disassembly), (5) firmware/NVRAM from the user's own phone image.
- **Gate 5**: iOS Settings shows Wi-Fi and the phone gets a connection.

## Phase 6: graphics

- Baseline today: CPU-rendered framebuffer through our IOMobileFramebuffer/IOSurface stand-ins (works for the boot logo).
- Research: Apple's GPU userland targets AGX; the Pixel 6a has an Arm Mali GPU. A real accelerated path needs a Metal/IOAccelerator
  layer over Mali (large). Scoped in `docs/research/17-gpu-kernel-gs101.md` (kernel side, read-only `shim --gpu-probe` first) and
  `docs/research/18-gpu-userland.md` (userland: sailfish-style Mesa Panfrost behind an EAGL shim; GLES, not Metal).

## Phase 4: input + USB

- Buttons: Alive GPIO poll (gpa7-3, gpa8-1, gpa10-1) into the existing `sweet_hid_key` hooks.
- Touch: verify controller from the live DT, then USI SPI + controller driver into `sweet_hid_touch`.
- USB: DWC3 gadget/ECM reuse with gs101 PHY bring-up.
- **Gate 4**: unlock, navigate, network over USB.

## Track B (parallel, after Gate 3): iPadOS 18

1. Mount the iPad7,11 iPadOS 18 SystemOS cryptex; stop if the shared cache is arm64e.
2. Minimal SWEET config on `xnu-11215`, then port the boot/storage/display/HID subset.
3. iPad identity (`/product`, 0059, 0060 canvas), root tweaks for the new build.

PAC emulation for iPhone iOS 17+ stays out of scope unless Track B proves the rebase path works
and an opcode census of an arm64e cache says it's tractable.


## Publishing layout: one private monorepo, three public repos (plan, 2026-10-22; nothing is published)

Status: *plan*, not decided. Nothing is pushed to a public remote until the user says so (AGENTS.md "Do not").
Generator side *implemented* (read from source + run of `tools/make-public-tree.py` on 2026-10-22, not yet reviewed by the user, nothing published):
`tools/public-manifest.json` assigns every tracked file to kernel / userland / site / private (`tools/test_public_manifest.py`),
`tools/make-public-tree.py OUTDIR --repo kernel|userland|site|all` writes `OUTDIR/<repo>/` with scan, reconstruction and a
cross-repo link rewrite (0 dangling), `--check` is the gate step `public-split` in `tools/check-all.sh`, and
`tools/pixos-workspace.sh` syncs `pixos-project/pixelios-kernel|userland|site`. Still open: the licence decision below, and
`tools/build-site.py` in the site repo needs `soc/` and `device/` from the kernel repo (*guess*: not verified standalone).
Precedent read from source (HackiOS, `oosexgang/hackios-xnu-kernel|userland|web`, ideas only): kernel, userland and website are
separate repositories; the kernel repo carries the Apple-licensed derivative work.

### Decision
- The working repo stays ONE private monorepo (git root). Reasons: a touch/clock fix usually spans `soc/`, `device/`, `shim/` and
  `xnu/patches` in one change; `tools/check-all.sh`, `tools/pix` and the delegate worktrees assume one tree.
- At publish time `tools/make-public-tree.py` writes one output tree per public repo from path lists (below). Each tree keeps the
  existing rules: files identical to the pinned `upstream/` (ios-sweet) are not copied but fetched at setup, modified ones become
  `upstream-patches/`, local paths are scrubbed, the private-data scan runs on every output, and the reconstruction check proves
  public trees + upstream rebuild the private tree byte for byte.

### Public repos (names are placeholders; org `PixOS-Project`)
| Repo | Contents (private-repo paths) | Licence |
|---|---|---|
| `pixelios-kernel` | `xnu/patches/`, `xnu/qr`, `shim/`, `soc/`, `device/`, `qrlog/`, board/ADT/payload tools (`tools/mkadt.py`, `mkpayload.py`, `boards.py`, `adt.py`, `fboot.sh`, `fflash-userdata.sh`, `to-fastboot.sh`, `phone-state`, `hang-recover`, `probe-run`, `xrun*`, `ci-kernel`, `stack-apply`, `check-all.sh`, `gate_select.py`, `test-bluejay-boot.py`, tests), `.github/workflows/xnu.yml`, `docs/research/` (public-safe ones), `docs/AUTOMATION.md`, `docs/BUILD.md`, `docs/SAFETY.md` | MIT for our files; `xnu/patches` are derivative of Apple code under APSL 2.0: ship them with the APSL notice and keep them in their own directory so the boundary is explicit (**open question: counsel/user decision before publishing**) |
| `pixelios-userland` | the iOS root recipe: `tools/build-ios-root.sh`, `build-ios-root-rootless.sh`, `rootless/`, `mkiosroot.sh`, `mkinit.py`, `sweet-init.S`, `sweet-root-tweaks.py`, `patch-launchd-plist.py`, `ios-root-plan.py`, `check-ios-root.py`, root-related docs (`docs/ROOTLESS_BUILD.md`) | MIT; contains NO Apple binaries: the IPSW is fetched on the user's machine |
| `pixelios-site` | `public-templates/` docs (index, STATUS, PLAN, CASE_STUDY, PORTING, MAP), `tools/build-site.py`, `.github/workflows/pages.yml`, screenshots/press assets | MIT / CC-BY for docs |
Shared by all: `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, a generated `README.md` linking the three repos (`public-templates/`).
Never in any public repo: `docs/HANDOFF.md`, `docs/tasks`, `docs/specs`, `.claude/`, `logs/`, `.env`, camera tooling credentials,
partition dumps, the REA container, `tools/third_party`, anything the scanner flags.

### Generator work (tools/make-public-tree.py)
1. Replace the single DROP list with a manifest `tools/public-manifest.json`: per repo `include` globs / `exclude` globs; every tracked
   file must be assigned to exactly one repo or to `private` (a test fails on an unassigned or doubly-assigned file).
2. `make-public-tree.py OUTDIR --repo kernel|userland|site|all` (default `all` writes `OUTDIR/<repo>/`); same scan + reconstruction per repo.
3. Cross-repo references (docs links, `tools/pix` subcommands for userland, the gate step that runs root checks) become relative-link
   rewrites or are dropped per repo; the generator reports every dangling link and the test requires zero.
4. `tools/pixos-workspace.sh` syncs the three clones under `pixos-project/` instead of one.
5. Gate step: `tools/make-public-tree.py /tmp/x --repo all --check` (no output kept) so a change that breaks the split fails `check-all.sh`.

### Order
1. Licence decision for `xnu/patches` (user). 2. Manifest + generator + tests (a Sonnet delegate, reviewed adversarially).
3. Dry run to `pixos-project/` (local only), read the three trees. 4. User decides when and where to publish.
Until step 4 the current single generated tree remains the only public-tree candidate.

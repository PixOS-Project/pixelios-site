# iOS 16.7 interface notes (build 20H392)

**Last verified: 2026-11-15.** Interface-level facts PixOS derived for interoperability with the iOS 16.7 (20H392) userland: selectors, traps,
struct and field layouts, protocol facts and observed behaviour, written in our own words. No addresses, no disassembly, no Apple code.

**These facts are per build.** Every selector number, size and layout here may differ on another iOS build: re-derive them from your
own decompile of your own IPSW before you rely on them ([Porting blueprint](BLUEPRINT.md#a-different-ios-build)). Tags: *obs* observed on hardware,
*read* read in our notes or sources, *bin* read in the binary by us, *guess* unconfirmed.

Generated from the maintainers' private fact store (187 rows); do not edit by hand.


## BT

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | BlueTool | callchain |  | BlueTool AppleBTMgmt selector calls: 0 PowerOn, 1 PowerOff (names inferred from log-string order) | guess |  |
| 20H392 | BlueTool | callchain |  | BlueTool arms a 30 s timer per request; on expiry it takes a stackshot and exits | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool arms a timeout per request; on expiry it takes a stackshot and exits | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool baud-change vendor cmd 01 18 FC 06 <baud>; result checked with opcode 0xfc18 | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool branch target when neither vendor nor internal install (b.ne) | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool btwake on; stores fd, logs error level, no exit | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool connect to the UART kernel control | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool copies the request's Bluetooth address into a buffer; whether its bcm -A command consumes it is unconfirmed | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool draws a random LE address from six one-byte arc4random_uniform calls and logs it as a random address | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool kern.bootargs read for address generator tokens | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool load of the obfuscated MobileGestalt key for the HW model string | guess |  |
| 20H392 | BlueTool | callchain |  | BlueTool power ON = close of the held /dev/btpoweroff fd | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool powers the chip off by opening the btpoweroff device node read-only and keeping the descriptor open in its context | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool puts the UART in raw mode (cfmakeraw), sets the speed and a cflag of 0x38b00 through TIOCGETA/TIOCSETA | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool raw write 01 2E FC 00 (0xfc2e minidriver) with usleep(0xc350)=50 ms | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool raw write of H4 packets on the control socket | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool read/select on the control socket | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool reads the UART CTS line with the TIOCMGET ioctl and logs its state | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool retries with a short sleep (~41 ms) up to 8 iterations while Wi-Fi is not up, logging each iteration | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool runCommandForCurrentConfig: override script lookup only if exactly one of _isVendorInstall/_isInternalInstall; else jumps to builtin step | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool socket(PF_SYSTEM) for kctl com.apple.uart.bluetooth (no .sk.) | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool stat of the override script file | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool status check of the 0xfc2e minidriver reply; chip-name switch follows | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool usleep(0xc350)=50 ms after minidriver cmd | bin |  |
| 20H392 | BlueTool | callchain |  | BlueTool's XPC reply carries an int64 result, an int64 manufacturer id and a firmware string | bin |  |
| 20H392 | BluetoothManager | callchain |  | BluetoothManager C callbacks call ObjC methods directly e.g. addDeviceIfNeeded: | bin |  |
| 20H392 | BluetoothManager | callchain |  | BluetoothManager _attach handleFailureInMethod when shared queue nil on a non-main thread | bin |  |
| 20H392 | BluetoothManager | callchain |  | BluetoothManager _restartScan calls _BTDiscoveryAgentStartScan: device-list scan, not via a CoreBluetooth session | bin |  |
| 20H392 | BluetoothManager | callchain |  | BluetoothManager setDevicePairingEnabled: does nothing (no error) while its session object is still nil | bin |  |
| 20H392 | MobileBluetooth | callchain |  | MobileBluetooth client: bluetoothd dropped first message -> non-dictionary reply -> result 0x515, retry with backoff | bin |  |
| 20H392 | MobileBluetooth | callchain |  | MobileBluetooth delays a session attach with an exponential retry/backoff on its async attach queue | bin |  |
| 20H392 | bluetoothd | callchain |  | AppleBTHci selector 2 (hci_write) takes a struct input of N items of 16 bytes each | bin |  |
| 20H392 | bluetoothd | callchain |  | BTDiscoveryAgentStartScan starts a classic inquiry in bluetoothd (a session asks for a classic scan) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd 1 s usleep before _exit(1) in the power-init failure path | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd A2DP SDP gate: attr 4 found -> state 4 else state 1 | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd AppleBTMgmt selector calls: 0 PowerOn, 1 PowerOff (names inferred from log-string order) | guess |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd AudioPipe nexus attrs: SLOT_BUF_SIZE 0x800, TX/RX_RINGS 1, TX/RX_SLOTS 8, MHINTS 2 | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd RX loop skips zero-length slots; RX slots carry raw UART bytes any chunking | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd SIGTERM (15) dispatch source set | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd VSC bitmap init id-9-only branch, not applicable to BCM_4357 | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd XPC listener event handler for the CB mach services | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd accepts the LE report while callbacks exist | guess |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd adsupport-style Discoverable/Connectable state set, read | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd assert in 0xfd48 parser when the reply has no instance-id byte | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd builds the BlueTool XPC request as a dictionary with a script name (e.g. boot) and the Bluetooth address as text | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd chipset-class reset wrapper: calls virtual slot +0x10 of this then slot +0x8 if 0; no BlueTool call (slot meaning unknown) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd chooses the Skywalk audio path or the shared-memory path through a virtual predicate on the audio device object (predicate not resolved) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd chooses the Skywalk or the plain control transport on one boolean check | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd close of the /dev/btwake fd | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd configures A2DP right after the streaming channel opens | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd connect(fd, sockaddr_ctl, len 0x20) to the UART control | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd creates the AudioPipe Skywalk server channel and logs its registration | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd doesDeviceMatch returns 0 (no match, no log) when the session gate check fails | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd exit(0) tail after the errx gate, reached BEFORE session attach and the runloop | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd exits with status 0 (no Bluetooth) when the device tree local-mac-address is absent or all zero | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd filters duplicate advertisements per session in doesDeviceMatch (a per-session advertisement-data map) and logs the drop | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd function prologue building the 0x110b UUID key | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd gate decision point (BD address + IOService present) at the end of the main preamble | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd kBTAudioMsgPropertyNexusUuid / SkywalkKey property sites | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd keeps looping (no exit) when chip power init returns a non-timeout error, logging that it stays in high power | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd limited-discoverable filter (inactive in the plain scan path) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd logs which service mask it connects to a device and whether the device is paired | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main CFRunLoopRun after server attach | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main attaches its local session (com.apple.bluetoothd) only after the presence gate passes | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main calls CBDaemonServer activate, entering -[CBDaemonServer _activate] | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main first sets its user dir suffix, then sets up its SCDynamicStore | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main reads the BT_DEVICE_ADDRESS environment variable (colon hex) and lets it override the device tree address | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main returns 1 when the local Bluetooth session cannot be attached, printing the error to stderr | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main session attach logs (com.apple.server.bluetooth); never reached when the gate errx fires | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main sscanf of BT_DEVICE_ADDRESS aa:bb:cc:dd:ee:ff | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main: IOService name gate (marconi-bt / bluetooth) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main: SCDynamicStore setup after _set_user_dir_suffix | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd main: no-address fallback via sysctl kern.bootargs wlan.debug.generate-mac / wlan.factory, stored in CFPreferences (rule not decoded in 109) | guess |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd matches the AppleConvergedIPCInterface IOService and dlopens AppleConvergedTransport.dylib (converged-IPC transport) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd matches the AppleConvergedIPCOLYBTControl IOService (transport 7) and rings its doorbell with a scalar IOConnect call | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd new peer connection path; no entitlement/TCC check before the object is built | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd non-sk path creates RxLoop thread after TIOCSETA | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd only logs when opening the btwake node fails and returns without changing the result (silent failure path) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd open of /dev/uart.log (uart.log file); none of its opens takes a bluetooth tty | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd opens one XPC mach-service connection to com.apple.BlueTool per request | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd opens the btwake device node read-only before opening the HCI socket, and closes it later; failure is logged as a BT_WAKE error | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd os_channel_create(uuid) then kqueue + os_channel_get_fd; I/O is on channel rings | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd parses kCBScanOptionAppleFilter* options (Payload, PayloadMask, Rssi, PuckType, ForceDups, Peers) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd power init success: power state 1, return 1 | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd presence gate: if the cu.bluetooth device node is accessible it skips the IOService check (it does not open it) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd presence gate: if the uart.bluetooth device node is accessible it skips the IOService check (it does not open it) | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd puts the Bluetooth address as text under the btaddress key of the BlueTool XPC request | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd puts the stage name under the script key of the BlueTool XPC request | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd read-back of paired devices from keychain | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd reads DT/IOService property transport-speed from the node named bluetooth | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd reference to the sk control name; com.apple.uart.bluetooth does not exist in bluetoothd | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd removes a stale local address from its plist and logs it | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd runBlueTool has an internal-diagnostics override gate before it asks BlueTool to boot the chip | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd runBlueTool use of the com.apple.BlueTool mach service name | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd second client UUID array gate | guess |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd sends a generic HCI_Reset (opcode 0x0c03) during bring-up | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd setenv call tied to BT_DEVICE_ADDRESS handling | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd socket(PF_SYSTEM=0x20,SOCK_DGRAM,SYSPROTO_CONTROL) for the UART kernel control | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd stores the link key in the keychain as 16 dash-separated hex pairs | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd stores the link key type in the keychain separately from the key data | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd treats a dotted bundle id outside com.apple.* as an app when BackBoardServices has no entry for it | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd tries to dlopen AppleConvergedTransport.dylib, which is absent on this root | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd wait point blocking in CFRunLoopRun when AppleBTHci is absent | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd waits 1 s and exits with status 1 when booting the chip times out or the platform/chipset combination is unknown | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd waits for the AppleBTHci IOService by name matching plus a first-match notification | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd wrapper pattern producing a logged 'VSC failed' only | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd xpc_connection_activate of the com.apple.bluetooth.xpc listener | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd's SDP parser recognises service-class UUID elements (element type 3) and writes a per-record attribute map | bin |  |
| 20H392 | bluetoothd | callchain |  | bluetoothd's singleton wrapper creates the Skywalk nexus provider | bin |  |
| 20H392 | bluetoothd | callchain |  | with multi-advertising off, bluetoothd uses a single advertising instance and sets the random address itself (HCI_LE_Set_Random_Address, type byte + 6 bytes) | bin |  |
| 20H392 | bluetoothd | selector | AppleBTHci sel 0 | AppleBTHci user-client selector 0 = hci_open, no args; item layout not decoded | bin |  |
| 20H392 | bluetoothd | selector | AppleBTHci sel 1 | AppleBTHci user-client selector 1 = hci_close, no args; item layout not decoded | bin |  |
| 20H392 | bluetoothd | selector | AppleBTHci sel 2 | AppleBTHci user-client selector 2 = hci_write: structIn N x 16-byte items, structOut >= 0x40 B + size word; item layout not decoded | bin |  |
| 20H392 | bluetoothd | selector | AppleBTHci sel 3 | AppleBTHci user-client selector 3 = hci_read: structIn N x 16 B, structOut + size (kAppleBTHciRead, EINTR retry); item layout not decoded | bin |  |
| 20H392 | bluetoothd | selector | AppleBTHci sel 4 | AppleBTHci user-client selector 4 = hci_transport_reset, no args; item layout not decoded | bin |  |

## GPU/CA

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | OpenGLES | callchain |  | +[EAGLContext setCurrentContext:] keeps the current context in a thread-local key that the gl* entry points read back | read |  |
| 20H392 | OpenGLES | callchain |  | EAGLContext attachImage returns NO for a FourCC that is not one of its four supported formats, after a log line | read |  |
| 20H392 | OpenGLES | callchain |  | glActiveTexture calls P+0xad8 = table offset 0xab8 = slot 342 (slot = P-offset/8 - 5) | read |  |
| 20H392 | OpenGLES | callchain |  | glDeleteProgram and glDeleteShader are identical stubs calling the same slot 591 (P+0x12a0, table offset 0x1280): two candidate names, unresolved | read |  |
| 20H392 | OpenGLES | callchain |  | glDiscardFramebufferEXT and glInvalidateFramebuffer both call slot 1023 (P+0x2020, table offset 0x2000) with identical stubs | read |  |
| 20H392 | PosterBoardServices | callchain |  | brk #0 at function +1592, reached only from the mkdtemp failure branch | read |  |
| 20H392 | QuartzCore | callchain |  | CA capture_backdrop gives up when create_surface returns NULL | read |  |
| 20H392 | QuartzCore | callchain |  | CA counts use itself by default: IncrementUseCount when an image is put in a slot | obs |  |
| 20H392 | QuartzCore | callchain |  | IOSurfaceLock(s,0,0)+IOSurfaceUnlock when seed [img+0x88] != [img+0x24] (unlock) | obs |  |
| 20H392 | QuartzCore | callchain |  | IsInUse reads state+0x18 != 0; our kernel never sets it (use-count traps count nothing), so every surface looks free | obs |  |
| 20H392 | QuartzCore | callchain |  | QuartzCore calls -[EAGLContext texImageIOSurface:...] from exactly two places; the surface-texture attach ignores its result | obs |  |
| 20H392 | QuartzCore | callchain |  | backboardd and PosterBoard call it; missing in our kernel (loud), GPU import coherence not established | read |  |
| 20H392 | QuartzCore | callchain |  | cold-path call inside attach_surface_texture reaching IOSurfaceAcceleratorCreate (needs YCbCr FourCC, helper object [ctx+0xb0], no converted surface yet); our kernel has no IOSurfaceAccelerator service | read |  |
| 20H392 | QuartzCore | callchain |  | create dict entry kIOSurfaceClientAddress = [img+0x58]; then Lock+Unlock | read |  |
| 20H392 | QuartzCore | callchain |  | the CA fragment program generator maps each slot's texture target: GL_TEXTURE_2D (0x0de1) -> 2D, GL_TEXTURE_3D (0x806f) -> 3D, anything else including 0 -> 2DRect; a 2DRect sampler means the pending target was 0 | obs |  |
| 20H392 | QuartzCore | field | CA::OGL::GLESContext+0x21c | CA::OGL::GLESContext+0x21c is a colour-match byte that QuartzCore only reads and never writes, so it stays 0 | obs |  |
| 20H392 | QuartzCore | field | CA::OGL::GLESContext+0x7f8 | GL dispatch table pointer (result of getMacroContextPrivate), stored in the constructor | obs |  |
| 20H392 | QuartzCore | field | CA::OGL::GLESContext+0x80c | max texture dimension L: min of nonzero IOSurfaceGetPropertyMaximum(width/height) clamp; used by the too-large gate | obs |  |
| 20H392 | QuartzCore | field | CA::OGL::GLESContext+0x810 | max bytes per row: IOSurfaceGetPropertyMaximum(kIOSurfaceBytesPerRow) clamp | obs |  |
| 20H392 | QuartzCore | field | CA::OGL::GLESContext+0x820 | max surface size = min(MAX_TEXTURE_SIZE, IOSurface max, MAX_VIEWPORT_DIMS); checked by create_surface and create_surface_from_iosurface | read |  |
| 20H392 | QuartzCore | field | CA::Render::Surface+0x68 | IOSurface passed to the constructor; NULL leaves attach_surface_texture without a wrapper | obs |  |
| 20H392 | QuartzCore | field | CA::Render::Texrec+0x34 | low 16 bits = GL texture target (0x0de1 or 0x806f), written by bind_image_impl and the Ex binders; 0 means unit empty -> assembler emits 2DRect | obs |  |
| 20H392 | QuartzCore | field | IOMFBServer+0x30d | bit 1 selects vsync source: 1 = IOMFB vsync run-loop source, 0 = CADisplayTimer | read |  |

## IOSurface/IOMFB

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | IOMobileFramebuffer | field | IOMobileFramebuffer conn+0xb38 | IOMobileFramebuffer keeps a benchmark-mode byte in its connection object, read from the benchmark CFPreferences key; default 0 | obs |  |
| 20H392 | IOSurface | callchain |  | IOCFSerialize(array,1) call that builds the sel 9 input buffer: [id][pad][binary [value,key]] | bin |  |
| 20H392 | IOSurface | callchain |  | IOSurface CreateChild reads the client address key from the create dictionary and records it in the client address set (the key's public name is inferred) | guess |  |
| 20H392 | IOSurface | callchain |  | dealloc path calling RemoveEventListener (sel 41) | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 10 | sel 10 UpdateNonBulkValueCache: in struct 9 bytes (id, pad, 0), out struct [u32][u32 generation][encoded dictionary of non-bulk values]; the kernel must write the real output size and return 0xe00002db if the buffer is too small | bin |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 11 | sel 11 RemoveValue: in struct id, pad, key UTF-8+NUL (empty = remove all), out struct = u32 new generation; 86 lists no kernel implementation (loud if called) | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 12 | sel 12 BindAccel: scalars in 3, no output; no QuartzCore importer, caller unknown; missing in our kernel | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 20 | sel 20 SetPurgeable: scalars in 2 (id, new state), scalar out 1 = old state | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 22 | sel 22 SetTiled: scalars in 2; sel 25 GetTileFormat: scalar in 1, scalar out 1; QuartzCore only calls IOSurfaceIsTiled (state page); missing in our kernel | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 27 | sel 27 SetBulkAttachments: struct in 136 bytes (id + 0x70-byte attachment block + mask); called once by backboardd and about 100 times by PosterBoard | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 35 | sel 35 CreateMachPortWithOptions: scalars in 2 (id, options), scalar out 1 = mach port name (0 on error) | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 40 | sel 40 SharedEvent AddEventListener: async method, wake port + 3-word async reference, no scalar/struct inputs; SpringBoard and AegirPoster call it; missing in our kernel, ignorable | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 41 | sel 41 SharedEvent RemoveEventListener: scalar in 1, no output; missing in our kernel, ignorable | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 42 | sel 42 SignalEvent: scalars in 4; QuartzCore calls it from layer_private_present; missing in our kernel (loud if called) | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 43 | sel 43 Init/SetDetachModeCode: scalars in 4 each; GetDetachModeCode reads state+0x14 byte; missing in our kernel, state+0x14 stays 0 | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 50 | sel 50-52 SetDataProperty / GetDataProperty / ClearDataProperties: QuartzCore calls only IOSurfaceGetDataProperty (iosurface_load_attachments); missing in our kernel | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 6 | sel 6 WrapClientImage: struct in 0x20, struct out 0xa68; backboardd calls it from CA::Render::Image::retain_iosurface; our kernel copies client rows in (snapshot semantics) | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 7 | sel 7 WrapClientMemory: scalars in 2, struct out 0xa68; never called by QuartzCore (hypothesis wrong for 7); our kernel answers kIOReturnUnsupported with a loud gap line | read |  |
| 20H392 | IOSurface | selector | IOSurfaceRootUserClient sel 9 | sel 9 SetValue: struct in = u32 id + pad + binary CFArray [value,key], struct out = u32 new generation; our kernel accepts and ignores, patch 0163 logs the key names | read |  |
| 20H392 | IOSurface | trap | IOSurfaceRootUserClient trap 0/1 | IOConnectTrap2 index 0/1 = Increment/DecrementUseCountForCategory(id, category), issued only on the 0->1 / 1->0 edge of the client-local count; our trapUseCount returns success and counts nothing, so info+0x18 stays 0 and IsInUse is always false | read |  |
| 20H392 | IOSurface | trap | IOSurfaceRootUserClient trap 2/3 | IOConnectTrap3 index 2/3 = Lock / Unlock (id, options, &seed); the kernel must re-copy client memory of wrapped surfaces here | read |  |

## VirtualAudio

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | MediaExperience | callchain |  | asks the VirtualAudio route configuration for active ports | bin |  |
| 20H392 | MediaExperience | callchain |  | cfstring use of bundle id com.apple.audio.CoreAudio.VirtualAudio; branch after it is the plug-in-lookup-failed path (expected empty route list [guess]) | bin |  |
| 20H392 | VirtualAudio | callchain |  | VirtualAudio AddPort sends its notification only when the port's connected flag changed during Connect | bin |  |
| 20H392 | VirtualAudio | callchain |  | VirtualAudio stores the AP port pointer at PortManager+0xd0 but never calls through it | bin |  |
| 20H392 | VirtualAudio | callchain |  | the VirtualAudio base-class Connect sets the port's connected flag and then refreshes the cached description, so base-class ports report connected | bin |  |
| 20H392 | VirtualAudio | callchain |  | the VirtualAudio route-failure log reports whether the source and destination port lists are non-empty, not the ports' connected flags | bin |  |

## Wi-Fi

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | Apple80211 | callchain |  | GetInfoCopy Get of AUTH_TYPE (2, 16 bytes) | bin |  |
| 20H392 | Apple80211 | callchain |  | extra CFString-keyed value fetched by GetInfoCopy | bin |  |
| 20H392 | wifid | callchain |  | IOInterfaceName match callback (match dictionary key) | bin |  |
| 20H392 | wifid | callchain |  | WiFiDeviceOpen CopyValue of CARD_CAPABILITIES (type 12, 13 bytes) | bin |  |
| 20H392 | wifid | callchain |  | event gate drop path: ASSOC_DONE 9, SCAN_DONE 10, 30 and 57 dropped unless wifid has a command pending; LINK_CHANGED 4 is not in the mask | bin |  |
| 20H392 | wifid | callchain |  | wifid CopyValue of HARDWARE_VERSION (type 44, 256 bytes) | bin |  |
| 20H392 | wifid | callchain |  | wifid Get POWER (type 19, 24 bytes) at WiFiDeviceOpen | bin |  |
| 20H392 | wifid | callchain |  | wifid Get of BSSID (type 9) | bin |  |
| 20H392 | wifid | callchain |  | wifid call of Apple80211GetInfoCopy when publishing State:/Network/Interface/en0/AirPort | bin |  |
| 20H392 | wifid | callchain |  | wifid keeps entries with SUP_CHANNEL and calls setChannel: here and setFlags:, then setSupportedChannels: | bin |  |
| 20H392 | wifid | callchain |  | wifid reader of OP_MODE (type 15) | bin |  |
| 20H392 | wifid | callchain |  | wifid reader of SUPPORTED_CHANNELS (27, 4824 bytes) | bin |  |
| 20H392 | wifid | callchain |  | wifid registers 62 events in WiFiDeviceOpen after EventMonitoringInit2; 3 more (ASSOC_DONE, SCAN_DONE, SOFTAP_CH_CHANGED_EVENT) | bin |  |
| 20H392 | wifid | callchain |  | wifid sets the country code with Apple80211 request type 51 (COUNTRY_CODE) | bin |  |
| 20H392 | wifid | callchain |  | wifid startup CopyValue of RSSI_BOUNDS (type 106, 16 bytes) | bin |  |

## system

| build | image | kind | name | fact | tag | |
|---|---|---|---|---|---|---|
| 20H392 | driverkitd | callchain |  | driverkitd holds an os_transaction only while it serves a kernel request | read |  |
| 20H392 | driverkitd | callchain |  | staging of the dext into the driverkitd store; copyfile | read |  |
| 20H392 | launchd_cache_loader | callchain |  | launchd_cache_loader looks for launchd_unsecure_cache= in the boot-args; present -> it uses the unsecure cache, absent -> the no-boot-args path | bin |  |
| 20H392 | libdispatch | callchain |  | frame in the abort chain: libdispatch catches the ObjC exception in a dispatch_async block and calls terminate | obs |  |
| 20H392 | libsystem_kernel | callchain |  | libsystem_kernel work_interval_instance_start calls the work_interval_ctl syscall with operation 6; open-source XNU 8796 defines operations 1-5 and 9-11 and returns ENOTSUP for 6 | bin |  |
| 20H392 | tccd | callchain |  | tccd policy function calls [service pardonMissingUsage]; if false the usage-description crash message is built | bin |  |
| 20H392 | tccd | callchain |  | tccd sets the formatted message as servicePolicyAction | bin |  |

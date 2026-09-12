---
name: esp32-serial-monitor
description: Connect to an ESP32 device over USB serial, send commands, and capture/parse its tagged log output for interactive debugging and manual protocol testing. Use when the user asks to talk to an ESP32/PlatformIO device over serial, watch its boot log, send a command and check the response, or manually drive a device through a multi-step flow (e.g. provisioning, enrollment) outside of an automated build.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/esp32-serial-monitor/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# ESP32 Serial Monitor Connection

Open a USB serial connection to an ESP32, send commands, and parse the device's own tagged
log lines to judge success/failure — for interactive, back-and-forth debugging sessions.

## When to use this vs. `esp32-firmware-engineer`

- **`esp32-firmware-engineer` agent**: one-shot bounded capture right after a build/upload
  (`pio device monitor` with a timeout) to verify a change worked.
- **This skill**: an open-ended interactive session — connect, watch boot output, send one
  or more commands, inspect responses, possibly repeat. Use it when the task is exploratory
  ("what does the device print when I send X") or spans a multi-step protocol (activation,
  pairing, a config handshake) rather than a single build-then-verify cycle.

## Detection

Identify available serial ports and match to the ESP32's USB-to-serial chip. The common
chips on ESP32 dev boards are CH340/CH343, CP210x and PL2303 — match by VID:PID, not by
port name, since port names shift across reboots and OSes.

**Windows (PowerShell):**
```powershell
$ports = Get-CimInstance Win32_PnPEntity | Where-Object {
  $_.PNPDeviceID -match "1A86:55D3|10C4:EA60|067B:2303"
}
$ports | Select-Object Description, @{N="ComPort"; E={($_.Description -match 'COM\d+' ? $Matches[0] : 'N/A')}}
```

**Linux:**
```bash
ls -la /dev/tty* | grep -E "USB|ACM"
udevadm info -n /dev/ttyUSB0 | grep ID_VENDOR_ID
```

If more than one candidate port matches, list them and ask which one to use — don't guess.

## Configuration

- **Baud rate**: 115200 is the common ESP32 default, but it's a project setting — grep the
  firmware for its serial-init call (e.g. `Serial.begin(...)`) or check `platformio.ini`'s
  `monitor_speed` before assuming it.
- **Line ending**: LF (`\n`)
- **Timeout**: 5000ms is a reasonable default for a command response; widen it for anything
  that waits on network/modem registration.
- **Non-blocking**: read only the bytes already available per iteration, don't block waiting
  for more.

## Connection Flow

1. **Detect port** — find the available COM/tty port matching the ESP32's USB-serial chip.
2. **Open** — `serial.Serial(port, baudrate, timeout=1)`.
3. **Monitor boot** — read the device's startup log before sending anything; it usually
   carries the most useful state (last reset reason, provisioning state, init failures).
4. **Send command** — `port.write((command + "\n").encode())`.
5. **Parse response** — match lines against the project's own tagged-log pattern.
6. **Close** — `port.close()`.

## Log Format

Don't assume a fixed log schema. Many ESP32 projects use a tagged format like:

```
[<timestamp>][TAG] LEVEL - message
[30008][ENROLL] INFO - Code accepted: ABCD****
[BOOT] ERROR - Modem init failed
```

parsed with something like `\[(\d+)?\]\[(\w+)\]\s+(\w+)\s*-?\s*(.*)` — but grep the actual
firmware's `Serial.print`/`Serial.println` calls first to confirm the real convention
(tag set, separator, whether a timestamp is even present) before reusing this regex. Treat
the pattern above as a starting point, not a given.

## Test Sequence Template

Structure an interactive verification as:

1. **Capture boot output** for a few seconds without sending anything — note any error/warn
   tags already present (e.g. a failed init from a previous run).
2. **Send one known command** the firmware is expected to handle, and match the response
   against the project's own success/failure log vocabulary (discovered above) — not a
   generic "OK"/"ERROR" guess.
3. **Repeat for each step of a multi-step flow** (e.g. a provisioning/enrollment sequence),
   waiting long enough between steps for network or peripheral init (modem registration,
   NTP sync) to complete before judging failure.

## Python Helper (PySerial)

Don't reinvent the connection/parsing logic — use [esp32_serial.py](esp32_serial.py):

```bash
cd "${CLAUDE_SKILL_DIR}"
python -m pip install pyserial   # inside the project's virtual environment
```

`${CLAUDE_SKILL_DIR}` resolves to this skill's own directory regardless of where the plugin
is installed, so the path stays correct on every machine.

```bash
python esp32_serial.py                       # auto-detect port, print boot output
python esp32_serial.py --port COM5            # use a specific port
python esp32_serial.py --send "PING" --timeout 5000
```

Or import it directly for a scripted multi-step session:

```python
from esp32_serial import ESP32SerialMonitor

with ESP32SerialMonitor() as monitor:      # auto-detects port, connects, closes on exit
    boot_lines = monitor.read_boot_output(timeout_ms=3000)
    response = monitor.send("PING", timeout_ms=5000)
    for line in response:
        parsed = monitor.parse_log_line(line)
        if parsed:
            print(parsed["tag"], parsed["level"], parsed["message"])
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port occupied | Check if a PlatformIO monitor, VSCode terminal, or other tool already has the port open |
| No output after connect | Verify baud rate, check the USB cable, try a board reset |
| Garbled text | Baud-rate mismatch — confirm against the firmware's `Serial.begin(...)` / `monitor_speed` |
| Timeout waiting for response | Device may be stuck — check watchdog behavior, try a reset |
| Port not detected | Verify the USB-serial driver is installed (CH340/CH343 or CP210x) |

#!/usr/bin/env python3
"""ESP32 Serial Monitor Helper - Connect, send commands, parse tagged log lines.

Reusable for any ESP32/PlatformIO project's serial console. Auto-detects the port by the
USB-to-serial chip's VID:PID (CH340/CH343, CP210x, PL2303 - the common chips on ESP32 dev
boards), not by port name, since port names shift across reboots and OSes.

CLI usage:
    python esp32_serial.py                       # auto-detect port, print boot output
    python esp32_serial.py --port COM5            # use a specific port
    python esp32_serial.py --send "PING" --timeout 5000
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from typing import Dict, List, Optional

import serial
import serial.tools.list_ports

KNOWN_USB_SERIAL_IDS = ["1A86:55D3", "10C4:EA60", "067B:2303"]


class ESP32SerialMonitor:
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        self.port = port or self._find_esp32_port()

    def _find_esp32_port(self) -> str:
        """Auto-detect ESP32 serial port by USB VID:PID."""
        for port, desc, hwid in serial.tools.list_ports.comports():
            if any(vid in hwid for vid in KNOWN_USB_SERIAL_IDS):
                print(f"[OK] Found ESP32: {port} - {desc}")
                return port
        raise RuntimeError("[FAIL] No ESP32 serial port found. Check USB cable and drivers.")

    def connect(self) -> bool:
        """Open the serial port."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(0.5)  # Wait for device to be ready
            print(f"[OK] Connected to {self.port} @ {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            print(f"[FAIL] Failed to open {self.port}: {e}")
            return False

    def send(self, command: str, timeout_ms: int = 5000) -> List[str]:
        """Send a command and return the response lines captured within timeout_ms."""
        if not self.ser and not self.connect():
            return []

        print(f"\n[>>>] Sending: {command}")
        self.ser.write((command + "\n").encode())
        self.ser.flush()
        return self.read_until_timeout(timeout_ms)

    def read_until_timeout(self, timeout_ms: int = 5000) -> List[str]:
        """Read lines until timeout_ms elapses with no more input assumed."""
        lines: List[str] = []
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            if self.ser and self.ser.in_waiting:
                line = self.ser.readline().decode(errors="replace").strip()
                if line:
                    lines.append(line)
                    print(line)
        return lines

    def read_boot_output(self, timeout_ms: int = 3000) -> List[str]:
        """Read device boot output without sending anything."""
        print("[>>>] Listening for boot output...")
        return self.read_until_timeout(timeout_ms)

    def parse_log_line(self, line: str) -> Optional[Dict]:
        """Extract tag, level, timestamp from a `[timestamp][TAG] LEVEL - message` line.

        This is a common convention, not a universal one - confirm the project's actual
        log format (grep its Serial.print/Serial.println calls) before relying on it.
        """
        match = re.match(r"\[(\d+)?\]\[(\w+)\].*?(\w+)\s*-?\s*(.*)", line)
        if match:
            timestamp, tag, level, message = match.groups()
            return {
                "timestamp": int(timestamp) if timestamp else None,
                "tag": tag,
                "level": level or "INFO",
                "message": message.strip(),
            }
        return None

    def close(self) -> None:
        """Close the serial connection."""
        if self.ser:
            self.ser.close()
            print(f"[OK] Disconnected from {self.port}")

    def __enter__(self) -> "ESP32SerialMonitor":
        self.connect()
        return self

    def __exit__(self, *args) -> None:
        self.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="ESP32 serial monitor helper")
    parser.add_argument("--port", help="Serial port (default: auto-detect)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--send", help="Command to send after connecting")
    parser.add_argument(
        "--timeout", type=int, default=5000, help="Response timeout in ms (default: 5000)"
    )
    args = parser.parse_args()

    try:
        with ESP32SerialMonitor(port=args.port, baudrate=args.baud) as monitor:
            if not monitor.ser:
                return 1

            print("\n[Step 1] Reading boot output...")
            boot_lines = monitor.read_boot_output(timeout_ms=3000)
            if not boot_lines:
                print("[WARN] No boot output received. Device may already be running.")

            if args.send:
                print(f"\n[Step 2] Sending command: {args.send}")
                monitor.send(args.send, timeout_ms=args.timeout)

        return 0
    except RuntimeError as e:
        print(f"\n[FAIL] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

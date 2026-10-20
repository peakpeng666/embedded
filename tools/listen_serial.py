#!/usr/bin/env python3
"""Capture existing serial output without sending commands to the firmware."""

import argparse
from datetime import datetime
from pathlib import Path
import time

import serial
from serial.tools import list_ports


def main(seconds):
    matches = [
        port for port in list_ports.comports()
        if (port.vid, port.pid, port.serial_number) == (0x04D8, 0x00DF, "ATK-03262021")
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one ATK serial port, found {len(matches)}.")
    port = serial.Serial(
        port=None, baudrate=115200, timeout=0.2,
        xonxoff=False, rtscts=False, dsrdtr=False, exclusive=True,
    )
    port.dtr = False
    port.rts = False
    port.port = matches[0].device
    captured = bytearray()
    print(f"Listening on {port.port}: 115200 baud, 8N1, {seconds}s; no serial data sent.", flush=True)
    try:
        port.open()
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            data = port.read(4096)
            if data:
                captured.extend(data)
                print(data.decode("utf-8", errors="replace"), end="", flush=True)
    finally:
        port.close()
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    log = Path(__file__).resolve().parents[1] / "logs" / f"serial_{stamp}.bin"
    log.parent.mkdir(exist_ok=True)
    log.write_bytes(captured)
    print(f"\nCaptured {len(captured)} bytes. Log: {log}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=8)
    args = parser.parse_args()
    main(max(1, min(args.seconds, 60)))

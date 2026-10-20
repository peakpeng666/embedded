#!/usr/bin/env python3
"""Request the installed RT-Thread firmware's version over USB serial."""

from datetime import datetime
import json
from pathlib import Path
import re
import time

import serial
from serial.tools import list_ports


def main():
    matches = [
        p for p in list_ports.comports()
        if (p.vid, p.pid, p.serial_number) == (0x04D8, 0x00DF, "ATK-03262021")
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one ATK serial port, found {len(matches)}.")
    result = {"port": matches[0].device, "baud": 115200, "format": "8N1"}
    with serial.Serial(
        matches[0].device, baudrate=115200, timeout=0.05, write_timeout=1,
        xonxoff=False, rtscts=False, dsrdtr=False, exclusive=True,
    ) as port:
        def capture(seconds):
            data = bytearray()
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                data.extend(port.read(4096))
            return {
                "bytes": len(data), "hex": data.hex(),
                "text": data.decode("utf-8", "replace"),
            }

        result["initial"] = capture(0.5)
        port.write(b"\r\n")
        port.flush()
        result["blank_line"] = capture(0.5)
        port.write(b"version\r\n")
        port.flush()
        result["version_reply"] = capture(2)
    reply = result["version_reply"]["text"]
    result["verified"] = bool(
        "Thread Operating System" in reply
        and re.search(r"\b4\.0\.1\b", reply)
        and "msh />" in reply
    )
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    result["time"] = stamp
    destination = Path(__file__).resolve().parents[1] / "logs" / f"serial_check_{stamp}.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    print(f"Report: {destination}", flush=True)
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

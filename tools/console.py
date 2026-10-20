#!/usr/bin/env python3
"""Open the matching board's serial console on Windows or Linux."""
import argparse
import subprocess
import sys
from serial.tools import list_ports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="Optional explicit port, for example COM5")
    args = parser.parse_args()
    port = args.port
    if not port:
        matches = [p for p in list_ports.comports()
                   if (p.vid, p.pid, p.serial_number) == (0x04d8, 0x00df, "ATK-03262021")]
        if len(matches) != 1:
            parser.error("Connect USB_COM or specify --port COMx. Available ports: "
                         + ", ".join(p.device for p in list_ports.comports()))
        port = matches[0].device
    print("115200 / 8N1; status or help; Ctrl+] exits.", flush=True)
    return subprocess.call([sys.executable, "-m", "serial.tools.miniterm", "--raw", "--eol", "CR",
                            "--dtr", "0", "--rts", "0", port, "115200"])


if __name__ == "__main__":
    raise SystemExit(main())

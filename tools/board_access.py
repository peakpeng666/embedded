#!/usr/bin/env python3
"""Grant or revoke temporary access to the connected ATK probe for the sudo user.

No persistent udev rules, group changes, or device firmware writes.
Run --check without sudo to inspect the matching device nodes.
"""

import argparse
import os
from pathlib import Path
import pwd
import subprocess


def device_nodes():
    found = []
    for path in Path("/sys/bus/usb/devices").glob("*"):
        try:
            identity = tuple(
                (path / field).read_text().strip()
                for field in ("idVendor", "idProduct", "serial")
            )
        except OSError:
            continue
        if identity == ("04d8", "00df", "ATK-03262021"):
            found.append(path)
    if len(found) != 1:
        raise RuntimeError(f"Expected exactly one ATK probe, found {len(found)}.")
    device = found[0]
    bus = int((device / "busnum").read_text())
    number = int((device / "devnum").read_text())
    nodes = [Path(f"/dev/bus/usb/{bus:03d}/{number:03d}")]
    for kind, pattern in (("tty", "ttyACM*"), ("hidraw", "hidraw*")):
        for entry in (Path("/sys/class") / kind).glob(pattern):
            if device.resolve() in (entry / "device").resolve().parents:
                nodes.append(Path("/dev") / entry.name)
    if not all(node.is_char_device() for node in nodes):
        raise RuntimeError("A matching device node disappeared; retry after reconnecting.")
    return nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--revoke", action="store_true")
    args = parser.parse_args()
    nodes = device_nodes()
    if args.check:
        for node in nodes:
            print(f"{node}: read={os.access(node, os.R_OK)} write={os.access(node, os.W_OK)}")
        return
    uid = int(os.environ.get("SUDO_UID", "-1"))
    if os.geteuid() != 0 or uid <= 0:
        parser.error("Run this command with sudo from your ordinary user account.")
    name = pwd.getpwuid(uid).pw_name
    operation = ["-x", f"u:{uid}"] if args.revoke else ["-m", f"u:{uid}:rw"]
    subprocess.run(["/usr/bin/setfacl", *operation, "--", *map(str, nodes)], check=True)
    print(f"{'Revoked' if args.revoke else 'Granted'} temporary access for {name}:")
    for node in nodes:
        print(node)


if __name__ == "__main__":
    main()

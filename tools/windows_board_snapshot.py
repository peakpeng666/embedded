#!/usr/bin/env python3
"""Read this board's internal Flash without halting/resetting/programming it."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path

from pyocd.core.helpers import ConnectHelper
from pyocd.coresight.ap import AccessPort, APv1Address, MEM_AP
from pyocd.coresight.dap import DP_CTRL_STAT, MASKLANE, TRNNORMAL
from pyocd.probe.debug_probe import DebugProbe


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("label", choices=("before_keil", "after_keil"))
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    session = ConnectHelper.session_with_chosen_probe(
        unique_id="ATK-03262021", blocking=False, auto_open=False,
        no_config=True, target_override="cortex_m", frequency=1_000_000,
        connect_mode="attach", auto_unlock=False, resume_on_disconnect=False,
        **{"pack.debug_sequences.enable": False, "user_script": os.devnull},
    )
    if session is None:
        raise RuntimeError("Expected ATK probe not found")
    dp = session.target.dp
    connected = False
    try:
        session.open(init_board=False)
        dp.connect(DebugProbe.Protocol.SWD)
        connected = True
        ap = AccessPort.create(dp, APv1Address(0))
        assert isinstance(ap, MEM_AP)
        assert ap.read32(0xE0042000) == 0x20006461, "Unexpected MCU"
        assert ap.read16(0x1FFF75E0) == 512, "Unexpected Flash size"
        assert ap.read32(0x40022020) & 0xFF == 0xAA, "Read protection enabled"
        data = bytearray()
        for offset in range(0, 512 * 1024, 4096):
            data.extend(ap.read_memory_block8(0x08000000 + offset, 4096))
            if len(data) % 65536 == 0:
                print(f"Read {len(data)//1024}/512 KiB", flush=True)
        halted = bool(ap.read32(0xE000EDF0) & (1 << 17))
    finally:
        try:
            if connected:
                dp.power_down_debug()
                dp.write_reg(DP_CTRL_STAT, MASKLANE | TRNNORMAL)
                dp.flush()
        finally:
            session.close()
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    destination = ROOT / "backups" / f"windows_{args.label}_{stamp}.bin"
    destination.parent.mkdir(exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(data)
    assert destination.read_bytes() == data
    record = {
        "time": stamp, "label": args.label, "file": str(destination),
        "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "core_halted_at_end": halted,
        "bootloader_sha256": hashlib.sha256(data[:0x10000]).hexdigest(),
        "application_tail_sha256": hashlib.sha256(data[0x11000:]).hexdigest(),
    }
    if args.compare:
        before = args.compare.read_bytes()
        assert len(before) == len(data)
        assert before[:0x10000] == data[:0x10000], "Bootloader changed"
        assert before[0x11000:] == data[0x11000:], "Flash outside application pages changed"
        record["outside_0x08010000_0x08010fff_unchanged"] = True
        record["changed_bytes"] = sum(a != b for a, b in zip(before, data))
    (ROOT / "logs").mkdir(exist_ok=True)
    log = ROOT / "logs" / f"windows_{args.label}.json"
    log.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()

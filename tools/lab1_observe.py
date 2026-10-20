#!/usr/bin/env python3
"""Observe real button levels, LED outputs and UART; never drive GPIO or flash."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import time

from elftools.elf.elffile import ELFFile
from pyocd.core.helpers import ConnectHelper
from pyocd.coresight.ap import AccessPort, APv1Address
from pyocd.coresight.dap import DP_CTRL_STAT, MASKLANE, TRNNORMAL
from pyocd.probe.debug_probe import DebugProbe

from lab1_flash import open_serial

ROOT = Path(__file__).resolve().parents[1]


def observe(seconds):
    stopped = False
    def request_stop(_signal, _frame):
        nonlocal stopped
        stopped = True
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    with (ROOT / "lab1/build/lab1.elf").open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    path = ROOT / "logs" / f"lab1_observe_{stamp}.json"
    result = {"time": stamp, "requested_seconds": seconds, "samples": [], "serial": []}
    session = ConnectHelper.session_with_chosen_probe(
        unique_id="ATK-03262021", blocking=False, auto_open=False, no_config=True,
        target_override="cortex_m", frequency=100000, connect_mode="attach",
        auto_unlock=False, resume_on_disconnect=False,
        **{"pack.debug_sequences.enable": False, "user_script": os.devnull,
           "cmsis_dap.limit_packets": True, "cmsis_dap.deferred_transfers": False})
    port = open_serial()
    dp = session.target.dp
    connected = False
    try:
        session.open(init_board=False)
        dp.connect(DebugProbe.Protocol.SWD)
        connected = True
        ap = AccessPort.create(dp, APv1Address(0))
        if ap.read32(0xe000ed08) != 0x08010000:
            raise RuntimeError("Lab application VTOR not active")
        result["registers"] = {
            name: hex(ap.read32(address)) for name, address in {
                "GPIOE_MODER": 0x48001000, "GPIOE_OTYPER": 0x48001004,
                "GPIOD_MODER": 0x48000c00, "GPIOD_PUPDR": 0x48000c0c,
                "EXTI_IMR1": 0x40010400, "EXTI_RTSR1": 0x40010408,
                "EXTI_FTSR1": 0x4001040c, "SYSCFG_EXTICR3": 0x40010010,
                "NVIC_ISER0": 0xe000e100, "RCC_CFGR": 0x40021008,
                "USART1_BRR": 0x4001380c,
            }.items()}
        port.timeout = 0
        port.write(b"status\r")
        started, next_status = time.monotonic(), time.monotonic() + 5
        previous = None
        pending_text = ""
        print(f"OBSERVING {seconds}s; physical button presses can begin. Log: {path}", flush=True)
        while not stopped and time.monotonic() - started < seconds:
            now = time.monotonic()
            chunk = port.read(4096)
            if chunk:
                pending_text += chunk.decode(errors="replace")
                while "\n" in pending_text:
                    line, pending_text = pending_text.split("\n", 1)
                    line = line.rstrip("\r")
                    result["serial"].append({"seconds": round(now - started, 3), "text": line})
                    print(line, flush=True)
            if now >= next_status:
                port.write(b"status\r")
                next_status = now + 5
            keys = (~ap.read32(0x48000c10) >> 9) & 3
            leds = (~ap.read32(0x48001014) >> 7) & 7
            ms = ap.read32(symbols["milliseconds"])
            state = (keys, leds)
            if state != previous:
                result["samples"].append({"seconds": round(now - started, 4),
                                          "milliseconds": ms,
                                          "keys_PD10_PD9": keys, "leds_BGR": leds})
                previous = state
            time.sleep(0.015)
        result["duration_seconds"] = time.monotonic() - started
        result["status"] = "captured"
    except KeyboardInterrupt:
        result["status"] = "capture_stopped"
    finally:
        port.close()
        # Save captured evidence even if the debug adapter cannot acknowledge
        # power-down. SIGINT is a stop flag, never an interruption mid-packet.
        try:
            if connected:
                result["debug_power_acknowledged_off"] = dp.power_down_debug()
                dp.write_reg(DP_CTRL_STAT, MASKLANE | TRNNORMAL)
                dp.flush()
        except Exception as error:
            result["cleanup_error"] = str(error)
        finally:
            session.close()
        path.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Saved {len(result['samples'])} output/input transitions: {path}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=180)
    observe(max(5, min(parser.parse_args().seconds, 600)))

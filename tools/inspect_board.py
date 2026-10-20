#!/usr/bin/env python3
"""Read STM32L4 identity/status and optionally back up its internal flash.

Uses pyOCD's DP/MEM-AP API without initializing a CPU target, loading a flash
algorithm, halting/resetting the CPU, or writing target memory/peripherals.
The debug transport necessarily configures its own DP/AP control registers.
"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

from pyocd.core.helpers import ConnectHelper
from pyocd.coresight.ap import AccessPort, APv1Address, MEM_AP
from pyocd.coresight.dap import DP_CTRL_STAT, MASKLANE, TRNNORMAL
from pyocd.probe.debug_probe import DebugProbe


ROOT = Path(__file__).resolve().parents[1]
PROBE_ID = "ATK-03262021"
FAMILIES = {0x415: "STM32L47x/L48x", 0x461: "STM32L49x/L4Ax"}


def inspect(backup=False):
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    result = {"time": stamp, "probe": PROBE_ID, "swd_hz": 100_000}
    session = ConnectHelper.session_with_chosen_probe(
        unique_id=PROBE_ID,
        blocking=False,
        auto_open=False,
        no_config=True,
        target_override="cortex_m",
        frequency=100_000,
        connect_mode="attach",
        auto_unlock=False,
        resume_on_disconnect=False,
        **{"pack.debug_sequences.enable": False, "user_script": "/dev/null"},
    )
    if session is None:
        raise RuntimeError("The expected ATK debug probe was not found.")

    dp = session.target.dp
    connected = False
    try:
        session.open(init_board=False)
        dp.connect(DebugProbe.Protocol.SWD)
        connected = True
        ap = AccessPort.create(dp, APv1Address(0))
        if not isinstance(ap, MEM_AP):
            raise RuntimeError("AP0 is not a memory access port.")

        result["dp_id"] = f"0x{dp.dpidr.idr:08x}"
        result["cpuid"] = f"0x{ap.read32(0xE000ED00):08x}"
        chip_id = ap.read32(0xE0042000)
        result["dbgmcu_idcode"] = f"0x{chip_id:08x}"
        device_id = chip_id & 0xFFF
        if device_id not in FAMILIES:
            raise RuntimeError(f"Unexpected device ID 0x{device_id:03x}; stopping.")
        result["family"] = FAMILIES[device_id]
        flash_kib = ap.read16(0x1FFF75E0)
        result["flash_kib"] = flash_kib
        if flash_kib not in (512, 1024):
            raise RuntimeError(f"Unexpected flash size {flash_kib}; stopping.")

        option_register = ap.read32(0x40022020)
        result["flash_optr_read_only"] = f"0x{option_register:08x}"
        result["rdp_byte"] = f"0x{option_register & 0xFF:02x}"
        status = ap.read32(0xE000EDF0)
        result["core_halted"] = bool(status & (1 << 17))
        result["core_sleeping"] = bool(status & (1 << 18))
        result["core_lockup"] = bool(status & (1 << 19))
        if (option_register & 0xFF) != 0xAA:
            raise RuntimeError("Read protection is enabled; no unlock will be attempted.")

        vectors = ap.read_memory_block32(0x08000000, 2)
        result["initial_stack"] = f"0x{vectors[0]:08x}"
        result["reset_vector"] = f"0x{vectors[1]:08x}"
        # Configuration/status registers only; never read UART RDR, since it
        # would consume data belonging to the running application.
        result["uart1_diagnostic"] = {
            name: f"0x{ap.read32(address):08x}"
            for name, address in {
                "RCC_CR": 0x40021000,
                "RCC_CFGR": 0x40021008,
                "RCC_PLLCFGR": 0x4002100C,
                "RCC_CCIPR": 0x40021088,
                "USART1_CR1": 0x40013800,
                "USART1_CR2": 0x40013804,
                "USART1_CR3": 0x40013808,
                "USART1_BRR": 0x4001380C,
                "USART1_ISR": 0x4001381C,
                "GPIOA_MODER": 0x48000000,
                "GPIOA_IDR": 0x48000010,
                "GPIOA_AFRH": 0x48000024,
            }.items()
        }
        print(json.dumps(result, indent=2), flush=True)

        if backup:
            data = bytearray()
            total = flash_kib * 1024
            for offset in range(0, total, 4096):
                data.extend(ap.read_memory_block8(0x08000000 + offset, min(4096, total - offset)))
                if len(data) % 65536 == 0 or len(data) == total:
                    print(f"Backup: {len(data) // 1024}/{flash_kib} KiB", flush=True)
            digest = hashlib.sha256(data).hexdigest()
            destination = ROOT / "backups" / f"stm32l4_internal_flash_{stamp}.bin"
            destination.parent.mkdir(exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(data)
            if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                raise RuntimeError("Backup file verification failed.")
            result["backup"] = str(destination)
            result["backup_bytes"] = len(data)
            result["backup_sha256"] = digest
            result["backup_scope"] = "Internal flash only; excludes external flash and option bytes."
            print(f"Backup saved: {destination}\nSHA256: {digest}", flush=True)
        result["status"] = "ok"
    except Exception as error:
        result["status"] = "failed"
        result["error"] = str(error)
        raise
    finally:
        try:
            if connected:
                result["debug_power_acknowledged_off"] = dp.power_down_debug()
                # Some MCUs keep power ACK asserted. Clear both request bits
                # after the standard two-stage release attempted above.
                dp.write_reg(DP_CTRL_STAT, MASKLANE | TRNNORMAL)
                dp.flush()
                result["debug_power_request_bits_clear"] = not bool(
                    dp.read_reg(DP_CTRL_STAT) & 0x50000000
                )
        finally:
            session.close()
        log_dir = ROOT / "logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / f"chip_{stamp}.json"
        log_path.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Report: {log_path}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup", action="store_true", help="Read internal flash into a local backup file.")
    args = parser.parse_args()
    try:
        inspect(args.backup)
    except Exception as error:
        print(f"Stopped: {error}", file=sys.stderr)
        sys.exit(1)

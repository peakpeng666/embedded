#!/usr/bin/env python3
"""Apply/restore only the two audited Lab 1 application pages.

Requires the original backup and the pinned lab binary. No chip erase, option
programming, unlocking, or arbitrary file/address input is provided.
"""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import time

from pyocd.core.helpers import ConnectHelper
from pyocd.core.target import Target
from pyocd.flash.flash import Flash
import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "backups/stm32l4_internal_flash_20261020T154711+0900.bin"
BACKUP_SHA = "18b55e23284658dd10fe83259900c99e0479a75a3094362e85b7939ecc05fc3d"
#
# New source builds are not silently picked up by this audited two-page tool.
IMAGE = ROOT / "firmware/lab1.bin"
IMAGE_SHA = "231683d50a998b4049ab6d5d939e86cf33b15599c28d222b3fb2cdfc777cec27"
PREVIOUS_IMAGES = (
    (ROOT / ".local_archive/releases/lab1_single_led_20261020.bin",
     "e1f959683b8b7baaf0a468c42e93b92bad7ae5c8fb2ae0204c830b826871be6e"),
)
PACK = ROOT / ".toolchains/Keil.STM32L4xx_DFP.3.1.0.pack"
PACK_SHA = "5672383c07fbdcee0e471a33f4f8beb2e1f3200bc999244dcd6858e0e8e8203f"
FLASH_BASE, FLASH_SIZE = 0x08000000, 512 * 1024
APP, SPAN, SECTOR = 0x08010000, 4096, 2048
OPTION_OFFSETS = (0x20, 0x24, 0x28, 0x2c, 0x30, 0x44, 0x48, 0x4c, 0x50)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_flash(ap, label, candidates, log):
    data = bytearray()
    # Faster transport only for reads, checked byte for byte against a known
    # image. Erasing and programming retain the established 100 kHz setting.
    ap.dp.probe.set_clock(500000)
    try:
        for offset in range(0, FLASH_SIZE, 4096):
            address = FLASH_BASE + offset
            chunk = bytes(ap.read_memory_block8(address, 4096))
            expected = [item[offset:offset + 4096] for item in candidates]
            if chunk not in expected:
                # Do not "fix" bytes from the expected image. Re-read the actual
                # target twice in small transfers and require both to agree.
                retries = [
                    b"".join(bytes(ap.read_memory_block8(address + p, 128))
                             for p in range(0, 4096, 128))
                    for _ in range(2)
                ]
                log.setdefault("read_transfer_retries", []).append(
                    {"phase": label, "address": hex(address),
                     "first_sha256": sha(chunk), "retry_sha256": [sha(r) for r in retries]})
                require(retries[0] == retries[1] and retries[0] in expected,
                        f"Confirmed readback mismatch at {address:#010x}; no further erase")
                chunk = retries[0]
                print(f"Two independent small-transfer reads verified {address:#010x}", flush=True)
            data.extend(chunk)
            require(ap.read32(0xe000edf0) & (1 << 17), "Core unexpectedly resumed during verification")
            if len(data) % 65536 == 0:
                print(f"{label}: {len(data) // 1024}/512 KiB", flush=True)
    finally:
        ap.dp.probe.set_clock(100000)
    return bytes(data)


def options(ap):
    return {hex(offset): hex(ap.read32(0x40022000 + offset))
            for offset in OPTION_OFFSETS}


def open_serial():
    ports = [p for p in list_ports.comports()
             if (p.vid, p.pid, p.serial_number) == (0x04d8, 0x00df, "ATK-03262021")]
    require(len(ports) == 1, "Expected exactly one ATK serial interface")
    port = serial.Serial(port=None, baudrate=115200, timeout=0.1,
                         exclusive=True, xonxoff=False, rtscts=False, dsrdtr=False)
    port.dtr = False
    port.rts = False
    port.port = ports[0].device
    port.open()
    return port


def capture(port, seconds):
    data = bytearray()
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        part = port.read(4096)
        if part:
            data.extend(part)
            print(part.decode(errors="replace"), end="", flush=True)
    return bytes(data)


def run(action):
    original, image = BACKUP.read_bytes(), IMAGE.read_bytes()
    require(len(original) == FLASH_SIZE and sha(original) == BACKUP_SHA,
            "Original backup size/hash mismatch")
    require(len(image) == 2724 and sha(image) == IMAGE_SHA, "Lab image size/hash mismatch")
    require(sha(PACK.read_bytes()) == PACK_SHA, "Device pack hash mismatch")
    (ROOT / "lab1/build").mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)
    offset = APP - FLASH_BASE
    patched = original[:offset] + image + original[offset + len(image):]
    known_images = [original, patched]
    for path, digest in PREVIOUS_IMAGES:
        if not path.exists():
            continue  # Prior local trials are not part of the shared project.
        previous = path.read_bytes()
        require(sha(previous) == digest and len(previous) <= SPAN,
                "Known previous image hash/size mismatch")
        known_images.append(original[:offset] + previous + original[offset + len(previous):])
    desired = original if action == "restore" else patched
    pages = original[offset:offset + SPAN]
    rollback = ROOT / "backups/lab1_original_pages_08010000_4096.bin"
    if rollback.exists():
        require(rollback.read_bytes() == pages, "Existing rollback page file differs")
    else:
        rollback.write_bytes(pages)
    (ROOT / "lab1/build/lab1_merged_pages.bin").write_bytes(patched[offset:offset + SPAN])
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    log_path = ROOT / "logs" / f"lab1_{action}_{stamp}.json"
    log = {"time": stamp, "action": action, "target": "STM32L496VETx",
           "probe": "ATK-03262021", "swd_hz": 100000, "read_swd_hz": 500000,
           "range_start": hex(APP), "range_end_inclusive": hex(APP + SPAN - 1),
           "erase_sectors": [hex(APP), hex(APP + SECTOR)],
           "rollback_file": str(rollback), "rollback_sha256": sha(pages),
           "backup_sha256": BACKUP_SHA, "firmware_sha256": IMAGE_SHA,
           "pack_sha256": PACK_SHA, "status": "started"}
    print(json.dumps(log, indent=2), flush=True)
    if action == "plan":
        log["status"] = "offline_plan_only"
        log_path.write_text(json.dumps(log, indent=2) + "\n")
        return

    session = ConnectHelper.session_with_chosen_probe(
        unique_id="ATK-03262021", blocking=False, auto_open=False, no_config=True,
        target_override="stm32l496vetx", frequency=100000, connect_mode="halt",
        auto_unlock=False, resume_on_disconnect=False,
        **{"pack": str(PACK), "pack.debug_sequences.enable": False,
           "dap_protocol": "swd", "user_script": os.devnull, "cache.enable_memory": False,
           "cmsis_dap.limit_packets": True, "cmsis_dap.deferred_transfers": False,
           "cache.enable_register": False, "cache.read_code_from_elf": False,
           "chip_erase": "sector", "keep_unwritten": True, "smart_flash": False,
           "reset_type": "sysresetreq"})
    require(session is not None, "Expected ATK debug probe not found")
    # pyOCD 0.46's disabled pack sequences can still suppress its default DP
    # setup/power-up hooks. Remove the delegate so normal SWD setup is used.
    # The exact pack's memory map and flash algorithm remain in use.
    session.target.debug_sequence_delegate = None
    session.target.dp.valid_aps = [0]
    port, flash, started_mutation, reset_done = None, None, False, False
    try:
        port = open_serial()
        session.open()
        target = session.target
        ap = target.selected_core.ap
        debug_freeze = ap.read32(0xe0042008)
        ap.write32(0xe0042008, debug_freeze | (1 << 11) | (1 << 12))
        target.halt()
        require(ap.read32(0xe0042000) & 0xfff == 0x461, "Wrong MCU family")
        require(ap.read16(0x1fff75e0) == 512, "Wrong flash capacity")
        require(ap.read32(0x40022020) == 0xffeff8aa, "Option register changed; stopping")
        log["options_before"] = options(ap)
        flash = target.memory_map.get_region_for_address(APP).flash
        require(flash is not None, "No flash algorithm at application address")
        require(flash.get_flash_info().rom_start == FLASH_BASE, "Wrong flash region")
        for address in (APP, APP + SECTOR):
            info = flash.get_sector_info(address)
            require(info.base_addr == address and info.size == SECTOR, "Unexpected erase geometry")
        page_size = flash.get_page_info(APP).size
        require(page_size in (1024, 2048), "Unexpected programming page size")
        # Remove the mass-erase entry point from this instance as a second guard.
        flash.flash_algo["pc_eraseAll"] = 0xffffffff
        before = read_flash(ap, "Read before", tuple(known_images), log)
        log["before_sha256"] = sha(before)
        require(before in known_images,
                "Flash differs from the known images; no erase permitted")
        require(before[:offset] == original[:offset]
                and before[offset + SPAN:] == original[offset + SPAN:],
                "Contents outside the allowed pages differ")
        log["outside_pages_before_matches_backup"] = True

        if before != desired:
            # Reset the clock/peripherals before the RAM-resident flash algorithm.
            target.reset_and_halt(Target.ResetType.SYSRESETREQ)
            require(ap.read32(0x40021008) & 0xc == 0, "SYSCLK did not reset to MSI")
            started_mutation = True
            log["status"] = "programming"
            log_path.write_text(json.dumps(log, indent=2) + "\n")
            flash.init(Flash.Operation.ERASE, address=APP)
            for address in (APP, APP + SECTOR):
                print(f"Erase one 2048-byte page at {address:#010x}", flush=True)
                flash.erase_sector(address)
            flash.init(Flash.Operation.PROGRAM, address=APP)
            for position in range(0, SPAN, page_size):
                address = APP + position
                flash.program_page(address, desired[offset + position:offset + position + page_size])
                print(f"Program {page_size} bytes at {address:#010x}", flush=True)
            flash.cleanup()
            target.halt()
        else:
            log["programming_skipped_already_matches"] = True

        after = read_flash(ap, "Verify after", (desired,), log)
        log["after_sha256"] = sha(after)
        require(after == desired, "Full flash readback differs from expected contents")
        log["full_readback_verified"] = True
        log["bootloader_unchanged"] = after[:offset] == original[:offset]
        log["outside_pages_unchanged"] = after[offset + SPAN:] == original[offset + SPAN:]
        log["options_after"] = options(ap)
        require(log["options_after"] == log["options_before"], "Option register comparison failed")
        log["options_unchanged"] = True
        ap.write32(0xe0042008, debug_freeze)
        log["watchdog_debug_freeze_restored"] = True
        port.reset_input_buffer()
        target.reset(Target.ResetType.SYSRESETREQ)
        target.resume()
        reset_done = True
        uart = capture(port, 6)
        # Original lab v1 polled RX after WFI; pacing also supports that image
        # while the corrected firmware is being prepared.
        for char in (b"\rversion\r" if action == "restore" else b"\rstatus\r"):
            port.write(bytes([char]))
            time.sleep(0.003)
        port.flush()
        uart += capture(port, 3)
        serial_path = log_path.with_suffix(".serial.txt")
        serial_path.write_bytes(uart)
        log["serial_log"] = str(serial_path)
        log["boot_verified"] = ((b"RT-Thread" in uart and b"msh" in uart)
                                if action == "restore" else
                                (b"LAB1 STM32L496" in uart and b"STATUS mode=" in uart))
        status = ap.read32(0xe000edf0)
        log["core_halted"] = bool(status & (1 << 17))
        log["core_lockup"] = bool(status & (1 << 19))
        require(log["boot_verified"], "Flash verified; expected serial boot response absent")
        require(not log["core_halted"] and not log["core_lockup"], "Core not running normally")
        log["status"] = "passed"
    except Exception as exc:
        log["status"] = "failed"
        log["error"] = str(exc)
        if started_mutation and not reset_done:
            log["recovery"] = "Target intentionally left halted; restore only the saved application pages."
        raise
    finally:
        if not started_mutation and not reset_done and session.is_open:
            session.target.resume()
        if port:
            port.close()
        if reset_done:
            session.options["resume_on_disconnect"] = True
        session.close()
        log_path.write_text(json.dumps(log, indent=2) + "\n")
        print(f"\nReport: {log_path}", flush=True)
        print(json.dumps(log, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "apply", "restore"))
    run(parser.parse_args().action)

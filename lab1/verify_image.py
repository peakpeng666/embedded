#!/usr/bin/env python3
"""Validate the linked image and record a local manifest; never access hardware."""
import hashlib
import json
from pathlib import Path
import struct

from elftools.elf.elffile import ELFFile
from intelhex import IntelHex

root = Path(__file__).resolve().parent
image = (root / "build/lab1.bin").read_bytes()
vectors = struct.unpack_from("<128I", image)
assert vectors[0] == 0x20010000, "Unexpected initial stack address"
assert vectors[1] & 1, "Reset vector must enter Thumb mode"
assert len(image) <= 448 * 1024
with (root / "build/lab1.elf").open("rb") as stream:
    elf = ELFFile(stream)
    assert elf["e_machine"] == "EM_ARM"
    symbols = {
        item.name: item["st_value"]
        for item in elf.get_section_by_name(".symtab").iter_symbols()
    }
    for index, name in ((1, "Reset_Handler"), (15, "SysTick_Handler"),
                        (16 + 23, "EXTI9_5_IRQHandler")):
        assert vectors[index] == (symbols[name] | 1), f"Wrong vector: {name}"
    regions = []
    for segment in elf.iter_segments():
        if segment["p_type"] != "PT_LOAD":
            continue
        start, size = segment["p_paddr"], segment["p_filesz"]
        assert 0x08010000 <= start <= start + size <= 0x08080000
        regions.append({"load_address": hex(start), "file_bytes": size})
hex_image = IntelHex(str(root / "build/lab1.hex"))
assert hex_image.minaddr() == 0x08010000
assert hex_image.maxaddr() == 0x08010000 + len(image) - 1
assert hex_image.tobinstr() == image
manifest = {
    "target": "STM32L496VET6", "flash_address": "0x08010000",
    "initial_stack": hex(vectors[0]), "reset_vector": hex(vectors[1]),
    "image_bytes": len(image), "sha256": hashlib.sha256(image).hexdigest(),
    "load_regions": regions, "vector_and_address_checks": "passed",
    "host_logic_tests": "See docs/validation.md",
    "validation_scope": "offline_image_only",
    "hardware_results": "docs/hardware_validation.json (if present)",
}
destination = root / "build/validation.json"
destination.write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))

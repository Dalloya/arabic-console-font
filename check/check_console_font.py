#!/usr/bin/env python3
"""Verify the kernel-console font budget, mappings, and 2x companion."""
import struct
import sys
from pathlib import Path

MAGIC = b"\x72\xb5\x4a\x86"
HEADER = struct.Struct("<4s7I")
LIMIT = 512
CONNECTORS = list(range(0xE010, 0xE019))
TATWEEL = 0x0640
JOIN_ROWS_8 = (10,)


def read(path):
    data = Path(path).read_bytes()
    if len(data) < HEADER.size:
        raise AssertionError(f"{path}: truncated header")
    magic, version, hs, flags, count, charsize, height, width = HEADER.unpack_from(data)
    if magic != MAGIC or version != 0 or hs < HEADER.size:
        raise AssertionError(f"{path}: invalid PSF2 header")
    if count > LIMIT:
        raise AssertionError(f"{path}: charcount={count} exceeds {LIMIT}")
    glyph_end = hs + count * charsize
    if len(data) < glyph_end:
        raise AssertionError(f"{path}: truncated glyph data")
    table, offset = [], glyph_end
    for slot in range(count):
        end = data.find(b"\xff", offset)
        if end < 0:
            raise AssertionError(f"{path}: missing Unicode terminator at slot {slot}")
        try:
            alternatives = data[offset:end].split(b"\xfe")
            if any(not entry for entry in alternatives):
                raise AssertionError(f"{path}: empty Unicode alternate at slot {slot}")
            values = [ord(ch) for entry in alternatives for ch in entry.decode("utf-8")]
        except UnicodeDecodeError as exc:
            raise AssertionError(f"{path}: invalid Unicode table at slot {slot}") from exc
        table.append(values)
        offset = end + 1
    if offset != len(data):
        raise AssertionError(f"{path}: trailing bytes after Unicode table")
    glyphs = [data[hs + slot * charsize:hs + (slot + 1) * charsize] for slot in range(count)]
    slots = {cp: slot for slot, values in enumerate(table) for cp in values}
    return (count, charsize, height, width), glyphs, slots


def doubled(glyph):
    rows = []
    for row in glyph:
        out = 0
        for x in range(8):
            if row & (0x80 >> x):
                out |= 0xC000 >> (2 * x)
        packed = out.to_bytes(2, "big")
        rows.extend((packed, packed))
    return b"".join(rows)


def main():
    small = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/console-8x16.psfu")
    large = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out/console-16x32.psfu")
    h8, g8, s8 = read(small)
    h16, g16, s16 = read(large)
    assert h8 == (512, 16, 16, 8), f"{small}: unexpected header {h8}"
    assert h16 == (512, 64, 32, 16), f"{large}: unexpected header {h16}"
    assert not any(g8[32]) and not any(g16[32]), "slot 32 must remain blank"
    assert all(doubled(a) == b for a, b in zip(g8, g16)), "16x32 is not exact 2x"
    required = CONNECTORS + [TATWEEL]
    assert all(cp in s8 and cp in s16 for cp in required), "required mappings missing"
    assert all(s8[cp] == s16[cp] for cp in required), "8x16/16x32 slot mappings differ"
    assert all(s8[cp] < LIMIT for cp in required), "required glyph outside kernel budget"
    tat = g8[s8[TATWEEL]]
    assert all(tat[row] == 0xFF for row in JOIN_ROWS_8), "tatweel join stroke changed"
    for cp in CONNECTORS:
        glyph = g8[s8[cp]]
        assert all(glyph[row] == tat[row] for row in JOIN_ROWS_8), f"U+{cp:04X} join rows differ"
        assert all(glyph[row] & 0x81 == 0x81 for row in JOIN_ROWS_8), f"U+{cp:04X} does not reach both edges"
    print(f"{small}: charcount=512 Unicode table=well-formed")
    print(f"{large}: charcount=512 Unicode table=well-formed exact-2x=PASS slot-32-blank=PASS")
    print("connector/tatweel join rows byte-identical=PASS")


if __name__ == "__main__":
    main()

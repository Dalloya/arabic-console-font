#!/usr/bin/env python3
"""Independent PSF2 reader and ASCII bitmap dumper."""
import argparse
import struct

MAGIC = b"\x72\xb5\x4a\x86"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("codepoints", nargs="+", help="U+FE8F or 0xFE8F")
    a = ap.parse_args()
    raw = open(a.font, "rb").read()
    if raw[:4] != MAGIC:
        raise ValueError("not PSF2")
    version, hs, flags, count, bpg, height, width = struct.unpack_from("<7I", raw, 4)
    print(f"magic=72 b5 4a 86 version={version} headersize={hs} flags={flags} "
          f"glyphs={count} bytes_per_glyph={bpg} height={height} width={width}")
    table = 32 + count * bpg
    mapping = {}
    pos = table
    for i in range(count):
        cps = []
        sequence = bytearray()
        while raw[pos] != 0xFF:
            if raw[pos] == 0xFE:
                if sequence:
                    cps.append(ord(bytes(sequence).decode("utf-8")))
                    sequence.clear()
            else:
                sequence.append(raw[pos])
            pos += 1
        if sequence:
            cps.append(ord(bytes(sequence).decode("utf-8")))
        pos += 1
        for cp in cps: mapping[cp] = i
    bpr = (width + 7) // 8
    for token in a.codepoints:
        cp = int(token[2:], 16) if token.upper().startswith("U+") else int(token, 0)
        if cp not in mapping: print(f"U+{cp:04X}: NOT IN UNICODE TABLE"); continue
        i = mapping[cp]; start = 32 + i * bpg
        print(f"U+{cp:04X} glyph={i}")
        for y in range(height):
            bits = raw[start + y*bpr:start + (y+1)*bpr]
            print("".join("#" if (bits[x//8] & (0x80 >> (x%8))) else "."
                          for x in range(width)))

if __name__ == "__main__": main()

# Arabic console font

A bitmap console font that makes Arabic readable on the Linux kernel text console, in
two sizes: **8x16** and **16x32**.

The kernel console has no shaping, no bidi and no combining marks. This font works around
each of those limits with cells, not with code.

## What is in the box

| file | cells | format |
|---|---|---|
| `psfu/console-8x16.psfu` | 8x16 | PSF2, 512 glyph slots, Unicode table |
| `psfu/console-16x32.psfu` | 16x32 | PSF2, 512 glyph slots, Unicode table |

The 16x32 face is an **exact 2x** of the 8x16 face, verified glyph by glyph.

## What is in the 512 cells

Measured from the shipped files, not from intent:

- 544 codepoints mapped into 512 glyph slots (several codepoints share a slot on purpose).
- **141 presentation forms** `U+FE70`–`U+FEFC` — the shaped Arabic the renderer emits.
- **37 base Arabic letters** `U+0620`–`U+064A`.
- **9 marks**: the eight tashkeel `U+064B`–`U+0652` plus `U+0670` superscript alef.
- **31 private-use cells** `U+E000`–`U+E03D`:
  - `U+E000`–`U+E008` — printable aliases for the nine marks. The console suppresses
    combining marks, so the shaper emits these ordinary cells and the mark actually
    appears.
  - `U+E010`–`U+E018` — the full-width **join stroke**. Its join rows are byte-identical
    to `U+0640` tatweel, and it reaches both cell edges, so a letter that must connect to
    its neighbour can be connected without the console having to join anything.
- 67 box-drawing and block glyphs, 95 printable ASCII cells.

## Why a private-use join stroke

A cell can hold one codepoint. A joining Arabic letter needs a stroke that runs to the
cell edge on one or both sides. Rather than bake every combination into the font, the font
supplies one full-width stroke on its own cells and the renderer places it. The check in
`check/check_console_font.py` asserts the stroke's join rows are byte-identical to tatweel
and that every connector reaches both edges — that assertion is the contract between font
and renderer.

## Build and verify

```
./build.sh                     # verify the shipped fonts (gate: check_console_font.py)
UNIFONT_HEX=/path/unifont.hex ./build.sh --rebuild    # regenerate from a Unifont hex source
```

`build/console_font.py` curates the vocabulary and emits the PSF2 with its Unicode table.
It reads a Unifont `.hex` file as the glyph source; the path is hardcoded in that script,
so pass nothing and use the shipped artifacts unless you are regenerating deliberately.

## Install

```
sudo cp psfu/console-8x16.psfu /usr/share/kbd/consolefonts/
sudo setfont console-8x16
```

For a persisted choice, set it in `/etc/vconsole.conf` (`FONT=console-8x16`).

## Provenance

- Glyph outlines are taken from **GNU Unifont** (GPL-2.0-or-later with the font embedding
  exception) and then curated, padded and re-cut for the console cell budget.
- The Arabic presentation-form vocabulary follows the four-form table of the Sakhr AX-170
  ROM, which is the joining model the renderer in `arabic-console` and
  `arabic-console-shaper` follows.
- The mark cells and the join-stroke cells are this project's own design.

## Licence

GPL-2.0-or-later, inherited from GNU Unifont. See `LICENSE`.

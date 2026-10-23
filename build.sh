#!/usr/bin/env bash
set -eu

cd "$(dirname "$0")"

# console_font.py's default source is /tmp/uni/usr/share/unifont/unifont.hex.
# To use another source, set UNIFONT_HEX=/path/to/unifont.hex; the exact
# override is passed as --font "$UNIFONT_HEX" below. The generator itself is
# intentionally left unchanged.
if [ "${1-}" = "--rebuild" ] && [ -n "${UNIFONT_HEX-}" ]; then
    mkdir -p build
    python3 build/console_font.py \
        --font "$UNIFONT_HEX" \
        --out build/console-8x16.rebuilt.psfu \
        --base psfu/console-8x16.psfu
elif [ "${1-}" = "--rebuild" ]; then
    printf '%s\n' 'REBUILD SKIP: --rebuild requires UNIFONT_HEX=/path/to/unifont.hex'
fi

python3 check/check_console_font.py psfu/console-8x16.psfu psfu/console-16x32.psfu

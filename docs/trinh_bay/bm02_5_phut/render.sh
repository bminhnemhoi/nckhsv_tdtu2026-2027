#!/bin/sh
# Xuất PDF từ index.html. CSS được nhúng thẳng vào bản _print.html để Chrome
# headless không dùng lại stylesheet đã cache (nguyên nhân bản PDF bị cũ).
set -eu
SLIDE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROFILE_DIR=$(mktemp -d /tmp/relyfetal-chrome.XXXXXX)
python3 "$SLIDE_DIR/build_print.py"
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --no-pdf-header-footer --disable-gpu --user-data-dir="$PROFILE_DIR" --print-to-pdf="$SLIDE_DIR/RelyFetal_BM02_5_phut.pdf" "file://$SLIDE_DIR/_print.html"
rm -f "$SLIDE_DIR/_print.html"
rm -rf "$PROFILE_DIR"

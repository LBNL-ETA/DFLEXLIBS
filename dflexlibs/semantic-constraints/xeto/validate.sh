#!/bin/sh
# Compile obcflex.df and check it against the example records.
#
# Needs the `xeto` CLI from Haxall 4.0.6 or later. Pass its location as the
# first argument, or set XETO. See README.md for why 4.0.6 is the floor.
#
#   ./validate.sh /path/to/haxall-4.0.6/bin/xeto
set -e
cd "$(dirname "$0")"
XETO="${1:-${XETO:-xeto}}"

echo "=== build ==="
"$XETO" build obcflex.df

echo
echo "=== conforming.trio (expect 0 errors) ==="
"$XETO" fits examples/conforming.trio -graph

echo
echo "=== non-conforming.trio (expect errors on 3 recs) ==="
"$XETO" fits examples/non-conforming.trio -graph

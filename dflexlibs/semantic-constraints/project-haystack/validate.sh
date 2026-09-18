#!/bin/sh
# Check the binding filters against the example models.
#
# Needs the `axon` shell from Haxall 4.0.6 or later (the Haystack filter
# grammar it evaluates is the same one SkySpark 3 uses). Pass its location as
# the first argument or set AXON.
#
#   ./validate.sh /path/to/haxall-4.0.6/bin/axon
set -e
cd "$(dirname "$0")"
AXON="${1:-${AXON:-axon}}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

run() {
  printf 'load(`%s`)\n' "$2" > "$TMP/run.axon"
  cat validate.axon >> "$TMP/run.axon"
  printf '\ndfHocCheck()\n' >> "$TMP/run.axon"
  echo "=== $1 ==="
  "$AXON" "$TMP/run.axon" | grep -v '^\[.*\] \[info\]'
  echo
}

run "conforming.trio  (expect every connector ok)"          examples/conforming.trio
run "non-conforming.trio  (expect MISSING, never AMBIGUOUS)" examples/non-conforming.trio

echo "=== why TCurZonSet needs 'not dfTarget' ==="
"$AXON" examples/check-ambiguity.axon | grep -v '^\[.*\] \[info\]'

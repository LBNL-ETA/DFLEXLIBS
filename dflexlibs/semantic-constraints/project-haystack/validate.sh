#!/bin/sh
# Check the binding filters against the example models.
#
# Needs the `axon` shell from Haxall 4.0.6 or later (the Haystack filter
# grammar it evaluates is the same one SkySpark 3 uses). Pass its location as
# the first argument or set AXON.
#
#   ./validate.sh /path/to/haxall-4.0.6/bin/axon
#
# Two kinds of check are run:
#
#   validate  - examples/conforming.trio and examples/non-conforming.trio are
#               hand-built to exercise the filters, so every connector is
#               expected to resolve (or to fail in a specific way).
#   survey    - alpha/bravo/charlie are real site exports from
#               project-haystack.org that know nothing about demand
#               flexibility. Nothing is expected to pass; the report is the
#               commissioning gap for the site.
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

# Same filters, but aggregated over every candidate zone and reported as a
# gap analysis rather than pass/fail. Explains each connector that came back
# ambiguous by listing what it actually matched in one zone.
survey() {
  printf 'load(`%s`)\n' "$2" > "$TMP/run.axon"
  cat validate.axon examples/site-survey.axon >> "$TMP/run.axon"
  cat >> "$TMP/run.axon" <<'EOF'

g: dfHocSurvey()
echo("")
echo("ambiguity detail:")
g.toRecList.findAll(r => r->ambiguous > 0).each(r => dfHocExplain(r->connector))
echo("")
g
EOF
  echo "=== $1 ==="
  "$AXON" "$TMP/run.axon" | grep -v '^\[.*\] \[info\]'
  echo
}

run "conforming.trio  (expect every connector ok)"          examples/conforming.trio
run "non-conforming.trio  (expect MISSING, never AMBIGUOUS)" examples/non-conforming.trio

echo "=== why TCurZonSet needs 'not dfTarget' ==="
"$AXON" examples/check-ambiguity.axon | grep -v '^\[.*\] \[info\]'
echo

survey "alpha.trio  (real site: 139 zones, DD/VAV)"    examples/alpha.trio
survey "bravo.trio  (real site: VAV + FCU)"            examples/bravo.trio
survey "charlie.trio  (real site: VAV, has siteMeter)" examples/charlie.trio

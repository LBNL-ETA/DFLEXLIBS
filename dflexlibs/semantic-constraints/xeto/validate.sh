#!/bin/sh
# Compile obcflex.df and check it against every model in examples/.
#
# Needs the `xeto` CLI and the `axon` shell from Haxall 4.0.6 or later. Pass the
# bin directory as the first argument, or set XETO and AXON. See README.md for
# why 4.0.6 is the floor.
#
#   ./validate.sh /path/to/haxall-4.0.6/bin
#
# Three steps:
#
#   build   - compile the lib.
#   fits    - `xeto fits -graph` over every model in examples/. Expected:
#             conforming 14 ok / 0 err, non-conforming 5 / 3, alpha 2032 / 0,
#             bravo 1070 / 7, charlie 623 / 1. The bravo and charlie failures
#             are deliberate; see README.md.
#   survey  - runs the library specs against every model in examples/ and reports
#             which zones, if any, the sequence can be bound to, followed by the
#             per-connector detail. The models are read only; nothing is
#             modified or assumed. Only conforming.trio has an applicable zone.
set -e
cd "$(dirname "$0")"

BIN="${1:-}"
if [ -n "$BIN" ]; then
  XETO="$BIN/xeto"
  AXON="$BIN/axon"
else
  XETO="${XETO:-xeto}"
  AXON="${AXON:-axon}"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "=== build ==="
"$XETO" build obcflex.df

echo
echo "=== fits ==="
for f in examples/*.trio; do
  echo "--- $f ---"
  "$XETO" fits "$f" -graph | tail -n +3
done

# Per-connector binding report. Uses Axon's fits() inference rather than
# `xeto fits`, because binding has to work out which spec a record fits
# without being told. See examples/site-survey.axon.
survey() {
  {
    echo 'libAdd(["ph","ph.points","ph.elec","obcflex.df"])'
    printf 'load(`%s`)\n' "$1"
    cat examples/site-survey.axon
    cat <<'EOF'

echo("")
echo("applicability:")
dfHocApplicability()
g: dfHocSurvey()
echo("")
echo("ambiguity detail:")
g.toRecList.findAll(r => r->ambiguous > 0).each(r => dfHocExplain(r->connector))
echo("")
g
EOF
  } > "$TMP/run.axon"
  echo
  echo "--- $1 ---"
  "$AXON" "$TMP/run.axon" | grep -v '^\[.*\] \[info\]'
}

echo
echo "=== survey ==="
for f in examples/*.trio; do
  survey "$f"
done

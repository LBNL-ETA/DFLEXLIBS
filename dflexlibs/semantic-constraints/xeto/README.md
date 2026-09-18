# Project-Haystack semantic constraints for the DF sequences

Xeto specs describing the semantic data requirements of the CDL demand
flexibility sequences, so that the points a sequence needs can be found
automatically in a Haystack model instead of being mapped by hand.

This is native Xeto, not SHACL. The lib is `obcflex.df`, under `src/xeto/`.

Currently covered:

| Sequence | File |
|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `src/xeto/obcflex.df/heating-or-cooling.xeto` |

`points.xeto` holds the point specs those depend on; `lib.xeto` is the lib pragma.

## Why Xeto rather than tags in the CDL annotation

- **There is a direct precedent.** `ashrae.g36` (in the Project-Haystack `xeto`
  repo) expresses ASHRAE Guideline 36 sequence requirements exactly this way: an
  equip spec whose `points` slot lists what the sequence needs. `obcflex.df` is
  built the same way.
- **It is checkable.** `xeto fits -graph` validates a Haystack model against the
  specs, including the required-points queries. Plain marker tags in the CDL
  annotation would carry the same information but nothing would verify it.
- **It is publishable and versioned** as a library, which Subtask 3.2 asks for.
- **It is not a dead end for the RDF pipeline.** `doc.xeto/Rdf.md` defines a
  standard Xeto to RDF mapping with a SHACL Core profile and QUDT identifiers,
  and the CLI ships `xeto export-rdf`. So these specs can feed the same
  pyshacl-based binding used by `../s223/` and `../brick/` rather than forking it.

## Running the checks

```sh
./validate.sh /path/to/haxall-4.0.6/bin/xeto
```

Expected: `conforming.trio` 14 recs ok / 0 err, `non-conforming.trio` 5 ok / 3 err.

### Tooling version matters

**Haxall 4.0.6 or later is required.** This is not incidental:

- The npm package `@haxall/haxall` is capped at **4.0.4** (Dec 2025), which is
  too old. It does not implement the `src/xeto/xeto-build.props` build-var
  mechanism that the current Project-Haystack source uses, so it cannot compile
  that checkout at all.
- 4.0.4 also ships an older lib layout: `ph.points.elec` where current source
  has `ph.elec`, and no `ZoneAirTempEffectiveSp` in `ph.points`. Both are used
  here.

Get 4.0.6 from <https://github.com/haxall/haxall/releases>, not from npm. It
runs on Java (tested on Java 21).

The libs bundled with 4.0.6 are enough to build this lib. Building against a
newer Project-Haystack source checkout also works — add it to `path` in
`xeto.props` — but note the checkout still splits out `ph.points.sugar`, so
`ZoneAirTempEffectiveSp` resolves from there rather than from `ph.points`.

## Specs

| CDL connector | Spec | Base |
|---|---|---|
| `TCurZon` | `ph.points::ZoneAirTempSensor` | stock |
| `TCurZonSet` / `TComZonSet` | `ph.points::ZoneAirTempEffectiveSp` | stock |
| `TPreTarSet` | `PreConditionZoneAirTempSp` | new |
| `TSheTarSet` | `LoadShedZoneAirTempSp` | new |
| `TDefSet` | `DefaultZoneAirTempSp` | new |
| `PBui` | `ph.elec::ElecAcActivePowerSensor` | stock |
| `PBuiThrVar` | `ElecDemandThresholdSp` | new |
| `rouZonFla` | `RogueZoneSp` | new |
| `demFleMod` | `DfModeSp` | new |

Container specs: `DfHeatingOrCoolingZoneEquip`, `DfHeatingOrCoolingElecMeter`,
`DfSupervisor`.

Haystack has no demand flexibility vocabulary — searches for `loadShed`,
`demandResponse`, `curtail` and `precool` across `xeto/` and `haystack-defs/`
all come back empty — so the event targets, the threshold, the rogue zone flag
and the mode point are defined here, as they had to be for s223 and Brick.

## How this differs from the s223 and brick libraries

**The container is the equip, not the zone.** In s223 the connectors hang off an
`s223:Zone` via `hasProperty`, and in Brick off a `brick:HVAC_Zone` via
`hasPoint`. Haystack has no equivalent: `points` is a Query on `ph::Equip` and
`ph::Space` does not have one. Zone points belong to the equip serving the zone
and reference the space through `spaceRef`. So the control target here is
`DfHeatingOrCoolingZoneEquip`, and the zone is reached through its `spaceRef`.

This also splits `demFleMod` out. It is a single building-level input, not a
per-zone point, so it sits on a `DfSupervisor` equip rather than on the zone
equip — where the s223 and Brick versions simply left it unattached.

**Unit checking comes from the quantity, not an enumeration.** The SHACL
libraries list `unit:K unit:DEG_C unit:DEG_F` explicitly. Xeto inherits
`unit: Unit <quantity:"temperature">` from the ph spec and reports
`Unit 'kPa' must be 'temperature' not 'pressure'` on its own.

**Ambiguity is detected rather than silently allowed.** See below.

## Modelling decisions

**`TCurZonSet` binds `ZoneAirTempEffectiveSp`, not `ZoneAirTempSp`.** This is the
one constraint worth understanding, and it was found by running the tools rather
than by reading the ontology.

The three demand flexibility targets inherit from `ZoneAirTempSp`. Requiring
plain `ZoneAirTempSp` for the active setpoint therefore matches all four points
in a zone, and `xeto fits -graph` reports:

```
Slot 'points': Ambiguous match for Point: ph.points::ZoneAirTempSp
  [@zone1TCurZonSet, @zone1TPreTarSet, @zone1TSheTarSet, @zone1TDefSet]
```

This is the same collision that needed an explicit exclusion in both other
libraries: `obc:not-a-df-target` in s223, and an `sh:not` node constraint in
Brick. Two things differ here:

- **Xeto catches it.** SHACL silently returns four candidates; the Brick and
  s223 libraries only reject them because of a constraint written specifically
  to do so, backed by a test. Xeto treats the ambiguity itself as the error.
- **Xeto cannot express the fix the same way**, because it has no negation —
  there is no `sh:not`. The `DfSetpointRole` Choice separates the three targets
  from *each other*, but it does not stop them matching their parent. The fix is
  to require a *sibling* spec instead: `ZoneAirTempEffectiveSp` is
  the currently-effective zone setpoint, which is what `TCurZonSet` is, and it
  is not an ancestor of the targets.

**`TCurZonSet` and `TComZonSet` are one point, not two** — the sequence reads the
effective zone setpoint and writes it back. The read/write distinction is the CDL
connector direction. The `points` slot lists it once.

**The `dfTarget` marker is for filters, not for fitting.** The Choice already
tells the three targets apart. `dfTarget` exists so a Haystack filter can exclude
all of them in one term, which is what a BAS-side binder would run:

```
point and zone and air and temp and sp and not dfTarget
```

Haystack filters do support `not`, so the exclusion is expressible at query time
even though it is not expressible in the spec.

**Vectorisation is handled at binding time.** One `DfHeatingOrCoolingZoneEquip`
per zone; binding produces one match per zone, in connector-array order.

## Known gaps

- **Heating vs cooling is not modelled.** The `airConMod` parameter selects
  heating or cooling, and a real binding should target the zone's heating or
  cooling setpoint accordingly. The specs are currently mode-agnostic.
- **Variant-conditional connectors are not expressed.** `PBui` and `PBuiThrVar`
  only exist for `ZoneControlVariant` 3 and 4, which is why they sit on a
  separate meter spec rather than being required of every deployment.
- **No BACnet reference requirement.** The s223 and Brick shapes require an
  external reference on the measured and commanded points. The Haystack
  equivalent is connector tags (`bacnetCur`, `bacnetWrite` and friends from
  `ph.protocols`), which are deployment-specific; they are deliberately not
  required here. Worth revisiting once a demonstration site is picked.
- **RDF export is untested.** `xeto export-rdf` exists and should let this lib
  feed the same pyshacl pipeline as the other two, but that path has not been
  exercised. `sys.rdf` is in the Project-Haystack source checkout and not in the
  4.0.6 bundle, which may matter.

## Layout

```
project-haystack/
├── xeto.props                 marks the Xeto workDir
├── validate.sh                build + check both example files
├── src/xeto/obcflex.df/
│   ├── lib.xeto               lib pragma and dependencies
│   ├── points.xeto            DF point specs, the DfSetpointRole Choice, DfModeEnum
│   └── heating-or-cooling.xeto  the three container specs
└── examples/
    ├── conforming.trio        14 recs that satisfy every spec
    └── non-conforming.trio    8 recs exercising each rejection path
```

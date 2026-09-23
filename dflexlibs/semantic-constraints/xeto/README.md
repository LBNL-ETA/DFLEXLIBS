# Xeto semantic constraints for the DF sequences

Xeto specs describing the semantic data requirements of the CDL demand
flexibility sequences, so that the points a sequence needs can be found
automatically in a Haystack model instead of being mapped by hand.

This is native Xeto, not SHACL. The lib is `obcflex.df`, under `src/xeto/`.
`../project-haystack/` holds the same requirements as Haystack 4 defs and
filters, for SkySpark 3, which does not support Xeto.

Coverage:

| Sequence | File |
|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `src/xeto/obcflex.df/heating-or-cooling.xeto` |

`points.xeto` holds the point specs those depend on; `lib.xeto` is the lib pragma.

## Why Xeto rather than tags in the CDL annotation

- **There is a direct precedent.** `ashrae.g36` (in the Project-Haystack `xeto`
  repo) expresses ASHRAE Guideline 36 sequence requirements the same way: an
  equip spec whose `points` slot lists what the sequence needs. `obcflex.df` is
  built to match.
- **It is checkable.** `xeto fits -graph` validates a Haystack model against the
  specs, including the required-points queries. Plain marker tags in the CDL
  annotation would carry the same information with nothing to verify it.
- **It is not a dead end for the RDF pipeline.** `doc.xeto/Rdf.md` defines a
  standard Xeto to RDF mapping with a SHACL Core profile and QUDT identifiers,
  and the CLI ships `xeto export-rdf`, so these specs can feed the same
  pyshacl-based binding used by `../s223/` and `../brick/`.

## Running the checks

```sh
./validate.sh /path/to/haxall-4.0.6/bin
```

Both the `xeto` CLI and the `axon` shell are used, so the argument is the bin
directory rather than one binary. Three steps run:

| Step | What it does |
|---|---|
| build | compiles `obcflex.df` |
| fits | `xeto fits -graph` over every model in `examples/` |
| survey | per-connector binding report over every model in `examples/` |

Expected `fits` results:

| Model | ok | err |
|---|---|---|
| `conforming.trio` | 14 | 0 |
| `non-conforming.trio` | 5 | 3 |
| `alpha.trio` | 2032 | 0 |
| `bravo.trio` | 1070 | 7 |
| `charlie.trio` | 623 | 1 |

The bravo and charlie failures are deliberate; see
[The building models](#the-building-models).

`fits` checks each record against the spec that record declares. None of the
building models declares an `obcflex.df` spec, so a clean `fits` run says the
model is internally consistent, not that the sequence can be bound to it. That
is what the survey answers.

`validate.sh` iterates over every `.trio` in `examples/`, so a new model dropped
in there is picked up by both passes without editing the script.

### Always pass `-graph`

`xeto fits` on its own validates each record against the spec it declares.
`-graph` additionally runs the required-points queries, which is what actually
checks a sequence's requirements. It matters here because the container specs
carry no markers of their own: `DfHeatingOrCoolingElecMeter` adds nothing to
`ph::ElecMeter` except a `points` query. Without `-graph`, a model whose meter
claims that spec while holding none of the DF points passes silently.

### Tooling version

**Haxall 4.0.6 or later is required.**

- The npm package `@haxall/haxall` is capped at 4.0.4 (Dec 2025), which does not
  implement the `src/xeto/xeto-build.props` build-var mechanism the current
  Project-Haystack source uses, so it cannot compile that checkout.
- 4.0.4 also ships an older lib layout: `ph.points.elec` where current source
  has `ph.elec`, and no `ZoneAirTempEffectiveSp` in `ph.points`. Both are used
  here.

Get 4.0.6 from <https://github.com/haxall/haxall/releases> rather than npm. It
runs on Java (tested on Java 21).

The libs bundled with 4.0.6 are enough to build this lib. Building against a
newer Project-Haystack source checkout also works: add it to `path` in
`xeto.props`. That checkout splits out `ph.points.sugar`, so
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

Haystack has no demand flexibility vocabulary; searches for `loadShed`,
`demandResponse`, `curtail` and `precool` across the Xeto and Haystack def
sources return nothing. The event targets, the threshold, the rogue zone flag
and the mode point are therefore defined here, as they are for s223 and Brick.

## Modelling decisions

**`TCurZonSet` binds `ZoneAirTempEffectiveSp`, not `ZoneAirTempSp`.** The three
demand flexibility targets inherit from `ZoneAirTempSp`, so requiring plain
`ZoneAirTempSp` for the active setpoint matches all four points in a zone and
`xeto fits -graph` reports:

```
Slot 'points': Ambiguous match for Point: ph.points::ZoneAirTempSp
  [@zone1TCurZonSet, @zone1TPreTarSet, @zone1TSheTarSet, @zone1TDefSet]
```

This is the same collision that needs `obc:not-a-df-target` in s223 and an
`sh:not` node constraint in Brick. Two things differ:

- **Xeto treats the ambiguity itself as an error.** SHACL silently returns four
  candidates; the s223 and Brick libraries reject them only because of a
  constraint written to do so.
- **Xeto cannot express the fix the same way**, because it has no negation.
  The `DfSetpointRole` Choice separates the three targets from each other but
  does not stop them matching their parent. The fix is to require a *sibling*
  spec: `ZoneAirTempEffectiveSp` is the currently-effective zone setpoint, which
  is what `TCurZonSet` is, and it is not an ancestor of the targets.

**`TCurZonSet` and `TComZonSet` are one point, not two.** The sequence reads the
effective zone setpoint and writes it back; the read/write distinction is the
CDL connector direction. The `points` slot lists it once.

**The `dfTarget` marker is for filters, not for fitting.** The Choice already
tells the three targets apart. `dfTarget` exists so a Haystack filter can
exclude all of them in one term, which is what a BAS-side binder runs:

```
point and zone and air and temp and sp and not dfTarget
```

Haystack filters support `not`, so the exclusion is expressible at query time
even though it is not expressible in the spec.

**Vectorisation is handled at binding time.** One `DfHeatingOrCoolingZoneEquip`
per zone; binding produces one match per zone, in connector-array order.

## How this differs from the s223 and brick libraries

**The container is the equip, not the zone.** In s223 the connectors hang off an
`s223:Zone` via `hasProperty`, and in Brick off a `brick:HVAC_Zone` via
`hasPoint`. Haystack has no equivalent: `points` is a Query on `ph::Equip`, and
`ph::Space` does not have one. Zone points belong to the equip serving the zone
and reference the space through `spaceRef`. The control target is therefore
`DfHeatingOrCoolingZoneEquip`, and the zone is reached through its `spaceRef`.

This also splits `demFleMod` out. It is a single building-level input rather
than a per-zone point, so it sits on a `DfSupervisor` equip rather than on the
zone equip, where the s223 and Brick versions leave it unattached.

**Unit checking comes from the quantity, not an enumeration.** The SHACL
libraries list `unit:K unit:DEG_C unit:DEG_F` explicitly. Xeto inherits
`unit: Unit <quantity:"temperature">` from the ph spec and reports
`Unit 'kPa' must be 'temperature' not 'pressure'` on its own.

## The building models

`examples/conforming.trio` is written to satisfy the specs, which makes it a
test of their internal consistency rather than of their usefulness.
`alpha.trio`, `bravo.trio` and `charlie.trio` are Xeto-form models of three
real buildings, tagged as a BAS would have them and carrying no demand
flexibility vocabulary:

| Model | Records | Zones | Plant |
|---|---|---|---|
| `alpha.trio` | 2032 | 139 | dual-duct and VAV, 4 AHUs, 3 chillers, 3 boilers |
| `bravo.trio` | 1077 | 97 | VAV and FCU, 4 AHUs, 2 chillers, 5 boilers |
| `charlie.trio` | 624 | 34 | VAV, 4 AHUs, 2 chillers, tagged `siteMeter` |

**Eight records fail `fits` on purpose**, seven in bravo and one in charlie, so
that the example set exercises Xeto's unit and quantity checking on realistic
tagging rather than only on a constructed failure case:

- `Bravo RTU-1 Percent Outside Air` is tagged `outside air temp sensor` with
  `unit:"%"`. It is an outside-air fraction carrying the tags of a temperature,
  and Xeto rejects it because the unit does not match the quantity. Five bravo
  records have this shape.
- `Bravo RTU-1 Min Outdoor Air Flow Setpoint` carries `unit:"%"` on an air flow
  setpoint. Two of these.
- `Charlie AHU 1 Mixed Air Damper Command` has no `unit` at all, and
  `DamperPoint` is a `NumberPoint`, which requires one.

### Binding results

`examples/site-survey.axon` asks what binding would actually produce: given a
building as it is tagged, which connectors resolve, which are missing, and which
are ambiguous. It selects candidate zones by the requirement itself, every equip
owning a point fitting `ZoneAirTempSensor`, rather than by local equip naming,
then aggregates the per-connector result across them.

`xeto fits` cannot answer this. It validates records that declare their spec,
whereas binding has to work out which spec a record fits without being told.
Axon's `fits()` does that inference, and the survey uses it.

Results, `ok` / `missing` / `ambiguous` counted over zones:

| Connector | alpha (139 zones) | bravo (97) | charlie (34) |
|---|---|---|---|
| `TCurZon` | **139 ok** | **97 ok** | **34 ok** |
| `TCurZonSet` / `TComZonSet` | 139 missing | 97 missing | 30 ambiguous (2-way) |
| `TPreTarSet` / `TSheTarSet` / `TDefSet` / `rouZonFla` | missing | missing | missing |
| `PBui` / `PBuiThrVar` / `demFleMod` | missing | missing | missing |

**`ZoneAirTempSensor` binds cleanly everywhere:** exactly one match in all 270
zones across the three models.

**`ZoneAirTempEffectiveSp` depends on a tag two of the three models do not
carry.** Choosing the effective setpoint over plain `ZoneAirTempSp` avoids the
collision with the three DF targets, but only matches where the building tags
`effective`. Alpha and bravo tag no zone temperature setpoint that way, so
`TCurZonSet` finds nothing; charlie tags 60, two per zone, so it finds two.
Using a sibling spec as a stand-in for a negation works only on models that
carry the distinguishing tag, and `effective` is not one a BAS export can be
relied on to have. The remaining ambiguity on charlie is the heating/cooling
axis, which no library models yet:

```
  TCurZonSet (ph.points::ZoneAirTempEffectiveSp) in Charlie Floor-4 VAV_21:
    - Charlie Floor-4 VAV_21 eff_cl_stpt
    - Charlie Floor-4 VAV_21 eff_ht_stpt
```

**`ElecAcActivePowerSensor` is the wrong spec for `PBui`.** Charlie has a
`siteMeter` with a whole-building demand point, and the spec matches nothing:
`ElecAcActivePowerSensor` requires six markers (`ac avg magnitude active power
elec`) plus an `elecDirection` choice, and a real main-meter demand point is
tagged `ac elec power sensor demand`. Measured against charlie:

| Spec | matches | on the site meter |
|---|---|---|
| `ElecAcActivePowerSensor` | 0 | 0 |
| `ElecAcPowerDemandSensor` | 5 | **1** |
| `ElecPowerSensor` | 21 | 1 |

`PBui` binds cleanly with `ElecAcPowerDemandSensor`, a one-line change to
`heating-or-cooling.xeto` that has not been made.

The `df*` connectors being missing everywhere is the expected result and is what
the survey is for: it is the commissioning checklist for a site. Before
`HeatingOrCooling` can be deployed to alpha, the site needs three target
setpoints and a rogue-zone flag per zone, a `DfSupervisor` equip carrying the
mode point, and a tagged main meter.

`applying-xeto-example.md` works one zone of `charlie.trio` through that
checklist record by record, from the point set the building already has to a
zone that `xeto fits -graph` accepts, and separates the genuine commissioning
additions from the edits that only compensate for an under-specified
requirement.

### Where the ph specs run out

Parts of these models have no precise spec to land on, or fit two equally well.
None of this shows up in the `fits` results above, and that is not an oversight:
`fits` asks whether a record satisfies the spec it *declares*, and Xeto permits
markers beyond the ones a spec requires. A record tagged both `vav` and
`thermostat` satisfies `ph::Thermostat`, and would equally satisfy `ph::Vav`.
The choice is under-determined for anything inferring a spec, and unremarkable
to the validator. The same goes for an abstract base: `fits` treats abstract as
modelling intent rather than an enforced constraint.

So these are open modelling questions, not failures:

- **`ph::Thermostat` and `ph::Vav` are siblings**, and 138 of alpha's zone
  equips and 93 of bravo's carry both markers. Each declares one of the two and
  validates; nothing in the model says which is the better reading.
- **There is no occupancy command spec.** `ph.points` has `ZoneOccupiedSensor`
  and `ZoneOccupiedSp` but nothing for a command, so the 142 occupancy override
  points in alpha and 34 in charlie have nowhere specific to land.
- **Dual-duct points are only half covered.** `ph.points` has
  `ColdDeckDischargeDamperCmd` but nothing for a cold-deck *flow*, which leaves
  206 of alpha's deck points on abstract bases.

None of these touch the demand flexibility connectors.

## Known gaps

- **Heating vs cooling is not modelled.** The `airConMod` parameter selects
  heating or cooling, and a real binding should target the zone's heating or
  cooling setpoint accordingly. The specs are mode-agnostic, which accounts for
  the whole of the remaining ambiguity on charlie. `ph.points` has
  `ZoneAirTempHeatingSp` and `ZoneAirTempCoolingSp` to use, but the same change
  has to land in `../s223/`, `../brick/` and `../project-haystack/` at the same
  time, since all four libraries have to agree on what a connector binds to.
- **`ZoneAirTempEffectiveSp` does not match two of the three building models.**
  The sibling-spec workaround for Xeto's missing negation only fires on models
  that tag `effective`.
- **`PBui` binds an over-specified spec.** `ElecAcActivePowerSensor` requires
  six markers plus a direction choice, none of which a real main-meter demand
  point carries. `ElecAcPowerDemandSensor` is the working alternative.
- **Variant-conditional connectors are not expressed.** `PBui` and `PBuiThrVar`
  exist only for `ZoneControlVariant` 3 and 4, which is why they sit on a
  separate meter spec rather than being required of every deployment.

## Layout

```
xeto/
├── xeto.props                 marks the Xeto workDir
├── validate.sh                build, fits and survey every model in examples/
├── applying-xeto-example.md   worked example: applying the specs to one zone
├── src/xeto/obcflex.df/
│   ├── lib.xeto               lib pragma and dependencies
│   ├── points.xeto            DF point specs, the DfSetpointRole Choice, DfModeEnum
│   └── heating-or-cooling.xeto  the three container specs
└── examples/
    ├── conforming.trio        14 recs that satisfy every spec
    ├── non-conforming.trio    8 recs exercising each rejection path
    ├── site-survey.axon       per-connector binding report for an un-prepared model
    ├── alpha.trio             dual-duct and VAV building, 2032 recs, 139 zones
    ├── bravo.trio             VAV and FCU building, 1077 recs, 97 zones
    └── charlie.trio           VAV building with a site meter, 624 recs, 34 zones
```

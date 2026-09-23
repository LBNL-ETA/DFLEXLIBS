# Checking a building model against the DF specs

What the check does, and a read of one zone of `examples/charlie.trio` in
detail.

The check is read-only. It runs the `obcflex.df` specs against a building's
metadata model as the building is tagged today and reports which zones, if any,
`ZoneTemperatureSetpointChange.HeatingOrCooling` can be bound to. Nothing in the
model is edited, and no missing point is assumed.

```sh
./validate.sh /path/to/haxall-4.0.6/bin
```

## What the specs ask for

From `src/xeto/obcflex.df/heating-or-cooling.xeto`:

```xeto
DfHeatingOrCoolingZoneEquip : Equip {
  dfHeatingOrCooling
  spaceRef: Ref
  points: {
    ZoneAirTempSensor
    ZoneAirTempEffectiveSp
    PreConditionZoneAirTempSp
    LoadShedZoneAirTempSp
    DefaultZoneAirTempSp
    RogueZoneSp
  }
}
```

Three connectors are not per-zone. `demFleMod` is published once for the
building by a `DfSupervisor`; `PBui` and `PBuiThrVar` apply only to
`ZoneControlVariant` 3 and 4 and hang off a `DfHeatingOrCoolingElecMeter`.

## How the check decides

**Candidate zones** are every equip owning a point that fits
`ph.points::ZoneAirTempSensor`. The selector is the requirement itself rather
than local equip naming, so it does not depend on a site calling its terminal
units `vav`, `thermostat` or anything else.

**Matching is by fit, not by declaration.** A record is a candidate for
`ZoneAirTempEffectiveSp` if its tags satisfy that spec, whatever its own `spec`
tag says. This is what binding has to do — a BAS model does not come labelled
with the specs a sequence happens to want — and it is why the check works on an
untouched model.

**A zone is applicable** when every zone-scoped connector resolves to exactly
one point within it. Zero matches means the sequence cannot be deployed there.
More than one means the tagging does not say which point to use, which is a
failure in the same way: a binder with two candidates has no basis to choose.

`xeto fits` answers a different question. It validates a record against the spec
that record claims, so it reports on declarations, not on applicability. The
check uses Axon's `fits()` inference instead; see `examples/site-survey.axon`.

## Result for charlie.trio

```
applicability:
  zones: 34   applicable: 0
    30 zone(s), e.g. Charlie Floor-4 VAV_21
      missing:   TPreTarSet, TSheTarSet, TDefSet, rouZonFla
      ambiguous: TCurZonSet, TComZonSet
    4 zone(s), e.g. Charlie AHU-2
      missing:   TCurZonSet, TComZonSet, TPreTarSet, TSheTarSet, TDefSet, rouZonFla
```

No zone is applicable, and the 34 candidates fall into two groups. The four in
the second group are air handlers, not terminal units: they own a zone air
temperature sensor, which makes them candidates, but they carry no zone
setpoints at all. The thirty in the first group are the VAV boxes, and they get
furthest.

## Reading one zone

`@c-0145`, *Charlie Floor-4 VAV_21*, is typical of those thirty.

```
zone                    verdict         resolved  required
----------------------  --------------  --------  --------
Charlie Floor-4 VAV_21  not applicable  1         7
```

It owns thirteen points:

| Id | `dis` | Declared spec |
|---|---|---|
| `@c-0146` | `dpr_pos` | `ph.points::DamperSensor` |
| `@c-0147` | `eff_cl_stpt` | `ph.points::ZoneAirTempOccCoolingSp` |
| `@c-0148` | `eff_ht_stpt` | `ph.points::ZoneAirTempOccHeatingSp` |
| `@c-0149` | `flow_input` | `ph.points::DischargeAirFlowSensor` |
| `@c-014a` | `hw_valve` | `ph.points::ValveSensor` |
| `@c-014b` | `occ_cl_stpt` | `ph.points::ZoneAirTempOccCoolingSp` |
| `@c-014c` | `occ_ht_stpt` | `ph.points::ZoneAirTempOccHeatingSp` |
| `@c-014d` | `occ_status` | `ph::CmdPoint` |
| `@c-014e` | `occ_switch` | `ph.points::OccupiedSensor` |
| `@c-014f` | `sa_temp` | `ph.points::DischargeAirTempSensor` |
| `@c-0150` | `space_temp` | `ph.points::ZoneAirTempSensor` |
| `@c-0151` | `unocc_cl_stpt` | `ph.points::ZoneAirTempUnoccCoolingSp` |
| `@c-0152` | `unocc_ht_stpt` | `ph.points::ZoneAirTempUnoccHeatingSp` |

Against the seven zone-scoped connectors:

| Connector | Result | Record |
|---|---|---|
| `TCurZon` | **resolved** | `@c-0150` `space_temp` |
| `TCurZonSet` | ambiguous | `@c-0147` `eff_cl_stpt`, `@c-0148` `eff_ht_stpt` |
| `TComZonSet` | ambiguous | same two |
| `TPreTarSet` | missing | — |
| `TSheTarSet` | missing | — |
| `TDefSet` | missing | — |
| `rouZonFla` | missing | — |

### Why `TCurZon` resolves

`@c-0150` carries `point sensor zone air temp` with `kind:Number` and a
temperature unit, which is exactly `ph.points::ZoneAirTempSensor`. No other
point in the zone fits it: `@c-014f sa_temp` is a discharge air temperature, and
the six setpoints are `sp` rather than `sensor`. One candidate, so the connector
binds. This holds in all 270 zones across the three building models.

### Why `TCurZonSet` is ambiguous

`@c-0147` and `@c-0148` both carry `effective`, so both fit
`ZoneAirTempEffectiveSp`:

```
  TCurZonSet (ph.points::ZoneAirTempEffectiveSp) in Charlie Floor-4 VAV_21:
    - Charlie Floor-4 VAV_21 eff_cl_stpt
    - Charlie Floor-4 VAV_21 eff_ht_stpt
```

The other four setpoints (`occ_*`, `unocc_*`) do not carry `effective` and are
not candidates, so the `not dfTarget` style of exclusion is not what is missing
here. The two that remain are the effective cooling setpoint and the effective
heating setpoint, and the requirement does not say which one it wants.

That is a gap in the requirement, not in the building. `airConMod` selects
heating or cooling on the CDL side, and the specs are mode-agnostic, so they
ask for something the zone has two of. `ph.points` already distinguishes the two
by the `cooling` and `heating` markers these records carry, so a mode-qualified
spec in `obcflex.df`:

```xeto
ZoneAirTempEffectiveCoolingSp : ZoneAirTempEffectiveSp { cooling }
```

resolves `TCurZonSet` and `TComZonSet` in all thirty zones against the model
exactly as it stands. This is recorded under *Known gaps* in the top-level
README and has not been made.

### Why the other four are missing

No building tags a pre-conditioning target, a load-shed target, a default target
or a rogue-zone flag before it is commissioned for demand flexibility. Haystack
has no vocabulary for any of them, which is why `obcflex.df` defines them.

This is the expected result, and it is what the check is for: the `missing` list
is the commissioning scope for the zone. For charlie that is four points per
zone across thirty zones, plus a `DfSupervisor` publishing the mode, plus
`spaceRef` on each terminal unit, since charlie models no spaces.

## Site-level connectors

The same run reports these once for the building rather than per zone:

| Connector | Result on charlie |
|---|---|
| `PBui` | missing |
| `PBuiThrVar` | missing |
| `demFleMod` | missing |

`PBui` is the interesting one. Charlie does have a `siteMeter` at `@c-007d` with
a whole-building demand point at `@c-007e`, tagged `ac elec power sensor
demand`. It does not resolve because `ph.elec::ElecAcActivePowerSensor` requires
six markers (`ac avg magnitude active power elec`) plus an `elecDirection`
choice. Measured against the model:

| Spec | matches | on the site meter |
|---|---|---|
| `ElecAcActivePowerSensor` | 0 | 0 |
| `ElecAcPowerDemandSensor` | 5 | **1** |
| `ElecPowerSensor` | 21 | 1 |

As with the effective setpoint, the point is tagged well enough to bind; the
requirement names a spec real meters do not claim.

## A zone that does pass

`examples/conforming.trio` carries a zone commissioned for demand flexibility,
and the same check reports:

```
applicability:
  zones: 1   applicable: 1
    applicable: Zone 1 DF Controller
```

Comparing that zone against `@c-0145` shows what the thirty charlie zones lack,
without needing to alter charlie to find out.

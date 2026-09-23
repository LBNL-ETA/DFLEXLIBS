# Brick semantic constraints for the DF sequences

SHACL shapes describing the semantic data requirements of the CDL demand
flexibility sequences in Brick, so that the points a sequence needs can be found
automatically in a building's Brick model instead of being mapped by hand.

Coverage:

| Sequence | File |
|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `heating-or-cooling.ttl` |

`obc-extensions.ttl` holds the vocabulary those shapes depend on and is required
by all of them.

This is the Brick counterpart of `../s223/`. Same connectors, same pipeline, same
`obc:binds` / `obc:controls` linking predicates; see that README for how the
CDL annotation, `modelica-json` extraction and SHACL inference fit together.

## Running the checks

```sh
python examples/validate.py
```

Runs inference over `examples/conforming-model.ttl` and
`examples/non-conforming-model.ttl` and checks the result.

## Shapes

| CDL connector | Shape | Brick class |
|---|---|---|
| `TCurZon` | `obc:TCurZon` | `brick:Zone_Air_Temperature_Sensor` |
| `TCurZonSet` | `obc:TCurZonSet` | `brick:Zone_Air_Temperature_Setpoint`, excluding DF targets |
| `TComZonSet` (out) | `obc:TComZonSet` | same as `TCurZonSet` |
| `TPreTarSet` | `obc:TPreTarSet` | `obc:Pre_Conditioning_Zone_Air_Temperature_Setpoint` * |
| `TSheTarSet` | `obc:TSheTarSet` | `obc:Load_Shed_Zone_Air_Temperature_Setpoint` * |
| `TDefSet` | `obc:TDefSet` | `obc:Default_Zone_Air_Temperature_Setpoint` * |
| `PBui` | `obc:PBui` | `brick:Electric_Power_Sensor`, point of a `brick:Building_Electrical_Meter` |
| `PBuiThrVar` | `obc:PBuiThrVar` | `obc:Building_Electrical_Demand_Threshold_Setpoint` * |
| `rouZonFla` | `obc:rouZonFla` | `obc:Rogue_Zone_Status` * |
| `demFleMod` | `obc:demFleMod` | `obc:Demand_Flexibility_Mode_Status` * |

`*` = added by `obc-extensions.ttl`; the rest are stock Brick.

Plus two structural shapes: `obc:hoc-zone` (the control target, a
`brick:HVAC_Zone`) and `obc:hoc-electrical-meter` (where `PBui` is read).

## How this differs from the 223P shapes

The two libraries cover the same connectors, but the modelling is not a
transliteration, because the two ontologies carry meaning differently.

**Brick puts the meaning in the class name; 223P puts it in aspects on a
property.** Where the 223P shapes say "a quantifiable actuatable property with
quantity kind Temperature and aspect `Aspect-LoadShedTarget`", the Brick shape
says `sh:class obc:Load_Shed_Zone_Air_Temperature_Setpoint`. That makes the
Brick shapes shorter, at the cost of needing new classes.

**Quantity kinds come for free.** Brick declares `brick:hasQuantity` on the
class, so `brick:Zone_Air_Temperature_Sensor` already implies Temperature. The
223P shapes check `qudt:hasQuantityKind` on every instance.

**A zone temperature is identified by class, not by sensor location.** The 223P
shapes need the sensor's `hasObservationLocation` to be a `DomainSpace` to tell a
zone temperature from a duct temperature. `brick:Zone_Air_Temperature_Sensor`
says it outright.

**Brick needs five new classes where 223P needed four new aspects.** Brick has
load-shedding vocabulary, but `brick:Load_Shed_Setpoint` is a *power* setpoint
(`brick:Load_Setpoint`, quantity Power), so it cannot be reused for a zone
temperature target. `brick:Demand_Setpoint` is a suitable parent for the demand
threshold and is used as one.

## Modelling decisions

**The active setpoint exclusion is a node constraint, not a property shape.**
Brick subclass entailment makes every DF target a
`brick:Zone_Air_Temperature_Setpoint` too, so without an explicit exclusion a
zone's three event targets also match `obc:TCurZonSet`, leaving the binder with
four candidates per zone. The exclusion is `obc:not-a-df-target`, applied with
`sh:node`.

It cannot be written as a property shape over the `rdf:type` path the way the
223P version is: there the value node would be the *class*, and a Brick class is
an `rdfs:Class` rather than an instance of itself. 223P aspects are punned that
way, which is why the same rule takes a different form in each library.
`examples/non-conforming-model.ttl` covers this with `Zone3_TSheTarSet`, and
`validate.py` asserts it explicitly.

**`TCurZonSet` and `TComZonSet` have identical requirements.** The sequence
reads the active zone setpoint and writes it back, so in most buildings both
connectors resolve to the same point. The read/write distinction is the CDL
connector direction, not the Brick class.

**Units are permissive:** K, degC, degF for temperature; W, kW, MW for power.
Converting to the CDL unit is the translator's job.

**BACnet references are required on measured and commanded points only:**
`TCurZon`, `TCurZonSet`, `TComZonSet`, `PBui` and `PBuiThrVar`. The three event
targets and `rouZonFla` do not require one, as they are typically supplied as
configuration or by a DF supervisor rather than read from a controller.

**Vectorisation is handled at binding time.** `obc:hoc-zone` describes a single
zone; binding produces one match per zone, in connector-array order.

## Known gaps

Same as the 223P library, plus one Brick-specific item:

- **Heating vs cooling is not modelled.** The `airConMod` parameter selects
  heating or cooling, and a real binding should target
  `brick:Zone_Air_Heating_Temperature_Setpoint` or
  `brick:Zone_Air_Cooling_Temperature_Setpoint` accordingly. Both are subclasses
  of `brick:Zone_Air_Temperature_Setpoint`, so both currently match
  `obc:TCurZonSet`, which is right for a mode-agnostic shape but not specific
  enough for deployment. The same change has to land in `../s223/`,
  `../project-haystack/` and `../xeto/` at the same time.
- **Variant-conditional connectors are not expressed.** `PBui` and `PBuiThrVar`
  only exist for `ZoneControlVariant` 3 and 4.
- **The new classes are not upstream.** The five classes in
  `obc-extensions.ttl` are OBC-Flex extensions. Proposing the ones that belong
  in Brick proper would remove the need for the extension file.
- **Namespace.** `obc:` is `urn:hpflex/shapes#`, carried over from the earlier
  HPFlex work so that the existing tooling keeps working.

## Toolchain notes

**pySHACL `sh:qualifiedMinCount`.** pySHACL 0.21 does not raise
`sh:qualifiedMinCount` when a path has *zero* values, so every
`sh:qualifiedMinCount 1` here is paired with a plain `sh:minCount 1`. Removing
the `sh:minCount` silently stops the shape from rejecting models where the point
is missing entirely.

**Brick.ttl is not loaded by `validate.py`.** The example models type their
points with the exact classes the shapes name, so only `obc-extensions.ttl` is
needed to resolve the subclass chains. A real building model is validated with
Brick loaded, which additionally lets Brick's own subclasses match, notably
`Zone_Air_Heating_Temperature_Setpoint` and
`Zone_Air_Cooling_Temperature_Setpoint` for `obc:TCurZonSet`.

## Layout

```
brick/
├── obc-extensions.ttl        vocabulary: 5 new classes, obc:binds/obc:controls
├── heating-or-cooling.ttl    shapes for HeatingOrCooling
└── examples/
    ├── conforming-model.ttl      minimal Brick model that satisfies every shape
    ├── non-conforming-model.ttl  model exercising each rejection path
    └── validate.py               runs inference over both and checks the result
```

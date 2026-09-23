# ASHRAE 223P semantic constraints for the DF sequences

SHACL shapes describing the semantic data requirements of the CDL demand
flexibility sequences, so that the points a sequence needs can be found
automatically in a building's 223P model instead of being mapped by hand.

Coverage:

| Sequence | File |
|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `heating-or-cooling.ttl` |

`obc-extensions.ttl` holds the vocabulary those shapes depend on and is required
by all of them.

## How it fits together

The CDL sequence and the shape library are kept apart:

- The **CDL annotation** on a connector names the shape that connector binds
  to: `ctrl:TCurZon a s223:Property ; obc:binds obc:TCurZon .`
- The **shape library** (here) defines what `obc:TCurZon` requires.

Nothing building-specific appears in either one, which is what lets the same
sequence deploy to different buildings. Resolution happens in three steps:

1. `modelica-json` extracts the `__cdl(semantic(...))` annotations from the `.mo`
   files into a controller graph.
2. SHACL inference runs these shapes over the building's 223P model. Every node
   conforming to a requirement shape is labelled with that shape as an
   `rdf:type` (the `*Annotation` rules at the bottom of `heating-or-cooling.ttl`).
3. Each connector's `obc:binds` target is looked up among the labelled nodes,
   giving the BACnet point behind it.

## Running the checks

```sh
python examples/validate.py
```

Runs inference over `examples/conforming-model.ttl` and
`examples/non-conforming-model.ttl` and checks the result, covering steps 2 and
3 above.

## Shapes

One shape per connector of `HeatingOrCooling`:

| CDL connector | Shape | 223P class | Distinguished by |
|---|---|---|---|
| `TCurZon` | `obc:TCurZon` | `QuantifiableObservableProperty` | Temperature, observed by a sensor located in a `DomainSpace` |
| `TCurZonSet` | `obc:TCurZonSet` | `QuantifiableActuatableProperty` | Temperature, `Aspect-Setpoint`, no DF target aspect |
| `TComZonSet` (out) | `obc:TComZonSet` | `QuantifiableActuatableProperty` | same as `TCurZonSet` |
| `TPreTarSet` | `obc:TPreTarSet` | `QuantifiableActuatableProperty` | `obc:Aspect-PreConditioningTarget` |
| `TSheTarSet` | `obc:TSheTarSet` | `QuantifiableActuatableProperty` | `obc:Aspect-LoadShedTarget` |
| `TDefSet` | `obc:TDefSet` | `QuantifiableActuatableProperty` | `obc:Aspect-DefaultTarget` |
| `PBui` | `obc:PBui` | `QuantifiableObservableProperty` | Power, observed by an `ElectricityMeter` |
| `PBuiThrVar` | `obc:PBuiThrVar` | `QuantifiableActuatableProperty` | Power, `s223:Aspect-Threshold` |
| `rouZonFla` | `obc:rouZonFla` | `EnumeratedObservableProperty` | `Binary-Logical`, `obc:Aspect-RogueZoneFlag` |
| `demFleMod` | `obc:demFleMod` | `EnumeratedObservableProperty` | `obc:EnumerationKind-DemandFlexibilityMode` |

Plus three structural shapes: `obc:hoc-zone` (the control target),
`obc:hoc-electrical-service` (where `PBui` is read) and `obc:heating-or-cooling`
(the sequence as an `s223:Function`).

## Modelling decisions

**Aspects carry the demand flexibility meaning.** 223P can say "this is a
temperature setpoint" but has no way to say "this is the load-shed target".
`obc-extensions.ttl` adds the missing aspects as `EnumerationKind-Aspect`
subclasses, using the same class/instance punning 223P uses for its own
(`s223:Aspect-Setpoint`, `s223:Aspect-Threshold`). `s223:Aspect-Threshold`
already exists and is reused for `PBuiThrVar`.

**`TCurZonSet` and `TComZonSet` have identical requirements.** The sequence reads
the active zone setpoint and writes it back, so in most buildings both connectors
resolve to the same property. The read/write distinction is carried by
`s223:hasInput` vs `s223:hasOutput` on the function, not by the property. The
example model shows one property matching both.

**The active setpoint excludes event targets.** Without this, a zone's three DF
target setpoints also match `obc:TCurZonSet`, giving the binder four candidates
per zone. `obc:not-a-df-target` rules them out via the shared
`obc:Aspect-DemandFlexibilityTarget` superclass.

**A zone temperature is defined by where the sensor is, not by the property.**
`obc:TCurZon` requires a sensor whose `hasObservationLocation` is a
`DomainSpace`. This keeps a duct or outdoor air temperature from matching.

**Units are permissive.** CDL works internally in kelvin, but real BAS points are
usually degC or degF, so the shapes accept K, degC and degF (W, kW, MW for
power). Converting to the CDL unit is the translator's job; rejecting a
correctly identified point because it reports degF would defeat the purpose.

**BACnet references are required on measured and commanded points only.**
`obc:has-external-ref` requires an `s223:BACnetExternalReference` on `TCurZon`,
`TCurZonSet`, `TComZonSet`, `PBui` and `PBuiThrVar`, since those must be
addressable in the BAS. The three event targets (`TPreTarSet`, `TSheTarSet`,
`TDefSet`) and `rouZonFla` do not require one: they are typically supplied as
configuration or by a DF supervisor rather than read from a controller. Remove
`obc:has-external-ref` from a shape to match models that do not yet carry
external references.

**Vectorisation is handled at binding time.** `HeatingOrCooling` is vectorised
over `nZon` zones, but `obc:hoc-zone` describes a single zone. Binding produces
one match per zone, and the order of those matches is the order of the connector
arrays.

## Known gaps

- **Heating vs cooling is not modelled.** The `airConMod` parameter selects
  heating or cooling, and a real binding should target the zone's heating
  setpoint or its cooling setpoint accordingly. The shapes are mode-agnostic;
  adding this means role-qualified variants of the setpoint shapes
  (`s223:hasRole s223:Role-Heating` / `s223:Role-Cooling`). The same change has
  to land in `../brick/`, `../project-haystack/` and `../xeto/` at the same
  time, since all four libraries have to agree on what a connector binds to.
- **Variant-conditional connectors are not expressed.** `PBui` and `PBuiThrVar`
  only exist for `ZoneControlVariant` 3 and 4, but their shapes are
  unconditional and `obc:heating-or-cooling` does not require them. Which
  connectors a given instance has is a CDL-side concern.
- **`s223:Zone` is used for the electrical service.** 223P has no `Building`
  class, so `obc:hoc-electrical-service` is an electrical-domain `s223:Zone`.
  Sites that model whole-building power differently need this shape revisited.
- **Namespace.** `obc:` is `urn:hpflex/shapes#`, carried over from the earlier
  HPFlex work so that the existing tooling keeps working.

## Toolchain note

These shapes target **pySHACL**, which is what the reference workflow uses.
pySHACL 0.21 does not raise `sh:qualifiedMinCount` when a path has *zero*
values, so every `sh:qualifiedMinCount 1` here is paired with a plain
`sh:minCount 1`. Removing the `sh:minCount` silently stops the shape from
rejecting models where the point is missing entirely.

## Layout

```
s223/
├── obc-extensions.ttl        vocabulary: aspects, DF modes, obc:binds/obc:controls
├── heating-or-cooling.ttl    shapes for HeatingOrCooling
└── examples/
    ├── conforming-model.ttl      minimal 223P model that satisfies every shape
    ├── non-conforming-model.ttl  model exercising each rejection path
    └── validate.py               runs inference over both and checks the result
```

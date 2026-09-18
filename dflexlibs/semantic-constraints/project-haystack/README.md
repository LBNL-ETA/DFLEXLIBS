# Project-Haystack semantic constraints for the DF sequences

Haystack 4 defs plus binding filters describing the semantic data requirements
of the CDL demand flexibility sequences, for deployment on **SkySpark 3**, which
does not support Xeto.

The Xeto version of the same requirements is in `../xeto/`. Use that one where
the tooling supports it: it is a real type system and `xeto fits -graph`
enforces it. This directory is what you can actually run on SkySpark 3.

Currently covered:

| Sequence | Filters | Equip def |
|---|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `filters.trio` | `^dfHeatingOrCooling` in `lib/equips.trio` |

## What a constraint looks like without Xeto

There is no single artifact that plays the role of a SHACL shape or a Xeto spec.
The requirements are split across three things, and only the last one is
enforced by anything:

1. **Tag defs** (`lib/tags.trio`) declare the vocabulary — seven markers Haystack
   does not have. This is documentation and namespace structure.
2. **Equip defs with `children` prototypes** (`lib/equips.trio`) declare what a
   conforming zone looks like. `children` is the Haystack 4 analogue of Xeto's
   `points` slot, and it is how stock Haystack describes e.g. a chiller's
   expected points. **Nothing enforces it.** There is no defs-level equivalent
   of `xeto fits -graph`.
3. **Filters** (`filters.trio`) are the operative artifact. One per CDL
   connector. Binding runs these; `validate.axon` runs them to check a project.

So the honest answer to "what do constraints look like in plain Haystack" is:
**they look like queries, not schemas.** The requirement "this zone must have a
load-shed target setpoint" is expressed as a filter that must return exactly one
record, and it is checked by running it, not by validating the model against a
shape.

## Running the checks

```sh
./validate.sh /path/to/haxall-4.0.6/bin/axon
```

Verified output: `conforming.trio` resolves all 10 connectors to exactly one
point each; `non-conforming.trio` reports 6 MISSING and no AMBIGUOUS.

The Axon shell from Haxall 4.0.6 evaluates the same Haystack filter grammar
SkySpark 3 uses, so the filters themselves are genuinely tested. **What is not
tested is SkySpark 3 itself** — the defs in `lib/` have not been loaded into a
SkySpark project, and `validate.axon` has not been run there. Two things to
check when you do:

- SkySpark 3 wants defs packaged in a pod or project-level def lib; `lib/` here
  is the source trio, not a packaged lib.
- `readAll(parseFilter(...))` and `.set()` behave the same in SkySpark's Axon as
  in the Haxall shell, but the shell has a smaller function set (`ioReadStr` and
  `toCode` are absent there, for instance), so a SkySpark run may allow a
  tidier implementation.

## The filters

| CDL connector | Scope | Filter |
|---|---|---|
| `TCurZon` | zone equip | `point and sensor and zone and air and temp` |
| `TCurZonSet` | zone equip | `point and sp and zone and air and temp and not dfTarget` |
| `TComZonSet` | zone equip | `… and not dfTarget and writable` |
| `TPreTarSet` | zone equip | `… and dfTarget and dfPreCondition` |
| `TSheTarSet` | zone equip | `… and dfTarget and dfLoadShed` |
| `TDefSet` | zone equip | `… and dfTarget and dfDefault` |
| `rouZonFla` | zone equip | `point and sp and zone and dfRogueZone` |
| `PBui` | site | `point and sensor and elec and power and equipRef->siteMeter` |
| `PBuiThrVar` | site | `point and sp and elec and power and dfThreshold` |
| `demFleMod` | site | `point and sp and dfMode` |

Zone-equip filters are additionally scoped to one `dfHeatingOrCooling` equip.
Each must return exactly one point: zero means the sequence cannot be deployed,
more than one means the tagging is ambiguous.

## Modelling decisions

**`not dfTarget` is doing real work.** The three event targets are zone air
temperature setpoints too, so without the exclusion the active-setpoint filter
matches all four. `examples/check-ambiguity.axon` demonstrates it:

```
count  status     variant
-----  ---------  ----------------------
4      AMBIGUOUS  without 'not dfTarget'
1      ok         with 'not dfTarget'
1      ok         with 'and effective'
```

This is the same collision that needed `obc:not-a-df-target` in `../s223/`, an
`sh:not` node constraint in `../brick/`, and a switch to
`ZoneAirTempEffectiveSp` in `../xeto/`. **Plain Haystack handles it the most
directly of the four**, because filters support `not` — which Xeto does not.
The `and effective` variant also works and is arguably more precise, but it is
not the default here because many BAS models never tag `effective`.

**The def taxonomy is not what filters match on.** `is:` in `lib/tags.trio`
builds the namespace, but a Haystack filter tests for tags literally present on
a record. So an event target carries **both** `dfTarget` and its specific marker
(`dfLoadShed`). That redundancy is normal Haystack practice — a zone temp sensor
literally carries `zone air temp sensor point` — and it is exactly what makes
`not dfTarget` work as a one-term exclusion.

**`TCurZonSet` and `TComZonSet` resolve to the same point.** The sequence reads
the active zone setpoint and writes it back. The only difference between the two
filters is `writable` on the output. The verified run shows both binding to
`@zone1TCurZonSet`.

**`PBui` is scoped by `equipRef->siteMeter`.** `siteMeter` is the stock Haystack
tag for a site's main meter, so the ref traversal pins this to whole-building
demand. `examples/non-conforming.trio` includes a chiller submeter to prove a
submetered power point is not picked up.

**The container is the equip, not the zone** — same as the Xeto version, and for
the same reason: Haystack hangs points off equips via `equipRef`, and the zone
is reached through the equip's `spaceRef`. `demFleMod` is building-level and
lives on a separate `^dfSupervisor` equip.

**No unit constraints.** This is a real loss relative to the other three
libraries. SHACL checks `unit:K unit:DEG_C unit:DEG_F` explicitly and Xeto
derives it from the quantity, reporting `Unit 'kPa' must be 'temperature' not
'pressure'`. A Haystack filter can test `unit=="°F"` but cannot express "any
temperature unit", so unit checking has to move into `validate.axon` as a
separate lookup against a list, or be skipped. It is currently skipped.

## Known gaps

- **Not run on SkySpark 3.** See above.
- **No unit or quantity checking.** See above.
- **`children` prototypes are decorative.** They document the expectation; only
  the filters enforce it.
- **Heating vs cooling is not modelled.** `airConMod` selects one or the other,
  and a real binding should target the zone's heating or cooling setpoint.
  Haystack has the tags for it (`heating` / `cooling`), so this is a smaller gap
  here than elsewhere.
- **Variant-conditional connectors.** `PBui` and `PBuiThrVar` only apply to
  `ZoneControlVariant` 3 and 4, which is why they are site-scoped rather than
  required of every zone.
- **No BACnet reference requirement.** The SkySpark equivalent is connector tags
  (`bacnetCur`, `bacnetWrite`), which are deployment-specific. Worth adding once
  the demonstration site is picked.

## Layout

```
project-haystack/
├── lib/
│   ├── lib.trio          def lib declaration (^lib:obcflexDf)
│   ├── tags.trio         7 demand flexibility marker tag defs
│   └── equips.trio       ^dfHeatingOrCooling and ^dfSupervisor, with children protos
├── filters.trio          one binding filter per CDL connector -- the operative artifact
├── validate.axon         resolve every connector against a project, report missing/ambiguous
├── validate.sh           run validate.axon over both example models
└── examples/
    ├── conforming.trio        14 recs, all 10 connectors resolve
    ├── non-conforming.trio    8 recs exercising each failure mode
    └── check-ambiguity.axon   why TCurZonSet carries `not dfTarget`
```

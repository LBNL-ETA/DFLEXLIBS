# Project-Haystack semantic constraints for the DF sequences

Haystack 4 defs plus binding filters describing the semantic data requirements
of the CDL demand flexibility sequences, for deployment on **SkySpark 3**, which
does not support Xeto.

The Xeto form of the same requirements is in `../xeto/`. Use that where the
tooling supports it: it is a type system, and `xeto fits -graph` enforces it.
This directory targets SkySpark 3.

Coverage:

| Sequence | Filters | Equip def |
|---|---|---|
| `ZoneTemperatureSetpointChange.HeatingOrCooling` | `filters.trio` | `^dfHeatingOrCooling` in `lib/equips.trio` |

## What a constraint looks like without Xeto

There is no single artifact that plays the role of a SHACL shape or a Xeto spec.
The requirements are split across three things, and only the last is enforced:

1. **Tag defs** (`lib/tags.trio`) declare the vocabulary: seven markers Haystack
   does not have. This is documentation and namespace structure.
2. **Equip defs with `children` prototypes** (`lib/equips.trio`) declare what a
   conforming zone looks like. `children` is the Haystack 4 analogue of Xeto's
   `points` slot, and is how stock Haystack describes, for example, a chiller's
   expected points. Nothing enforces it; there is no defs-level equivalent of
   `xeto fits -graph`.
3. **Filters** (`filters.trio`) are the operative artifact, one per CDL
   connector. Binding runs these; `validate.axon` runs them to check a project.

Constraints in plain Haystack are therefore queries rather than schemas. The
requirement "this zone must have a load-shed target setpoint" is expressed as a
filter that must return exactly one record, and is checked by running it.

## Running the checks

```sh
./validate.sh /path/to/haxall-4.0.6/bin/axon
```

Two kinds of check run.

**Validation** against `examples/conforming.trio` and
`examples/non-conforming.trio`, which are built to exercise the filters.
Expected: `conforming.trio` resolves all 10 connectors to exactly one point
each; `non-conforming.trio` reports 6 MISSING and no AMBIGUOUS.

**Survey** against `examples/alpha.trio`, `bravo.trio` and `charlie.trio`, real
site exports from project-haystack.org. Nothing is expected to pass; see
[Checking against real buildings](#checking-against-real-buildings).

The Axon shell from Haxall 4.0.6 evaluates the same Haystack filter grammar
SkySpark 3 uses, so the filters themselves are exercised. SkySpark 3 itself is
not: the defs in `lib/` have not been loaded into a SkySpark project, and
`validate.axon` has not been run there. Two things to check when doing so:

- SkySpark 3 wants defs packaged in a pod or project-level def lib. `lib/` here
  is the source trio, not a packaged lib.
- `readAll(parseFilter(...))` and `.set()` behave the same in SkySpark's Axon as
  in the Haxall shell, but the shell has a smaller function set (`ioReadStr` and
  `toCode` are absent, for instance), so a SkySpark run may allow a tidier
  implementation.

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

## Checking against real buildings

`conforming.trio` and `non-conforming.trio` are written to match the filters,
which makes them a test of the filter grammar rather than of the filters'
usefulness. The three site models are real exports (`alpha.trio` 2032 recs,
`bravo.trio` 1077, `charlie.trio` 624) that carry no demand flexibility tagging.

Running `validate.axon` over them unmodified reports only that the `df*` tags
are absent. `examples/site-survey.axon` asks a more useful question: given a
building as it is actually tagged, which connectors would bind today, which are
missing, and which are ambiguous. It selects candidate zones by the requirement
itself, every equip owning a point matching the `TCurZon` filter, rather than by
local equip naming, then aggregates the per-connector result across them.

Results, `ok` / `missing` / `ambiguous` counted over zones:

| Connector | alpha (139 zones) | bravo (97) | charlie (34) |
|---|---|---|---|
| `TCurZon` | **139 ok** | **97 ok** | **34 ok** |
| `TCurZonSet` | 138 ambiguous (4-way) | **97 ok** | 30 ambiguous (6-way) |
| `TComZonSet` | 139 missing | 97 missing | 34 missing |
| `TPreTarSet` / `TSheTarSet` / `TDefSet` / `rouZonFla` | missing | missing | missing |
| `PBui` | missing | missing | **ok** |
| `PBuiThrVar` / `demFleMod` | missing | missing | missing |

**`TCurZon` resolves everywhere.** `point and sensor and zone and air and temp`
returns exactly one point in all 270 zones across the three sites. Zone air
temperature is tagged consistently in the field.

**`TCurZonSet` is under-specified.** In alpha every zone carries four zone air
temperature setpoints, and in charlie six:

```
  TCurZonSet in Charlie Floor-4 VAV_21:
    - Charlie Floor-4 VAV_21 unocc_cl_stpt
    - Charlie Floor-4 VAV_21 unocc_ht_stpt
    - Charlie Floor-4 VAV_21 occ_cl_stpt
    - Charlie Floor-4 VAV_21 occ_ht_stpt
    - Charlie Floor-4 VAV_21 eff_cl_stpt
    - Charlie Floor-4 VAV_21 eff_ht_stpt
```

`not dfTarget` removes the demand flexibility collision the filter was designed
for, but real buildings split the active setpoint along two further axes the
filter does not address: heating vs cooling, and occupied vs unoccupied vs
effective. Both are already tagged (`heating`/`cooling`, `occ`/`unocc`/
`effective`), so the filter can use them. Bravo passes only because its zones
carry a single setpoint each.

**`TComZonSet` fails on `writable` everywhere.** None of the three exports tag
any point `writable`. It is a SkySpark connector-layer concept, applied when a
point is bound to a BACnet write, and does not survive into a trio export. Using
it to distinguish the output connector from the input works in a live project
but not in a model, which makes it unsuitable as a portable discriminator.

**`PBui` needs `siteMeter`, which only charlie has.** Where it exists, the
`equipRef->siteMeter` traversal resolves to exactly one point. Alpha has 13 elec
power sensors and bravo none, and neither marks a main meter, so this is a model
gap at those sites rather than a filter problem.

The `df*` connectors being missing everywhere is the expected result, and is
what the survey is for: it is the commissioning checklist for a site. Before
`HeatingOrCooling` can be deployed to alpha, the site needs three target
setpoints and a rogue-zone flag per zone, a `dfSupervisor` equip carrying the
mode point, and a tagged main meter.

`../xeto/` runs an equivalent survey against its own building models, reporting
in the same grid with Xeto specs in place of these filters. On the active zone
setpoint the two libraries fail in opposite directions: the filter here
over-matches, while the Xeto spec under-matches because it depends on an
`effective` tag many models do not carry.

## Modelling decisions

**`not dfTarget` is load-bearing.** The three event targets are zone air
temperature setpoints too, so without the exclusion the active-setpoint filter
matches all four. `examples/check-ambiguity.axon` demonstrates it:

```
count  status     variant
-----  ---------  ----------------------
4      AMBIGUOUS  without 'not dfTarget'
1      ok         with 'not dfTarget'
1      ok         with 'and effective'
```

This is the same collision that needs `obc:not-a-df-target` in `../s223/`, an
`sh:not` node constraint in `../brick/`, and a switch to
`ZoneAirTempEffectiveSp` in `../xeto/`. Plain Haystack handles it most directly
of the four, because filters support `not`, which Xeto does not. The
`and effective` variant also works and is more precise, but is not the default
because many BAS models never tag `effective`.

**The def taxonomy is not what filters match on.** `is:` in `lib/tags.trio`
builds the namespace, but a Haystack filter tests for tags literally present on
a record. An event target therefore carries both `dfTarget` and its specific
marker (`dfLoadShed`). That redundancy is normal Haystack practice, a zone temp
sensor literally carries `zone air temp sensor point`, and it is what makes
`not dfTarget` work as a one-term exclusion.

**`TCurZonSet` and `TComZonSet` resolve to the same point.** The sequence reads
the active zone setpoint and writes it back. The only difference between the two
filters is `writable` on the output; both bind to `@zone1TCurZonSet` in
`conforming.trio`.

**`PBui` is scoped by `equipRef->siteMeter`.** `siteMeter` is the stock Haystack
tag for a site's main meter, so the ref traversal pins this to whole-building
demand. `examples/non-conforming.trio` includes a chiller submeter to confirm a
submetered power point is not picked up.

**The container is the equip, not the zone**, as in the Xeto version and for the
same reason: Haystack hangs points off equips via `equipRef`, and the zone is
reached through the equip's `spaceRef`. `demFleMod` is building-level and lives
on a separate `^dfSupervisor` equip.

**No unit constraints.** SHACL checks `unit:K unit:DEG_C unit:DEG_F` explicitly
and Xeto derives it from the quantity, reporting `Unit 'kPa' must be
'temperature' not 'pressure'`. A Haystack filter can test `unit=="°F"` but
cannot express "any temperature unit", so unit checking has to move into
`validate.axon` as a separate lookup against a list, or be skipped. It is
currently skipped.

## Known gaps

- **Not run on SkySpark 3.** See [Running the checks](#running-the-checks).
- **`writable` does not survive export.** `TComZonSet` is distinguished from
  `TCurZonSet` by `writable`, which none of the three real site exports carry,
  so the output connector binds in a live project but never in a model. A
  portable discriminator is needed.
- **No unit or quantity checking.** See above.
- **`children` prototypes are decorative.** They document the expectation; only
  the filters enforce it.
- **Heating vs cooling is not modelled, and neither is occupancy.** `airConMod`
  selects heating or cooling, and a real binding should target the zone's
  heating or cooling setpoint accordingly. This makes `TCurZonSet` ambiguous in
  168 of 270 real zones. Haystack has the tags for both axes, so closing it here
  is cheap, but the same change has to land in `../s223/`, `../brick/` and
  `../xeto/` at the same time, since all four libraries have to agree on what a
  connector binds to.
- **Variant-conditional connectors.** `PBui` and `PBuiThrVar` apply only to
  `ZoneControlVariant` 3 and 4, which is why they are site-scoped rather than
  required of every zone.
- **No BACnet reference requirement.** The SkySpark equivalent is connector tags
  (`bacnetCur`, `bacnetWrite`), which are deployment-specific. Add once the
  demonstration site is selected.

## Layout

```
project-haystack/
├── lib/
│   ├── lib.trio          def lib declaration (^lib:obcflexDf)
│   ├── tags.trio         7 demand flexibility marker tag defs
│   └── equips.trio       ^dfHeatingOrCooling and ^dfSupervisor, with children protos
├── filters.trio          one binding filter per CDL connector; the operative artifact
├── validate.axon         resolve every connector against a project, report missing/ambiguous
├── validate.sh           run both checks over all five example models
└── examples/
    ├── conforming.trio        14 recs, all 10 connectors resolve
    ├── non-conforming.trio    8 recs exercising each failure mode
    ├── check-ambiguity.axon   why TCurZonSet carries `not dfTarget`
    ├── site-survey.axon       per-connector gap report for a real, un-prepared model
    ├── alpha.trio             real site from project-haystack.org, 2032 recs, 139 zones
    ├── bravo.trio             real site, 1077 recs, 97 zones
    └── charlie.trio           real site, 624 recs, 34 zones
```

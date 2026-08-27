# Context specification

The contract for `_docs/context/`. Hand-written, never generated.

`_docs/context/` is the backbone an agent reads instead of opening Unity or the 3,900-line raw
export. It carries **structure**, not narrative: what exists and where it lives in the twin.
Behaviour lives in `_docs/reference/`. What a control platform makes of that structure lives in
that vendor module's own `context/`. Status lives nowhere — it is derived on demand, never written
down.

## Rules

1. **Structure only.** A fact belongs here when it answers *what exists and where*. If it answers
   *why* or *what happens next*, it belongs in `_docs/reference/`.
2. **No temporal facts.** No implementation status, no progress, no decision logs, no "the old
   sequence used to". A file that would be wrong next week does not belong in the backbone.
3. **Short and technical.** Prose is capped per key (below). `build_knowledge.py` **refuses to
   write** on an over-cap value or an unknown key — an unenforced cap is a cap that drifts, and the
   twelve keys this vocabulary replaced grew out of six exactly that way. Tables and trees over
   paragraphs.
4. **Every fact traceable.** Each generated section names the file it was read from. A fact with no
   source is not written.
5. **Never hand-edit `_docs/context/`.** Every `.md` under it is regenerated wholesale.
   Author in the Unity ContextNodes, or in the curated files listed below.

## File layout

```
_workflow/                 PUBLIC - how the project is built
  CLAUDE.md                the agent's instructions, imported by the root stub
  CONTEXT-SPEC.md          this file - the contract
  README.md                how the skills chain
  skills/                  read by path - not auto-discovered, see CLAUDE.md
  config/modules.json      which vendor modules exist

_docs/
  context/                 GENERATED - never hand-edit
    PROVENANCE.md          freshness of every scene export, and the documentation gaps
    machine.md             process flow, group index, circulation ring, the scene list
    plc-symbols.md         global twin symbol index: name, twin path, device type, FB type
    fg-*.md                one per functional group, fixed section pattern
    devices/*.md           one per OC device TYPE
    .machine.json          the vendor handoff - this structure as schema-versioned JSON
    .topology.json         the probed scene wiring
  ImageDescription.md      CURATED SOURCE - the figures, their scopes and their callouts
  DeviceDescription-SPEC.md  THE CONTRACT for the files below. Describes no device
  devices/<type>.md        CURATED SOURCE - one file per device TYPE, rendered into context/devices/
  reference/               CURATED - hand-written, never generated
    *-behaviour.md         one per group: sequences, interlocks, faults, recovery
    gripper-station-reset.md  the reset model FG_03 and FG_05 share
    fg-system-safety.md    the safety chain
    state-lamp.md          the signal tower mapping
```

Platform-specific pages are **not** here. `plc-io.md`, `spt-framework.md` and
`plc-io-exceptions.md` moved into `Beckhoff/_docs/`, along with the per-group control sections,
when the second vendor arrived — see `Beckhoff/_workflow/README.md`.

Deleted by this spec, and why: `implementation-status.md` (temporal), `interfaces.md` (behaviour →
`reference/`; ring order → `machine.md`), `plc-instance.md` (per-group process image → the vendor's
`fg-*.md`).

## ContextNode key vocabulary

Authored in the Unity scene. **Nine keys, no others.** `build_knowledge.py` fails the build on an
unknown key or an over-length value — a cap that is not enforced is a cap that drifts.

| Key | Where | Cap | Answers |
|---|---|---:|---|
| `Function` | any node | 200 | What this is and what it does. One or two sentences. |
| `Role` | instance override | 120 | Which instance this is, in this machine. |
| `Signal` | device | 200 | I/O semantics and sense, where not obvious from the type. |
| `BitLayout` | `LinkByte`, `PanelSampler` | 300 | Which control/status bit carries what. |
| `Twin` | any node | 250 | **How Unity realises it** — which components, wired to what. |
| `Approximation` | any node | 250 | **Where the model differs from real hardware**, or is abstract. |
| `Caution` | any node | 200 | **The trap** — what will bite someone writing PLC code against it. |
| `ProcessFlow` | **root only** | 400 | The path a pallet takes through the machine. |
| `Layout` | **root only** | 300 | Physical arrangement of the cell. |

### The three twin-fidelity keys

`Function`, `Role`, `Signal` and `BitLayout` describe the machine. These three describe **the model of
it**, and that is knowledge only the twin holds — the PLC cannot state it, and `reference/` is the
wrong home because it is not behaviour, it is fidelity.

| Key | The question it answers |
|---|---|
| `Twin` | *"What is actually in the scene?"* — the OC/Unity components and their wiring |
| `Approximation` | *"Where does this lie to me?"* — abstract, simplified, or divergent from real hardware |
| `Caution` | *"What will bite me?"* — the consequence a PLC author has to design around |

They earn their place on the **mechanism** nodes, not only on devices. `Y_Gripper1/Gripper` carries no
`oc.deviceType` and is not a PLC symbol, yet its component wiring is the single reason a
de-energised solenoid drops the part — the fact that cost a dropped part to learn.

**`Caution` is not a second safety policy.** Machine safety is the PLC's and lives in
`reference/fg-system-safety.md`. `Caution` is twin-side: *this component releases on any movement*,
*this sensor cannot see a part it never picked up*, *this button is a toggle so a click latches*.

### Where to author: the prefab or the instance

> **A prefab-asset entry only reaches instances that have NOT overridden the ContextNode.**

Authoring on the asset (`context_set --prefab true`) is the high-leverage move — one write covered
all nine `Y_Stopper/Axis` nodes, because none of them carried a node of their own. But every device
that already has an authored `Function` has an overridden entry list, and an asset write **silently
fails to reach it**: the call succeeds, the instance keeps its old keys, and only a re-export shows
the entry never arrived.

| The node… | Author on |
|---|---|
| has no `ContextNode` yet | the **prefab** — every instance inherits |
| already carries authored keys | the **instance** — the asset cannot reach it |
| says something instance-specific (`Role`) | the **instance**, always |

Check with `context_get` after a prefab write. If the key is not in the instance's `entries`, write
it again per instance.

### Excluding a variant

There is no authored key for it. **Disable the GameObject.**

`ContextTreeFactory.HasMeaningfulContent` returns false for an inactive object and skips its whole
subtree, which is what the OC Project Tree export has always done — so the two exports agree by
construction and their device counts reconcile. A disabled variant is absent from the knowledge base
entirely: no symbol, no codegen input, and not even a `context_sync` scan target.

### Vendor hardware: a scene, not a disabled sibling

Hardware that belongs to **one vendor** is not a disabled object in a shared scene. It belongs to
that vendor's own scene under `Unity/Assets/Demo_1/Scenes/`, which instances the shared
`Machine_1` prefab and adds only what is its own. Today that is the operator panel:
`VC_Demo_1_Beckhoff_1` carries `H_ControlPanel`, `VC_Demo_1_Siemens_1` carries
`H_ControlPanel_Siemens`, and 171 nodes are identical because they come from the prefab.

Each scene exports its own `<Scene>_Context.json` and `<Scene>_Project_Tree.xml`, discovered by
glob. Adding a vendor is adding a scene and exporting it — there is no list to edit.

**A device shared by every vendor goes in the prefab.** Editing one scene's copy of a shared device
is what the cross-scene comparison catches: the node starts carrying `†`, which is the build saying
the edit landed in the wrong place.

Retired keys and where their content goes:

| Retired | Was | Goes to |
|---|---:|---|
| `Process` | 11 | `reference/<group>-behaviour.md` |
| `Interfaces` | 6 | derived from the probed topology → `machine.md` |
| `Safety` | 3 | `reference/<group>-behaviour.md` |
| `PlcTree` | 13 | derived from `oc.hierarchyRole` — the renderer emits it |
| `Purpose` | 1 | `Function` |
| `Variant` | 1 | `Function` |

**`Signal` states sense, not story.** `"Extending closes the gate; retracted is home."` — not the
paragraph explaining which nine authored entries got it backwards. That correction is a behaviour
fact and belongs in `reference/`.

## The functional group page

Every `fg-*.md` carries these sections, in this order, always — an empty section renders as
`_None._` rather than being omitted, so a reader can tell "nothing here" from "not generated".

| # | Section | Source | Content |
|---|---|---|---|
| 1 | _(header table)_ | context export | scene path, twin PLC path, serving Index, symbol count, behaviour link |
| 2 | `## Figure` | `ImageDescription.md` | the group's screenshot and caption. Numbered arrows that point at **devices** carry no legend — their numbers are the `#` column of section 3. Arrows that point at a **module** get a one-line map, because a module has no row in that table |
| 3 | `## Devices` | both exports | **one table per group**, one row per symbol: figure callout, device type (linked to its type page), twin FB type, twin PLC path, and the authored `Function` as *what it does* |
| 4 | `## Bit mapping` | context export + `_docs/devices/` | one table per device whose bits are addressable: an aggregate's bits are derived from its children, a plain byte's are parsed from its `BitLayout`, and the rest of that sentence is kept as the comment under the table. **Every bit is named as the PLC addresses it** — `Control.1`, `StatusData.7` — from the `Control:`/`Status:` member each type declares in its `_docs/devices/<type>.md`, because a plain link and a data link spell it differently and a bare "bit 3" does not say which |
| 5 | `## Hierarchy` | context export | the scene tree as YAML — one key per node, with what the node is as the comment |
| 6 | `## Unity` | context export | MIL component, aggregated and simulation-only devices, then `### Notes`: the authored prose **no table already carries**, and what carries no context at all |
| 7 | `## Control implementations` | **declared** | one row per vendor module in `_workflow/config/modules.json`: an absolute URL into that module's repository, or a note that it publishes no knowledge base yet |

**Each fact appears once on the page.** A device's `Function` is its *what it does* cell and is not
repeated under `### Notes`; a `BitLayout` that became a table is not repeated as prose. Two tables
listing the same devices with different columns — which is what the figure legend and the old
`## Components` table were — is the failure this ordering exists to prevent.

**The `†` mark.** Every scene instances the same `Machine_1` prefab and adds its own vendor's
operator panel, so the exports agree everywhere except that subtree. The root pages render one
**reference scene** and mark every node that is not identical across all of them — in the hierarchy
tree, in the device table, in the Unity lists, and with a banner at the top of the group page.
The mark is computed by comparing all scenes on content (name, components, every entry), never on
scene path: the two panels sit at the same path and are different devices, so a path-only comparison
would call them identical and the mark would never appear. **Unmarked is the machine; marked is one
vendor's example.**

**Every section is the twin's truth, and that is the point.** A root group page states what the
group *is*; what it *becomes* in a control platform has one answer per platform and belongs to that
platform's own knowledge base. The last section is the only thing that crosses the boundary, and it
carries links, never facts.

Nothing in a group page is authored directly — sections 3, 4 and 6 render authored ContextNode
values, and the rest are derived.

**The control-implementations section is declared, never discovered, and always absolute.** A vendor module is a separate
repository cloned into this root and gitignored here, so what is on disk varies per user while what
*exists* does not. These pages are tracked: building the section from the filesystem would make a
tracked file's content depend on which optional modules someone happened to clone, and a user with
one module would delete the other's links and commit that. So the rows come from
`_workflow/config/modules.json`, and each link is an absolute URL into the module's own repository —
`../Beckhoff/…` is dead for anyone who did not clone it, and dead on GitHub outright.

**The handoff crosses as a copy.** `.machine.json` is written here and copied byte-for-byte into
each consuming module's `_workflow/config/handoff/` by `sync_machine.py`, where it is committed. The schema
is unchanged in transit and no keys are added, so a consumer's schema check needs no special case
and staleness is a plain sha256 compare. A consumer reads **its own copy** — never a path across
`../` into a repository that may not be there.

**No control-platform fact may appear here**, in any section. Function blocks, process-image members,
terminal channels, `.plcproj` registration and HMI structs are a vendor module's. The root generator
does not import a vendor tool and cannot verify such a fact, so one written here has nothing keeping
it true. The vendor page sections are specified in that module's own README — for TwinCAT,
`Beckhoff/_workflow/README.md`, in that module's own private half.

**The twin FB type is not a control fact.** It comes from the scene's `_Project_Tree.xml`, which OC
Assistant writes into the Unity project, so it is part of the twin's own export. What the *control*
PLC makes of that device is resolved against a real type model, on the vendor page.

## The device type page

One per OC device type, under `context/devices/`, generated. **It is documentation of the component
first and an index second.**

```
# Cylinder

<Summary>                    from _docs/devices/<type>.md
Twin device type · twin FB `FB_Cylinder` · 35 instances in … · Unity component `OC.Components.Cylinder`

<the hand-written block: what it is, what the PLC sees, how the twin models it, what to watch out for>

## In this machine           prose every instance shares verbatim, the shared bit mapping,
                             then where the instances are
## Control implementations   a link per vendor module
```

**What a device type *is* cannot be derived from the export.** The export carries a type's *name*
and nothing else — that a `Cylinder` has two control bits, that both end-position bits are false
while it travels, that an end-position bit is not proof of a grip, are properties of the Unity
component. So they are hand-written once per type in **`_docs/devices/<type>.md`** — one file per
type, curated exactly like `ImageDescription.md` — and rendered here.
**`_docs/DeviceDescription-SPEC.md`** is the contract those files implement; it describes the
format and describes no device.

**The build refuses to write when a type in the scene has no file there.** A new device type is a
device somebody has to describe; a page rendered with the description silently missing would not be
noticed until a reader needed it. A file for a type with no addressable instance — `Lamp`, which
exists only as bits inside a panel — still gets a page, because a bit-mapping table names it and a
reader has to be able to click through.

Prose identical across every instance is hoisted to `## In this machine` and **not** repeated per
row. An instance gets prose of its own only through a `Role`, or a `Signal` that differs from its
siblings'. There is no per-instance file.

**The twin device type does not determine the control FB**, which is exactly why that mapping is not
on this page. `Cylinder` is `FB_DoubleSolenoidFeedback` 24 times and `FB_SingleSolenoidFeedback` 11
times; `SensorBinary` and `SignalBinary` are two twin types over one `FB_DigitalSensor`. Neither
export states this — it is resolved through a control platform's type model, and it is stated on
that platform's page for this type, where it can be verified.

## Control function block contracts

A control FB's contract is behaviour, so it lives in `reference/`, not here — and **not in a file per
FB**. `FB_TransferIndex`, `FB_TransferLift` and `FB_TransferStopper` are all FG_Transport's, and
their contract is one system: the derived interface, the shared transfer latch, one reset model.
Splitting it into three pages would separate rules that only make sense together.
[`transport-behaviour.md`](../_docs/reference/transport-behaviour.md) is that page.

## PLC comment policy

The `.md` backbone carries the explanation; the ST carries what a reader needs at the cursor.

**POU header — 5 lines maximum:**

```
// FG_02 - optical inspection. Camera handshake, no moving parts.
// Triggered by Index02; reports OperationDone. NOK aborts (fault 1).
// Twin side: FB_Camera in SIM_1 - bit layouts must agree.
// Contract: _docs/reference/fg-02-behaviour.md
```

Name, what it does, its interface partner, one non-obvious constraint — and **one pointer line to
the contract**. That last line is the single cross-reference this policy keeps, and it is deliberate:
the point of moving the explanation out of the ST is that the `.md` becomes the place to read it, and
a POU with no way back to it is a dead end for the workflow this whole layout exists to serve. One
line, at the end of the header, never repeated inside a method.

**Inside a method:** one line per `CASE` step, stating what the step does and what makes it move on.

```
10: // Enable, wait for Ready. Timeout -> fault 2.
20: // Trigger. Busy OR ResultValid acknowledges.
```

**Delete on sight:** history ("which is why the old sequence was..."), rationale paragraphs,
cross-references to reference docs, restatements of what the next line says, and any comment longer
than the code it describes.

**Keep regardless of length:** a comment that records a constraint the code cannot express — a
required call order, a bit layout that must match the twin, a framework rule the compiler does not
check. These are the reason the file is not self-evident, and cutting them is how the bug comes back.

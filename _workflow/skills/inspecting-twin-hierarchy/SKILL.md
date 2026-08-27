---
name: inspecting-twin-hierarchy
description: Use when you need to find or understand a part of the Open Commissioning digital twin scene from the terminal - locating a functional group, station, or PLC device, resolving its PLC path, or checking which parts of the machine already carry context.
---

# Inspecting the twin hierarchy

## Overview

The machine is the `Machine_1` prefab: thousands of GameObjects, almost all CAD mesh noise, of which ~180 mean anything. Each vendor scene instances that prefab and adds only its own operator panel.
**Never read the scene YAML to answer a structural question** — it is ~195,000 lines, and prefab
instances are not expanded in it, so the real hierarchy is not even visible there.

Query the **live Unity Editor** instead: a round-trip costs about a second and returns the semantic
machine structure with PLC paths already resolved.

## Try the knowledge base first

`_docs/context/` already answers most structural questions — the group index in `machine.md`,
every real PLC symbol with its path and type in `plc-symbols.md`, and each group's devices in
`fg-XX.md` — with no Editor and no round-trip. Check `PROVENANCE.md` for how fresh it is.

Use the live Editor for what the digest cannot give you: anything below device level, anything about
components or transforms, and anything you need to be certain reflects the scene *right now*.

## Otherwise gate on a live Editor

```bash
unity status --format json     # need an instance with state "ready"
```

No ready Editor and no answer in the digest means no inspection. Ask the user to open the project —
do not fall back to grepping `.unity` or `.prefab` files, and do not guess.

## The four tiers

Every query classifies targets into tiers. Learn this vocabulary; the commands use it.

| Tier | What | How it is identified | Count in Demo_1 |
|---|---|---|---|
| `machine` | Export root | the root GameObject you walk from, `Project` by default | 1 |
| `group` | Functional group | direct child of the root | 7 |
| `assembly` | Station / sub-assembly | not a device, but has at least one device below it | 31 |
| `device` | Controller-linked device | recognised as a device by the installed integration | 93 |

Anything else — CAD geometry, `Interaction` colliders, `Axis` kinematics — is **not** a context
target and will not appear in any listing. Note that `Axis` is *not* a device; it is kinematics
animated by its parent actuator.

**Device-ness comes from an installed integration**, not from the package itself. Here that is
`com.open-commissioning.core`, whose provider treats any `IDevice` as a device. With no
`IContextMetadataProvider` present there would be no devices at all, so `assembly` would collapse too
and you would be left with `machine` and `group`. If a scene you expect to be full of devices reports
none, that is the first thing to check.

## Three axes, not one

Every target reports several independent things. Do not read one for another.

| Field | What it is |
|---|---|
| `tier` / `tierName` | Documentation granularity: `machine`, `group`, `assembly`, `device` |
| `scenePath` | Where the object sits in the Unity hierarchy |
| `topologyPath` | Where it sits in the authored `ContextNode` tree — un-annotated levels are absent, so this is shorter than `scenePath` and empty for a target with no node |
| `entryCount` / `entryKeys` | **Authored** entries only. This is coverage |
| `derivedCount` | How many entries a sync wrote under a framework's namespace |

In `Demo_1` every one of the 132 targets carries a node, so `topologyPath` currently equals
`scenePath` on all of them. That is a property of this scene being fully provisioned, not a rule —
the moment an un-annotated level appears between two nodes, the two paths diverge.

A node keeps one dictionary holding both kinds of entry. `context_get` returns all of it as
`entries`; a key with no prefix is a human's, a prefixed key belongs to an installed integration and
was written by `context_sync`. **Never write a prefixed key** — `context_set` refuses them, because
the next sync would revert the edit.

The vocabulary is open: nothing in the package defines or interprets those keys, and an absent key
means the framework did not state that fact, not that it is false. Open Commissioning writes:

| Key | Value | Means | Count in Demo_1 |
|---|---|---|---|
| `oc.plcPath` | `MAIN.FG_01.P_Reader` | Position in the PLC symbol tree | 132 (every node) |
| `oc.hierarchyRole` | `group` | Opens a level in the PLC path, joined with `.` | 7 |
| | `sampler` | Opens **no** level; prefixes its children instead, joined with `_` | 13 |
| `oc.deviceType` | `SensorBinary` | The `IDevice` component's type. Present on devices only | 93 |
| `oc.aggregatedBy` | a panel name | A `PanelSampler` folded this device into its own single symbol | 10 |
| `oc.simulationDevice` | `true` | The device talks to no PLC and no sampler explains why | 3 |

So a tier-2 `assembly` may be either real PLC structure (`Index01`, a sampler) or pure Unity grouping
(`Laser Unit`, `Barcode Reader`). Check whether it carries an `oc.hierarchyRole` before treating it as
a PLC level — **18** of the structural targets carry no `Hierarchy` at all and are invisible to the
PLC.

A target is a real PLC symbol when it has an `oc.deviceType` and **neither** `oc.aggregatedBy` nor
`oc.simulationDevice` — every target resolves an `oc.plcPath`, including pure structure, so the path
alone proves nothing. That is **83 of the 180 nodes**, matching
the scene's `_Project_Tree.xml` exactly.

**A target with `derivedCount: 0` was never synced**, which is not the same as OC having nothing to
say about it. Run `context_sync --dry_run true` before concluding anything from an absence.

## Quick reference

```bash
# Overview: nested tree, structure only, 2 levels deep
unity command context_tree --scope structural --depth 2

# Every device as a flat list (name, both paths, components, coverage counts)
unity command context_tree --scope devices --flat --format json

# What still has no context?
unity command context_tree --scope missing --flat --format json

# One target in full, addressed three different ways — all equivalent
unity command context_get --target "Project/FG_01/Barcode Reader/P_Reader"
unity command context_get --target "MAIN.FG_01.P_Reader"
unity command context_get --target "P_Reader"

# Coverage numbers per tier
unity command context_audit --format json
```

`--target` accepts a **scenePath**, a **topologyPath**, the value of any **prefixed entry** that is
unique under the root (case-insensitive — this is how an OC path like `MAIN.FG_01.P_Reader` still
resolves, and it reads the node rather than OC, so it works even where OC is not installed), or a
**bare name** when it is unique. An ambiguous value or name returns an error listing a full path to
disambiguate — read it and retry with the path.

`--scope` takes `all | structural | devices | missing`, where `missing` means *no `ContextNode` at
all, or one with zero entries* — an empty node is not coverage. On `Demo_1` that scope is currently
empty.

## Naming conventions (DIN/EN 81346 style)

Names are load-bearing. The prefix tells you what a thing is before you read any component list.

| Prefix | Meaning | Typical OC component |
|---|---|---|
| `FG_` | Funktionsgruppe (functional group) | `Hierarchy` |
| `Y_` | Valve / pneumatic actuator | `Cylinder` |
| `B_` | Binary sensor | `SensorBinary` |
| `M_` | Motor / drive | `DriveSimple` |
| `P_` | Optical inspection device | `TagReader`, `DataReader` |
| `H_` | HMI / signalling | `PanelSampler`, `Lamp` |
| `SS_` | Safety switch | `Button` |
| `Axis_` | Kinematic joint (not a device) | `Axis` |

Some names carry trailing spaces (`H_Monitor 1 `). Match exactly.

## When the commands do not cover it

For structural questions with no dedicated command, run C# in the Editor:

```bash
unity command eval --code 'return UnityEngine.GameObject.Find("Project")
    .GetComponentsInChildren<OC.Communication.Hierarchy>(true).Length;'
```

Prefer the `context_*` commands — they already resolve paths and tiers. Reach for `eval` only for
one-off queries, and keep it read-only; use `authoring-context-nodes` to write.

## Common mistakes

- **Reading a `.unity` scene or `Machine_1.prefab` directly.** A scene only instances the prefab, and a prefab instance is not expanded in a scene, so
  you will not even see the real hierarchy. Query the Editor.
- **Assuming a short path.** `P_Reader` is at `Project/FG_01/Barcode Reader/P_Reader`, not
  `Project/FG_01/P_Reader`. Let `context_get` resolve the name for you.
- **Treating `Axis` or `Interaction` as devices.** They are not; only 12 OC types are `IDevice`.
- **Reading `oc.plcPath` as proof of a PLC symbol.** Every node has one. `oc.deviceType` without
  `oc.aggregatedBy` or `oc.simulationDevice` is the test.

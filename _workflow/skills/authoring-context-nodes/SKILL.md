---
name: authoring-context-nodes
description: Use when documenting what a part of the digital twin is or does - adding, updating, or reviewing ContextNode entries on a device, station, assembly, or functional group in the Unity scene.
---

# Authoring ContextNode entries

## Overview

A `ContextNode` holds free-form key/value prose describing what a part of the machine *is for*. The
annotated hierarchy exports as a JSON tree that feeds downstream engineering — PLC code generation
first. The value of an entry is the engineering judgement in it, so **the user is the source, not
you**. Your job is to gather every fact the project already encodes, then ask only for what it
cannot tell you.

## The rule that matters most

**Never invent the "why".** Component types, PLC paths and sequence logic are readable from the
project — read them. Process intent, operational constraints and the reason a station exists are
not — ask. A plausible-sounding invented `Function` entry is worse than no entry, because it will be
believed and then generated into PLC code.

## Before writing anything

```bash
unity status --format json     # need state "ready"
```

No live Editor means stop. Do not edit `.unity` or `.prefab` files by hand — a scene write behind the
Editor's back is silently overwritten when it saves.

## Process

1. **Confirm scope.** Which GameObject(s)? If the name is ambiguous, ask rather than guessing. Use
   `inspecting-twin-hierarchy` to locate targets.

2. **Read what exists.** `unity command context_get --target <t>` — returns tier, both paths,
   components and the current entries. Never write without reading first.

3. **Ground it in real code.** Read the behaviour scripts that drive the target before describing
   what it does. Project-specific sequence logic is where the surprises live; OC component types have
   standard semantics and do not need re-reading each time (see `reference.md`).

4. **Ask the user for the rest.** Open conversation, not multiple choice — process purpose, operating
   constraints, what a failure here means.

5. **Show the drafted entries and get agreement before writing.**

6. **Write**, then `unity command save_all`.

7. **Report** exactly which keys landed on which target, and whether they went to the scene or a
   prefab asset.

## Writing

```bash
# Single entry — preferred; no JSON quoting to get wrong
unity command context_set --target "Project/FG_01/Barcode Reader/P_Reader" \
  --key "Function" --value "Reads the tag on the incoming pallet to confirm identity."

# Several at once
unity command context_set --target "Project/FG_01" \
  --entries '[{"key":"Function","value":"..."},{"key":"Process","value":"..."}]'

unity command context_remove --target "P_Reader" --key "Obsolete"
```

`context_set` is an **upsert** — it goes through `ContextNode.Set()`, so keys you do not mention are
preserved. You do not need to read-merge-write by hand. It also creates the `ContextNode` if the
target lacks one.

**Prefixed keys are refused.** `oc.plcPath`, `oc.deviceType` and the rest belong to the Open
Commissioning integration and are written by `context_sync`. Any hand-written value there would be
reverted by the next sync, so the command fails loudly instead. Never restate one of those facts in
an authored entry either — it duplicates data that keeps itself correct, and your copy will drift.

## Prefabs: type context on the asset, role context on the instance

> **A prefab-asset entry only reaches instances that have NOT overridden the ContextNode.** If the
> instance already carries an authored key, its entry list is an override and the asset write will
> not reach it — the call still reports success. Verify with `context_get` on an instance after any
> `--prefab true` write, and fall back to per-instance writes when the key is missing.

Where a station repeats as prefab instances, split the description:

```bash
# Generic "what this kind of unit is" -> the asset, shared by every instance
unity command context_set --target "Project/FG_Transport/Index01" --prefab true \
  --key "Function" --value "Pallet index station. Stops an incoming pallet and lifts it clear..."

# Instance-specific "which station this is" -> the scene instance, as an override
unity command context_set --target "Project/FG_Transport/Index03" \
  --key "Role" --value "Feeds the downstream pick-and-place. Releases on OperationComplete."
```

Ask yourself: *would this sentence be true of every instance of this prefab?* Yes → `--prefab true`.
No → write it on the instance. **An asset-level value must never name one instance**: a sentence on
the `Stopper Unit` asset that cites `Stopper01_B_Detect` is wrong on the other three instances, and
nothing will flag it.

**Always write the prefab before the instance.** `_entries` is a `List<>`, so the first write to an
instance turns the whole list into a prefab override. Anything added to the asset afterwards is
shadowed and never appears on that instance — and saving the asset while an override exists can have
Unity reconcile the two lists by index, leaving a blank entry behind. If you have already written to
the instance, write the shared text onto the instance too rather than fighting the override.

After any prefab-side write, verify with `context_get` on a **different** instance than the one you
addressed, and re-run `context_audit`.

## Common mistakes

- **Writing prose that restates the component type.** "This is a cylinder" adds nothing — the
  exporter already emits the component list. Say what it *does in this machine*.
- **Restating synced metadata in an authored key.** If `oc.hierarchyRole` already says `sampler`, an
  authored entry explaining that it is a sampler is duplication that can go stale.
- **Authoring a device before its group.** A device's description only makes sense against the
  group's purpose. Work top-down: machine → group → assembly → device.
- **Duplicating type text across instances.** That is what `--prefab true` is for.
- **Skipping step 5.** Entries are engineering documentation; the user reviews before it lands.

See `reference.md` for the key vocabulary in use, OC component semantics, how `Hierarchy` shapes the
PLC path, this project's sequence scripts, and a worked example.

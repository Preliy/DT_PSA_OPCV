---
name: refreshing-project-knowledge
description: Use when the machine knowledge base in _docs/context/ needs rebuilding - after changing the Unity twin, after authoring context, before generating PLC code against a stale export, or when a skill reports the digest is out of date. Also covers exporting the machine context from the Unity Editor.
allowed-tools:
  - Bash
  - Read
---

# Refreshing the project knowledge base

## Overview

`_docs/context/` is the machine's memory: what every device is, what every group does, and
which PLC symbols are real. Every vendor module builds its own knowledge base on top of it, and
every downstream skill reads one of the two instead of opening Unity.

This skill owns the whole path from scene to digest, both halves, so no other skill has to:

```
each scene ─sync─> ContextNodes ─export─> <Scene>_Context.json ─build─> _docs/context/*.md
                                                                        + .machine.json
                                                                             │ sync_machine.py
                                                                             ▼
                                            Beckhoff/_workflow/config/handoff/.machine.json  (committed)
                                                                             │
                                            Beckhoff/_docs/context/*.md ─┘ ─scan TwinCAT_1/
```

**Two generators, and the order matters.** The root one knows the machine and no control platform;
a vendor one reads **its own committed copy** of `.machine.json` and its own projects. Run the root
build, sync the handoff, then each vendor build.

**There is no second root build.** The root pages link vendor pages by URL from
`_workflow/config/modules.json`, which is declared rather than discovered, so they no longer depend on a
vendor build having run — or on that module being cloned at all.

**A vendor module is a separate repository** cloned into this root and gitignored here. Its changes
never appear in this repo's `git status`.

**It works with Unity closed.** That is the point of the design — the committed export is the
handoff artifact, and the digest built from it is honest about not having been verified live.

Run everything from the repo root.

## The refresh

### 1. Is a live Editor reachable?

```bash
unity status --format json     # look for an instance with state "ready"
```

`STATUS_NO_INSTANCES` is not a failure. It decides which of the two paths below you take.

### 2a. With a ready Editor — re-export EVERY scene

**There is one scene per vendor, and each exports its own pair.** The machine is the
`Machine_1` prefab that all of them instance; a scene adds only its vendor's operator panel. The
build discovers the exports by glob and parses them all — so a scene you did not re-export is
simply invisible, and its differences go unmarked on the root pages.

```bash
unity command list_open_scenes --format json   # which scene is open right now
```

Repeat the sync-and-export below **once per scene**, opening each in turn:

```bash
unity command open_scene --path Assets/Demo_1/Scenes/VC_Demo_1_Beckhoff_1.unity
# ... sync, clear selection, export ...
unity command open_scene --path Assets/Demo_1/Scenes/VC_Demo_1_Siemens_1.unity
# ... sync, clear selection, export ...
```

```bash
unity command context_sync --dry_run true      # drift check; expect changed: 0
```

Non-empty drift means the scene changed and the metadata was never re-synced. Fix it before
exporting, or the digest describes a machine that has moved:

```bash
unity command context_sync --dry_run false
unity command save_all
```

Then export. **Clear the Editor selection first — this one bites.** An explicit selection *wins*
over the default root, so whatever a human last clicked in the Hierarchy silently becomes the export
root. A leftover selection on a single cylinder once produced a structurally valid **2-node** export
that reported no error anywhere.

```bash
unity command eval --code 'UnityEditor.Selection.objects = new UnityEngine.Object[0]; return "cleared";'
unity command menu --path "PILLAR/Context/Export Machine Context (JSON)"
unity command console --format json     # expect "exported machine context of 'Project'"
```

The console line naming the root is the fastest tell that the export is the whole machine.

Each export lands as `Unity/Assets/StreamingAssets/<Scene>_Context.json` plus its
`<Scene>_Project_Tree.xml`. Check the file timestamps afterwards: two scenes and only one fresh pair
means the second export never ran, and the build will happily render the stale one.
`build_knowledge.py` checks it too and refuses a wrong root, but do not make the script the only
thing paying attention.

Then probe the scene wiring, and build with the live flag that stamps the digest as trustworthy:

```bash
python _private/tools/probe_topology.py                    # scene wiring - needs the Editor
python _private/tools/build_knowledge.py --live-verified
python _private/tools/sync_machine.py                      # handoff -> each module's handoff/
python Beckhoff/_private/tools/plc_io.py build             # I/O map + .plc-image.json snapshot
python Beckhoff/_private/tools/build_plc_knowledge.py
python Beckhoff/_private/tools/hmi_check.py
python _workflow/tools/check_compatibility.py --write       # refresh the COMPATIBILITY.md table
```

Everything is written from the **main repo root**, vendor tools included — they anchor on their own
file, not on the working directory, so they also run from inside the module, but write them from the
root here. The Beckhoff steps read the TwinCAT solution, not Unity. `plc_io.py build` writes
`Beckhoff/_docs/context/.plc-image.json`, which the other two fall back to, so it goes first
among them.

**The probe is the only step that cannot be done offline.** The context export records which
component a node carries but not what that component's events are wired to, so the Index → group
coupling lives in the scene and nowhere else. `probe_topology.py` measures it through the same
read-only `get_serialized_fields` command and caches it to `_docs/context/.topology.json` —
which is what lets `machine.md` render a verified ring later with Unity closed.

Run it whenever the wiring may have changed: a new station, a re-pointed `_nextSequence`, a
re-targeted `ReadyForOperation`.

### 2b. With no Editor — build from the committed export

```bash
python _private/tools/build_knowledge.py
python _private/tools/sync_machine.py
python Beckhoff/_private/tools/plc_io.py build
python Beckhoff/_private/tools/build_plc_knowledge.py
python Beckhoff/_private/tools/hmi_check.py
python _workflow/tools/check_compatibility.py --write
```

With TwinCAT closed too, skip `plc_io.py build`: the rest render from the committed snapshot and
banner themselves as behind.

Identical output, minus the live-verified stamp. `PROVENANCE.md` will say the digest was not
verified against a live scene. **Say the same in your report** — it is a real limitation, not a
formality: nothing proves the scene has not changed since the export timestamp.

`probe_topology.py` needs only **one** scene open: FG_Transport lives in the shared `Machine_1`
prefab, so the wiring is the same in every scene and one probe serves them all. It takes its unit
list from the open scene's export and records which scene it measured.

The topology comes from the cached `.topology.json`, and `machine.md` reports the date it was
measured. With no cache at all, that page still carries both protocol contracts — they come from
committed C# — and marks the topology `not probed`. It never falls back to guessing the Index →
group pairing from the numbering.

Never pass `--live-verified` without having actually re-exported from a ready Editor in this
session. The flag is a claim about provenance, and a false one poisons every decision downstream.

## When the build refuses

`build_knowledge.py` writes nothing rather than emit a half-digest. Each refusal names a real
failure that is invisible in the export itself:

| Refusal | What actually happened | Fix |
|---|---|---|
| export root is not `Project` | An Editor selection leaked into the export | Clear the selection, re-export |
| no scene exports found | `StreamingAssets/` has no `<Scene>_Context.json` | Export from Unity; the old single `Demo_1_Context.json` name is gone |
| `<Scene>_Context.json` has no `_Project_Tree.xml` beside it | Only half the export ran | Re-run the OC Assistant device-tree export for that scene |
| no exported scene for reference vendor | The reference scene has never been exported | Export it, or build with `--reference <OtherVendor>` |
| transport chain does not close | Following `_nextSequence` from a station never returns to it — pallets would pile up somewhere | Fix the wiring in the scene, re-probe |
| station is fed by more than one station | Two units point `_nextSequence` at the same successor | Fix the wiring, re-probe |
| triggers a group that reports completion to nobody | An Index raises `ReadyForOperation` at a group whose `OperationComplete` is unwired — that station would start the group and wait forever | Wire the return half in the scene, re-probe |
| symbol count mismatch | A scene's `_Context.json` and its `_Project_Tree.xml` disagree — the twin and the OC project tree have drifted | Re-export both from the Editor; the message names the scene and the devices on each side |
| max depth at the truncation window | `JsonUtility` silently drops data past ~7–10 levels; this scene sits at 7 | The hierarchy grew too deep — flatten it, or the export is lossy |
| malformed authored entries | Prefab override reconciliation left a blank key or value, which still counts as coverage | Fix the entries with `authoring-context-nodes` |
| too few nodes | The export is truncated | Re-export and check the console |

`Beckhoff/_private/tools/plc_io.py` refuses on the TwinCAT half for the same reason:

| Refusal | What actually happened | Fix |
|---|---|---|
| snapshot **behind the sources** | A PLC source declares something `.plc-image.json` predates. Comments are ignored by this check, so it is a real structural change | Rebuild `PLC_1` in XAE, then `python Beckhoff/_private/tools/plc_io.py build` |
| `PLC_1.tmc` is stale | Only `plc_io.py build` can raise this, because nothing else reads the `.tmc` | Rebuild `PLC_1` in XAE and re-run it |
| links are in `Mapping_PLC.xml` but not in the tsproj | The link file was edited and never imported on the Mappings node — the links exist on disk and nowhere in the running configuration | Import it in XAE (clear the node first; the import is additive) |
| channel booked twice | Two symbols point at one terminal channel | Re-allocate with `plc_io.py propose` |
| terminal has no such channel | A link names `Channel 9` on an 8-channel card | Fix the allocation |
| direction mismatch | An input symbol is linked to an `Output` entry, or the reverse | Fix the allocation |

**Do not work around a refusal.** Every one of them means a downstream skill would otherwise
generate code for a machine that does not exist, or the machine would run with a signal that is
silently dead.

## What gets written

| File | Built from | Holds |
|---|---|---|
| `PROVENANCE.md` | the export header + git | Export timestamp, commit, node/symbol counts, live-verified or not, and every node with no authored context |
| `machine.md` | root node | Purpose, process flow, layout, the group index |
| `plc-symbols.md` | both exports | Every real PLC symbol with its path, device type and `FB_*` type |
| `fg-*.md` | both exports | **One page per group**: header, figure, one device table, bit mapping, hierarchy, Unity, and a link to each vendor's page |
| `devices/*.md` | both exports + `_docs/devices/<type>.md` | One per twin device type: the hand-written description of the component, then what this machine does with it and where its instances are |
| `.machine.json` | every scene | The vendor handoff — the reference scene under `groups`, **every** scene under `vendors`, schema-versioned |

And in each vendor module, e.g. `Beckhoff/_docs/context/`:

| File | Built from | Holds |
|---|---|---|
| `PROVENANCE.md` | the type model + `.machine.json` | How current the control side is, and which build of the twin export it was matched against |
| `machine.md` | the type model | The groups as that platform sees them |
| `fg-*.md` | `.machine.json` + the projects | Verified control PLC paths, the `SIM_1` POU, the `PLC_1` module, the terminal mapping |
| `devices/*.md` | the type model | Which control FB each twin type becomes, its process-image members and channel widths |
| `plc-io.md` | tsproj + `Mapping_PLC.xml` | Terminals and channels, the allocation per terminal, free channels, and the reconciliation identity |

Stale per-group pages are deleted on every run, so a renamed group cannot linger as a ghost file.
**Each generator sweeps only its own directory** — that is why the two knowledge bases must never
share one.

## The rule that keeps this honest

**Every `context/` directory is generated. Never hand-edit one.** The next refresh erases the edit
without warning, on either side of the vendor boundary.

A fact that belongs in the knowledge base belongs in a `ContextNode` in the scene. Author it with
`authoring-context-nodes` — where the user is the source — and it survives every refresh, reaches
the PLC code, and stays with the twin. Editing the digest instead puts the fact in the one place
guaranteed to lose it.

## Report

Say which path you took (live or committed), **which scenes you re-exported**, whether any node
newly started or stopped carrying `†`, what the assertions reported, and what changed. Call out any
new group that appeared, any symbol count change, and any node that lost its context.

**Diff two repositories, not one.** A vendor module is a separate repo cloned into this root and
gitignored here, so nothing you changed inside it shows up in the main repo's diff:

```bash
git diff --stat _docs/context/          # the twin half
git -C Beckhoff diff --stat                 # the vendor half - INCLUDING _workflow/config/handoff/
```

Reporting only the first is the easiest way to lose this work: the handoff snapshot and the whole
vendor knowledge base would look untouched, and the module's commit would never be made.

## Common mistakes

- **Exporting without syncing.** The export dumps what the nodes hold and queries no framework
  itself. An unsynced scene exports no `oc.*` metadata at all and looks complete while doing it.
- **Exporting with a selection active.** Covered above; it is the single most expensive mistake here.
- **Passing `--live-verified` from habit.** It is a provenance claim. Earn it or omit it.
- **Editing a `context/` page to "fix" a fact.** Fix the scene, or the PLC.
- **Syncing the handoff and not committing it in the module.** `sync_machine.py` writes into another
  repository; this one cannot commit for you, and its `git status` says nothing about it. An
  unsynced-and-uncommitted snapshot is the one way the vendor pages go quietly stale.
- **Assuming a missing vendor build is a failure.** A module is optional and separately cloned. If
  `Beckhoff/` is not there, `sync_machine.py` skips it and the root pages are unchanged — that is
  correct, not a fault. `build_wiki.py` produces byte-identical output either way; all it loses is
  the ability to *verify* its cross-repo links, and it says which ones.
- **Rebuilding the root wiki and expecting the module's pages to change.** There is one wiki per
  repository. A refreshed vendor knowledge base reaches its wiki through that module's own
  `build_wiki.py`, never through the root's.
- **Running only the root build after a PLC change.** The vendor pages are a separate generator; a
  root-only refresh leaves them exactly as stale as they were.
- **Treating a refusal as a script bug.** The script is the only thing checking. Read what it said.

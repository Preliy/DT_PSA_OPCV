# Engineering workflow

Where the machine description comes from, and how it reaches PLC code.

The short version: **the machine documents itself.** What a part of the twin *is* and what it is
*for* is written onto the part, in the Unity scene, once. Everything downstream — these pages, the
vendor handoff, the symbols a PLC generator emits — is derived from that. Nothing is transcribed by
hand into a second place, because a second place is a place that goes stale.

> This page is about the **method**. [03 · How it works](03-how-it-works.md) is about the running
> system.

## 1. The context node

Every part of the twin can carry a **`ContextNode`** — a list of key/value entries on the
GameObject, provided by [`com.pilar.context`](https://github.com/Preliy/unity-pilar-context). It
holds two kinds of fact, and the difference between them is the whole design:

| | Keys | Written by | Example |
|---|---|---|---|
| **Synced** | `oc.*` — `oc.plcPath`, `oc.deviceType`, `oc.hierarchyRole`, `oc.aggregatedBy`, … | OC Assistant, from the scene itself | `oc.deviceType: Cylinder` |
| **Authored** | nine keys, no others — see below | A human who knows the machine | `Function`: *"Stops an incoming pallet and lifts it clear of the belt so the group can work on it."* |

The authored vocabulary is closed, and the build fails on an unknown key or an over-length value — a
cap that is not enforced is a cap that drifts:

| Key | Where | Answers |
|---|---|---|
| `Function` | any node | What this is and what it does |
| `Role` | instance override | Which instance this is, in this machine |
| `Signal` | device | I/O semantics and sense, where not obvious from the type |
| `BitLayout` | byte-interface devices | Which control or status bit carries what |
| `Twin` | any node | **How Unity realises it** — which components, wired to what |
| `Approximation` | any node | **Where the model differs from real hardware**, or is abstract |
| `Caution` | any node | **The trap** — what will bite someone writing PLC code against it |
| `ProcessFlow` | the machine root | The path a pallet takes through the machine |
| `Layout` | the machine root | The physical arrangement of the cell |

Three of those describe the **model** rather than the machine: `Twin`, `Approximation` and `Caution`
are knowledge only the twin holds — the PLC cannot state them, and they are not behaviour, so
`reference/` is the wrong home for them. *This component releases on any movement* is a twin fact
with real consequences for PLC code, and it belongs on the node it is true of.

**A synced key is read out of the project; an authored key cannot be.** A component type, a PLC path
and a hierarchy role are all facts the scene already contains, so they are synced and any hand-typed
copy of one is refused — it would be reverted by the next sync anyway. Why a station exists, what a
failure there means, what the process actually needs: none of that is anywhere in the project, and
none of it can be inferred from a hierarchy.

Hence the rule that governs everything on this page:

> **Never invent the "why".** A plausible-sounding invented `Function` entry is worse than no entry,
> because it will be believed — and then generated into PLC code.

### Type context and role context

Where a station repeats as prefab instances, the description splits the way the prefab does:
*"what this kind of unit is"* goes on the **prefab asset**, shared by every instance; *"which station
this one is"* goes on the **instance**. The test is one question — would this sentence be true of
every instance? An asset-level sentence that names one instance is wrong on all the others, and
nothing will flag it.

## 2. The loop

```
  ┌─ the Unity twin ─────────────────────────────────────────────────────────┐
  │                                                                          │
  │   find the part          resolve a group, station or device and its path │
  │   author the context     write the "why" onto it -> ContextNode entries  │
  │   audit the coverage     no empty nodes, no malformed entries            │
  └────────────────────────────────────┬─────────────────────────────────────┘
                                       │  sync, then export every scene
                                       ▼
                    Unity/Assets/StreamingAssets/
                    <Scene>_Context.json      the annotated hierarchy
                    <Scene>_Project_Tree.xml  the device list
                                       │  build
                                       ▼
                    ═══════════ _docs/context/ ═══════════   the knowledge base
                    PROVENANCE · machine · plc-symbols
                    fg-*.md      one page per functional group
                    devices/     one page per device type
                    .machine.json    the handoff, structure as JSON
                    † marks anything that differs between scenes
                                       │  copied into each module
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
              Beckhoff/_docs/context/          your module
              + PLC code generation,           + your control program
                I/O mapping, HMI
```

The left half needs Unity open. **The right half does not** — that is the entire point of the
knowledge base. The twin can be closed, on another machine, or mid-refactor, and PLC work continues
against the last good export, with `PROVENANCE.md` saying exactly how old it is.

## 3. What is generated and what is not

| | Where | Who writes it |
|---|---|---|
| The machine description | [`_docs/context/`](context/) | **generated** from the twin, wholesale |
| The device type prose | [`_docs/devices/`](devices/) | hand-written — it is an *input*, rendered into `context/devices/` |
| The figures' captions and callouts | [`ImageDescription.md`](ImageDescription.md) | hand-written — also an input |
| The behaviour contracts | [`reference/`](reference/) | hand-written, and never generated |
| These narrative pages | `_docs/*.md` | hand-written |

**Never hand-edit anything under `context/`.** Each generator sweeps its own output directory and
deletes what it did not write, so an edit there is erased without warning and without a diff. A fact
worth keeping belongs in a `ContextNode` in the scene, where it survives the refresh *and* reaches
the PLC code. If a generated page is wrong, the twin is wrong.

Three things are checked while the pages are built, and each one is a refusal rather than a warning:

- **Every figure callout is resolved against the export.** `ImageDescription.md` numbers the callouts
  on each screenshot; a name that no longer exists, or that resolves to two nodes, stops the build.
  A picture cannot quietly outlive the device it points at.
- **Every device type in the twin must have a hand-written page.** A new kind of device that nobody
  has described stops the build rather than shipping an empty section.
- **Every scene is compared against the reference scene.** A node that is not identical everywhere is
  marked `†` — "this is one vendor's example, not the machine". The mark is computed, so it cannot
  drift away from the fact it qualifies.

## 4. Two generators, one direction

The knowledge base is built in two passes, and the split is deliberate:

| | Reads | Writes |
|---|---|---|
| **The root generator** | the Unity export | `_docs/context/` and `.machine.json` |
| **A vendor generator** | `.machine.json` **only**, plus its own PLC project | that module's `_docs/context/` |

The root generator knows about the machine and **no control platform** — it does not import a vendor
tool and has no idea what a `.tmc` file is. A vendor generator knows its own platform and reaches the
twin exclusively through the handoff. Two parsers over one Unity export is precisely how a twin and
a control project come to disagree, so there is only ever one.

`.machine.json` is **schema-versioned**. Adding a field is free; moving or removing one bumps the
schema, and a vendor generator that does not recognise the schema **refuses** rather than rendering
fields it guessed at.

The handoff crosses as a **copy**: it is written into each module's
`_workflow/config/handoff/` and committed there. That is what lets a module build from a
standalone clone with no main repository and no Unity anywhere.

## 5. From context to PLC code

This is the payoff, and the reason authored context is held to the standard it is.

A vendor generator turns the handoff into that platform's own knowledge base: one page per
functional group, one per device type, and the platform's **verified** control paths — the twin says
`MAIN.FG_01.P_Camera`, TwinCAT says `MAIN.Machine.FG_01.P_Camera`, and the difference fails silently
in a link and in an HMI binding, so it is checked against a real type model rather than assumed.

From there, code generation has everything it needs without anybody retyping a device list:

| It needs | It gets |
|---|---|
| Which devices exist in a group, and their types | the handoff |
| What each device is *for* | the authored context, carried through |
| What the group must **do** | the [behaviour contracts](reference/transport-behaviour.md) — hand-written, machine-level, and not derivable from the twin |
| How this platform spells all of it | that module's own knowledge base |

Note what is **not** in that list: the twin's own MIL animation scripts. They implement an older
contract, and a handshake copied from them reproduces bugs that are already fixed. The control
program is master for behaviour; the twin is master for structure. Neither reads the other's mind.

**Do not generate against a stale export.** `PROVENANCE.md` states the export's commit, whether the
working tree was dirty, and how many devices it found. If that commit predates the last change to
the Unity scene, refresh first — symbols for devices that moved or no longer exist compile
perfectly.

## 6. The tooling, and what you can run

The line is **what a tool reads**, not what language it is written in.

| | Where | You can run it |
|---|---|---|
| The wiki builder and publisher | [`_workflow/tools/`](../_workflow/tools/) | **yes** — they read only tracked files |
| The compatibility check | [`_workflow/tools/`](../_workflow/tools/) | **yes** |
| The generators that read the Unity export | a separate repository, cloned in as `_private/` and gitignored | maintainers only |

That is why some pages under [`_workflow/`](../_workflow/) name commands you cannot run: they are
addressed to whoever builds the project, and they say where the tools come from. **The pages you are
expected to use — these, the README, CONTRIBUTING — never do.** Everything they ask of you works
with this repository alone, and the generated pages are committed, so you never need to build the
machine description in order to read it.

The method itself is published even where the tool is not, so it can be read and argued with:

| | |
|---|---|
| [`_workflow/README.md`](../_workflow/README.md) | The loop in full: what runs when, and every gate that stops it |
| [`_workflow/CONTEXT-SPEC.md`](../_workflow/CONTEXT-SPEC.md) | The contract the generated pages implement — the authored key vocabulary, the sections, what may never go in |
| [`_docs/DeviceDescription-SPEC.md`](DeviceDescription-SPEC.md) | The contract a hand-written device page implements |
| [`_workflow/WIKI-SPEC.md`](../_workflow/WIKI-SPEC.md) | How each repository's wiki is named, linked and published |
| [`_workflow/skills/`](../_workflow/skills/) | The step-by-step procedures, including their refusals |

## 7. If you want to change something

| The problem | Do this |
|---|---|
| A device is missing, misnamed or in the wrong group | Fix the Unity scene and open a PR against `Unity/` |
| A description of what a station is *for* is wrong or absent | Open an issue saying what it should say — that text is authored in the scene, not in the page |
| A **behaviour** contract is wrong | Edit [`reference/`](reference/) directly and open a PR. Those pages are hand-written |
| A page under `context/` is wrong | Fix the twin. Editing the page cannot work — the next build overwrites it |
| A figure points at the wrong thing | Edit [`ImageDescription.md`](ImageDescription.md), never the generated page |

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the rest.

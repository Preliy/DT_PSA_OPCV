# DT_PSA_OPCV — Digital Twin for Laser Welding & Assembly System (PSA OPCV)

A Unity-based digital twin built for **virtual commissioning**. The twin runs on **Open Commissioning
Core** and the **Open Commissioning UI framework**; **TwinCAT** is the simulation unit — it hosts the
behaviour models and emulates the real-time industrial fieldbus, so the twin and a control program
meet over EtherCAT exactly as a real cell does.

One Unity digital twin of the machinery, and one **vendor module per control platform** that
realises it.

**Authority is split three ways, and the splits are the thing to get right.**

- The **Unity twin** is master for **structure** — which devices exist, their twin PLC paths, device
  types and I/O. It states that once, here, in `_docs/context/`.
- The **control PLC** is master for **behaviour** — sequences, the station handshake, interlocks,
  fault codes and recovery. Behaviour is a machine-level contract every platform must honour, so it
  is written down once in `_docs/reference/`, not in a vendor module.
- A **vendor module** is master for its own **realisation** — its function blocks, its terminal
  channels, its HMI. That lives in the module, never here.

```
   Machine_1.prefab ── instanced by ──> VC_Demo_1_Beckhoff_1.unity
   (the whole machine)                  VC_Demo_1_Siemens_1.unity
                                        each adds its vendor's control panel
                                               │
                                     one context export per scene
                                               ▼
                                      _docs/context/            THE MEMORY
                                      structure + behaviour
                                               │ .machine.json
                    ┌──────────────────────────┴──────────────────┐
                    ▼                                             ▼
              Beckhoff/ TwinCAT_1                          Siemens/ TIA_1
              PLC_1  control, port 851                     work in progress
                    │ EtherCAT
               real master ⇄ EtherCAT_1_SIM
                    │
   Unity ── ADS ── SIM_1  twin devices, port 852

   Beckhoff/TwinCAT_1/HMI (TE2000) ──ADS──> PLC_1 as runtime PLC1 (bound by PORT 851, not by name)
```

| Module | Path | Role |
|---|---|---|
| Unity twin | `Unity/` | Digital twin of the machinery, on Open Commissioning + `com.pilar.context` |
| **Beckhoff** | `Beckhoff/` | TwinCAT 3: `TwinCAT_1/PLC/PLC_1` (control), `SIM_1` (twin devices), `TwinCAT_1/HMI` (TE2000). **Active.** |
| **Siemens** | `Siemens/` | TIA port — **work in progress**. Has its own Unity scene and export; no PLC knowledge base yet |

**Each vendor module is a separate repository**, cloned into this root and **gitignored here** so
the two git repos do not collide. `_workflow/config/modules.json` declares which exist; `COMPATIBILITY.md`
says which versions pair. A module is optional — most checkouts have one, some have none — and both
of those are normal.

Each is self-contained: its own `_docs/`, its own gitignored `_private/`, and its own `module.json`.
Nothing here may depend on a vendor module, and a vendor module reaches this repo through exactly
one generated file, `_docs/context/.machine.json` — **copied** into
`<Module>/_workflow/config/handoff/` by `_private/tools/sync_machine.py` and committed there, so the
module builds from a standalone clone with no main repo present.

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff   # optional
git clone <the tooling repo> _private          # maintainers only - the generators
```

## One machine, one prefab, one scene per vendor

The machine is a **prefab** — `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab` — and every scene under
`Unity/Assets/Demo_1/Scenes/` instances it. What a scene adds is its vendor's operator panel:

| Scene | Adds |
|---|---|
| `VC_Demo_1_Beckhoff_1.unity` | `H_ControlPanel` → `MAIN.FG_System.H_ControlPanel`, 8 PackML buttons |
| `VC_Demo_1_Siemens_1.unity` | `H_ControlPanel` → `MAIN.FG_System.H_ControlPanel_Siemens`, 7 controls incl. a `SwitchRotary` |

Each scene exports its **own** pair into `Unity/Assets/StreamingAssets/`:
`<Scene>_Context.json` and `<Scene>_Project_Tree.xml`. Both are discovered by glob — adding a vendor
scene and exporting it is the whole of adding a vendor, with no file to edit.

**The root pages are rendered from one reference scene, currently Beckhoff.** That is a deliberate
compromise: showing only what every scene agrees on would leave `FG_System` with no operator panel
at all, and a machine with no panel is a worse picture than a panel labelled as an example. So the
reference scene's panel is shown and **every node that differs between scenes is marked `†`** — in
the hierarchy tree, in the device table, in `plc-symbols.md`, on the device-type page, and with
a banner at the top of the group page. The mark is generated from a comparison of all scenes, so it
cannot drift away from the fact it qualifies.

**Read `†` as "this is one vendor's example".** What is unmarked is the machine. Change the
reference with `--reference <Vendor>`.

## Scope

| Path | Status |
|---|---|
| `Unity/` | **Active** — the twin itself: the prefab, the scenes, the scripts, the exports |
| `_docs/` | **Active** — everything published. `01-`…`04-*.md` and `images/` are hand-written narrative; `context/` is generated; `reference/` is the hand-written behaviour contracts; `config/` holds `modules.json` |
| `_workflow/` | **Active and published** — how the project is built: `CLAUDE.md`, `README.md` (the skill chain), `CONTEXT-SPEC.md`, `WIKI-SPEC.md`, `skills/`, `settings.json`, `config/modules.json`, and `tools/` — the **wiki tooling** and the **compatibility check**, public because GitHub Actions has to run both |
| `package.json`, `CHANGELOG.md`, `.releaserc.json` | **Release machinery, tracked.** `package.json` is not a Node package — private, no dependencies, never published. It is where semantic-release writes the version, and the only thing a module's `requiresMain` can be checked against. Both it and `CHANGELOG.md` are owned by the release bot: **never hand-edit either** |
| `_private/` | **Gitignored — its own repository. The generators that read the Unity export, and nothing else** |
| `_wiki/` | **Generated and gitignored** — a build artifact, not a tracked copy. **This repository's `_docs/` only**; a module builds its own. `build_wiki.py` writes it, `publish_wiki.py` pushes it. Never hand-edit, never commit |
| `Beckhoff/` | **Active** — a separate repository cloned in here. Read `Beckhoff/CLAUDE.md` before touching anything in it |
| `Siemens/` | A separate repository. Its Unity scene and export live in **this** repo and are read by the root build; the module itself holds no `_private/` yet. `Siemens/TIA_1/` is a **parked TwinCAT template, not the TIA program** — ignore that folder |
| `*/_data/` | Third-party sources, in every module — **read only on explicit permission from the user** |
| `_archive/` | Hard archive — **ignore entirely** |

## Two conventions that everything depends on

**Run every command from this repo root.** Every tool anchors on its own file rather than on your
working directory, so a vendor module's tools work from either level — but write them main-repo
relative (`python Beckhoff/_private/tools/plc_io.py …`), because that is the level everything else
here is written from. The two tools that cross the module boundary — `build_knowledge.py` and
`sync_machine.py` — **must** run from here. The `unity` CLI is a global binary and connects to
running Editor instances, so it works from here too; there is never a reason to `cd Unity/`.

**Three directories are generated and swept: `_docs/context/`, every vendor's
`_docs/context/`, and `_wiki/`.** Each generator deletes anything in its own output directory it
did not write. The rest of `_docs/` is hand-written — the narrative pages, the figure source and the
behaviour contracts — and holds no machine facts, because the machine description is generated.

**Every `_docs/context/` is generated. Never hand-edit one.** The root one is derived from the
Unity export by `_private/tools/build_knowledge.py`; a vendor's is derived from `.machine.json` plus
that vendor's project by its own builder. A fact that belongs in the knowledge base belongs in a
`ContextNode` in the scene — author it there with `authoring-context-nodes` so it survives the next
refresh. An edit made directly in a `context/` directory is erased without warning.

## Public and private

**This repository is the public one. Everything tracked here is published as-is.** There is no
filtering step at publish time and no override tree — the boundary is a directory, and it falls in
one place only:

| | Where | Git |
|---|---|---|
| What the machine is | `_docs/` | tracked, published |
| How the project is built | `_workflow/` | tracked, published |
| The **wiki** tooling and the **compatibility** tooling | `_workflow/tools/` | tracked, published |
| The generators that read the **Unity export** | `_private/` | its own repository, cloned in, gitignored here |

**The line is what a tool READS, not the fact that it is Python.** A tool that reads only tracked
files belongs in `_workflow/tools/`; a tool that reads the Unity export, probes a live Editor or
digests a vendor project belongs in `_private/`. Everything else — the skills, the workflow
guideline, `CONTEXT-SPEC.md`, `WIKI-SPEC.md`, `CLAUDE.md` and the module declaration — is in
`_workflow/`, tracked, because a reader who wants to know how this project is put together should be
able to read it.

**`build_compatibility.py` moved out of `_private/` for exactly that reason.** It reads
`modules.json`, each module's `module.json` and handoff, and `_docs/context/.machine.json` — four
tracked files — and writes the marked region of `README.md` and `COMPATIBILITY.md`. It never
touched the Unity export; it was in `_private/` by habit, and being there meant the table it
writes could not be regenerated, or even checked, by anyone but a maintainer. **A generated
public page must not name a private tool**: two of its notes used to print a `_private/tools/…`
command into `COMPATIBILITY.md`, which is an instruction the reader cannot follow, in text nobody
reviews before it lands.

**`_workflow/tools/` exists because CI has to run the wiki build.** `build_wiki.py`,
`publish_wiki.py` and `modules.py` read only `_docs/`, `_workflow/config/modules.json` and a
module's `module.json` — all tracked — so nothing is disclosed by publishing them, and
`.github/workflows/wiki.yml` can run them from a checkout of this repository alone. When they lived
in `_private/` the wiki could only ever be published from a maintainer's laptop, and the CI gate
that used to check every wiki link had to be deleted for exactly that reason.

**Where a `_private/tools/…` path may appear depends on who the page is for.** `_workflow/` is
addressed to whoever builds the project, so its skills name the commands they run — that is the
point of them, and the directory says plainly that the tools come from elsewhere. `_docs/`, the
root `README.md` and `CONTRIBUTING.md` are addressed to a reader who has only this repository, and
must never tell them to run something they do not have. A `_workflow/tools/…` path is safe to name
anywhere, because every reader of this repository has it.

This used to be enforced by a leak gate over a rendered public tree. It is now a convention, which
means it is a review question.

**There is no `.claude/` directory in this project, by design.** One folder holds the agent
material and it is `_workflow/`. The root `CLAUDE.md` is a tracked one-line `@_workflow/CLAUDE.md`
import, which is how you are reading this. The consequence is stated in *Skill routing* below and
is worth knowing before you look for a skill that is not there.

The same split is mirrored inside each vendor module, including the machine handoff — a generator
input that must nonetheless be *committed* for a module to build from a standalone clone, so it sits
with the other configs at `<Module>/_workflow/config/handoff/`.

## The knowledge base

`_docs/context/` is the machine's memory, and it works with Unity closed. Read it before
reaching for the Unity Editor or the 3,900-line raw export.

| File | Answers |
|---|---|
| `PROVENANCE.md` | How fresh is this, and was it verified against a live scene? **Read first.** |
| `machine.md` | What is this machine, which groups exist, and the circulation ring |
| `plc-symbols.md` | Every twin device OC Assistant generates: name, twin PLC path, device type, `FB_*` type, group |
| `fg-*.md` | **One page per group**: hierarchy, components, Unity — then a link to each vendor's page |
| `devices/*.md` | One per device **type**: what the component is, what its bits do, what to watch out for, and every instance. Rendered from the hand-written `_docs/devices/<type>.md`; `_docs/DeviceDescription-SPEC.md` is the contract those files implement |
| `.machine.json` | The vendor handoff: the same structure as machine-readable JSON. Copied into each consuming module by `sync_machine.py` and read there, never across `../` |

**A root group page is the whole answer for what a group *is*** — its hierarchy, its devices, and
everything a human authored about it. **What a group *becomes* in a control platform is on that
platform's page**, linked from the bottom of the root page, because that answer is now one per
vendor. `_workflow/CONTEXT-SPEC.md` is the contract the root pages implement: the closed authored
vocabulary, the sections, and what may never go in there.

**Structure only, and no status.** Implementation progress, decision logs and "where we got to" are
deliberately absent — a fact that would be wrong next week is not backbone. `implementation-status.md`,
`interfaces.md` and `plc-instance.md` were removed for that reason; do not recreate them.

Refresh it with the `refreshing-project-knowledge` skill. `_workflow/README.md` is the guideline for
how the skills chain — read it when you are unsure which to use.

## Curated reference

`_docs/reference/` is the other half of the knowledge base: **hand-written, never generated**, for
knowledge that does not come from the twin.

**One behaviour contract per group.** Each was written from the shipped TwinCAT ST, because that is
where the behaviour was first made to work — but what it states is a **machine-level contract**, and
any control platform that runs this line has to honour it. That is why these pages stay in the main
repo rather than in `Beckhoff/`. A group page in `_docs/context/` links to its contract here, and
that link is the boundary between structure and behaviour.

| File | Answers |
|---|---|
| `transport-behaviour.md` | How FG_Transport sequences, interlocks and recovers — the derived interface, the transfer latch, the reset model, and where the twin's prose is wrong |
| `fg-01-behaviour.md` | Identify and mark: the camera handshake, the step chain, and **what the laser interlock does and does not enforce** |
| `fg-02-behaviour.md` | Optical inspection: the four-bit camera protocol and why a NOK stops the pallet |
| `fg-03-behaviour.md` | Slot 1 → slot 2 transfer: the axis-naming trap, the handover, the three sub-sequences |
| `fg-04-behaviour.md` | Press and seat check: why `B_NIO` is a verdict, and why every stop retracts the press |
| `fg-05-behaviour.md` | Capping: the continuously-running bunker, `B_Part` vs `B_Detect`, and why the read comes first |
| `fg-system-safety.md` | The safety chain: who owns the facts, who owns the policy, and the lock rule |
| `gripper-station-reset.md` | How FG_03 and FG_05 reset with a part in the gripper — the grip sensors, the branch routes, the fault codes |
| `state-lamp.md` | The signal tower's state-to-colour mapping |

Platform-specific reference — the SPT framework guideline, the unlinked-signal exceptions — lives in
the vendor module that owns it (`Beckhoff/_docs/reference/`), not here.

When a source disagrees with the shipped binary, the binary wins. When the twin's authored prose
disagrees with the running PLC, the PLC wins.

## Skill routing

Root skills — the twin and the machine:

**These skills are NOT auto-discovered — there is no `.claude/` directory. Open the file.**
They are ordinary Markdown at the paths below. Before starting one of these tasks, `Read` the
skill's `SKILL.md` and follow it; a `reference.md` beside it is the deep detail, read on demand.
Do not work from the one-line summary in this table — it is an index, not the instruction.

| Task | Read this file |
|---|---|
| Find a group, station or device; resolve its PLC path | `_workflow/skills/inspecting-twin-hierarchy/SKILL.md` |
| Document what a part of the twin is or does | `_workflow/skills/authoring-context-nodes/SKILL.md` (+ `reference.md`) |
| Check documentation coverage; find undocumented parts | `_workflow/skills/auditing-context-coverage/SKILL.md` |
| Re-export the twin context and rebuild the knowledge base | `_workflow/skills/refreshing-project-knowledge/SKILL.md` |
| Change how a wiki is built, named or cross-linked | `_workflow/WIKI-SPEC.md` (a contract, not a skill — two builders implement it) |
| Drive the Unity Editor from the terminal | `_workflow/skills/unity-cli/SKILL.md` (+ `references/`) |

Each vendor module keeps its own set the same way, under `<Module>/_workflow/skills/`. Working on
TwinCAT means reading from `Beckhoff/_workflow/skills/`:

| Task | Read this file |
|---|---|
| Write or extend a `PLC_1` equipment module | `Beckhoff/_workflow/skills/generating-plc-code/SKILL.md` (+ `reference.md`) |
| Allocate and link PLC I/O to EtherCAT terminals | `Beckhoff/_workflow/skills/mapping-plc-io/SKILL.md` (+ `reference.md`) |
| Read the PLC's symbols, process image or free channels | `Beckhoff/_workflow/skills/exporting-plc-symbols/SKILL.md` |
| Build or change TE2000 HMI content | `Beckhoff/_workflow/skills/building-hmi-elements/SKILL.md` (+ `reference.md`) |

A module that is not cloned has no `_workflow/` and therefore no skills — that is the only reason
one of these paths should ever be missing.

`_workflow/settings.json` is a **reference** permission allowlist, not a live one: nothing reads it
from here. Copy what you want from it into your own `.claude/settings.local.json` or user settings.

The main-repo tools that manage modules:

| Task | Command |
|---|---|
| Copy the machine handoff into every consuming module | `python _private/tools/sync_machine.py` |
| Refresh the compatibility tables in `README.md` and `COMPATIBILITY.md` | `python _workflow/tools/build_compatibility.py` |
| Check the declared modules still pair with this twin | `python _workflow/tools/check_compatibility.py` (`--strict` to exit 1) |
| Build **this repo's** wiki into `_wiki/` | `python _workflow/tools/build_wiki.py` |
| Publish **this repo's** wiki (dry run by default) | `python _workflow/tools/publish_wiki.py` |

**One wiki per repository.** These two cover `_docs/` and nothing else. A vendor module publishes
its own wiki with its own tooling — `python Beckhoff/_workflow/tools/build_wiki.py` and
`publish_wiki.py` beside it. `_workflow/WIKI-SPEC.md` is the contract both sides implement, and it
is the file to read before changing either builder: page naming and cross-repo links have to agree
between two independent implementations, and a divergence is a dead wiki link that nothing catches.

**In normal use nobody runs these by hand.** `.github/workflows/wiki.yml` publishes on a release
and on manual dispatch, and runs `build_wiki.py --check` on any pull request that touches `_docs/`
— which is the only thing that catches a dead wiki link, because the namespace is flat and a broken
link is invisible until a reader clicks it. Each vendor module carries the same workflow. Run them
locally to see a diff before it lands; `publish_wiki.py` is a dry run unless given `--publish`.

## Hard rules

These are lifted out of the skills so they are visible without loading one. They are the
**vendor-neutral** ones; each vendor module's `CLAUDE.md` carries its own.

- **Never read a `.unity` scene or `Machine_1.prefab` to answer a structural question.** The
  machine is a prefab and the scenes only instance it, so a scene file contains almost none of the
  hierarchy — and a prefab instance is not expanded in a scene at all. Use `_docs/context/`, or
  query a live Editor.
- **A `†` in a root page means "one vendor's example, not the machine".** It marks a node that is
  not identical across every scene — today, only the operator panel. Never generate machine-level
  code or documentation from a marked row; take the vendor's own from that vendor's page.
- **A device that belongs to every vendor goes in `Machine_1.prefab`, not in a scene.** Editing one
  scene's copy of a shared device is exactly what the cross-scene comparison catches: the node
  starts being marked `†`, which is the build telling you the edit went to the wrong place.
- **Never invent the "why".** Device types, PLC paths and sequence logic are readable from the
  project — read them. Process intent and the reason a station exists are not — ask the user. A
  plausible invented `Function` entry is worse than no entry, because it will be believed.
- **`oc.plcPath` does not prove a PLC symbol exists.** Every node carries one, including pure Unity
  grouping. A node is a symbol when it has `oc.deviceType` and **neither** `oc.aggregatedBy` **nor**
  `oc.simulationDevice`. 83 of 180 nodes pass.
- **The twin path is not the control path.** The twin says `MAIN.FG_01.P_Camera`; a control platform
  spells it differently — TwinCAT says `MAIN.Machine.FG_01.P_Camera` — and the twin's spelling fails
  silently in a link and in an HMI binding. The root page states the twin path only; the **verified**
  control path is on the vendor page, where it can be checked against a real type model. A row
  showing `—` there means the PLC does not address that device under that group, which is a fact,
  not a lookup failure.
- **No functional group runs on its own.** Each is served by an Index unit in `FG_Transport` that
  fixes the pallet, triggers the group, and waits for it to report done before releasing. A group
  designed without that handshake is designed wrong — the ring is in `machine.md`, the step chain
  and its three invariants in `_docs/reference/transport-behaviour.md`.
- **The PLC is master for behaviour; the MIL scripts are the twin's animation.** They implement the
  *older* contract — no transfer latch, no check that a lift is at a level before running its
  carriage belt, no reset path at all — so a handshake read out of them today reproduces bugs that
  are already fixed. Take the station contract, the interlocks and the reset model from
  `_docs/reference/transport-behaviour.md`. The measured ring order and the Index→group
  couplings in `machine.md` are current — they are probed from the scene, not read out of the MIL.
- **A station's readiness is derived, never remembered.** `CanAccept` and `Occupied` are property
  getters computed from the sensors and one transfer latch, so they are correct in every PackML state
  and mode. A stored flag maintained only inside `Execute` is stale everywhere else — that is what
  put two pallets on one lift carriage. Never reintroduce a `_Ready`.
- **A reset must terminate on time and on its own cylinders.** Never on another unit, and never on an
  event that may not arrive. Both violations of this shipped and both deadlocked the whole group —
  see the reset section of `transport-behaviour.md` before writing any `Resetting`.
- **A reset may *branch* on a sensor but must never *wait* on one.** FG_03 and FG_05 sample their
  grip sensors once at `Resetting` step 0 and read the snapshot thereafter; a live read inside a
  waiting step is the same deadlock as waiting on another unit. See `gripper-station-reset.md`.
- **A gripper's cylinder limit is not a grip witness.** Jaws closed on *nothing* reach `.Extended`
  sooner than jaws closed on a part, so `.Extended` is true either way. Only `B_Detect*` says a part
  is held.
- **A de-energised double solenoid does NOT hold a gripped part in the twin.** The scene wires
  `Cylinder.OnActiveChanged → Gripper.Place(bool)` and `IsActive` means *moving*, so the payload
  drops as soon as the gripper cylinder drifts off its limit. Never leave a grip uncommanded to
  "hold itself" — FG_03 and FG_05 re-assert `Extend()` in `CyclicLogic` for every state but
  `Execute`.
- **Retracted holds the pallet; extending releases it.** Nine authored `Function` entries in the twin
  say the opposite and are known to be wrong — `transport-behaviour.md` carries the correction
  register and the two prefabs that need fixing.
- **A figure's callouts are checked against the twin.** `_docs/ImageDescription.md` gives each
  screenshot a `Scope:`, a `Caption:` and numbered callouts; `build_knowledge.py` resolves every one
  against the export — by relative scene path, by a name unique in the scope's subtree, or by a
  unique `oc.plcPath` leaf — and **refuses to build** if one is missing or ambiguous. Add a figure by
  editing that file, never by pasting an image into a generated page.
- **Documentation splits the way authority does.** `_docs/` covers the machine and the twin;
  everything about a control platform — installing it, running the machine on it, how its projects
  are organised — is in `<Vendor>/_docs/`, because each vendor module is a self-contained
  repository. The root set **links out** to a vendor set and never describes it. A TwinCAT install
  step written into `_docs/02-setup.md` is the same mistake as a `.tmc` detail written into
  `_docs/context/`.
- **A link that crosses a repository boundary is an absolute URL, never `../`.** In both directions.
  A vendor module's directory is gitignored here, so `../Beckhoff/_docs/README.md` is dead for every
  user who did not clone it and dead on GitHub outright; from the other side, `../../../_docs/`
  climbs out of the module's own repository. Generated links are built from `_workflow/config/modules.json`
  and the module's committed handoff sidecar; hand-written ones are spelled out. Each wiki build
  maps them to the **other wiki's** page URL, so a published wiki still cross-links to its sibling
  instead of dropping the reader on a raw Markdown blob.
- **Generated pages must not vary with which modules are cloned.** `_docs/context/` is tracked,
  so building it from what happens to be on disk means a user with one module deletes the other's
  links and commits that. Vendor links come from `modules.json` — which is *declared* — never from a
  filesystem probe. **This now holds for `build_wiki.py` too**, which used to be the exception: it
  builds `_docs/` only, so a module's absence removes nothing. It still *reads* a module's checkout
  when there is one, but only to **verify** a cross-repo link it would emit either way, and it says
  which links it could not check.
- **One wiki per repository, and the naming rule is a shared contract.** A GitHub wiki *is* a
  repository, and a module is its own, so each builds and publishes its own from its own `_docs/`.
  The two builders are independent, which means a cross-repo link is computed by *one* of them using
  the *other's* rule — read `_workflow/WIKI-SPEC.md` before touching either, and change both
  together. **A figure is never copied into a wiki**; a raw-content URL points at the one copy in
  the source repository.
- **Branch off `development`, never off `master`.** `master` is the released state and is
  protected — no direct pushes, pull request and review only. `development` is the integration
  branch and the only branch that may open a PR into `master`. An issue or feature branch comes
  off `development` and is **squash**-merged back into it, so each one arrives as a single
  conventional commit.
- **`development` → `master` must be a MERGE COMMIT, never a squash.** semantic-release reads
  the individual commit subjects to pick the version and write the changelog. A squash collapses
  a whole release into one subject: ten features become one changelog line, and one arbitrary
  subject decides the bump. The other direction is squashed on purpose — the two are not
  symmetric, and getting them the wrong way round produces a plausible-looking release that has
  quietly lost its history.
- **Merging `development` into `master` publishes a release immediately.** There is no separate
  "release" action to take afterwards and no confirmation step. The PR into `master` carries a
  comment saying which version the merge will publish; that comment is the last chance to check.
- **A commit subject is the release mechanism, not a style preference.** semantic-release reads
  the conventional-commit subjects on `master` to decide the next version: `feat:` is a minor,
  `fix:`/`perf:`/`refactor:` a patch, `BREAKING CHANGE:` in the body a major, and `chore:`/`ci:`/
  `test:` release nothing. The subject is also the changelog entry a reader sees, verbatim. Write
  it accordingly, and never hand-edit `package.json`'s `version` or `CHANGELOG.md` — the bot owns
  both and the next release overwrites whatever you put there.
- **The Unity build gates the release, and nothing is written before it passes.** `release.yml`
  runs `version` (checks + a dry run, writing nothing) → `build` (the Windows player, stamped
  with that version) → `release` (semantic-release writes, commits, tags and publishes) → `wiki`.
  Releasing first and building after would leave a tag, a version commit on a protected branch
  and an empty release to undo by hand whenever a build failed; this way a failure leaves
  nothing behind. The build is downloaded into the release job so `.releaserc.json`'s `assets`
  attaches it as the release is created — never a draft, never announced empty.
- **The version is computed twice on purpose.** The dry run in `version` tells the build what to
  stamp and what to name the zip; the real run in `release` does the release. Both must use the
  same `semantic_version`, or the preview can disagree with the release it previewed.
- **There is no separate preview workflow.** `release.yml` runs on both the pull request into
  `master` and the push that merges it; the same `version` job answers both, which is what makes
  the PR comment trustworthy. Do not add a second workflow that recomputes it.
- **`EditorBuildSettings.asset` decides what ships.** Every release builds the scenes enabled
  there to a Windows executable and attaches it to the GitHub release — today exactly one,
  `VC_Demo_1_MIL.unity`. There is no build script and no scene argument, so enabling a second
  scene there silently puts it in the public download, and disabling the MIL scene silently
  ships nothing. Standalone has no `scriptingBackend` override, which is why a Linux runner can
  cross-build the `.exe` at all; switching Standalone to IL2CPP would need a Windows runner.
- **A release publishes the wiki by *calling* `wiki.yml`, not by triggering it.** A release created
  with `GITHUB_TOKEN` does not fire other workflows, so `wiki.yml`'s `release: published` trigger
  would silently never run for an automated release. `release.yml` calls it and passes the new tag
  as `ref`, because the version bump lands *after* the commit that started the run and every
  published page links back to the commit it was built from. The trigger stays for a release made
  by hand, which does fire it.
- **The compatibility check never blocks; it only colours the badge.** This repository is master
  for the machine, so a module being out of range is a fact about someone else's repository that
  no change here can fix. `check_compatibility.py` exits 0 by default and only `--strict` — used
  by the `master` and scheduled runs — exits 1. Do not add it as a gate to a pull request.
- **`not published` and `unreachable` are not verdicts about a module.** They mean the check
  learned nothing: no network, or nothing at that URL. Never report one as a mismatch, and never
  let one fail a build — before the first release *every* module reads `not published`.
- **Never write a control-platform fact into `_docs/context/` or `_docs/reference/`.**
  Function blocks, terminal channels, `.tmc` details, HMI structs and `.plcproj` mechanics belong to
  a vendor module. The root builder does not even import a vendor tool, so a fact placed here has no
  generator to keep it true.

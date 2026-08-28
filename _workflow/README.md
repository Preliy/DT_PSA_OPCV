# The engineering workflow

How the skills in this project chain together, and where each one refuses to proceed.

> **This page names tools that are not in this repository.** The generators live in `_private/`,
> a separate repository the maintainers clone in; it is gitignored here. The method is published
> so it can be read and argued with — but if a command below fails with *no such file*, that is
> why, and nothing in `_docs/` depends on your being able to run it.

This is not a skill list — [CLAUDE.md](../CLAUDE.md) has that. This is the loop: what runs when, what
artifact each step leaves behind, and which gate stops you from building on something that is not
there yet.

## The loop

```
  ┌─ Unity twin ── Machine_1.prefab + one scene per vendor ───────────────────┐
  │                                                                           │
  │  inspecting-twin-hierarchy   find a group / station / device, resolve      │
  │                              its PLC path                                 │
  │  authoring-context-nodes     write the "why" into the scene               │
  │                              → ContextNode entries                        │
  │  auditing-context-coverage   coverage gate: no empty nodes, no             │
  │                              malformed entries                            │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    refreshing-project-knowledge
                    export + probe wiring + build + rebuild each vendor
                                      │
                                      ▼
                    ══════ _docs/context/ ══════      ← THE MEMORY
                    PROVENANCE · machine · plc-symbols
                    fg-*.md   ← one page per group: hierarchy,
                                components, Unity
                    devices/  ← one page per twin device type, from _docs/devices/<type>.md
                    .machine.json  ← the handoff, structure as JSON
                    † marks anything that differs between scenes
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
              Beckhoff/_docs/context/    Siemens/_docs/context/
              fg-*.md · devices/ · plc-io    (not yet)
                       │
        ┌──────────────┼──────────────────────────┐
        ▼              ▼                          ▼
  Beckhoff:            Beckhoff:            Beckhoff:
  generating-plc-code  mapping-plc-io       building-hmi-elements
  PLC_1 module + its   channels ⇄ EtherCAT  HMI pages against the
  published HMI struct ⇄ SIM_1 Mapping      module's published structs
```

The left half needs Unity open. **The right half does not** — that is the whole point of the
knowledge base. The twin can be closed, on another machine, or mid-refactor, and PLC work continues
against the last good export, with `PROVENANCE.md` saying exactly how old it is.

## The two-generator split

The knowledge base is built in two passes, and the order is not optional.

```bash
python _private/tools/build_knowledge.py                    # twin → context/ + .machine.json
python Beckhoff/_private/tools/build_plc_knowledge.py       # .machine.json + TwinCAT → Beckhoff/
python _private/tools/build_knowledge.py                    # again: root pages link what now exists
```

The root generator knows about the machine and **no control platform** — it does not import a vendor
tool and has no idea what a `.tmc` is. A vendor generator knows about its own platform and reads the
twin only through `.machine.json`. Two parsers over one Unity export is exactly how the twin and the
OC project tree came to disagree, so there is only ever one.

The third run is not superstition: the root pages link to the vendor pages that exist, so a vendor
module's *first* build has to happen before the root pages can point at it. After that, either order
converges.

`.machine.json` is schema-versioned. Adding a field is free; moving or removing one bumps
`MACHINE_SCHEMA`, and a vendor generator that does not recognise the schema **refuses** rather than
rendering fields it guessed at.

## The gates

Each of these is a refusal, not a suggestion. Every one of them exists because the failure it
prevents is silent.

**Don't author context you inferred.** The user is the source for process intent, operational
constraints and the reason a station exists. Component types, PLC paths and sequence logic are
readable from the project — read those. A plausible invented `Function` entry is worse than no
entry, because it will be believed all the way down into the PLC code.

**Don't refresh from a scene with drift.** `context_sync --dry_run true` first. A rename or a deleted
component leaves stored values wrong, and the export dumps what the nodes hold without asking any
framework — so an unsynced scene exports stale metadata and looks complete while doing it.

**Don't export with an Editor selection active.** A leftover selection silently becomes the export
root. It once produced a structurally valid 2-node export that reported no error anywhere.

**Don't generate PLC code against a stale `PROVENANCE.md`.** If its export commit predates the last
commit touching the Unity scene, refresh before you generate. Symbols for devices that moved or no
longer exist compile perfectly.

**Don't design a group as if it ran on its own.** Every functional group is started by its Index
unit in `FG_Transport` and must report completion back before the pallet moves. Read the ring in
`machine.md` and the step chain in `reference/transport-behaviour.md` before sequencing anything.

**Don't take a station handshake from a MIL coroutine.** The PLC is master for behaviour. The Unity
sequences are the twin's animation and implement the older contract — no transfer latch, no check
that a lift is at a level before running its carriage belt, no reset path — so copying them
reproduces bugs that are already fixed. Read `reference/transport-behaviour.md` for the contract,
the interlocks and the reset model. The measured ring order and the Index→group couplings in
`machine.md` are current — they are probed from the scene, not read out of the MIL.

**Don't write a `Resetting` that waits on something outside itself.** A reset must terminate on time
and on its own cylinders — never on another unit, and never on an event that may not arrive. Both
violations shipped in FG_Transport and both deadlocked the whole group.

**Don't hand-edit `_wiki/`.** It is generated from `_docs/` by `build_wiki.py`, and swept on every
run. A page there is a *view*; fix the source it was rendered from. The tool also **refuses on any
link it cannot resolve**, because the wiki's namespace is flat and a dead link there is invisible
until someone clicks it.

**Don't try to publish a module's pages from here.** There is **one wiki per repository** — this
build covers `_docs/` and stops, and each vendor module builds and publishes its own from its own
tooling. `_workflow/WIKI-SPEC.md` is the contract both sides implement: the page-naming rule, how a
cross-repo link resolves to the *other* wiki's page, and why a figure is never copied.

**Don't paste an image into a generated page.** A figure belongs in `_docs/ImageDescription.md`,
where its callouts are resolved against the export and a name that no longer exists stops the build.

**Don't hand-edit any `context/` directory.** Both are regenerated wholesale, and each generator
deletes any `.md` in its own output directory it does not recognise. A fact worth keeping belongs in
a `ContextNode` in the scene, where it survives the refresh and reaches the PLC code. A platform fact
belongs in that platform's `reference/` instead.

**Don't put a control-platform fact in the main repo.** Function blocks, terminal channels, `.tmc`
details, HMI structs and `.plcproj` mechanics belong to a vendor module. Nothing here generates them,
so nothing here keeps them true. The vendor gates — pragma trust, the `.tmc`, the HMI struct, the
process image — are in that module's own README.

## Starting a new functional group

Each group's Beckhoff page shows how far it has got: whether the `SIM_1` POU is registered, what its
`Mapping` action targets, and how many process-image members are still unlinked. Read those before
picking one up.

| # | Skill | Does | Leaves behind |
|---|---|---|---|
| 1 | `inspecting-twin-hierarchy` | Find the group's devices and PLC paths | Nothing — it reads |
| 2 | `authoring-context-nodes` | Ask the user what the group is *for*; write `Function`, and `Role`/`Signal`/`BitLayout` where they apply — **those four keys and no others** | `ContextNode` entries in the scene |
| 3 | `auditing-context-coverage` | Prove nothing is empty or malformed | A coverage number you can quote |
| 4 | `refreshing-project-knowledge` | Sync, export, rebuild both halves | `_docs/context/fg-02.md` and `Beckhoff/_docs/context/fg-02.md` |
| 5 | `Beckhoff:generating-plc-code` | The SPT equipment module, its components and its `HMI` struct | `Modules/NN FG_02/FG_02.TcPOU`, `ST_HMI_FG02*` DUTs, `.plcproj` entries |
| 6 | `Beckhoff:mapping-plc-io` | `propose` → review → `write-mapping` → import in XAE | `Mapping_PLC.xml` links, a populated `Mapping` action in `SIM_1` |
| 7 | `Beckhoff:building-hmi-elements` | Device tiles and a group page, bound to the published struct | `Pages/FG_02.content`, user controls |
| 8 | `refreshing-project-knowledge` | Re-scan so both group pages tell the truth | An updated `fg-02.md` on each side |

Steps 5–7 each end by re-running the vendor build and reading the group's own vendor page back — its
**Components**, **PLC_1** and **Mapping** sections are the cheapest check that nothing was left
half-wired. Step 7 also runs `python Beckhoff/_private/tools/hmi_check.py`.

## Refreshing the knowledge base

**Every vendor scene must be exported before the root build.** The build discovers the exports by
glob and renders from the reference scene, but it parses them all — an unexported scene is simply
invisible, and its differences then go unmarked on the root pages.

```bash
# with Unity open — syncs, exports EVERY scene, then builds
# (via the refreshing-project-knowledge skill, which drives the Editor first)
python _private/tools/probe_topology.py                     # scene wiring; Editor required
python _private/tools/build_knowledge.py --live-verified
python _private/tools/sync_machine.py                       # handoff -> each module's handoff/
python Beckhoff/_private/tools/plc_io.py build              # I/O map + .plc-image.json snapshot
python Beckhoff/_private/tools/build_plc_knowledge.py
python Beckhoff/_private/tools/hmi_check.py
python _workflow/tools/check_compatibility.py --write        # refresh the README/COMPATIBILITY table

# with Unity closed — same digest, honestly stamped as unverified,
# topology read from the cached probe
python _private/tools/build_knowledge.py
python _private/tools/sync_machine.py
python Beckhoff/_private/tools/plc_io.py build
python Beckhoff/_private/tools/build_plc_knowledge.py
python Beckhoff/_private/tools/hmi_check.py
python _workflow/tools/check_compatibility.py --write
```

`check_compatibility.py` reads each module **from your checkout if it is cloned and over https if
it is not**, and says which per row. So after a re-export it reports `current` for a module whose
handoff you have synced locally — while CI, which clones nothing, keeps reporting `behind` until
that module commits and pushes the snapshot. Both are true about the copy they read; push to make
them agree.

**There is no longer a second `build_knowledge.py` run.** The root pages link to vendor pages by URL
from `_workflow/config/modules.json`, which is *declared* rather than discovered, so their content no
longer depends on a vendor build having happened first — or on that module being cloned at all.

**Commit in two repositories.** `sync_machine.py` writes the handoff snapshot into the module, and
the module is a separate repo: `git status` here will not mention it. Run `git -C Beckhoff status`
too, every time.

With TwinCAT closed, skip `plc_io.py build`: everything else reads the committed
`.plc-image.json` snapshot anyway, and the vendor pages banner themselves as behind.

Everything is written from the **main repo root**, vendor tools included. Those tools anchor on their
own file rather than on your working directory, so they also run from inside the module — that is
what lets a module build from a standalone clone — but the commands here are spelled from the root,
because that is the level everything else is written from. `build_knowledge.py` **refuses to write**
rather than emit a digest it cannot vouch for — wrong export root, symbol counts that
disagree between the two exports, a truncated tree, malformed entries. Read what it says; do not work
around it.

`--live-verified` is a claim about provenance, not a formatting flag. Pass it only when you actually
re-exported from a ready Editor in the same session.

## Where things live

| Path | What | Edited by |
|---|---|---|
| `_workflow/` | **Published** — how the project is built: `CLAUDE.md`, this file, `CONTEXT-SPEC.md`, `skills/`, `settings.json`, `config/`. There is no `.claude/`: the skills are read by path, and `settings.json` is a reference allowlist nothing loads from here | You, deliberately |
| `_docs/context/` | The generated twin knowledge base, including `.topology.json` and `.machine.json` | **Nobody — it is generated** |
| `_workflow/CONTEXT-SPEC.md` | The contract `context/` implements: the authored key vocabulary, the sections, the PLC comment policy | You, deliberately |
| `_docs/reference/` | Machine-level behaviour contracts — one per group, plus the safety chain and the state lamp | You, deliberately — no generator touches it |
| `_workflow/config/modules.json` | Which vendor modules exist, their repository URLs, and which versions pair with this repo | You, when a module is added or a version is proven |
| `_workflow/tools/` | **Published** — `build_wiki.py`, `publish_wiki.py`, `modules.py`, `check_compatibility.py`. They read only tracked files and public URLs, and GitHub Actions has to run them from a checkout of this repo alone | You, when the wiki or pairing contract changes |
| `_private/tools/` | `build_knowledge.py` (the twin digest and the handoff), `sync_machine.py`, `figures.py`, `probe_topology.py` — the ones that read the Unity export | You, when the shape of the knowledge changes |
| `.github/workflows/wiki.yml` | Publishes the wiki on a release, a manual dispatch, or a call from `release.yml`; builds it as a gate on any PR touching `_docs/` | You, deliberately |
| `.github/workflows/release.yml` | The whole release: checks + next version (writes nothing) → Windows build of the MIL scene, as a gate → semantic-release writes `package.json`/`CHANGELOG.md`, tags, and publishes the release with the build attached → the wiki. Also runs on a PR into master, where it stops after the version and comments it | You, deliberately |
| `Unity/ProjectSettings/EditorBuildSettings.asset` | **Which scenes go into the public download.** One enabled scene today, `VC_Demo_1_MIL.unity`; the release build takes whatever is enabled here | The Unity Editor — but know that it is load-bearing |
| `.github/workflows/compatibility.yml` | Runs `check_compatibility.py` on master and development, on a relevant PR, and weekly. Strict on master and the schedule only, so the README badge tells the truth without blocking work | You, deliberately |
| `package.json`, `CHANGELOG.md` | The version, and the generated changelog. Not a Node package — see `CONTRIBUTING.md` | **Nobody — the release bot owns both** |
| `_docs/` | What the machine **is**: the narrative pages, the figures and `ImageDescription.md`, the generated `context/` and the curated `reference/` | You, deliberately — except `context/` |
| `_private/` | **The Python generators, and nothing else.** Its own repository, cloned into this root and gitignored here | You, when the shape of the knowledge changes |
| `_workflow/WIKI-SPEC.md` | The contract every wiki builder implements: page naming, cross-repo links, images. Shared, because each repository has its own builder | You, deliberately |
| `_wiki/` | The flat GitHub-wiki view of **this repository's** `_docs/`. **Gitignored** — a build artifact, not a tracked copy. A module has its own | **Nobody — it is generated** by `build_wiki.py`, published by `publish_wiki.py` |
| `COMPATIBILITY.md` | How the module pairing works, plus a generated table of what is actually here | Hand-written outside the markers; generated between them |
| `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab` | The machine itself; every scene instances it | The Unity Editor |
| `Unity/Assets/Demo_1/Scenes/*.unity` | One scene per vendor — the prefab plus that vendor's operator panel | The Unity Editor |
| `Unity/Assets/StreamingAssets/<Scene>_Context.json` | The raw export, one per scene | The Unity exporter |
| `Unity/Assets/StreamingAssets/<Scene>_Project_Tree.xml` | OC's independent device tree, one per scene | OC Assistant |
| `Beckhoff/` | The TwinCAT projects, their knowledge base in `_docs/`, their skills and handoff in `_workflow/`, their tools in `_private/` | The Beckhoff skills, and you — see `Beckhoff/_workflow/README.md` in that module |
| `Siemens/` | Stub for the TIA port. Its Unity scene and export live in **this** repo | Not yet |

Both vendor paths are **separate repositories** cloned into this root and gitignored here, so the two
git repos do not collide. `modules.json` declares them; `COMPATIBILITY.md` explains the pairing.

Generic engineering-process skills (planning, debugging, code review, worktrees) live at user level
in `~/.claude/skills/` — they are not project knowledge and are available in every project.

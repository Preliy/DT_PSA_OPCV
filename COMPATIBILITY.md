# Module compatibility

This machine is split across repositories. The **main repository** holds the Unity twin, the machine
description and the behaviour contracts. Each **control platform** is a separate, optional repository
you clone into the main repo's root:

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff
```

The module paths are gitignored here, so the two git repositories do not collide: inside `Beckhoff/`
everything is a normal checkout on a normal branch, and `git status` in the main repo never mentions
it. Take only the platform you use — a Siemens user has no reason to fetch a TwinCAT solution.

## Which versions pair

<!-- BEGIN GENERATED - do not edit between the markers. -->
| Module | Platform | Version | Tested | Built against | Verdict |
|---|---|---|---|---|---|
| [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff) | Beckhoff TwinCAT 3 | 1.0.0 | 1.0.0 | export `5010e82 2026-08-23` | current |
| [Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens) | Siemens TIA Portal | 0.1.0 | 0.1.0 | — | not a consumer |

**This twin is** `unreleased`, carrying machine schema `2`, export `5010e82 2026-08-23`.

_Beckhoff, Siemens — read from the local checkout rather than the published repository, so unpushed work is included._
<!-- END GENERATED -->

**Clone the module at the version in the `Tested` column.** That is the pairing that was actually
verified, and it is the one number you need.

## What the pairing is made of

Two things — and only one of them is written by hand.

| | Lives in | Says |
|---|---|---|
| `tested` | this repo's `_workflow/config/modules.json` | **hand-written.** The module version this twin was verified against. A fact, not a promise — it is the version to clone |
| the handoff | each module's `_workflow/config/handoff/` | **derived.** A byte-identical copy of this repo's `.machine.json`, plus a sidecar stamping which twin version it was synced from. Comparing the two sha256s says exactly whether the module was built against the machine as it is now |
| `version` | the module's `module.json` | which module this is. Written by that module's release bot; never by hand |
| `version` | this repo's `package.json` | which twin this is. Written by semantic-release; never by hand |

### There are deliberately no version ranges

This used to be stated from both sides as ranges — `requires` here and `requiresMain` in each
module — and both were checked. **Neither ever fired**, and the reason is structural: a range
admits versions that do not exist yet, so it gets written wide once (`>=1.0.0`) and nobody ever
narrows it. It reports "in range" forever and reads like a check. A rail bolted to nothing is
worse than no rail.

Both are gone. What replaced them was already here and is already exact:

- **`tested`** answers *which version should I clone* — the question a person setting up actually asks.
- **The handoff sha256** answers *is this module still current* — derived, so nobody maintains it
  and it cannot drift.
- **The handoff schema** answers *is this fatal* — and it is the only thing that ever was. A format
  change means fields the module reads may have moved, so its own build refuses rather than guessing.

The sidecar also records `mainVersion`: the twin's version at the moment the snapshot was taken.
That is the pairing, **stamped at the one instant it becomes true** rather than declared by hand in
two repositories and kept in step by memory.

## The check runs in CI

[`_workflow/tools/check_compatibility.py`](_workflow/tools/check_compatibility.py) does the
comparison, and `.github/workflows/compatibility.yml` runs it on every push to `master`, on any
pull request touching the declaration, and **once a week on a schedule**. The schedule is the
point: a module can go stale with no commit in this repository at all, so a check that only ran on
a push here would never notice.

**One rule decides where each row comes from: the module is read from your checkout if it is
cloned, and fetched from its own repository over https if it is not.** So the check works with no
module on disk — which is what CI always has, and what most checkouts have for at least one of
them — and a maintainer still sees the truth about their own working tree. Every row says which it
was.

**A mismatch never fails a pull request or blocks a release.** This repository is master for the
machine; a module being behind is a fact about someone else's repository and cannot be fixed by a
change here. The `master` and scheduled runs are strict, so the **vendor compatibility badge**
in the README goes red — which is where the state is surfaced to a reader.

Run it yourself at any time:

```bash
python _workflow/tools/check_compatibility.py            # report
python _workflow/tools/check_compatibility.py --strict   # exit 1 on a mismatch
python _workflow/tools/check_compatibility.py --write    # refresh the tables above
python _workflow/tools/check_compatibility.py --check    # exit 1 if they are stale
```

## Why a pin exists at all

Cloning a module in beats a git submodule for everyday work — one commit, one push, nothing to
initialise — and costs the one thing a submodule would have given for free: **a recorded pin.**
Nothing in git says which Beckhoff version belongs with which twin, so a stale module against a fresh
twin is invisible. The pages still build; they just describe a machine that has moved on.

So each module carries a **committed snapshot of the machine's structure** — a byte-identical copy of
this repo's [`_docs/context/.machine.json`](_docs/context/.machine.json), kept at
`<Module>/_workflow/config/handoff/.machine.json`. Comparing the two sha256s answers exactly one
question: was this module built against the machine as it is now?

| Verdict | Meaning |
|---|---|
| **current** | The module was built against this machine. Nothing to do |
| **behind** | The twin has been re-exported since. The module still builds and is still correct about itself, but it describes an older machine |
| **schema mismatch** | **Fatal.** The structure format changed, so fields the module reads may have moved. Its build refuses rather than guessing |
| **handoff never synced** | The module opted in to the machine handoff — it has the sidecar — but no snapshot is committed beside it |
| **not a consumer** | The module does not build documentation from the machine description, so it carries no snapshot and there is nothing to compare. Not a fault: Siemens is here today |
| **not published** | Nothing was found at the module's repository, and it is not cloned here either. Before the first release that is the normal state; afterwards it means a rename, a deletion, or a repository turned private |
| **unreachable** | No network, a timeout, or GitHub said something other than 404. **Nothing was learned** — this is not a claim that anything is wrong |

**Only a schema mismatch is fatal to a module's own build.** Everything else is reported and left
to you — a module one version behind still documents a real machine, and blocking over it would
stop work that is perfectly valid. A module at a version other than `tested` is a **note**, never a
verdict: it usually works, and the handoff is what actually decides.

Keep **not published** and **unreachable** apart from the rest. They mean the check could not
observe the module, not that it observed a problem. Neither turns the badge red, because a module
that has not been published yet would otherwise make the badge red on the day the project ships.
Both are annotated on the run, because "not published" is also what a repository that was renamed
without telling anyone looks like.

### One tool, and why it used to be two

[`check_compatibility.py`](_workflow/tools/check_compatibility.py) is the whole of it.

There were two: one reading the modules on disk to write the tables, one fetching them over https
for CI. They asked the same question of different copies, so they could disagree — a maintainer who
had synced a handoff locally but not pushed it saw `current` while the badge said `behind` — and
this page needed a paragraph telling you which to believe. That paragraph was a symptom, not a
feature. One tool with one rule (**disk if cloned, https if not**) removes the disagreement, and
each row names the copy it read. If a locally-read row worries you, push and let CI read the
published one.

It compares the machine snapshot by **content hash, normalised for line endings** — not by
`exportCommit`. That field looks like the right one and is not: re-exporting a single scene
updates that scene's entry and leaves `exportCommit` and the top-level `exportedAtUtc` alone, so
a module can be a whole export behind while both top-level fields match exactly. A check built
on them reports a stale module as current, which is the one thing this must never do.

## Re-syncing a module

The snapshot is written by the maintainer's tooling and **committed inside the module**, so a stale
module is fixed in two repositories:

```bash
git -C Beckhoff add _workflow/config/handoff && git -C Beckhoff commit -m "chore: sync machine handoff"
```

## Adding a platform

A new control platform is a new repository, cloned in the same way. Nothing in this repository needs
editing to accept one — the machine's structure is published as JSON and its behaviour as a
platform-neutral contract, so you implement against a specification.

**→ [How the setups are put together](_docs/04-plc-connectivity.md)** · **→ [CONTRIBUTING.md](CONTRIBUTING.md)**

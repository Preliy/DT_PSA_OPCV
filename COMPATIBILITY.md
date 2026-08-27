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
| Module | Version | Source | Requires | Tested | Handoff | Verdict |
|---|---|---|---|---|---|---|
| [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff) | 1.0.0 | module.json | `>=1.0.0` | 1.0.0 | schema 2, export `5010e82 2026-08-23` | current |
| [Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens) | 0.1.0 | module.json | `>=0.1.0` | 0.1.0 | not a consumer | no handoff |

**This main repository carries** machine handoff schema `2`, export `5010e82 2026-08-23`, exported `2026-08-23T17:09:36.0996372Z`.

Every verdict above is computed against that line. Without it the table could not be checked, only believed.
<!-- END GENERATED -->

A module declares its own version in its `module.json`. Clone the module at the version named above
if you want the pairing that was actually tested.

## What is declared where

The pairing is stated from both sides, and both sides are checked.

| Field | Lives in | Says |
|---|---|---|
| `version` | this repo's `package.json` | which twin this is. Written by semantic-release; never by hand |
| `requires` | this repo's `_workflow/config/modules.json` | which module versions **this twin** admits |
| `tested` | this repo's `_workflow/config/modules.json` | the module version this twin was actually verified against. Not derived — stated honestly |
| `version` | the module's `module.json` | which module this is |
| `requiresMain` | the module's `module.json` | which twin versions **that module** admits |

Neither side is trusted to be right about the other, which is why both ranges exist. A module
that has moved on can refuse an old twin through `requiresMain` without this repository being
edited at all.

## The check runs in CI

[`_workflow/tools/check_compatibility.py`](_workflow/tools/check_compatibility.py) does the
comparison, and `.github/workflows/compatibility.yml` runs it on every push to `master`, on any
pull request touching the declaration, and **once a week on a schedule**. The schedule is the
point: a module can fall out of range with no commit in this repository at all, so a check that
only ran on a push here would never notice.

It does not clone anything. Each module's `module.json` and committed handoff are fetched from
that module's own repository over https — so the check works with no module on disk, which is
what CI always has, and what most checkouts have for at least one of them.

**A mismatch never fails a pull request or blocks a release.** This repository is master for the
machine; a module being behind is a fact about someone else's repository and cannot be fixed by a
change here. The `master` and scheduled runs are strict, so the **vendor compatibility badge**
in the README goes red — which is where the state is surfaced to a reader.

Run it yourself at any time:

```bash
python _workflow/tools/check_compatibility.py            # report
python _workflow/tools/check_compatibility.py --strict   # exit 1 on a mismatch
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
| **version out of range** | The module's `requiresMain` does not admit this twin, or `modules.json` does not admit the module's version |
| **schema mismatch** | **Fatal.** The structure format changed, so fields the module reads may have moved. Its build refuses rather than guessing |
| **handoff never synced** | The module opted in to the machine handoff — it has the sidecar — but no snapshot is committed beside it |
| **not a consumer** | The module does not build documentation from the machine description, so it carries no snapshot. Not a fault: Siemens is here today |
| **not published** | Nothing was found at the module's repository. Before the first release that is the normal state; afterwards it means a rename, a deletion, or a repository turned private |
| **unreachable** | No network, a timeout, or GitHub said something other than 404. **Nothing was learned** — this is not a claim that anything is wrong |
| **not cloned** | Declared in `_workflow/config/modules.json`, absent from *your* checkout. Only the local tooling says this; modules are optional |

**Only a schema mismatch is fatal to a module's own build.** Everything else is reported and left
to you — a module one version behind still documents a real machine, and blocking over it would
stop work that is perfectly valid.

Keep **not published** and **unreachable** apart from the rest. They mean the check could not
observe the module, not that it observed a problem. Neither turns the badge red, because a module
that has not been published yet would otherwise make the badge red on the day the project ships.
Both are annotated on the run, because "not published" is also what a repository that was renamed
without telling anyone looks like.

### Two tools answer this, and they can disagree

Both are in [`_workflow/tools/`](_workflow/tools/) and both are yours to run.
[`build_compatibility.py`](_workflow/tools/build_compatibility.py) writes the table above from
the modules **on disk** — it describes *your* checkout, which is what makes it useful to the
person running it, and why it refuses when nothing is cloned.
[`check_compatibility.py`](_workflow/tools/check_compatibility.py) asks each module's **own
repository** over https, which is what CI and every reader see.

They are asking the same question of different copies, so they can disagree: a maintainer who
has synced a handoff locally but not pushed it sees `current` while the badge says `behind`.
**When they disagree, believe the badge and push** — the badge is the copy the world has.

Both compare the machine snapshot by **content hash, normalised for line endings** — not by
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

**→ [How the setups are put together](_docs/04-architecture.md)** · **→ [CONTRIBUTING.md](CONTRIBUTING.md)**

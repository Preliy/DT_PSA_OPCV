# Contributing

Thanks for looking. DT_PSA_OPCV is meant to be forked, extended and ported to other control
platforms.

Before you change anything, please read the rules below. They are short, and every one of them
exists because breaking it fails **silently**.

## The most useful things you could do

| | |
|---|---|
| **Connect another control system** | Rockwell, CODESYS, B&R, Omron, Siemens, your own soft PLC — nobody has done any of them. The machine's structure is published as JSON and its behaviour as a platform-neutral contract, so you implement against a spec rather than guessing. **[See how the setups fit together](_docs/04-architecture.md)** — this is the most interesting work in the project |
| **Get HIL working** | Everything here was validated in SIL, on an emulated runtime. Real controller hardware uses the same mechanism, but its concrete steps are still missing from [Setup](_docs/02-setup.md) |
| **Fill a setup gap** | The TwinCAT gaps in the [Beckhoff setup guide](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/01-setup.md) — ADS route, EtherCAT simulation pairing, licence activation, OC Assistant install. Blank because nobody has captured them from a working install, not because they are secret |
| **Report what does not work** | Especially a setup step that fails on a fresh machine |

## Where a change belongs

### The machine description is generated

Everything under [`_docs/context/`](_docs/context/) is **generated from the Unity twin** — the device
list, the PLC paths, the hierarchy of every group. That is deliberate: it means the documentation
cannot quietly drift away from the thing it describes.

**A pull request that edits a page under `_docs/context/` cannot be merged**, because the next build
overwrites it. If one of those pages is wrong, the twin is wrong:

| The problem is | Do this |
|---|---|
| A device is missing, misnamed, or in the wrong group | Fix it in the Unity scene and open a PR against `Unity/` |
| A description of what a station is *for* is wrong or absent | Open an issue saying what it should say — that text is authored in the scene |
| A **behaviour** contract is wrong | Edit [`_docs/reference/`](_docs/reference/) directly and open a PR. Those pages are hand-written |

### Documentation splits the way authority does

[`_docs/`](_docs/) covers the **machine and the twin**. Everything about a control platform —
installing it, running the machine on it, how its projects are organised — lives in that platform's
own repository, because each control module is self-contained.

This repository **links out** to a platform's documentation and never describes it. A TwinCAT
install step written into [`_docs/02-setup.md`](_docs/02-setup.md) puts a fact where nothing owns
it.

A link that crosses a repository boundary is an **absolute URL**, in both directions — a module's
directory is gitignored here, so `../Beckhoff/…` is dead for anyone who did not clone it.

### Behaviour is machine-level; realisation belongs to the platform

[`_docs/reference/`](_docs/reference/) holds **contracts**. They were written from the TwinCAT
program, because that is where the behaviour was first made to work — but a Siemens implementation
has to honour the same ones. A control module documents its *realisation* of a contract, never a
second version of the contract.

Conversely: **never write a control-platform fact into this repository.** Function blocks, terminal
channels, HMI structures and project mechanics belong to the module that owns them.

### This repository is the public one

Everything tracked here is published — including [`_workflow/`](_workflow/), which is how the
project is built: the agent skills, the workflow guideline, the knowledge-base contract and the
module declaration. That is deliberate. If you want to understand how the generated half is
produced, or to propose a change to it, the method is in front of you.

Some of the tooling is here and some is not, and the line is **what a tool reads**. Anything that
reads only tracked files is in [`_workflow/tools/`](_workflow/tools/) and you can run it: the wiki
builder and publisher, and the two compatibility tools. The generators that read the Unity export
live in a separate repository cloned in as `_private/`, which is gitignored, and only the
maintainers have it.

That is why some pages under [`_workflow/`](_workflow/) name commands you cannot run — they are
addressed to whoever builds the project, and they say where the tools come from. The pages you are
expected to *use* — [`_docs/`](_docs/), this file, the README — never do: everything they ask of you
works with this repository alone. There is no filtering step at publish time; the boundary is the
directory, and keeping it right is a review question.

## The rules

### 1. Get the modules you need

The twin is one repository; each control platform is a **separate, optional repository** cloned into
this one's root. The module paths are gitignored, so the two git repos do not collide:

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff   # optional
```

[COMPATIBILITY.md](COMPATIBILITY.md) explains which versions pair and how a stale one is caught.
Inside a module everything is a normal checkout on a normal branch — one commit, one push, nothing
to pin.

### 2. A shared device goes in the prefab, not in a scene

The machine is `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab`; each scene only instances it and adds
that vendor's operator panel. Editing one scene's copy of a shared device breaks the other scenes
silently — the device stops being the same device in each.

A `†` on a generated page means "this is one vendor's example, not the machine". Never take
machine-level code or documentation from a marked row.

### 3. Never invent the "why"

Device types, PLC paths and sequence logic are readable from the project — read them. Process intent
and the reason a station exists are not. **A plausible invented explanation is worse than none,
because it will be believed.** If you do not know, leave it out or ask in an issue.

### 4. Do not read the machine's behaviour out of the MIL scripts

`Unity/Assets/Demo_1/Scripts/MIL/` is the twin's *animation* — model in the loop. It implements an
**older contract**: no transfer latch, no check that a lift is at a level before running its carriage
belt, no reset path at all. Code written from it reproduces bugs that are already fixed.

The contract is [`_docs/reference/transport-behaviour.md`](_docs/reference/transport-behaviour.md),
and the PLC is master for it.

### 5. A reset must terminate on its own

A reset may **branch** on a sensor but must never **wait** on one, and it must never wait on another
unit or on an event that may not arrive. Both violations of this have shipped in this project, and
both deadlocked a whole functional group. Read the reset section of
[`_docs/reference/transport-behaviour.md`](_docs/reference/transport-behaviour.md) before writing
one.

## Branches

Two long-lived branches, and everything else is short.

| Branch | What it is |
|---|---|
| **`master`** | The **released** state. Protected: no direct pushes, pull request and review only. Merging into it *is* cutting a release |
| **`development`** | The integration branch. Work lands here first, and it is the only branch that may open a pull request into `master` |
| **your branch** | One per issue or feature, branched off `development`, merged back into `development` |

```
  issue-42 ──┐
  issue-57 ──┤ squash merge
             ▼
        development ───── merge commit (an admin decides when) ─────▶ master ──▶ release
```

**Branch off `development`, not `master`.** A branch off `master` is missing whatever has
already landed on `development`, and the merge back will be painful.

**How things get merged matters, and the two directions differ:**

- **Your branch → `development`: squash.** Your work arrives as exactly one commit, and that
  commit's subject is the changelog entry the world will read. Tidy it before merging; the
  intermediate "fix typo" and "address review" commits should not survive.
- **`development` → `master`: a merge commit, never a squash.** semantic-release reads the
  individual subjects to decide the version and write the changelog. Squashing a release into
  one commit turns ten features into one changelog line and lets one arbitrary subject choose
  the version.

Opening a pull request from `development` into `master` posts a comment saying exactly which
version merging it would release, and what the notes will say. Read it before you merge — the
merge publishes immediately.

## Pull requests

- Branch off `development`.
- **Conventional commit subjects** — `feat:`, `fix:`, `docs:`, with an optional scope:
  `fix(hmi): mapping`. This is not a style preference. The subject decides the next version
  number; see below.
- Say what you verified. "Builds pass" is worth more than a description of intent.
- If your change affects the Unity twin, say so — the generated machine pages are rebuilt from it
  and that happens outside your PR.

## Releases

A release happens when a maintainer merges `development` into `master`. There is no other way to
cut one, and nothing else about merging is special — the pipeline does the rest.

Releases are cut by [semantic-release](https://semantic-release.gitbook.io/) from the commit
history. The merge runs `.github/workflows/release.yml`, which works out the next version from
the commit subjects since the last tag.

**What a release contains:**

| | |
|---|---|
| **Version** | The tag `vX.Y.Z`, with `package.json` and `CHANGELOG.md` written and committed back to `master` |
| **Changelog** | Release notes generated from the commit subjects since the previous tag, grouped into Features and Bug Fixes — and the same text prepended to `CHANGELOG.md` |
| **Download** | `DT_PSA_OPCV-vX.Y.Z-win64.zip` — the MIL scene as a Windows executable, with a `.sha256` beside it. Unzip and run: no Unity, no PLC, no clone |
| **Wiki** | Republished from the released tag |

**Nothing is written until everything that could fail already has:**

```
checks + next version  ──▶  Windows build  ──▶  release  ──▶  wiki
   nothing written          nothing written      tag, commit,
                                                 GitHub release
```

The version is computed first so the build can be stamped with it, the build runs as a **gate**,
and only then does semantic-release write anything. A failed build leaves **nothing behind** —
no tag, no version commit, no half-published release to undo on a protected branch. Re-run the
workflow and try again.

The build is downloaded into the release job before semantic-release runs, so the GitHub release
is created with its download already attached, in one operation. It is never announced empty.

What gets built is whatever `Unity/ProjectSettings/EditorBuildSettings.asset` has enabled — one
scene today; enabling a second one puts it in the public download.

**A Unity licence is required to release.** The build gates the release, so missing or expired
`UNITY_LICENSE` secrets stop it rather than shipping a release with nothing to download.

**Your commit subject chooses the version bump:**

| Subject | Bump |
|---|---|
| `feat:` | minor |
| `fix:`, `perf:`, `revert:`, `refactor:`, `docs(README):` | patch |
| `BREAKING CHANGE:` in the commit body | major |
| `docs:` (any other scope), `style:`, `test:`, `build:`, `ci:`, `chore:` | none |

Two files are owned by the release bot:

- **`CHANGELOG.md`** is generated from the commit subjects. Never write an entry by hand — the
  next release regenerates the file and your entry is gone.
- **`package.json`** holds the version, and nothing else. It is not a Node package: it is
  private, has no dependencies and is never published to npm. It exists because
  semantic-release needs a file to write the version into, and because each control module's
  `requiresMain` needs a main-repo version to be checked against. **Never edit `version` by
  hand.**

That is also why a good subject line matters more here than in most projects: it is the
changelog entry a reader will see, verbatim.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Contributions are accepted under [GPL-3.0](LICENSE), the license this project is released under.

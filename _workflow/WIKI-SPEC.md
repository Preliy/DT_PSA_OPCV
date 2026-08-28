# Wiki specification

The contract every wiki builder in this project implements. Hand-written, never generated.

**One wiki per repository.** A GitHub wiki *is* a repository — `<repo>.wiki.git` — with a flat page
namespace and no directories. A module is its own repository, so it gets its own wiki, built and
published by its own tooling from its own `_docs/`. The main repo's wiki carries the machine; a
module's wiki carries that platform's realisation. **Neither builds the other**, and neither can be
incomplete because of what the reader did or did not clone.

| Repository | Wiki | Built by |
|---|---|---|
| `DT_PSA_OPCV` | `DT_PSA_OPCV/wiki` | `_workflow/tools/build_wiki.py` |
| `DT_PSA_OPCV_Beckhoff` | `DT_PSA_OPCV_Beckhoff/wiki` | `Beckhoff/_workflow/tools/build_wiki.py` |

**Why a copy at all.** Nothing inside a wiki repo can reach a file in the source repo by a relative
path, so publishing to a wiki always means rendering a copy into that other repository. What is *not*
copied is the figures — see *Images* below. And `_wiki/` itself is not a second tracked copy: it is
gitignored, swept on every run, and mirrored into a throwaway clone at publish time.

**This file is the contract because the builders are independent.** Each repository has its own
builder, and a cross-repo link is computed by *one* builder using the *other* repository's naming
rule. If the two rules drift apart the result is a dead wiki link that no compiler catches. So the
rule is written down here, once, and each builder implements *this*, not its own habit.

---

## 1. Page naming

**One rule, applied to a path relative to the repository that owns it.** There is no vendor prefix:
`Beckhoff/_docs/context/fg-01.md` is `_docs/context/fg-01.md` in its own repo, and its page is
`Machine-FG_01` in its own wiki.

| Source, repo-relative | Page |
|---|---|
| the repository's landing page | `Home` |
| `_docs/NN-<stem>.md` | `<Title>` |
| `_docs/context/machine.md` | `Machine` |
| `_docs/context/PROVENANCE.md` | `Machine-Provenance` |
| `_docs/context/<stem>.md` | `Machine-<Title>` |
| `_docs/context/devices/<x>.md` | `Device-<first word of that page's H1>` |
| `_docs/reference/<stem>.md` | `<RefPrefix>-<Title>`, with a trailing `-Behaviour` removed |

`<Title>` — drop a leading `NN-`, split on `-`, capitalise each part, then apply the special-case
map `fg→FG, plc→PLC, io→IO, spt→SPT, hmi→HMI, ads→ADS, mil→MIL, sil→SIL, ui→UI`, then rewrite
`FG-01` → `FG_01` (also `FG-System`, `FG-Transport`), because `FG_01` is how the project spells a
group everywhere else.

A device page takes its name from its own H1 rather than its file name: the generator lower-cases
the file (`controlbunker.md`), and the heading carries the spelling the twin uses (`ControlBunker`),
which is also how every table that links there spells it.

That makes a device page the one name a builder cannot compute from a path alone — a problem when
it has to name a device page in a repository that is not cloned. It is resolvable because **every
knowledge base derives its device pages from the same `.machine.json`**, so the builder's own page
for the same slug answers the same question. When both are present and they **disagree**, the two
generators have drifted and the build stops: either spelling would be a dead link in one of the two
wikis.

`<RefPrefix>` is **`Behaviour` in the main repository** and **`Reference` in a module**. The main
repo's `_docs/reference/` holds machine-level behaviour contracts; a module's holds platform notes
that are not behaviour at all — `spt-framework.md` is a framework guideline, and filing it under
`Behaviour-` would be a lie. Both builders already know which kind of repository a URL names: the
root from `_workflow/config/modules.json`, a module from `upstreamUrl` in its committed
`.handoff.json`. This needs no config field.

### Home, and the other overrides

**`Home` is the repository's landing page, and that is `_docs/README.md` in every repository** —
the main repo and each module alike. It is still stated as an override rather than derived, because
a cross-repo link to another repository's landing page has to resolve too, so every builder must
know its siblings' spelling as well as its own.

| Repository | Overrides | What a sibling must know |
|---|---|---|
| main | `_docs/README.md` → `Home` | `_docs/README.md` → `Home` |
| a module | `_docs/README.md` → `Home` | `_docs/README.md` → `Home` |

The main repo used to open on `_docs/01-introduction.md` instead. That page is gone — the project's
welcome text is the root `README.md`, which is not a wiki page — and the rule is now the same
everywhere, which is one fewer entry a sibling builder can get wrong.

Beyond `Home`, keep the table empty. An override is a fact that lives in one builder and nowhere
else, so every entry is one more thing the other builder cannot compute. One name that used to be an
override in the shared wiki is now produced by the rule and is deliberately left that way:
`_docs/reference/fg-system-safety.md` is `Behaviour-FG_System-Safety` (not `Behaviour-Safety`),
which is consistent with the other eight `Behaviour-FG_*` pages.

### Aliases

A file that is a real link target but gets no page of its own redirects instead: every repo's root
`README.md` redirects to `Home`, and `CONTRIBUTING.md` links out to the repository rather than into
the wiki.

### Collisions

The namespace is flat. Two sources that want the same page name **stop the build** — a silent
overwrite publishes one page and loses the other with nothing to show for it.

## 2. Links

Every link in a rendered page is resolved. **A link that cannot be resolved stops the build**, because
in a flat namespace a broken link is invisible until a reader clicks it and there is no compiler to
catch one.

| Link in the source | Becomes |
|---|---|
| relative, to a page this wiki publishes | the bare page name — `Machine-FG_01` |
| relative, to an aliased source | the alias target |
| relative, to an image | a raw-content URL — see *Images* |
| relative, to anything else in the repo | an absolute `blob`/`tree` URL into this repository |
| absolute, naming a path this wiki publishes | the bare page name |
| absolute, naming a path a **sibling** wiki publishes | that wiki's page URL — `https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/wiki/Machine-FG_01` |
| anything else | left exactly as written |

**A sibling is declared, never probed.** The root learns its siblings from
`_workflow/config/modules.json`; a module learns its upstream from `.handoff.json`. Building this
list from what happens to be on disk would make the output depend on which optional modules the
builder happened to have cloned — the same rule that governs `_docs/context/`.

**Cross-repo links are verified when the sibling is on disk, and emitted either way.** A builder
resolves the target path in the sibling's working tree, applies the rule above, and refuses if the
file is missing. When the sibling is not cloned it cannot check, so it emits the link and *reports*
that it could not verify. Refusing there would make a module a build dependency of the main repo,
which is the coupling this whole split removes.

## 3. Images

**A figure is never copied into a wiki.** A relative image link becomes a raw-content URL into the
repository that holds the file:

```
_docs/context/machine.md    ![The machine](../images/Machine_Overview.png)
                                        ↓
wiki/Machine.md   ![The machine](https://raw.githubusercontent.com/Preliy/DT_PSA_OPCV/master/_docs/images/Machine_Overview.png)
```

The figure then exists in exactly one place, a re-rendered screenshot is live in the wiki the moment
it is pushed with no wiki build at all, and no wiki carries a duplicate of the figure set that can go
stale between publishes.

The file is still **resolved on disk and the build still refuses when it is missing** — that check is
the whole value, and it is unaffected by where the published URL points. Only `github.com` URLs can
be spelled; any other host is a refusal rather than a guess.

This depends on the source repository being public, which this one is by design.

## 4. Page rendering

Each page is the source file with three changes, in this order:

1. **Provenance comments stripped.** `<!-- GENERATED … -->` and `<!-- Source(s): … -->` are for
   someone editing the repository, not for a wiki reader.
2. **Links rewritten**, per *Links* above.
3. **A banner inserted under the H1** — under, so the page still opens with its title:

   > This page is **generated from …**. Published from [`_docs/context/fg-01.md`](…) in the
   > … repository — **edit it there, not here.** Changes made in the wiki are overwritten on the
   > next sync.

Every source link in a banner names **the repository the build is running in**. A wiki is built from
one repository now, so there is no other repository it could name.

## 5. Sidebar and footer

`_Sidebar.md` groups pages into sections, in reading order:

| Repository | Sections |
|---|---|
| main | Getting started · The machine · Behaviour · Device types |
| module | Getting started · The machine · Reference · Device types |

The sidebar ends with a **link to every sibling wiki**, from the declared list — so a reader who
lands on the machine can reach the platform, and back. That block is the only place a wiki mentions
another repository's wiki as a whole.

`_Footer.md` names the source repository, the builder, and the page count.

## 6. Sweeping and publishing

**`_wiki/` is generated.** Anything in it the current run did not write is deleted and the deletion
reported. Never hand-edit a page there; fix the source it was rendered from.

**Sweep before writing, not after.** On a case-insensitive filesystem, overwriting an existing file
keeps its *old* spelling — so a page whose name changed only in case is written to the old name, and
a sweep that runs afterwards sees a name it did not render and deletes the page it was just told to
publish. This is not hypothetical: it silently dropped `Connecting-A-Control-System` on the first
build after the rename. Deleting first is correct on both kinds of filesystem.

**Publishing is a separate, deliberate act.** A build writes `_wiki/` and stops. The publisher
rebuilds from scratch — whatever is on disk may be stale or from another branch — refuses on an
uncommitted or unpushed working tree, because every banner links to a committed path, then
**mirrors**: a file the wiki has and `_wiki/` does not is deleted, so a removed page does not stay
published forever. A dry run is the default; `--publish` pushes.

The publish target is the checkout's **actual** `origin`, not the declared repository URL — it is a
real push and has to go where this checkout points. Generated links use the declared URL. The two
differ only while a repository rename is pending, and the publisher says so when they do.

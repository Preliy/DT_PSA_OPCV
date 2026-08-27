#!/usr/bin/env python3
"""Which vendor module version pairs with this main repo, and what is actually here.

Reads  _workflow/config/modules.json             what exists, and what pairs
       <Module>/module.json                      what version is here
       <Module>/_workflow/config/handoff/*.json  which machine it was built against
       _docs/context/.machine.json               the machine it should be built against
Writes the marked region in README.md and COMPATIBILITY.md

Run from the repo root:  python _workflow/tools/build_compatibility.py [--check]

WHY THIS EXISTS. A vendor module is a separate repository the user clones into this
repo's root, and that path is gitignored - so git records nothing about which vendor
version belongs with which main-repo version. A submodule would have pinned it with a
commit sha. This table is that pin, computed instead from two things that are
committed and checkable: the version the module declares, and the sha256 of the
machine handoff it was last synced with.

That makes the table load-bearing rather than decorative. It is the only mechanism
that can catch a stale module, so it must never quietly omit a row - a module that is
declared but not cloned keeps its row and says how to clone it, because that is the
most useful row a new reader can see.

ONLY A SCHEMA MISMATCH IS FATAL. A module a version behind still builds and still
documents a real machine, just an older one; saying so loudly is the right answer. A
schema mismatch is different - the fields the module reads may have moved, so there is
nothing safe for it to build, and its own generator already refuses.

WHY IT IS PUBLIC. The line is what a tool READS. This one reads four tracked files and
writes two more; it touches no Unity export, probes no Editor and digests no vendor
project. It lived in _private/ only by habit, and being there meant the table it writes
could not be regenerated or even checked by anyone but a maintainer.

IT READS THE MODULES ON DISK. That is the difference between this tool and
check_compatibility.py beside it, which asks each module's own repository over https.
This one describes YOUR checkout - which modules you cloned, at what version, synced
against which machine - and that is what makes the table useful to the person running
it. It is also why it cannot run in CI, where no module is ever cloned: every row would
read "not cloned" and the table would be rewritten to say nothing.

NOTHING IT PRINTS INTO A PAGE MAY NAME A PRIVATE TOOL. README.md and COMPATIBILITY.md
are addressed to a reader who has only this repository. A note telling them to run
something out of _private/ is an instruction they cannot follow, and it is generated
text, so nobody reviews it before it lands.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modules as mod  # noqa: E402

ROOT = mod.ROOT
BEGIN = "<!-- BEGIN GENERATED - do not edit between the markers. -->"
END = "<!-- END GENERATED -->"

TARGETS = [ROOT / "README.md", ROOT / "COMPATIBILITY.md"]


class Fail(Exception):
    """A refusal. Nothing is written."""


# --------------------------------------------------------------------- the verdicts


def assess(name, info, ref):
    """Everything known about one declared module, and what it adds up to."""
    row = {"name": name, "url": info["url"], "requires": info.get("requires", ""),
           "tested": info.get("tested", ""), "platform": info.get("platform", ""),
           "present": mod.is_present(name, ROOT), "version": None, "source": None,
           "gitTag": None, "notes": [], "verdict": "", "fatal": False}

    if not row["present"]:
        row["verdict"] = "not cloned"
        return row

    ident = mod.module_identity(name, ROOT)
    row.update({k: ident[k] for k in ("version", "source", "gitTag")})
    if ident["mismatch"]:
        row["notes"].append(ident["mismatch"])
    if row["version"] is None:
        row["notes"].append("no module.json and no git tag - version unknown")

    ok = mod.satisfies(row["version"], row["requires"])
    if ok is False:
        row["notes"].append(f"version {row['version']} does not satisfy "
                            f"{row['requires']}")

    hand = mod.handoff_state(name, ROOT)
    row["handoff"] = hand

    if hand["status"] == "opted-out":
        row["verdict"] = "no handoff"
    elif hand["status"] == "missing":
        row["verdict"] = "handoff never synced"
        # Deliberately no command. This note is spliced into COMPATIBILITY.md, which is
        # read by people who have only this repository; the sync tool is a maintainer's.
        row["notes"].append("no machine snapshot committed yet - see "
                            "'Re-syncing a module' below")
    elif hand["status"] == "unreadable":
        row["verdict"] = "handoff unreadable"
    elif ref and hand["schema"] != ref["schema"]:
        row["verdict"] = (f"schema {hand['schema']} vs {ref['schema']} - "
                          f"this module refuses to build")
        row["fatal"] = True
    elif ref and hand["sha256"] != ref["sha256"]:
        row["verdict"] = f"behind - synced from {hand['exportCommit'] or '?'}"
    elif ref:
        row["verdict"] = "current"
    else:
        row["verdict"] = "no machine export to compare against"

    if ok is False and not row["fatal"]:
        row["verdict"] += ", version out of range"
    return row


# ---------------------------------------------------------------------- the tables


def _v(row):
    if not row["present"]:
        return "—"
    return row["version"] or "unknown"


def readme_table(rows):
    out = ["| Module | Platform | Version | Status |", "|---|---|---|---|"]
    for r in rows:
        if r["present"]:
            status = r["verdict"]
        else:
            status = f"not cloned — `git clone {r['url']} {r['name']}`"
        out.append(f"| [{r['name']}]({r['url']}) | {r['platform'] or '—'} "
                   f"| {_v(r)} | {status} |")
    return out


def compat_table(rows, ref):
    out = ["| Module | Version | Source | Requires | Tested | Handoff | Verdict |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        hand = r.get("handoff") or {}
        if not r["present"]:
            h = "—"
        elif hand.get("status") == "opted-out":
            h = "not a consumer"
        elif hand.get("status") == "ok":
            h = f"schema {hand['schema']}, export `{hand['exportCommit'] or '?'}`"
        else:
            h = hand.get("status", "?")
        out.append(f"| [{r['name']}]({r['url']}) | {_v(r)} | {r['source'] or '—'} "
                   f"| `{r['requires']}` | {r['tested'] or '—'} | {h} | {r['verdict']} |")
    out.append("")
    if ref:
        out += [
            f"**This main repository carries** machine handoff schema `{ref['schema']}`, "
            f"export `{ref['exportCommit']}`, exported `{ref['exportedAtUtc']}`.",
            "",
            "Every verdict above is computed against that line. Without it the table "
            "could not be checked, only believed.",
        ]
    else:
        # No command here either, for the same reason: the machine description is built
        # by a maintainer's generator, and this line lands in a public page.
        out += ["_No `_docs/context/.machine.json` yet - the machine description has "
                "not been generated, so there is nothing to check a module against._"]
    notes = [(r["name"], n) for r in rows for n in r["notes"]]
    if notes:
        out += ["", "**Notes**", ""]
        out += [f"- **{n}** — {t}" for n, t in notes]
    return out


# ------------------------------------------------------------------------- writing


def splice(path, body):
    """Replace the marked region. Refuses rather than appending."""
    if not path.exists():
        raise Fail(f"{path.name} does not exist. This tool fills in a marked region; "
                   f"it does not create the page around it.")
    text = path.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise Fail(
            f"{path.name} must contain the generated markers exactly once each:\n"
            f"  {BEGIN}\n  {END}\n"
            f"Found {text.count(BEGIN)} begin and {text.count(END)} end. Refusing "
            f"rather than appending a second table nobody asked for.")
    start, stop = text.index(BEGIN), text.index(END)
    if stop < start:
        raise Fail(f"{path.name}: the END marker comes before the BEGIN marker.")
    new = text[:start] + BEGIN + "\n" + "\n".join(body).rstrip() + "\n" + text[stop:]
    return new, new != text


def main():
    check_only = "--check" in sys.argv
    declared = mod.declared_modules(ROOT)
    ref = mod.reference_machine(ROOT)
    rows = [assess(name, info, ref) for name, info in declared.items()]

    # A run with nothing cloned would rewrite both tables to say "not cloned" for every
    # module and then report them as drifted. That is a true statement about this
    # working copy and a useless one to commit, so refuse instead - it is always either
    # a checkout that has not cloned a module yet, or CI, which never will.
    if declared and not any(r["present"] for r in rows):
        raise Fail(
            "no declared module is cloned here, so every row would read 'not cloned' "
            "and the committed tables would lose everything they say. This tool "
            "describes the modules on disk; clone at least one, or use "
            "`python _workflow/tools/check_compatibility.py`, which asks each module's "
            "own repository instead and needs nothing cloned.")

    bodies = {ROOT / "README.md": readme_table(rows),
              ROOT / "COMPATIBILITY.md": compat_table(rows, ref)}

    drifted = []
    for path, body in bodies.items():
        new, changed = splice(path, body)
        if changed:
            drifted.append(path.name)
        if not check_only:
            path.write_text(new, encoding="utf-8")

    for r in rows:
        print(f"  {r['name']}: {_v(r)} - {r['verdict']}")
        for n in r["notes"]:
            print(f"      {n}")

    for name in mod.undeclared_dirs(ROOT):
        print(f"  {name}/ looks like a vendor module but is not in modules.json - "
              f"no tool will look at it")

    fatal = [r["name"] for r in rows if r["fatal"]]
    if fatal:
        print(f"\nINCOMPATIBLE: {', '.join(fatal)} cannot build against this machine "
              f"export. Re-sync the handoff and rebuild that module.", file=sys.stderr)

    if check_only:
        if drifted:
            print(f"REFUSED: {', '.join(drifted)} is out of date - run "
                  f"`python _workflow/tools/build_compatibility.py`", file=sys.stderr)
            return 1
        print("compatibility tables are current")
        return 1 if fatal else 0

    print(f"\n{'updated ' + ', '.join(drifted) if drifted else 'already current'}")
    return 1 if fatal else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Fail, mod.ModuleError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        sys.exit(1)

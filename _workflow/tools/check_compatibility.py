#!/usr/bin/env python3
"""Which vendor module version pairs with this twin, and is each one still current?

Reads  _workflow/config/modules.json    which modules exist, and the version each was tested at
       package.json                     this repository's own version
       _docs/context/.machine.json      the machine every module's snapshot is compared against
       a module's module.json           its version - from your checkout, or over https
       a module's _workflow/config/handoff/  the machine snapshot it was built against
Writes the marked region in COMPATIBILITY.md, with --write

    python _workflow/tools/check_compatibility.py            report, always exit 0
    python _workflow/tools/check_compatibility.py --strict    exit 1 on any mismatch
    python _workflow/tools/check_compatibility.py --write     refresh the table
    python _workflow/tools/check_compatibility.py --check     exit 1 if the table is stale
    python _workflow/tools/check_compatibility.py --json      machine-readable

ONE TOOL, ON PURPOSE. This used to be two - one reading the modules on disk to write the
tables, one fetching them over https for CI - and they answered the same question about
two different copies, so COMPATIBILITY.md needed a section explaining that they could
disagree and which to believe. That section was a symptom. There is now one tool and one
rule: READ THE MODULE FROM DISK IF IT IS CLONED, OTHERWISE FETCH IT. A maintainer gets
the truth about their checkout, CI - which clones nothing, ever - gets the published
truth, and each row says which it was.

WHAT THE PAIRING IS MADE OF. Two things, and only one of them is written by hand:

    tested        modules.json    the module version this twin was verified against.
                                  A fact, not a promise - it is the version to clone.
    the handoff   derived         each module commits a byte-identical copy of this
                                  repo's _docs/context/.machine.json. Comparing the two
                                  sha256s answers "was this module built against the
                                  machine as it is now" exactly, and nobody maintains it.

There are deliberately NO VERSION RANGES. `requires` here and `requiresMain` in a module
used to state the pairing from both sides and both were checked; neither ever fired,
because a range admits versions that do not exist yet and so gets written wide once and
never narrowed. The handoff already answers the sharp question, and the schema below
already refuses the one case that is genuinely fatal.

WHAT COUNTS AS A MISMATCH

    schema N vs M           the module's snapshot is a different format - its own build
                            refuses, because fields it reads may have moved. FATAL.
    handoff never synced    the module opted in but has no snapshot committed yet
    behind                  same schema, older export - it describes a machine that moved

A 404 on the handoff is `not a consumer`, not a fault: a module that does not build
documentation from the machine description has no reason to carry a copy of it.

STRICT IS FOR THE BADGE, NOT FOR THE GATE. Default is report-and-exit-0 because this
repository is master for the machine: a module being behind is a fact about somebody
else's repository, it cannot be fixed by a change here, and failing a pull request or a
release over it would block work that is perfectly valid. --strict exists so the
scheduled and master runs can go red and turn the README badge red with them, which is
the only place the state is ever surfaced to a reader.

WHY IT IS IN _workflow/ AND NOT _private/. The line is what a tool READS. This one reads
three tracked files and a few public URLs. It touches no Unity export, probes no Editor
and digests no vendor project, so publishing it discloses nothing - and a check CI cannot
run is not a check.

NOTHING IT PRINTS INTO A PAGE MAY NAME A PRIVATE TOOL. COMPATIBILITY.md is addressed to a
reader who has only this repository. A note telling them to run something out of
_private/ is an instruction they cannot follow, in generated text nobody reviews.

README.md IS NOT WRITTEN. Its platform table is hand-written (Done / Work in progress) and
links here for the pairing; the landing page states intent, this tool states the facts.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modules as mod                                              # noqa: E402

ROOT = mod.ROOT

# The files a module publishes about its own side of the pairing.
MODULE_JSON = "module.json"
HANDOFF_JSON = f"{mod.HANDOFF_REL}/.machine.json"
# The sidecar sync_machine.py writes beside the snapshot. It carries mainVersion - the
# pairing itself - and doubles as the opt-in marker: on disk, wants_handoff() answers that
# by looking for the directory, and a directory is not a thing raw.githubusercontent.com
# can be asked about. Reading the sidecar is how the same question gets asked over https.
HANDOFF_META = f"{mod.HANDOFF_REL}/.handoff.json"

BEGIN = "<!-- BEGIN GENERATED - do not edit between the markers. -->"
END = "<!-- END GENERATED -->"

# Verdicts that mean the pairing is broken, worst first. Kept as one ordered list so that
# --strict and the summary cannot drift apart - the exit code and the text a reader sees
# come from the same place - and so that a module failing two checks at once reports the
# more serious one.
SEVERITY = ["schema mismatch", "handoff never synced", "behind"]
BAD = set(SEVERITY)

# Verdicts that mean nothing was learned. NOT in BAD, because a module that is not
# published yet is the normal state before the first release and must not turn the badge
# red on day one - but they are annotated, because "not published" is also what a
# repository that was renamed, deleted or made private looks like, and a check that goes
# quiet in exactly that case is the staleness it exists to catch.
UNKNOWN = {"not published", "unreachable"}


class Fail(Exception):
    """A refusal. Nothing is written."""


def _worse(current, candidate):
    """The more serious of two verdicts. Anything outside SEVERITY loses to anything in it."""
    if current is None:
        return candidate
    rank = {v: i for i, v in enumerate(SEVERITY)}
    return min(current, candidate, key=lambda v: rank.get(v, len(SEVERITY)))


def _first_difference(handoff, reference):
    """A short phrase naming what actually moved, or "" if nothing obvious did.

    The hash says two snapshots differ; it cannot say why, and "behind" with no reason
    attached is the kind of finding people learn to ignore. The per-scene export stamps
    are almost always the answer, because re-exporting one scene is the usual way a
    module falls behind - and they are the field the top-level ones fail to reflect.
    """
    theirs = {s.get("name"): s.get("exportedAtUtc")
              for s in (handoff.get("scenes") or []) if isinstance(s, dict)}
    ours = reference.get("scenes") or {}
    moved = [n for n in sorted(set(ours) | set(theirs)) if ours.get(n) != theirs.get(n)]
    if not moved:
        return ""
    if len(moved) == 1:
        n = moved[0]
        return (f"scene `{n}` was re-exported "
                f"({theirs.get(n) or 'absent'} → {ours.get(n) or 'absent'})")
    return f"{len(moved)} scenes were re-exported: {', '.join(f'`{n}`' for n in moved)}"


# ------------------------------------------------------------------ reading one module
#
# Two readers, one shape. Both return the same dict so assess() below has a single code
# path and cannot end up checking a local module differently from a published one.


def _blank(name, info):
    return {"name": name, "url": info["url"], "ref": mod.module_ref(info),
            "platform": info.get("platform") or "", "tested": info.get("tested"),
            "read": None, "version": None, "handoff": None, "schema": None,
            "sha256": None, "exportCommit": None, "mainVersion": None,
            "machine": {}, "verdict": None, "notes": []}


def read_local(name, info):
    """From the checkout. What the person running this actually has."""
    row = _blank(name, info)
    row["read"] = "local checkout"
    ident = mod.module_identity(name, ROOT)
    row["version"] = ident["version"]
    if ident["mismatch"]:
        row["notes"].append(ident["mismatch"])

    st = mod.handoff_state(name, ROOT)
    if st["status"] == "opted-out":
        row["handoff"] = "not a consumer"
        return row
    if st["status"] == "missing":
        row["handoff"] = "never synced"
        row["verdict"] = "handoff never synced"
        # Deliberately no command: this note is spliced into COMPATIBILITY.md, which is
        # read by people who have only this repository, and the sync tool is a
        # maintainer's.
        row["notes"].append("no machine snapshot committed yet - see "
                            "'Re-syncing a module' in COMPATIBILITY.md")
        return row
    if st["status"] != "ok":
        row["handoff"] = st["status"]
        row["notes"].append(f"{HANDOFF_JSON} could not be read")
        return row

    row.update({k: st[k] for k in ("schema", "sha256", "exportCommit", "mainVersion")})
    p = mod.handoff_dir(name, ROOT) / ".machine.json"
    try:
        row["machine"] = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        row["machine"] = {}
    return row


def read_published(name, info):
    """From the module's own repository over https. What CI and every reader see."""
    row = _blank(name, info)
    row["read"] = "published"

    try:
        mj_url = mod.raw_url(info["url"], row["ref"], MODULE_JSON)
    except mod.NotGitHub as e:
        row["verdict"] = "unreachable"
        row["notes"].append(str(e))
        return row

    got = mod.fetch_json(mj_url)
    if got["status"] != "ok":
        # A 404 here cannot tell three things apart, and raw.githubusercontent.com gives
        # no way to: the repository does not exist yet, it exists but is private, or it
        # exists and simply has no module.json on this branch. Say what was observed
        # rather than picking one - and note all three, because before the first release
        # the first is normal and afterwards the second is a rename nobody announced.
        row["verdict"] = "unreachable" if got["status"] == "unreachable" else "not published"
        if got["status"] == "missing":
            row["notes"].append(
                f"nothing at {mj_url} — the repository does not exist yet, is private, or "
                f"has no {MODULE_JSON} on branch `{row['ref']}`")
        else:
            row["notes"].append(f"{MODULE_JSON}: {got['detail']}")
        # Not a mismatch. Nothing was learned about the module, and reporting a state we
        # did not observe is worse than reporting that we could not observe it.
        return row

    row["version"] = str((got["data"] or {}).get("version") or "") or None

    hs = mod.fetch_json(mod.raw_url(info["url"], row["ref"], HANDOFF_JSON))
    meta = mod.fetch_json(mod.raw_url(info["url"], row["ref"], HANDOFF_META))
    if meta["status"] == "ok":
        row["mainVersion"] = (meta["data"] or {}).get("mainVersion")

    if hs["status"] == "missing":
        # A 404 on the snapshot alone cannot say whether the module opted out or opted in
        # and never synced, and the difference matters: the first is a module that has no
        # reason to carry the machine description, the second is one whose documentation
        # is built from a snapshot that does not exist. The sidecar tells them apart.
        if meta["status"] == "ok":
            row["handoff"] = "never synced"
            row["verdict"] = "handoff never synced"
            row["notes"].append(
                f"the module has {HANDOFF_META} but no .machine.json beside it — it opted "
                f"in to the machine handoff and has no snapshot committed")
        else:
            row["handoff"] = "not a consumer"
        return row
    if hs["status"] != "ok":
        row["handoff"] = "unreachable"
        row["notes"].append(f"{HANDOFF_JSON}: {hs['detail']}")
        return row

    row["machine"] = hs["data"] or {}
    row["schema"] = row["machine"].get("schema")
    row["exportCommit"] = row["machine"].get("exportCommit")
    # The bytes as received, not a re-serialisation of them.
    row["sha256"] = mod.sha256_bytes(hs.get("raw"))
    return row


def assess(name, info, reference):
    """One module's row. Never raises; every failure becomes a verdict."""
    row = read_local(name, info) if mod.is_present(name, ROOT) else read_published(name, info)

    if row["version"] is None and row["verdict"] is None:
        row["notes"].append("no version could be read from module.json")
    # A module at a version other than the one this twin was verified against still
    # works far more often than not, so this is a note and never a verdict. The handoff
    # below is what actually decides whether it is current.
    if row["version"] and row["tested"] and row["version"] != row["tested"]:
        row["notes"].append(
            f"module is {row['version']}, this twin was tested against {row['tested']}")

    if row["verdict"] is not None:
        return row
    # No snapshot to compare, for a reason that is not a fault. Say the reason - calling
    # a module with no handoff "current" would claim it was checked against this machine
    # when nothing was compared at all.
    if row["handoff"] == "not a consumer":
        row["verdict"] = "not a consumer"
        return row
    if row["handoff"] == "unreachable":
        row["verdict"] = "unreachable"
        return row

    if not reference:
        row["handoff"] = f"schema {row['schema']}, export `{row['exportCommit']}`"
        row["verdict"] = "no machine export to compare against"
        row["notes"].append("this repository has no _docs/context/.machine.json to "
                            "compare against")
        return row

    # Schema first: a different format means the fields the module reads may have moved,
    # and nothing below it is worth comparing.
    if row["schema"] != reference["schema"]:
        row["verdict"] = _worse(row["verdict"], "schema mismatch")
        row["handoff"] = f"schema {row['schema']} vs {reference['schema']}"
        row["notes"].append(
            f"module built against schema {row['schema']}, this repo carries "
            f"{reference['schema']} - the structure format changed, so this module's "
            f"own build refuses rather than guessing")
        return row

    row["handoff"] = f"schema {row['schema']}, export `{row['exportCommit']}`"

    # Compare the CONTENT, normalised for line endings - not exportCommit.
    #
    # exportCommit looks like the right field and is not: re-exporting one scene updates
    # that scene's entry and leaves exportCommit and the top-level exportedAtUtc alone, so
    # a module can be a whole export behind while both top-level fields match exactly.
    # That happened here - a Siemens re-export on 2026-08-26 shipped under exportCommit
    # `5010e82 2026-08-23` - and a check built on those fields reports a stale module as
    # current, which is the one failure this tool exists to prevent.
    #
    # The hash normalises CRLF first (see modules.sha256_bytes), so it compares a local
    # working tree against a blob served over https without answering differently
    # depending on which platform did the checkout.
    if row["sha256"] != reference["sha256"]:
        row["verdict"] = _worse(row["verdict"], "behind")
        detail = _first_difference(row["machine"], reference)
        row["notes"].append(
            f"module's machine snapshot differs from this repo's"
            + (f" — {detail}" if detail else "")
            + f" (module export `{row['exportCommit']}`, this repo "
              f"`{reference['exportCommit']}`)")
    else:
        row["verdict"] = "current"
    return row


# ---------------------------------------------------------------------------- the tables


def _built_against(r):
    """What twin this module was built against - the pairing, as one cell."""
    if r["handoff"] in (None, "not a consumer", "never synced", "unreachable"):
        return "—"
    if r["mainVersion"]:
        return f"main {r['mainVersion']} (export `{r['exportCommit']}`)"
    # No mainVersion: a snapshot synced before the field existed, or from a main repo
    # that had no version yet. The export is still a real pin, so say that instead of
    # inventing a version.
    return f"export `{r['exportCommit']}`"


def compat_table(rows, main, reference):
    out = ["| Module | Platform | Version | Tested | Built against | Verdict |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| [{r['name']}]({r['url']}) | {r['platform'] or '—'} "
                   f"| {r['version'] or '—'} | {r['tested'] or '—'} "
                   f"| {_built_against(r)} | {r['verdict']} |")
    out.append("")

    v = main["version"] or "unreleased"
    line = f"**This twin is** `{v}`"
    if reference:
        line += (f", carrying machine schema `{reference['schema']}`, "
                 f"export `{reference['exportCommit']}`")
    out.append(line + ".")
    if main["mismatch"]:
        out += ["", f"> {main['mismatch']}"]

    local = [r["name"] for r in rows if r["read"] == "local checkout"]
    if local:
        out += ["", f"_{', '.join(local)} — read from the local checkout rather than the "
                    f"published repository, so unpushed work is included._"]

    notes = [(r["name"], n) for r in rows for n in r["notes"]]
    if notes:
        out += ["", "**Notes**", ""]
        out += [f"- **{name}** — {n}" for name, n in notes]
    return out


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


def render(rows, main, reference):
    """The report, as Markdown. Written to stdout and to the job summary alike."""
    return "\n".join(compat_table(rows, main, reference))


def main(argv):
    strict = "--strict" in argv
    as_json = "--json" in argv
    write = "--write" in argv
    check = "--check" in argv

    try:
        declared = mod.declared_modules(ROOT)
    except mod.ModuleError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1                       # a broken declaration IS this repository's fault

    identity = mod.main_version(ROOT)
    reference = mod.reference_machine(ROOT)
    rows = [assess(n, i, reference) for n, i in declared.items()]

    if as_json:
        print(json.dumps({"main": identity,
                          "reference": {k: v for k, v in (reference or {}).items()
                                        if k != "path"},
                          "modules": rows}, indent=2))
        return 0

    report = render(rows, identity, reference)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Vendor compatibility\n\n" + report + "\n")
    # One annotation per module that is either broken or unknown, so the state is
    # visible on the run page without opening the log.
    for r in rows:
        if r["verdict"] in BAD or r["verdict"] in UNKNOWN:
            print(f"::warning title={r['name']} {r['verdict']}::" + "; ".join(r["notes"]))

    drifted = []
    if write or check:
        # A run where nothing was learned about any module would rewrite the table to
        # say "not published" everywhere and throw away everything they currently say.
        # That is a true statement about this run and a useless one to commit, so refuse
        # - it means no module is cloned AND none is reachable, which is CI, or an
        # offline checkout, and neither should be writing a tracked page.
        if declared and all(r["verdict"] in UNKNOWN for r in rows):
            raise Fail(
                "nothing was learned about any declared module - every row would read "
                "'not published' and the committed tables would lose everything they "
                "say. Clone a module, or run this where the module repositories are "
                "reachable.")
        bodies = {ROOT / "COMPATIBILITY.md": compat_table(rows, identity, reference)}
        for path, body in bodies.items():
            new, changed = splice(path, body)
            if changed:
                drifted.append(path.name)
            if write:
                path.write_text(new, encoding="utf-8")
        print(f"\n{('updated ' + ', '.join(drifted)) if drifted else 'tables already current'}"
              if write else
              f"\n{('STALE: ' + ', '.join(drifted)) if drifted else 'tables are current'}")

    for name in mod.undeclared_dirs(ROOT):
        print(f"  {name}/ looks like a vendor module but is not in modules.json - "
              f"no tool will look at it")

    if check and drifted:
        print(f"REFUSED: run `python _workflow/tools/check_compatibility.py --write`",
              file=sys.stderr)
        return 1

    broken = [r["name"] for r in rows if r["verdict"] in BAD]
    if broken and strict:
        print(f"\nnot compatible: {', '.join(broken)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (Fail, mod.ModuleError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        raise SystemExit(1)

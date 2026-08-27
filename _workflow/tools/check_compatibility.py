#!/usr/bin/env python3
"""Does each declared vendor module still pair with this twin?

Reads  _workflow/config/modules.json    which modules exist, and the version range each must be in
       package.json                     this repository's own version
       _docs/context/.machine.json      the machine every module's snapshot is compared against
       <module repo>/module.json                            over https
       <module repo>/_workflow/config/handoff/.machine.json  over https

    python _workflow/tools/check_compatibility.py            report, always exit 0
    python _workflow/tools/check_compatibility.py --strict    exit 1 on any mismatch
    python _workflow/tools/check_compatibility.py --json      machine-readable

WHY IT FETCHES RATHER THAN READS. A vendor module is a separate repository, gitignored
here and optional - CI has none of them on disk and never will, because cloning them
would make an optional repository a hard dependency of this repository's checks. So the
two files that carry a module's side of the pairing are fetched from its own repository
at the branch modules.json names. That needs no token, no submodule and no clone.

WHY IT IS IN _workflow/ AND NOT _private/. The line is what a tool READS. This one reads
three tracked files and two public URLs. It touches no Unity export, probes no Editor and
digests no vendor project, so publishing it discloses nothing - and a check CI cannot run
is not a check.

WHAT COUNTS AS A MISMATCH

    version out of range    the module's version fails modules.json `requires`, or this
                            repo's version fails the module's `requiresMain`
    schema N vs M           the module's committed machine snapshot is a different format
    behind                  same schema, older export - it describes a machine that moved
    handoff never synced    the module opted in but has no snapshot committed yet

A 404 on the handoff is `not a consumer`, not a fault: a module that does not build
documentation from the machine description has no reason to carry a copy of it.

STRICT IS FOR THE BADGE, NOT FOR THE GATE. Default is report-and-exit-0 because this
repository is master for the machine: a module being behind is a fact about somebody
else's repository, it cannot be fixed by a change here, and failing a pull request or a
release over it would block work that is perfectly valid. --strict exists so the
scheduled and master runs can go red and turn the README badge red with them, which is
the only place the state is ever surfaced to a reader.
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
# The sidecar sync_machine.py writes beside the snapshot. It is the opt-in marker: on
# disk, wants_handoff() answers this by looking for the directory, and a directory is not
# a thing raw.githubusercontent.com can be asked about. Reading the sidecar is how the
# same question gets asked over https.
HANDOFF_META = f"{mod.HANDOFF_REL}/.handoff.json"

# Verdicts that mean the pairing is broken, worst first. Kept as one ordered list so that
# --strict and the summary cannot drift apart - the exit code and the text a reader sees
# come from the same place - and so that a module failing two checks at once reports the
# more serious one. A module that is both out of range and behind is out of range; saying
# "behind" there understates it, and "behind" is the check that happens to run last.
SEVERITY = ["schema mismatch", "version out of range", "handoff never synced", "behind"]
BAD = set(SEVERITY)

# Verdicts that mean nothing was learned. NOT in BAD, because a module that is not
# published yet is the normal state before the first release and must not turn the badge
# red on day one - but they are annotated, because "not published" is also what a
# repository that was renamed, deleted or made private looks like, and a check that goes
# quiet in exactly that case is the staleness it exists to catch.
UNKNOWN = {"not published", "unreachable"}


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


def check_module(name, info, main, reference):
    """One module's row. Never raises; every failure becomes a verdict."""
    row = {"name": name, "url": info["url"], "ref": mod.module_ref(info),
           "platform": info.get("platform") or "", "requires": info.get("requires"),
           "tested": info.get("tested"), "version": None, "requiresMain": None,
           "handoff": None, "verdict": None, "notes": []}

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

    raw = got["data"] or {}
    row["version"] = str(raw.get("version") or "") or None
    row["requiresMain"] = raw.get("requiresMain")

    # --- the two version ranges, checked in both directions -------------------------
    if row["version"] is None:
        row["notes"].append("module.json declares no version")
    elif mod.satisfies(row["version"], info["requires"]) is False:
        row["verdict"] = _worse(row["verdict"], "version out of range")
        row["notes"].append(
            f"module is {row['version']}, this repo admits `{info['requires']}`")

    if row["requiresMain"] and main["version"]:
        if mod.satisfies(main["version"], row["requiresMain"]) is False:
            row["verdict"] = _worse(row["verdict"], "version out of range")
            row["notes"].append(
                f"this repo is {main['version']}, the module admits `{row['requiresMain']}`")
    elif row["requiresMain"] and not main["version"]:
        row["notes"].append(
            f"module requires main `{row['requiresMain']}`, but this repository has no "
            f"version yet - no tag and package.json still holds the placeholder")

    # --- the machine snapshot -------------------------------------------------------
    hs = mod.fetch_json(mod.raw_url(info["url"], row["ref"], HANDOFF_JSON))
    if hs["status"] == "missing":
        # A 404 on the snapshot alone cannot say whether the module opted out or opted in
        # and never synced, and the difference matters: the first is a module that has no
        # reason to carry the machine description, the second is one whose documentation
        # is built from a snapshot that does not exist. The sidecar tells them apart, and
        # is only fetched here, in the one case where the answer is ambiguous.
        meta = mod.fetch_json(mod.raw_url(info["url"], row["ref"], HANDOFF_META))
        if meta["status"] == "ok":
            row["verdict"] = _worse(row["verdict"], "handoff never synced")
            row["handoff"] = "never synced"
            row["notes"].append(
                f"the module has {HANDOFF_META} but no .machine.json beside it — it opted "
                f"in to the machine handoff and has no snapshot committed")
        else:
            row["handoff"] = "not a consumer"
    elif hs["status"] != "ok":
        row["handoff"] = "unreachable"
        row["notes"].append(f"{HANDOFF_JSON}: {hs['detail']}")
    else:
        h = hs["data"] or {}
        row["handoff"] = f"schema {h.get('schema')}, export `{h.get('exportCommit')}`"
        if not reference:
            row["notes"].append("this repository has no _docs/context/.machine.json to "
                                "compare against")
        # Schema first: a different format means the fields the module reads may have
        # moved, and nothing below it is worth comparing.
        elif h.get("schema") != reference["schema"]:
            row["verdict"] = _worse(row["verdict"], "schema mismatch")
            row["handoff"] = (f"schema {h.get('schema')} vs {reference['schema']}")
            row["notes"].append(
                f"module built against schema {h.get('schema')}, this repo carries "
                f"{reference['schema']} - the structure format changed")
        # Compare the CONTENT, normalised for line endings - not exportCommit.
        #
        # exportCommit looks like the right field and is not: re-exporting one scene
        # updates that scene's entry and leaves exportCommit and the top-level
        # exportedAtUtc alone, so a module can be a whole export behind while both
        # top-level fields match exactly. That happened here - a Siemens re-export on
        # 2026-08-26 shipped under exportCommit `5010e82 2026-08-23` - and a check built
        # on those fields reports a stale module as current, which is the one failure
        # this tool exists to prevent.
        #
        # The hash normalises CRLF first (see modules.sha256_bytes), so it compares a
        # local working tree against a blob served over https without answering
        # differently depending on which platform did the checkout.
        elif mod.sha256_bytes(hs.get("raw")) != reference["sha256"]:
            row["verdict"] = _worse(row["verdict"], "behind")
            detail = _first_difference(h, reference)
            row["notes"].append(
                f"module's machine snapshot differs from this repo's"
                + (f" — {detail}" if detail else "")
                + f" (module export `{h.get('exportCommit')}`, this repo "
                  f"`{reference['exportCommit']}`)")

    if row["verdict"] is None:
        row["verdict"] = "current"
    return row


def render(rows, main, reference):
    """The report, as Markdown. Written to stdout and to the job summary alike."""
    out = ["| Module | Platform | Version | Requires | Handoff | Verdict |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        out.append("| [{name}]({url}) | {platform} | {version} | `{requires}` | "
                   "{handoff} | {verdict} |".format(
                       name=r["name"], url=r["url"], platform=r["platform"] or "—",
                       version=r["version"] or "—", requires=r["requires"],
                       handoff=r["handoff"] or "—", verdict=r["verdict"]))

    v = main["version"] or "unreleased"
    src = main["source"] or "no version yet"
    line = f"\n**This repository is** `{v}` (from {src})"
    if reference:
        line += (f", carrying machine handoff schema `{reference['schema']}`, "
                 f"export `{reference['exportCommit']}`")
    out.append(line + ".")
    if main["mismatch"]:
        out.append(f"\n> {main['mismatch']}")

    notes = [(r["name"], n) for r in rows for n in r["notes"]]
    if notes:
        out.append("\nNotes:\n")
        out += [f"- **{name}** — {n}" for name, n in notes]
    return "\n".join(out)


def main(argv):
    strict = "--strict" in argv
    as_json = "--json" in argv

    try:
        declared = mod.declared_modules(ROOT)
    except mod.ModuleError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1                       # a broken declaration IS this repository's fault

    identity = mod.main_version(ROOT)
    reference = mod.reference_machine(ROOT)
    rows = [check_module(n, i, identity, reference) for n, i in declared.items()]

    if as_json:
        print(json.dumps({"main": identity,
                          "reference": {k: v for k, v in (reference or {}).items()
                                        if k != "path"},
                          "modules": rows}, indent=2))
    else:
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
                print(f"::warning title={r['name']} {r['verdict']}::"
                      + "; ".join(r["notes"]))

    broken = [r["name"] for r in rows if r["verdict"] in BAD]
    if broken and strict:
        print(f"\nnot compatible: {', '.join(broken)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

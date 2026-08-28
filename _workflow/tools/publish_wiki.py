#!/usr/bin/env python3
"""Publish _wiki/ to the GitHub wiki repository.

Run from the repo root:

    python _workflow/tools/publish_wiki.py             dry run - shows the diff, pushes nothing
    python _workflow/tools/publish_wiki.py --publish   commits and pushes

WHY A DRY RUN BY DEFAULT. Pushing to <repo>.wiki.git publishes to the world in one
step and there is no review between here and a reader. So the default prints exactly
what would change and stops; --publish is a second, deliberate act.

WHY IT REBUILDS. _wiki/ is a gitignored build artifact, so whatever is on disk may be
absent, stale, or left over from another branch. Publishing what happens to be sitting
there is how a wiki comes to describe a machine nobody has.

THIS WIKI IS THIS REPOSITORY'S. It carries _docs/ and nothing else, so it cannot be
incomplete because a vendor module is not cloned - a module publishes its own wiki from
its own repository. This tool used to refuse until every declared module was on disk,
which made an optional repository a hard dependency of publishing; see
_workflow/WIKI-SPEC.md.

WHY IT MIRRORS. Files the wiki has and _wiki/ does not are deleted, not left behind.
A copy that only ever adds leaves deleted pages published forever, still linked from
search results, still wrong.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wiki as bw  # noqa: E402  - local module, same directory
import modules as mod  # noqa: E402  - local module, same directory

ROOT = mod.ROOT
WIKI = ROOT / "_wiki"


class Fail(Exception):
    """A refusal. Nothing is pushed."""


def run(args, cwd, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)
    if check and r.returncode != 0:
        raise Fail(f"`{' '.join(args)}` failed:\n{(r.stderr or r.stdout).strip()}")
    return r.stdout.strip()


# ------------------------------------------------------------------------- the gates


def check_source(allow_dirty):
    """The pages say "Published from <path> in <repo>" - so those paths must exist there."""
    dirty = run(["git", "status", "--porcelain"], ROOT)
    if dirty and not allow_dirty:
        raise Fail(
            "the working tree has uncommitted changes. Every published page carries a "
            "'Published from ...' link to a committed path, so publishing now puts a 404 "
            "in the header of each one. Commit and push first, or pass --allow-dirty if "
            "you know the changed files are not sources.")
    ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"], ROOT, check=False)
    if ahead and ahead != "0" and not allow_dirty:
        raise Fail(
            f"{ahead} commit(s) are not pushed. The wiki would link to source files that "
            f"are not on the remote yet. Push first, or pass --allow-dirty.")
    return bool(dirty)


def rebuild():
    """Build the wiki fresh, and report what it is made of."""
    found = bw.discover()
    r = subprocess.run([sys.executable, str(Path(__file__).parent / "build_wiki.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise Fail(f"the wiki build refused, so there is nothing to publish:\n"
                   f"{(r.stderr or r.stdout).strip()}")
    print(r.stdout.rstrip())
    return found


# ---------------------------------------------------------------------- the mirror


def mirror(src, dst):
    """Make dst's contents identical to src's, leaving dst/.git alone."""
    keep = {".git"}
    for item in dst.iterdir():
        if item.name in keep:
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    for item in src.iterdir():
        target = dst / item.name
        shutil.copytree(item, target) if item.is_dir() else shutil.copyfile(item, target)


def main():
    publish = "--publish" in sys.argv
    allow_dirty = "--allow-dirty" in sys.argv

    # The ACTUAL remote, not the declared published URL. This is a real push: it has to
    # go where this checkout's origin points, whatever modules.json says the project
    # will be called. The two differ on purpose while a rename is pending.
    base = mod.origin_url(ROOT)
    if not base:
        raise Fail("no git remote 'origin', so there is no wiki to publish to.")

    declared = mod.repo_url(ROOT)
    if declared and declared != base:
        print(f"  note: publishing to {base}.wiki.git (this checkout's origin), while "
              f"generated links name {declared} (declared in modules.json). That is the "
              f"expected state while a repository rename is pending.")

    dirty = check_source(allow_dirty)
    found = rebuild()

    tmp = Path(tempfile.mkdtemp(prefix="oc-wiki-"))
    clone = tmp / "wiki"
    try:
        r = subprocess.run(["git", "clone", "--quiet", f"{base}.wiki.git", str(clone)],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            raise Fail(
                f"could not clone {base}.wiki.git:\n{(r.stderr or r.stdout).strip()}\n"
                f"If this wiki has never been used, GitHub has not created the repository "
                f"yet - it cannot be initialised from the command line. Create one page in "
                f"the web UI, then re-run this.")

        branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], clone)
        mirror(WIKI, clone)
        run(["git", "add", "-A"], clone)
        stat = run(["git", "diff", "--cached", "--stat"], clone)

        if not stat:
            print("\nwiki already up to date - nothing to publish")
            return 0

        print(f"\n{'-' * 60}\nchanges against the published wiki ({branch}):\n{stat}")

        if not publish:
            print(f"\nDRY RUN - nothing was pushed.")
            print(f"  staged in {clone}")
            print(f"  publish with: python _workflow/tools/publish_wiki.py --publish")
            return 0

        sha = run(["git", "rev-parse", "--short", "HEAD"], ROOT)
        msg = [f"docs: publish from {sha} ({len(found)} pages)"]
        if dirty:
            msg += ["", "Published from a dirty working tree (--allow-dirty)."]

        run(["git", "commit", "-m", "\n".join(msg)], clone)
        run(["git", "push", "origin", branch], clone)
        print(f"\npublished to {base}/wiki")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Fail, bw.WikiError, mod.ModuleError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        print("Nothing was published.", file=sys.stderr)
        sys.exit(1)

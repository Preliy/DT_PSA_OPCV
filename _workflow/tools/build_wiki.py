#!/usr/bin/env python3
"""Render THIS repository's documentation into _wiki/, ready to push to its GitHub wiki.

Reads  _docs/*.md                   hand-written narrative docs
       _docs/context/**.md          GENERATED machine description
       _docs/reference/*.md         hand-written behaviour contracts
Writes _wiki/*.md, _wiki/_Sidebar.md, _wiki/_Footer.md

Run from the repo root:  python _workflow/tools/build_wiki.py [--check]

WHY THIS EXISTS. A GitHub wiki is a separate git repository with a FLAT page
namespace: there are no directories, and a relative link like ../reference/x.md
resolves to nothing. Meanwhile the documentation in this repo is nested on purpose and
must stay readable in the repo itself. So the docs are written once, nested, and this
tool produces the flat view - rewriting every link and renaming every page.

ONE WIKI PER REPOSITORY. This build covers _docs/ and nothing else. A vendor module is
a separate repository, so it has its own wiki, built and published by its own tooling
from its own _docs/ - see _workflow/WIKI-SPEC.md, which is the contract both sides
implement. This build therefore cannot be incomplete because of what the reader did or
did not clone, and it never reaches into a module's directory except to VERIFY a link
it was going to emit anyway.

IMAGES ARE NEVER COPIED. A figure link becomes a raw.githubusercontent.com URL into
this repository, so the figure exists in exactly one place and a re-rendered screenshot
is live in the wiki the moment it is pushed. The file is still resolved on disk and a
missing one still stops the build.

_wiki/ IS GENERATED. It is swept on every run: a file this tool did not write is
deleted. Edit the source in this repo, never a page in _wiki/.

A LINK THAT CANNOT BE RESOLVED STOPS THE BUILD. In a flat namespace a broken link is
invisible until a reader clicks it, and there is no compiler to catch one. So every
relative link is resolved against the source tree and mapped, and anything left over
is an error rather than a silently dead link.

PUBLISHING IS MANUAL, on purpose. Pushing to <repo>.wiki.git publishes to the world,
so this tool writes _wiki/ and stops. publish_wiki.py is the second, deliberate step.
"""

import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modules as mod  # noqa: E402  - local module, same directory

ROOT = mod.ROOT
OUT = ROOT / "_wiki"
DOCS = ROOT / "_docs"

# Both generators write "GENERATED from ..."; the vendor one also writes "Sources:"
# plural. Match both spellings of each - for want of that `s` every vendor page once
# published a raw HTML comment and pushed its own H1 below the banner, and for want of
# "from" every generated page did the same and lost the word "generated" from its
# banner as well.
GENERATED_COMMENT = re.compile(r"^<!--\s*GENERATED\s+(?:by|from)\b.*?-->\s*$", re.M | re.S)
SOURCE_COMMENT = re.compile(r"^<!--\s*Sources?:.*?-->\s*$", re.M | re.S)
LINK_RE = re.compile(r"(?<!\\)\[(?P<text>[^\]]*)\]\((?P<target>[^)\s]+)(?P<title>\s+\"[^\"]*\")?\)")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


class WikiError(Exception):
    """Something that would publish a broken page. Stops the build."""


# ------------------------------------------------------------------ this repository

# The published URL, DECLARED in modules.json - never probed from `git remote`. A
# generated link must not name whichever machine happened to build it.
SRC_URL = mod.repo_url(ROOT)

# The ref a link into this repository should name. origin/HEAD, not the current branch:
# a published page must point at the ref a reader will actually find the file on, which
# is the repository's default branch - not whichever feature branch built the wiki.
SRC_REF = mod.src_ref(ROOT)

# What _docs/reference/ is called here. "Behaviour" in the main repository, because
# these are machine-level behaviour contracts; "Reference" in a module, whose reference
# pages are framework and wiring notes and are not behaviour at all. Both builders need
# to spell the other's, so this is stated in _workflow/WIKI-SPEC.md, not invented here.
REF_PREFIX = "Behaviour"
REF_SECTION = "Behaviour"

# Home is the repository's landing page. Here that is the introduction, so README.md
# has no page of its own and redirects instead.
OVERRIDES = {
    "_docs/01-introduction.md": "Home",
}

# A source file with no page of its own. A link to one is redirected instead.
ALIASES = {
    "_docs/README.md": "Home",
    "README.md": "Home",
    "CONTRIBUTING.md": None,        # None -> link out to the repo, not into the wiki
}

SECTIONS = ["Getting started", "The machine", REF_SECTION, "Device types"]

DEVICE_DIRS = [DOCS / "context/devices"]


# ------------------------------------------------------------------- page naming
# The rule below is the contract in _workflow/WIKI-SPEC.md. Both this builder and every
# module's implement it, because a cross-repo link is computed by ONE builder using the
# OTHER repository's rule - a divergence produces a dead wiki link that nothing catches.


def _title(stem):
    """fg-01 -> FG_01, plc-io -> PLC-IO, spt-framework -> SPT-Framework."""
    special = {"fg": "FG", "plc": "PLC", "io": "IO", "spt": "SPT", "hmi": "HMI",
               "ads": "ADS", "mil": "MIL", "sil": "SIL", "ui": "UI"}
    parts = [special.get(p.lower(), p.capitalize()) for p in stem.split("-")]
    # FG-01 reads as a group name; FG_01 is how the project spells it everywhere else.
    out = "-".join(parts)
    return re.sub(r"\bFG-(\d\d|System|Transport)\b", r"FG_\1", out)


def _h1_word(path):
    """The first word of a page's H1, or None."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip().split()[0]
    except (OSError, IndexError):
        pass
    return None


def _device_name(stem, device_dirs):
    """A device type's real spelling, taken from the page's own H1.

    The file name is lower-cased by the generator, so capitalising it gives
    'Controlbunker'. The heading carries the type as the twin spells it - which is also
    how it is spelled in every table that links here.

    More than one directory is consulted when naming a page in ANOTHER repository whose
    checkout may be absent: every knowledge base derives its device pages from the same
    .machine.json, so this repo's own page for the same slug answers the same question.
    When both are present and they DISAGREE, that is the two generators having drifted -
    and a silently wrong name is a dead cross-repo link, so it stops the build.
    """
    found = []
    for d in device_dirs:
        name = _h1_word(Path(d) / f"{stem}.md")
        if name:
            found.append((d, name))
    distinct = {n for _, n in found}
    if len(distinct) > 1:
        detail = "; ".join(f"{Path(d).as_posix()} says {n}" for d, n in found)
        raise WikiError(
            f"the device type '{stem}' is spelled differently in two knowledge bases: "
            f"{detail}. Both are generated from the same .machine.json, so this is "
            f"drift - a cross-repo link built from either spelling is dead in one wiki.")
    return found[0][1] if found else _title(stem)


def page_name(rel, ref_prefix=REF_PREFIX, overrides=None, device_dirs=None):
    """The flat wiki page name for a path relative to the repository that owns it."""
    overrides = OVERRIDES if overrides is None else overrides
    device_dirs = DEVICE_DIRS if device_dirs is None else device_dirs
    if rel in overrides:
        return overrides[rel]
    p = PurePosixPath(rel)
    # Hand-written docs are numbered for reading order. The number orders the sidebar;
    # it has no business in the page name.
    stem = _title(re.sub(r"^\d+-", "", p.stem))
    if p.parent.name == "devices":
        return f"Device-{_device_name(p.stem, device_dirs)}"
    if p.parts[:2] == ("_docs", "reference"):
        return f"{ref_prefix}-{stem.replace('-Behaviour', '')}"
    if p.parts[:2] == ("_docs", "context"):
        if p.stem == "machine":
            return "Machine"
        if p.stem == "PROVENANCE":
            return "Machine-Provenance"
        return f"Machine-{stem}"
    return stem


def publishable(rel):
    """Does a repo-relative path get a wiki page at all, under the rule above?

    Used to decide whether a link into ANOTHER repository can be pointed at that
    repository's wiki. _docs/ImageDescription.md and TwinCAT_1/... are real files and
    perfectly good link targets - they are just not pages, so they stay blob URLs.
    """
    p = PurePosixPath(rel)
    if p.suffix != ".md" or not p.parts or p.parts[0] != "_docs":
        return False
    if len(p.parts) == 2:
        return p.stem == "README" or bool(re.match(r"^\d+-", p.stem))
    if len(p.parts) == 3 and p.parts[1] in ("context", "reference"):
        return True
    return len(p.parts) == 4 and p.parts[1:3] == ("context", "devices")


# --------------------------------------------------------------------- discovery


def discover():
    """[(repo-relative source, page name, sidebar section)], in reading order."""
    found = []

    # Globbed, not listed, so adding _docs/06-whatever.md needs no edit here. The
    # leading number is the reading order and is dropped from the page name.
    for name in ("01-introduction.md", "02-setup.md", "03-usage.md", "04-architecture.md"):
        if not (DOCS / name).exists():
            raise WikiError(f"_docs/{name} is missing - the wiki's core narrative pages "
                            f"come from _docs/. Nothing else can stand in for them.")
    for src in sorted(DOCS.glob("[0-9]*.md")):
        rel = f"_docs/{src.name}"
        found.append((rel, page_name(rel), "Getting started"))

    ctx = DOCS / "context"
    for rel in ["_docs/context/machine.md", "_docs/context/plc-symbols.md",
                "_docs/context/PROVENANCE.md"]:
        if (ROOT / rel).exists():
            found.append((rel, page_name(rel), "The machine"))
    for f in sorted(ctx.glob("fg-*.md")):
        rel = f.relative_to(ROOT).as_posix()
        found.append((rel, page_name(rel), "The machine"))
    for f in sorted((ctx / "devices").glob("*.md")):
        rel = f.relative_to(ROOT).as_posix()
        found.append((rel, page_name(rel), "Device types"))

    for f in sorted((DOCS / "reference").glob("*.md")):
        rel = f.relative_to(ROOT).as_posix()
        found.append((rel, page_name(rel), REF_SECTION))

    seen = {}
    for rel, page, _ in found:
        if page in seen:
            raise WikiError(f"two sources want the same wiki page '{page}': "
                            f"{seen[page]} and {rel}. The namespace is flat - add an "
                            f"entry to OVERRIDES to separate them.")
        seen[page] = rel
    return found


# ------------------------------------------------------------------- the siblings


def siblings():
    """{repo URL: info} for every repository whose wiki this one may link into.

    DECLARED in modules.json, never probed from disk. Building this from what happens
    to be cloned would make the emitted links depend on the builder's checkout, which
    is the same rule that governs _docs/context/.

    `knowledgeBase` is the declaration of whether a module publishes documentation
    pages at all; one that does not has no wiki to link into, and its blob URLs are
    left exactly as written.
    """
    out = {}
    try:
        declared = mod.declared_modules(ROOT)
    except mod.ModuleError:
        return out
    for name, info in declared.items():
        if not info.get("knowledgeBase"):
            continue
        url = info["url"].rstrip("/")
        d = ROOT / name
        present = mod.is_present(name, ROOT)
        out[url] = {
            "name": name,
            "wiki": mod.wiki_url(url),
            "dir": d,
            "present": present,
            # A module's reference pages are not behaviour - see WIKI-SPEC.md.
            "refPrefix": "Reference",
            "overrides": {"_docs/README.md": "Home"},
            "deviceDirs": ([d / "_docs/context/devices"] if present else []) + DEVICE_DIRS,
        }
    return out


BLOB_RE = re.compile(r"^(?P<repo>https?://[^\s]+?)/(?:blob|tree)/[^/]+/(?P<path>.+)$")


def as_wiki_page(target, sibs, pages, stats):
    """An absolute GitHub URL that some wiki publishes -> the link that reaches it.

    Cross-repository links have to be absolute URLs in the source: a vendor module and
    the main repo are separate repositories, and the module's directory is gitignored
    here, so no relative spelling resolves in every checkout. But both sides publish a
    wiki, and sending a reader out to a raw Markdown blob for a page that is one click
    away in a wiki is a worse result than the dead link this replaced. So the URL is
    mapped to a page - a bare name for this wiki, a full URL for a sibling's - and left
    alone only when it names something no wiki carries.
    """
    m = BLOB_RE.match(target)
    if not m:
        return None
    repo = m.group("repo").rstrip("/")
    path, _, anchor = unquote(m.group("path")).partition("#")
    frag = f"#{anchor}" if anchor else ""

    if SRC_URL and repo == SRC_URL.rstrip("/"):
        page = pages.get(path)
        return f"{page}{frag}" if page else None

    s = sibs.get(repo)
    if s is None or not publishable(path):
        return None

    # Verified when the sibling is on disk, emitted either way. Refusing on an
    # unverifiable link would make a module a build dependency of this repo, which is
    # the coupling the per-repository split exists to remove.
    if s["present"]:
        if not (s["dir"] / path).exists():
            raise WikiError(
                f"link into the {s['name']} module names {path}, which is not in the "
                f"checkout at {s['dir'].relative_to(ROOT).as_posix()}/. Either the file "
                f"moved and the link was not updated, or that checkout is stale.")
        stats["verified"] += 1
    else:
        stats["unverified"].add(s["name"])

    page = page_name(path, ref_prefix=s["refPrefix"], overrides=s["overrides"],
                     device_dirs=s["deviceDirs"])
    return f"{s['wiki']}/{page}{frag}"


# ---------------------------------------------------------------- link rewriting


def rewrite(text, src_rel, pages, images_root, sibs, stats):
    """Rewrite every link for the flat namespace. Raises on a dead one."""
    src_dir = PurePosixPath(src_rel).parent

    def one(m):
        target, text_, title = m.group("target"), m.group("text"), m.group("title") or ""
        if re.match(r"^(https?:|mailto:|#)", target):
            page = as_wiki_page(target, sibs, pages, stats)
            return f"[{text_}]({page}{title})" if page else m.group(0)

        path_part, _, anchor = target.partition("#")
        if not path_part:                                  # a bare in-page anchor
            return m.group(0)

        # A path in a markdown link is URL-encoded - "11%20FG_01" is a real directory
        # with a space in it. Decode before touching the filesystem, but keep the
        # encoded spelling in whatever URL we emit.
        resolved = (ROOT / src_dir / unquote(path_part)).resolve()
        try:
            rel = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            raise WikiError(f"{src_rel}: link '{target}' points outside the repository.")

        # An image -> the copy in THIS repository, addressed directly. Nothing is
        # copied into the wiki, but the file still has to be here: a raw URL to a file
        # that does not exist renders as a broken image and says nothing about why.
        if resolved.suffix.lower() in IMAGE_SUFFIXES:
            if not resolved.is_file() or images_root not in resolved.parents:
                raise WikiError(
                    f"{src_rel}: image '{target}' is not a file in "
                    f"{images_root.relative_to(ROOT).as_posix()}/, so the wiki cannot "
                    f"address it. Put the figure there and reference it from "
                    f"_docs/ImageDescription.md.")
            try:
                return f"[{text_}]({mod.raw_url(SRC_URL, SRC_REF, quote(rel, safe='/'))}{title})"
            except mod.NotGitHub as e:
                raise WikiError(f"{src_rel}: {e}")

        # another documentation page -> its flat name
        if rel in ALIASES:
            alias = ALIASES[rel]
            if alias is None:
                return f"[{text_}]({SRC_URL}/blob/{SRC_REF}/{rel}{title})" if SRC_URL \
                    else f"[{text_}]({rel}{title})"
            return f"[{text_}]({alias}{'#' + anchor if anchor else ''}{title})"
        if rel in pages:
            return f"[{text_}]({pages[rel]}{'#' + anchor if anchor else ''}{title})"

        # Anything else in the repo -> point back at this repository on GitHub. Every
        # source in this build is in one repository now, so there is no other it could
        # be in: a path under a module's directory cannot appear, because a link that
        # crosses a repository boundary is written as an absolute URL and was handled
        # above.
        if not resolved.exists():
            raise WikiError(
                f"{src_rel}: link '{target}' resolves to {rel}, which does not exist. "
                f"A dead link in a flat wiki is invisible until someone clicks it.")
        if not SRC_URL:
            raise WikiError(
                f"{src_rel}: link '{target}' points at {rel}, which is not a wiki page, "
                f"and no repository URL is declared to link out to.")
        kind = "tree" if resolved.is_dir() else "blob"
        return f"[{text_}]({SRC_URL}/{kind}/{SRC_REF}/{quote(rel, safe='/')}{title})"

    return LINK_RE.sub(one, text)


# -------------------------------------------------------------------- rendering


def banner(src_rel, generated):
    what = "This page is **generated from the Unity twin**. " if generated else ""
    link = f"{SRC_URL}/blob/{SRC_REF}/{src_rel}" if SRC_URL else src_rel
    return [
        f"> {what}Published from [`{src_rel}`]({link}) — **edit it there, not here.** "
        f"Changes made in the wiki are overwritten on the next sync.",
        "",
    ]


def render(src, src_rel, pages, images_root, sibs, stats):
    text = src.read_text(encoding="utf-8")
    generated = bool(GENERATED_COMMENT.search(text))
    # The agent-facing provenance comments are for someone editing the repo, not for
    # a wiki reader; the banner below says the same thing in words.
    text = GENERATED_COMMENT.sub("", text)
    text = SOURCE_COMMENT.sub("", text)
    text = rewrite(text, src_rel, pages, images_root, sibs, stats).lstrip("\n")

    head = banner(src_rel, generated)

    # The banner goes under the H1 so the page still opens with its title.
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join([lines[0], ""] + head + lines[1:]).rstrip() + "\n"
    return "\n".join(head + lines).rstrip() + "\n"


def sidebar(found):
    out = [f"### {mod.repo_name(ROOT) or 'DT_PSA_OPCV'}", ""]
    by_section = {}
    for rel, page, section in found:
        by_section.setdefault(section, []).append(page)
    order = SECTIONS + [s for s in by_section if s not in SECTIONS]
    for section in order:
        if section not in by_section:
            continue
        out += [f"**{section}**", ""]
        out += [f"- [[{page}]]" for page in by_section[section]]
        out.append("")

    # The one place a wiki names another repository's wiki as a whole, so a reader who
    # landed on the machine can reach the platform that runs it. Declared, so this
    # block is the same in every checkout.
    try:
        declared = mod.declared_modules(ROOT)
    except mod.ModuleError:
        declared = {}
    if declared:
        out += ["**Control platforms**", ""]
        for name, info in declared.items():
            url = info["url"].rstrip("/")
            label = info.get("platform") or name
            if info.get("knowledgeBase"):
                out.append(f"- [{label}]({mod.wiki_url(url)})")
            else:
                out.append(f"- [{label}]({url}) — no wiki yet")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def footer(n_pages):
    src = f"[{mod.repo_name(ROOT) or 'the source repository'}]({SRC_URL})" if SRC_URL \
        else "the source repository"
    return (f"_Generated from {src} by `_workflow/tools/build_wiki.py` — "
            f"{n_pages} pages. Edit the source there; changes made here are "
            f"overwritten._\n")


# ------------------------------------------------------------------------- main


def build():
    """(found, rendered, stats) - everything the wiki is made of, nothing written."""
    found = discover()
    pages = {rel: page for rel, page, _ in found}
    sibs = siblings()
    stats = {"verified": 0, "unverified": set()}
    images_root = (DOCS / "images").resolve()

    rendered = {f"{page}.md": render(ROOT / rel, rel, pages, images_root, sibs, stats)
                for rel, page, _ in found}
    rendered["_Sidebar.md"] = sidebar(found)
    rendered["_Footer.md"] = footer(len(found))
    return found, rendered, stats, sibs


def report(found, stats, sibs):
    for section in SECTIONS:
        n = sum(1 for _, _, s in found if s == section)
        if n:
            print(f"  {section}: {n}")
    for s in sorted({s for _, _, s in found if s not in SECTIONS}):
        print(f"  {s}: {sum(1 for _, _, x in found if x == s)}")
    if not sibs:
        return
    print("  sibling wikis:")
    for info in sibs.values():
        if info["present"]:
            print(f"    {info['name']}: {info['wiki']} (cross-links verified against "
                  f"{info['dir'].relative_to(ROOT).as_posix()}/)")
        else:
            print(f"    {info['name']}: {info['wiki']} (not cloned - cross-links "
                  f"emitted unverified)")
    if stats["verified"]:
        print(f"  {stats['verified']} cross-repo link(s) verified")
    if stats["unverified"]:
        print(f"  cross-repo links into {', '.join(sorted(stats['unverified']))} could "
              f"not be verified - that checkout is not here. Clone it to check them.")


def main():
    check_only = "--check" in sys.argv
    found, rendered, stats, sibs = build()

    if check_only:
        print(f"{len(found)} pages, 0 images copied, every link resolved")
        report(found, stats, sibs)
        return

    OUT.mkdir(parents=True, exist_ok=True)

    # Sweep FIRST, then write. _wiki/ is generated, so anything this run did not write
    # is stale - and that now includes the images/ directory this build used to fill,
    # because a figure is addressed at its source and a leftover copy beside the pages
    # is a second answer to the same question.
    #
    # The order matters on a case-insensitive filesystem. Sweeping afterwards deletes a
    # page this run had just written whenever its name changed only in case: Windows
    # keeps the OLD spelling when an existing file is overwritten, so the sweep sees a
    # name that is not in `rendered` and removes the page it was told to publish.
    # Deleting before writing is correct on both kinds of filesystem.
    for f in sorted(OUT.rglob("*"), reverse=True):
        if f.is_file() and f.name not in rendered:
            f.unlink()
            print(f"  removed stale {f.relative_to(OUT).as_posix()}")
        elif f.is_dir() and not any(f.iterdir()):
            f.rmdir()
            print(f"  removed stale {f.relative_to(OUT).as_posix()}/")

    for name, text in rendered.items():
        (OUT / name).write_text(text, encoding="utf-8")

    print(f"wiki written to {OUT.relative_to(ROOT)}")
    print(f"  {len(found)} pages + _Sidebar + _Footer, no images copied")
    print(f"  linking out to {SRC_URL or '(no repository URL declared)'} at ref {SRC_REF}")
    report(found, stats, sibs)
    print("  _wiki/ is a build artifact and is gitignored - "
          "publish with _workflow/tools/publish_wiki.py")


if __name__ == "__main__":
    try:
        main()
    except (WikiError, mod.ModuleError) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        print("Nothing was written. Fix the source page, do not work around this.",
              file=sys.stderr)
        sys.exit(1)

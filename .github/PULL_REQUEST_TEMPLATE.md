# What this changes

<!-- One or two sentences. Link the issue if there is one. -->

## Which part

<!-- Unity twin / Beckhoff / a new control platform / docs -->

## How it was verified

<!-- What you actually ran, and what it said. "It builds" is worth more than a description
     of intent. If you ran the machine, say which scene and how far it got. -->

## Checklist

- [ ] Conventional commit subjects — `feat:`, `fix:`, `docs:`, with an optional scope. The
      subject decides the next version and is the changelog entry a reader sees, verbatim
- [ ] No hand edits to `package.json`'s `version` or to `CHANGELOG.md` — the release bot owns
      both and the next release overwrites them
- [ ] No hand edits under `_docs/context/` — those pages are generated from the Unity twin
      and the next build overwrites them
- [ ] Behaviour facts went to `_docs/reference/`, platform facts to the control module —
      neither crossed into the other
- [ ] A shared device was changed in `Machine_1.prefab`, not in one scene's copy
- [ ] Nothing was invented — every "why" came from the project or from a maintainer
- [ ] If the Unity twin changed, said so: the generated machine pages are rebuilt from it
      and that happens outside this PR

---
name: auditing-context-coverage
description: Use when checking how much of the digital twin has been documented, finding which parts still lack context, or exporting the annotated machine hierarchy for downstream use.
---

# Auditing context coverage

## Overview

Coverage is the gate between authoring and export. The exported JSON is only as useful as it is
complete, and a gap is invisible in the export itself — a node with no entries just looks like a
node. Measure before you ship it downstream.

Keys are free-form, so the audit checks **presence and non-emptiness only**. It never validates key
names.

## Coverage

```bash
unity status --format json                       # need state "ready"
unity command context_audit --format json
```

Returns per-tier `total` / `withNode` / `nonEmpty`, plus `missingNode[]` (no `ContextNode` at all)
and `emptyNode[]` (has one, zero entries). Scope it with
`--scope all | structural | devices | missing`.

Two numbers matter, and they are easy to confuse:

- **`withNode`** should reach `total` once provisioning has run. That is mechanical, and reaching it
  proves nothing about documentation.
- **`nonEmpty`** is the real progress measure, and it only moves through `authoring-context-nodes`.

## Demo_1 baseline

This scene is fully documented. These are *its* numbers to re-check against, not universal ones — if
the hierarchy grows, re-measure and update this section rather than trusting it.

| Tier | Total | withNode | nonEmpty |
|---|---|---|---|
| machine | 1 | 1 | 1 |
| group | 7 | 7 | 7 |
| assembly | 31 | 31 | 31 |
| device | 93 | 93 | 93 |
| **all** | **132** | **132** | **132** |

Export: **177 nodes at depth 7**. PLC symbols: **80** of the 93 devices (the other 13 split 10
aggregated + 3 simulation — see `authoring-context-nodes/reference.md`).

A drop in any of these means something regressed. `missingNode[]` and `emptyNode[]` must both be
empty.

## Provisioning the gaps

`context_ensure` adds empty `ContextNode` components. It is **dry-run by default** — always inspect
the report before applying.

```bash
unity command context_ensure --scope all --mode scene                      # preview
unity command context_ensure --scope all --mode scene   --dry_run false    # apply
unity command context_ensure --scope all --mode prefabs --dry_run false    # backing assets
unity command save_all
```

`--mode scene` covers plain scene objects, `--mode prefabs` writes to the prefab assets behind
prefab-instance members (one write per distinct asset + child, not per instance), `--mode all` does
both. **Run `prefabs` first** so scene objects do not pick up redundant overrides.

## Exporting

**If all you want is a current export and knowledge base, use `refreshing-project-knowledge`** — it
runs the sequence below plus the digest build, and handles the no-Editor case. What follows is the
mechanism it drives, and what you need when auditing the export itself.

The export is an existing Editor menu item; drive it rather than reimplementing it.

```bash
unity command eval --code 'UnityEditor.Selection.objects = new UnityEngine.Object[0]; return "cleared";'
unity command menu --path "PILAR/Context/Export Machine Context (JSON)"
```

**Clear the selection first — this one bites.** An explicit Editor selection *wins* over the default
root, so whatever a human last clicked in the Hierarchy silently becomes the export root. A leftover
selection on a single cylinder produced a **2-node** `<Scene>_Context.json` that was structurally valid,
carried the right `sceneName`, and reported no error anywhere. Only the node count gave it away, and
`context_audit` still said 132/132 because the scene was never the problem. Always check the exported
`root.name` is `Project`.

The exporter names the root it used in the console, which is the fastest tell:

```bash
unity command console --format json     # expect "exported machine context of 'Project'"
```

Writes `Unity/Assets/StreamingAssets/<Scene>_Context.json` — a nested tree of
`{name, scenePath, topologyPath, components, entries[], children[]}`, pruned to semantically relevant
structure.

**One export per vendor scene.** The machine is the `Machine_1` prefab that every scene instances; a
scene adds only its vendor's operator panel. So there is a `VC_Demo_1_Beckhoff_1_Context.json` and a
`VC_Demo_1_Siemens_1_Context.json`, and **coverage has to be audited per scene** — a panel documented
in one is not documented in the other. The snippets below take the newest export; pass a specific
scene's file to audit that one.

`entries` is each node's whole dictionary. A bare key is authored; a prefixed one (`oc.plcPath`) was
written by `context_sync` from an installed twin framework.

**Sync before you export.** The export dumps what the nodes hold and queries no framework itself, so
an unsynced scene exports no metadata at all and looks complete while doing it:

```bash
unity command context_sync --dry_run true     # what would change
unity command context_sync --dry_run false    # write it
unity command menu --path "PILAR/Context/Export Machine Context (JSON)"
```

The dry run is also the only drift check there is: a rename or a deleted component leaves stored
values wrong until someone syncs again. On a clean scene it reports `changed: 0`.

Repeat sync-and-export for **each** scene, opening it first:

```bash
unity command open_scene --path Assets/Demo_1/Scenes/VC_Demo_1_Siemens_1.unity
```

## Verify the export, do not assume it

```bash
python -c "
import json, glob
EXPORTS = sorted(glob.glob('Unity/Assets/StreamingAssets/*_Context.json'))
d = json.load(open(EXPORTS[0]))   # or name one scene's file
n = [0]; depth = [0]
def walk(x, k=0):
    n[0] += 1; depth[0] = max(depth[0], k)
    for c in x.get('children', []): walk(c, k+1)
walk(d['root'])
print('root', d['root']['name'], 'nodes', n[0], 'maxDepth', depth[0], 'scene', d['sceneName'])
"
```

Expect `root Project nodes 177 maxDepth 7 scene Demo_1`.

The exporter uses `JsonUtility`, which **silently drops data nested past roughly 7–10 levels**. Depth
7 means this scene sits right at the edge of that window, so re-check node count and depth whenever
the hierarchy grows. If either drops unexpectedly, the serializer is truncating and the export can no
longer be trusted.

## Check for malformed entries too

Coverage counts entries; it does not inspect them. Prefab override reconciliation can leave an entry
with a blank key and value, which counts as coverage but carries nothing:

```bash
python -c "
import json, glob
EXPORTS = sorted(glob.glob('Unity/Assets/StreamingAssets/*_Context.json'))
d = json.load(open(EXPORTS[0]))   # or name one scene's file
bad = []
def walk(x):
    for e in x.get('entries', []):
        if '.' in e.get('key',''): continue          # synced, not authored
        if not e.get('key','').strip() or not e.get('value','').strip():
            bad.append((x['scenePath'], e.get('key')))
    for c in x.get('children', []): walk(c)
walk(d['root'])
print('malformed entries:', bad or 'NONE')
"
```

Run this after any batch that wrote to prefab assets.

## Cross-check the PLC symbols against OC's own tree

`Unity/Assets/StreamingAssets/<Scene>_Project_Tree.xml` is Open Commissioning's independent export of the
device tree. Every device that should be a PLC symbol must appear in both, and nothing may appear in
one alone. A mismatch means the twin and the PLC project have drifted, and the export must not be
trusted for code generation until they agree.

A node is a PLC symbol when its entries carry `oc.deviceType` and **neither** `oc.aggregatedBy` nor
`oc.simulationDevice`. Do not filter on `oc.plcPath` alone — every node has one, including pure
structure. The XML root is `<Main>` and its paths omit the `MAIN.` prefix, so strip it before
comparing.

```bash
python -c "
import json, glob, xml.etree.ElementTree as ET
d = json.load(open(sorted(glob.glob('Unity/Assets/StreamingAssets/*_Context.json'))[0]))
real = set()
def wj(n):
    e = {x['key']: x['value'] for x in n.get('entries', [])}
    if 'oc.deviceType' in e and 'oc.aggregatedBy' not in e and 'oc.simulationDevice' not in e:
        p = e.get('oc.plcPath', '')
        real.add(p[5:] if p.startswith('MAIN.') else p)
    for c in n.get('children', []): wj(c)
wj(d['root'])
xml_dev = set()
def wx(el, path):
    for c in el:
        if c.tag == 'Group': wx(c, path + [c.get('Name')])
        elif c.tag == 'Device': xml_dev.add('.'.join(path + [c.get('Name')]))
        else: wx(c, path)
wx(ET.parse(sorted(glob.glob('Unity/Assets/StreamingAssets/*_Project_Tree.xml'))[0]).getroot(), [])
print('context', len(real), 'xml', len(xml_dev))
print('only in context:', sorted(real - xml_dev))
print('only in xml    :', sorted(xml_dev - real))
"
```

Expect `context 80 xml 80` with both difference sets empty.

Two symbols must never collide, either. Duplicate `oc.plcPath` values among *real* symbols would mean
two devices writing the same PLC variable:

```bash
python -c "
import json, glob, collections
d = json.load(open(sorted(glob.glob('Unity/Assets/StreamingAssets/*_Context.json'))[0]))
paths = []
def wj(n):
    e = {x['key']: x['value'] for x in n.get('entries', [])}
    if 'oc.deviceType' in e and 'oc.aggregatedBy' not in e and 'oc.simulationDevice' not in e:
        paths.append(e.get('oc.plcPath'))
    for c in n.get('children', []): wj(c)
wj(d['root'])
print('duplicates:', [p for p, c in collections.Counter(paths).items() if c > 1] or 'NONE')
"
```

Unlinked devices *may* share a path harmlessly — both gate `SimSensor`s resolve to
`MAIN.FG_Transport.SimSensor` — which is exactly why the filter above must exclude them.

## Facet the framework metadata yourself

`context_audit` deliberately reports **coverage only** — totals, per-tier counts, missing and empty
nodes. It does not group by framework vocabulary, because the pipeline does not own that vocabulary.
Build the OC-side view from the prefixed entries:

```bash
python -c "
import json, glob, collections
d = json.load(open(sorted(glob.glob('Unity/Assets/StreamingAssets/*_Context.json'))[0]))
facets = collections.defaultdict(collections.Counter)
def walk(x):
    for e in x.get('entries', []):
        if '.' in e['key']: facets[e['key']][e['value']] += 1
    for c in x.get('children', []): walk(c)
walk(d['root'])
for k, v in facets.items(): print(k, dict(v))
"
```

On a clean `Demo_1`: `oc.plcPath` 132, `oc.deviceType` 93 across 12 types, `oc.hierarchyRole`
7 `group` + 13 `sampler`, `oc.aggregatedBy` 10, `oc.simulationDevice` 3. An empty result means the
scene was never synced, not that OC knows nothing.

## Common mistakes

- **Reporting coverage from `withNode`.** An empty node is not documentation. Report `nonEmpty`.
- **Applying `context_ensure` without reading the dry run.** It is dry-run by default for a reason.
- **Exporting before `save_all`.** The export reads live scene state, so it includes unsaved edits —
  which are then lost if the Editor closes without saving. Save first.
- **Exporting before `context_sync`.** The export no longer queries OC; it dumps what the nodes
  hold. An unsynced scene exports zero `oc.*` entries and still reports full coverage.
- **Exporting with something selected.** The selection becomes the root. Clear it, then confirm
  `root.name == "Project"` in the written file.

<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# Knowledge base provenance

Read this before trusting anything else in `_docs/context/`.

| | |
|---|---|
| Scene | `VC_Demo_1_Beckhoff_1` |
| Exported (UTC) | `2026-08-23T17:09:36.0996372Z` |
| Export commit | `5010e82 2026-08-23` |
| Export uncommitted | no |
| Reference scene | `VC_Demo_1_Beckhoff_1` (Beckhoff) |
| Nodes | 180 |
| Max depth | 7 (JsonUtility truncates past ~7-10) |
| Real PLC symbols | 83 |
| Devices in `VC_Demo_1_Beckhoff_1_Project_Tree.xml` | 83 (must equal the row above) |
| Functional groups | 7 |
| Nodes with no authored context | 0 |
| Nodes differing between scenes | 15 (marked †) |
| Figures | 12 from `_docs/ImageDescription.md`, 66 callouts all resolved against this export |

## Scenes

The machine is one prefab, `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab`, instanced by every scene. A scene adds its vendor's operator panel and nothing else, so the exports agree everywhere except that subtree.

| Scene | Vendor | Nodes | Symbols | Exported (UTC) | |
|---|---|---:|---:|---|---|
| `VC_Demo_1_Beckhoff_1` | Beckhoff | 180 | 83 | `2026-08-23T17:09:36.0996372Z` | **reference** |
| `VC_Demo_1_Siemens_1` | Siemens | 179 | 83 | `2026-08-26T11:52:16.8621701Z` |  |

**The pages here are rendered from `VC_Demo_1_Beckhoff_1`.** Taking only what every scene agrees on would leave FG_System with no operator panel at all, which is a worse picture of the machine than one panel labelled as an example - so the reference scene's panel is shown, and every node that differs between scenes carries †. Anything *un*marked is the machine. Each vendor's own panel is on that vendor's page.

This is the **twin** half only. Each vendor module stamps its own control-side freshness - how current its type model is, and against which build of this export - in its own `PROVENANCE.md`:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/PROVENANCE.md)
- **Siemens** — _no knowledge base published yet_

## Verified against a live scene?

**No.** This was built from the committed export without a live Unity Editor. The digest is internally consistent and every assertion passed, but nothing proves the scene has not changed since the export timestamp above.

That is a supported way to work - open Unity and run `refreshing-project-knowledge` when you need the stronger guarantee, and say which you had in any report.

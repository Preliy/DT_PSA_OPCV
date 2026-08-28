# Third-party notices

DT_PSA_OPCV is licensed under [GPL-3.0](LICENSE). It uses the third-party components listed
below, each under its own licence and copyright.

**This repository redistributes none of them.** Every Unity package is fetched by the Unity
Package Manager from its own registry or git repository when the project is opened, using the
versions declared in [`Unity/Packages/manifest.json`](Unity/Packages/manifest.json) and resolved
in `Unity/Packages/packages-lock.json`. Those two files are the authority; this page is a
human-readable summary of them, and every licence below was read from the package as resolved
rather than assumed from its name.

Versions are those resolved for the Unity editor this project targets, `6000.3.18f1`. A licence
here describes the package, not this project — nothing below is granted to you by us.

**Every dependency is under a permissive or Unity-standard licence**, and none of them restricts
who may use this project.

## Unity packages installed from git

These six track a moving branch rather than a pinned tag, so the version you resolve may be newer
than the one recorded here. The licences were read from each repository's current `upm` or
`master` branch.

| Package | Version | Licence | Source |
|---|---|---|---|
| **Open Commissioning** `com.open-commissioning.core` | 1.3.14 | BSD 3-Clause — © 2024 SpiraTec AG | [OC_Unity_Core](https://github.com/OpenCommissioning/OC_Unity_Core) · [licence](https://github.com/OpenCommissioning/OC_Unity_Core/blob/master/LICENSE.md) |
| **Open Commissioning UI** `com.open-commissioning.ui` | 1.1.8 | BSD 3-Clause — © 2024 SpiraTec AG | [OC_Unity_UI](https://github.com/OpenCommissioning/OC_Unity_UI) · [licence](https://github.com/OpenCommissioning/OC_Unity_UI/blob/master/LICENSE.md) |
| **PILAR Context** `com.pilar.context` | 1.4.1 | MIT — © 2026 Viktor Gaponenko | [unity-pilar-context](https://github.com/Preliy/unity-pilar-context) · [licence](https://github.com/Preliy/unity-pilar-context/blob/master/LICENSE.md) |
| **Outline** `com.cqf.outline` | 1.0.0 | MIT — © 2024-2026 Cristian Qiu | [Unity-URP-Outline](https://github.com/CristianQiu/Unity-URP-Outline) · [licence](https://github.com/CristianQiu/Unity-URP-Outline/blob/main/LICENSE.md) |
| **UniTask** `com.cysharp.unitask` | 2.5.11 | MIT — © 2019 Yoshifumi Kawai / Cysharp, Inc. | [UniTask](https://github.com/Cysharp/UniTask) · [licence](https://github.com/Cysharp/UniTask/blob/master/LICENSE) |
| **NaughtyAttributes** `com.dbrizov.naughtyattributes` | 2.1.6 | MIT — © 2017 Denis Rizov | [NaughtyAttributes](https://github.com/dbrizov/NaughtyAttributes) · [licence](https://github.com/dbrizov/NaughtyAttributes/blob/master/LICENSE) |

## Assets

| | Author | Terms |
|---|---|---|
| **Laser Welding & Assembly System (PSA OPCV)** — the CAD model every shape in the twin derives from | [Villette Oh](https://grabcad.com/villette.oh-1) | Published on [GrabCAD](https://grabcad.com/library/laser-welding-assembly-system-psa-opcv-1); use is governed by GrabCAD's terms and the uploader's stated conditions. See the model page |

## Control platform modules

Each control platform is a **separate repository** with its own dependencies and its own notices.
Nothing in this file covers them:

- [DT_PSA_OPCV_Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff)
- [DT_PSA_OPCV_Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens)

## Corrections

If an attribution here is wrong, incomplete, or names your work under the wrong licence, please
[open an issue](https://github.com/Preliy/DT_PSA_OPCV/issues) — it will be fixed promptly.

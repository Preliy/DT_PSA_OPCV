# Setup

What you need, and how to get the machine running. There are three ways to run it and this page
covers the first two; the third is [04 · PLC connectivity](04-plc-connectivity.md).

| Mode | | The machine is driven by | You need |
|---|---|---|---|
| **MIL** | Model in the Loop | C# sequences inside Unity — an abstract animation | Nothing but the twin |
| **SIL** | Software in the Loop | A real PLC program on an **emulated** runtime | The runtime |
| **HIL** | Hardware in the Loop | The same PLC program on **real controller hardware** | The controller |

Start with MIL. It takes minutes and proves the Unity side works before any PLC is involved.

> Unfamiliar terms? [07 · Glossary](07-glossary.md).

---

## 1. What you need

### A PC

| | |
|---|---|
| **Operating system** | **Windows 10 or 11, x64.** The released build is a Windows player, and every PLC runtime this twin has been driven by runs on Windows |
| **Graphics** | A GPU that runs Unity 6 comfortably. The scene is CAD-derived and rendered in real time |
| **Disk** | Room for the Unity project, its imported meshes and library cache — several GB |

`TODO(setup)`: no minimum specification has been measured on a clean machine. If you find the floor,
that is a useful contribution.

Linux and macOS are not supported for the PLC setups, because the simulation unit and every control
runtime involved are Windows software. The Unity editor itself is cross-platform, so MIL may well
work — nobody has tried it.

### Unity, and a Unity licence

| | |
|---|---|
| **Version** | `6000.3.18f1` — the exact version in [`Unity/ProjectSettings/ProjectVersion.txt`](../Unity/ProjectSettings/ProjectVersion.txt). Install it through Unity Hub |
| **Licence** | A Unity account with a licence activated in the Hub. **Unity Personal is free**; whether you qualify for it is between you and Unity's licensing terms |

You need neither of those to **watch** the machine — the [packaged
build](https://github.com/Preliy/DT_PSA_OPCV/releases/latest) is a plain Windows executable. Unity
is needed to open the project, to run it against a PLC, and to change anything.

### For a PLC setup: TwinCAT, whichever platform you use

The **simulation unit is a TwinCAT project** — that is where the twin's device models live and where
the fieldbus is emulated. It is not a Beckhoff-only requirement: a Siemens setup uses the same
simulation unit and reaches it through an OC Assistant plugin. [03 · How it
works](03-how-it-works.md) explains why.

| | |
|---|---|
| **TwinCAT 3** | The engineering environment and the runtime, plus **OC Assistant** and the OC TwinCAT library |
| **Your control platform** | Whatever runs your program — TwinCAT again for Beckhoff, TIA Portal and PLCSIM Advanced for Siemens, or your own |

**Installation, licensing and versions are the vendor's own, and are documented by the module that
owns them** — for TwinCAT, the [Beckhoff setup
guide](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/01-setup.md). This page does
not repeat them, because nothing here would keep them true.

### Tooling

| Component | Version | Notes |
|---|---|---|
| **Git** | — | Several Unity packages are pulled from git URLs |
| **Python** | 3.9+ | Only for the documentation tooling. Developed against 3.12. Standard library only — nothing to `pip install` |

### New to Open Commissioning?

This twin is built on **Open Commissioning**, and its own documentation is the place to learn the
framework itself — how a scene is put together, what OC Assistant does, how the simulation project
is generated. Nothing here repeats it.

| | |
|---|---|
| [OC_Unity_Core](https://github.com/OpenCommissioning/OC_Unity_Core) | the Unity package: devices, the `Client` gateway, the hierarchy model |
| [OC_Assistant](https://github.com/OpenCommissioning/OC_Assistant) | the tool that keeps Unity and the simulation project in step |
| [OC_TwinCAT_Core](https://github.com/OpenCommissioning/OC_TwinCAT_Core) | the TwinCAT library the simulation project uses |

Two video tutorials from the Open Commissioning team are the fastest way in:

- [Tutorial 1 — Getting Started](https://www.youtube.com/watch?v=0VS6-7F2n1U)
- [Tutorial 3 — Generating a TwinCAT Project](https://www.youtube.com/watch?v=KT6Brv2ppE4)

---

## 2. Just want to look at the machine?

Download the packaged build from the [latest
release](https://github.com/Preliy/DT_PSA_OPCV/releases/latest), extract it, run the `.exe`.

That is MIL, with nothing to install and nothing to clone — see [02 · Using the
application](02-using-the-application.md) for the controls. Everything below is for running it
yourself.

---

## 3. Getting the project

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV
```

That is everything you need to run the twin on its own. To drive it with a PLC you also need that
platform's module, which is a **separate repository cloned into this directory**:

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff
```

Take only the platform you use — the modules are optional and independent, and a Siemens user has no
reason to fetch a TwinCAT solution. The module paths are gitignored here, so the two git
repositories do not collide: inside `Beckhoff/` everything is an ordinary checkout on an ordinary
branch, and `git status` in this directory never mentions it.

Which module version goes with which twin is in [COMPATIBILITY.md](../COMPATIBILITY.md), and the
table there is checked rather than asserted.

**Run every command from this directory** — including the vendor modules' own tools. There is never
a reason to `cd Unity/`.

### The Unity project

Open `Unity/` with Unity `6000.3.18f1`. On first open, the Package Manager resolves the dependencies
in `Unity/Packages/manifest.json`, six of which come from git URLs and need network access:

| Package | Source | Licence |
|---|---|---|
| `com.open-commissioning.core` | `github.com/OpenCommissioning/OC_Unity_Core` | BSD 3-Clause |
| `com.open-commissioning.ui` | `github.com/OpenCommissioning/OC_Unity_UI` | BSD 3-Clause |
| `com.pillar.context` | `github.com/Preliy/unity-pillar-context` | MIT |
| `com.cqf.outline` | `github.com/CristianQiu/Unity-URP-Outline` | MIT |
| `com.cysharp.unitask` | `github.com/Cysharp/UniTask` | MIT |
| `com.dbrizov.naughtyattributes` | `github.com/dbrizov/NaughtyAttributes` | MIT |

All six are permissive, and every licence is listed in
[THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md). They track a branch rather than a pinned
tag, so a fresh resolve may bring a newer version than the one you last had.

First import takes a while — the project carries CAD-derived meshes.

---

## 4. MIL: the twin on its own

Open `Unity/Assets/Demo_1/Scenes/VC_Demo_1_MIL.unity` and press **Play**.

Pallets circulate, the stations run, and the whole line works — driven by C# coroutines under
`Unity/Assets/Demo_1/Scripts/MIL/`, with no control system anywhere.

This is the fastest way to confirm your Unity setup is correct, and it is where to stop if you only
wanted to see the machine.

> **The MIL scripts are the twin's animation, not the machine's specification.** They implement an
> *older* contract — no transfer latch, no check that a lift is at a level before running its
> carriage belt, no reset path at all. Never write PLC code from them; the behaviour that counts is
> in the [behaviour contracts](reference/transport-behaviour.md).

---

## 5. Then what

| You want to | Go to |
|---|---|
| Move the camera, use the panels, find a device on screen | [02 · Using the application](02-using-the-application.md) |
| Drive it with a PLC — SIL or HIL | [04 · PLC connectivity](04-plc-connectivity.md) |
| Understand what you just started | [03 · How it works](03-how-it-works.md) |
| Know what the machine is made of | [06 · Machine description](06-machine-description.md) |

Everything under [`context/`](context/) is generated from the Unity twin and **committed**, so you
never need to build anything in order to read it.

## Checking it worked

| Check | Expect |
|---|---|
| `VC_Demo_1_MIL` in Play mode | Pallets circulate on their own, with no PLC |
| A vendor scene with its runtime up | Devices respond to the PLC — see [04 · PLC connectivity](04-plc-connectivity.md) |

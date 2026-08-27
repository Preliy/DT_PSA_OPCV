# Setup

Three ways to run this machine, and this page covers all of them.

| Mode | | The machine is driven by | You need |
|---|---|---|---|
| **MIL** | Model in the Loop | C# sequences inside Unity — an abstract animation | Nothing but the twin |
| **SIL** | Software in the Loop | A real PLC program on an **emulated** runtime — TwinCAT on this PC, PLCSIM Advanced | The runtime |
| **HIL** | Hardware in the Loop | The same PLC program on **real controller hardware** | The controller |

**SIL and HIL are the same setup** — twin, twin device layer and control program are identical, and
only where the PLC executes changes. Part 3 covers both.

Start with MIL. It takes minutes and proves the Unity side works before any PLC is involved.

> Unfamiliar terms? [05 · Glossary](05-glossary.md).

### New to Open Commissioning?

This twin is built on **Open Commissioning**, and its own documentation is the place to learn the
framework itself — how a scene is put together, what OC Assistant does, how the simulation project
is generated. Nothing below repeats it.

| | |
|---|---|
| [OC_Unity_Core](https://github.com/OpenCommissioning/OC_Unity_Core) | the Unity package: devices, the `Client` gateway, the hierarchy model |
| [OC_Assistant](https://github.com/OpenCommissioning/OC_Assistant) | the tool that keeps Unity and the simulation project in step |
| [OC_TwinCAT_Core](https://github.com/OpenCommissioning/OC_TwinCAT_Core) | the TwinCAT library the simulation project uses |

Two video tutorials from the Open Commissioning team are the fastest way in:

- [Tutorial 1 — Getting Started](https://www.youtube.com/watch?v=0VS6-7F2n1U)
- [Tutorial 3 — Generating a TwinCAT Project](https://www.youtube.com/watch?v=KT6Brv2ppE4)

---

## Part 1 — Common setup

### Just want to look at the machine?

Download the packaged build, extract it, run the `.exe`. That is MIL, with nothing to install — see
[03 · Usage](03-usage.md) for the controls. Everything below is for running it yourself.

### Prerequisites

| Component | Version | Notes |
|---|---|---|
| **Unity** | `6000.3.18f1` | The exact version in `Unity/ProjectSettings/ProjectVersion.txt`. Unity 6.3 |
| **Python** | 3.9+ | For the knowledge-base tooling. Developed against 3.12. Standard library only — nothing to `pip install` |
| **Git** | — | Several Unity packages are pulled from git URLs |

Plus, for SIL or HIL, whatever your control platform needs — see Part 3.

### Clone

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV
```

That is everything you need to **watch** the machine run. To drive it with a PLC you also need that
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
| `com.pilar.context` | `github.com/Preliy/unity-pilar-context` | MIT |
| `com.cqf.outline` | `github.com/CristianQiu/Unity-URP-Outline` | MIT |
| `com.cysharp.unitask` | `github.com/Cysharp/UniTask` | MIT |
| `com.dbrizov.naughtyattributes` | `github.com/dbrizov/NaughtyAttributes` | MIT |

All six are permissive, and every licence is listed in
[THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md). They track a branch rather than a pinned
tag, so a fresh resolve may bring a newer version than the one you last had.

First import takes a while — the project carries CAD-derived meshes.

---

## Part 2 — MIL: the twin on its own

Open `Unity/Assets/Demo_1/Scenes/VC_Demo_1_MIL.unity` and press **Play**.

Pallets circulate, the stations run, and the whole line works — driven by C# coroutines under
`Unity/Assets/Demo_1/Scripts/MIL/`, with no control system anywhere.

This is the fastest way to confirm your Unity setup is correct, and it is where to stop if you only
wanted to see the machine.

> **You can skip Part 1 entirely for this.** Every release carries a prebuilt Windows version of
> this exact scene —
> [download it from the latest release](https://github.com/Preliy/DT_PSA_OPCV/releases/latest),
> unzip, run. No Unity, no clone, no PLC. Everything below Part 2 does need the Unity project.

> **The MIL scripts are the twin's animation, not the machine's specification.** They implement an
> *older* contract — no transfer latch, no check that a lift is at a level before running its
> carriage belt, no reset path at all. Never write PLC code from them; the behaviour that counts is
> in the [behaviour contracts](reference/transport-behaviour.md).

---

## Part 3 — SIL and HIL: driving it with a control system

Now the machine is driven by an actual PLC program, over a fieldbus, exactly as it would be on real
steel.

### How it fits together

```
   Unity twin
      │  ADS (or your protocol) - a process image, each cycle
      ▼
   twin device layer      one function block per device
      │  fieldbus         simulated on this side, real terminals on the other
      ▼
   control program        the thing being tested
```

The control program never talks to Unity. It talks to terminals. That indirection is the point — see
[04 · Architecture](04-architecture.md).

### Pick your platform

| Platform | Setup guide |
|---|---|
| **Beckhoff / TwinCAT** | [`Beckhoff/_docs/01-setup.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/01-setup.md) |
| **Siemens / TIA** | Not yet — the Unity scene is ready, the control side is not written |
| **Something else** | Planned — see [Other control platforms](04-architecture.md#7-other-control-platforms); this is where help is wanted |

Then open that platform's scene:

| Scene | Platform |
|---|---|
| `VC_Demo_1_Beckhoff_1` | Beckhoff / TwinCAT |
| `VC_Demo_1_Siemens_1` | Siemens — scene only, for now |

**Start the PLC runtime first, then enter Play mode in Unity.** The twin binds its devices on
connect, so a runtime that appears later is a runtime the twin never found.

### SIL or HIL

Same project, same program, same twin. Only the runtime differs:

| | **SIL** — emulated runtime | **HIL** — controller hardware |
|---|---|---|
| Where the PLC runs | On this PC — TwinCAT runtime, PLCSIM Advanced | On a real controller |
| Address | Local loopback — TwinCAT uses `127.0.0.1.1.1` | The controller's real network address |
| Fieldbus | Simulated pair on one machine | Real master on the controller, simulated side facing the twin |
| Timing | Not real time — the PC schedules it | Real cycle time, real jitter, real bus |
| Good for | Everyday development, CI, learning | Proving the program on the hardware that will ship |

**Validate in SIL, then move to HIL without touching the program.** That the same binary runs both
ways is the property that makes the SIL result worth anything.

Everything documented in this repository today was run in **SIL**. HIL uses the same mechanism, but
the concrete steps have not been captured from a working installation:

- `TODO(setup)`: creating the route to a physical controller, and what to enter where.
- `TODO(setup)`: network configuration between the PC running Unity and the controller.
- `TODO(setup)`: which parts of the fieldbus configuration change when the master is real.

If you get it working, that is one of the most useful contributions you could send.

---

## Part 4 — The machine description

Everything under [`context/`](context/) is generated from the Unity twin and **committed**, so you
never need to build anything in order to read it. It is refreshed by the maintainers whenever the
twin changes; if a page disagrees with the scene, that is a bug worth reporting.

---

## Checking it worked

| Check | Expect |
|---|---|
| `VC_Demo_1_MIL` in Play mode (MIL) | Pallets circulate on their own, with no PLC |
| A vendor scene with its runtime up | Devices respond to the PLC — see that platform's usage page |

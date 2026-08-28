# How it works

How the digital twin is put together, and how a control program gets to drive it. The concrete
per-vendor setups are on the next page, [04 · PLC connectivity](04-plc-connectivity.md); this one is
the design they are all variations on.

> This page uses the trade names as they are: [07 · Glossary](07-glossary.md) has them in plain
> language.

## 1. The shape of it

```
   Unity twin              the machine: geometry, kinematics, sensors, engineering context
      │  a process image, once per cycle
      ▼
   simulation unit         one function block per twin device — TwinCAT, real time
      │  fieldbus          simulated on this side, terminals on the other
      ▼
   control program         the thing being tested. It sees terminals, never Unity
```

Three layers, and the middle one is what makes the result mean anything. The control program is
never given a special interface into the simulation: it talks to fieldbus terminals, exactly as it
would on the real machine.

The project is built on [Open Commissioning](https://github.com/OpenCommissioning), and an Open
Commissioning setup always has the **same two parts**. Everything vendor-shaped is added around
them.

## 2. The two parts

### Unity — the digital twin

The Unity scene is where the twin lives. The model is a **hierarchy of parts and components** —
actors, sensors, drives, cylinders — assembled into a hierarchical kinematic, so a movement applied
to a parent carries everything mounted on it. Together with **PILAR Context**, each part also carries
its engineering context: its type and role, its properties, its metadata. That context is what
[05 · Engineering workflow](05-engineering-workflow.md) is about.

The scene's **Client** is the gateway. It aggregates every component in the scene into one interface
and owns the connection to the second part.

### The simulation unit — TwinCAT

The simulation unit is a TwinCAT PLC project (`SIM_1`) holding the **same hierarchy and the same
component list as Unity**, imported and kept in sync from the Unity side by **OC Assistant**.

**Why TwinCAT, even for a setup that is not Beckhoff.** It runs in real time at a 1 ms cycle, and it
can host an emulated industrial fieldbus — EtherCAT emulation, emulated PROFINET devices. Real-time
execution plus an emulated fieldbus is what lets the behaviour models run under the timing a PLC
actually imposes, and it is what makes high-quality field device simulation possible at all. That
matters for everything time-critical: drives, safety, fast I/O, and acyclic data exchange.

So TwinCAT here is **infrastructure, not a control platform choice**. What runs your program is a
separate question, and the answer is the next page.

### OC Assistant holds the two together

OC Assistant is the orchestration and synchronisation layer between them. It synchronises the model,
the hierarchy and the components between Unity and `SIM_1`, imports and updates components and their
context, generates the interface GVLs, scans networks and creates emulation units, and manages the
lifecycle of its plugins.

## 3. Why the indirection is the point

In every setup the control program talks to **fieldbus terminals**, never to Unity. The twin sits
behind the simulated side of the bus.

That is what makes the result mean something: the control program cannot tell it is running against
a twin, so nothing about it has to change when it runs against steel. A test rig the program is
aware of proves much less.

It is also why **SIL and HIL are the same setup** — the twin, the simulation unit and the control
program are identical, and only where the PLC executes changes:

| Mode | The machine is driven by | Where the PLC runs |
|---|---|---|
| **MIL** | C# sequences inside Unity | Nowhere — there is no PLC |
| **SIL** | A real control program | On this PC, on an emulated runtime |
| **HIL** | The same control program | On real controller hardware |

MIL is for seeing the machine and understanding the process. It proves nothing about a control
program, and it is not meant to.

## 4. The Unity packages

| Package | Provides |
|---|---|
| `com.open-commissioning.core` | Device components (`Cylinder`, `SensorBinary`, `DriveSimple`, …), the `Client` gateway and its transport, the hierarchy model |
| `com.open-commissioning.ui` | The runtime application UI — toolbar, selection, cameras, industrial panels |
| `com.pilar.context` | The authored engineering context on each part |

Project-specific behaviour is small and lives in `Unity/Assets/Demo_1/Scripts/`:
`ControlBunker`, `DataReader`, `GripSensor`, `PartPressDetector`, plus the `MIL/` animation
coroutines.

## 5. One machine, one prefab, one scene per vendor

The machine is a **prefab** — `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab` — and every scene under
`Unity/Assets/Demo_1/Scenes/` instances it. What a scene adds is its vendor's operator panel and the
`Client` for that setup:

| Scene | Adds |
|---|---|
| `VC_Demo_1_MIL` | Nothing — the machine, driven by the C# sequences |
| `VC_Demo_1_Beckhoff_1` | `H_ControlPanel` → `MAIN.FG_System.H_ControlPanel`, 8 PackML buttons |
| `VC_Demo_1_Siemens_1` | `H_ControlPanel` → `MAIN.FG_System.H_ControlPanel_Siemens`, 7 controls incl. a rotary switch |

A device that belongs to every vendor lives in the prefab, so there is exactly one copy of it.
Editing one scene's copy of a shared device is a mistake the build detects: the node stops being
identical across scenes and starts being marked `†` on the generated pages.

**Read `†` as "this is one vendor's example".** The generated machine pages are rendered from one
reference scene, currently Beckhoff. What is unmarked is the machine.

Adding a vendor is therefore adding a scene, not forking the machine.

## 6. Where the facts live

The project keeps three kinds of fact apart, because each has a different owner and a different
lifetime. Mixing them is how documentation starts to lie.

| | The question it answers | Where it is written | By |
|---|---|---|---|
| **Structure** | Which devices exist, what type each is, what its address is | [`context/`](context/) | a generator, straight from the Unity twin |
| **Behaviour** | What the machine has to *do* — sequences, interlocks, faults, recovery | [`reference/`](reference/) | a human, once, for every platform |
| **Realisation** | How one particular PLC spells all that — function blocks, terminals, the HMI | each vendor's own repository | that platform's maintainers |

Structure is generated because it can be *read* out of the twin, so a generated page cannot drift
away from the machine. That is also why editing a page under `context/` achieves nothing: the next
build overwrites it. Change the Unity scene instead — see
[05 · Engineering workflow](05-engineering-workflow.md).

Behaviour is written by hand because it cannot be read out of anything — a sequence is a decision,
and guessing one from a hierarchy produces something plausible and wrong. It is written once and
platform-neutrally, so a Siemens implementation has to satisfy exactly the same contract the TwinCAT
one does.

Realisation is one answer per platform, so it lives with that platform and nowhere else.

**The twin path is not the control path.** The twin says `MAIN.FG_01.P_Camera`; TwinCAT says
`MAIN.Machine.FG_01.P_Camera`. The twin's spelling fails *silently* in a link and in an HMI binding,
so the machine pages state the twin path, and the verified control path is on the platform's page.

## 7. How the repository is organised

| Module | Path | Role |
|---|---|---|
| **Unity twin** | `Unity/` | The digital twin of the machinery, on Open Commissioning |
| **Documentation** | `_docs/` | These pages, the generated machine description, the behaviour contracts |
| **How it is built** | `_workflow/` | The specifications, the agent skills, and the tooling that reads only tracked files |
| **A control platform** | `Beckhoff/`, `Siemens/`, … | One **separate, optional repository** per platform, cloned into this root |

Each vendor module is a separate repository you clone into the main repo's root, where its path is
gitignored so the two do not collide. Take only the platform you use. **Nothing in the main
repository depends on a vendor module being present**, and each module carries a committed copy of
the machine's structure, so it also builds on its own.

What crosses from this repository into a vendor's is a single generated file,
[`context/.machine.json`](context/.machine.json) — the machine's structure as schema-versioned JSON.
It crosses as a **copy, not a reference**: each module commits its own snapshot, so it builds from a
standalone clone with no Unity present.

Which modules exist and which versions pair with this twin is in
[COMPATIBILITY.md](../COMPATIBILITY.md); the declaration itself is
[`_workflow/config/modules.json`](../_workflow/config/modules.json).

## 8. Next

| You want to | Read |
|---|---|
| See the concrete setups, and add your platform | [04 · PLC connectivity](04-plc-connectivity.md) |
| Know where the generated description comes from | [05 · Engineering workflow](05-engineering-workflow.md) |
| Know what the machine is made of | [06 · Machine description](06-machine-description.md) |

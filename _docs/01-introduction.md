# Introduction

![The machine](images/Machine_Overview.png)

*The line: FG_System, FG_Transport and FG_01 to FG_05 assembled together.*

## What this project is for

**DT_PSA_OPCV** is a digital twin of a laser welding and assembly system: a working model of a real
production line, built in Unity, that your own PLC program can drive as if it were the real machine.

That is what **virtual commissioning** means — testing the control program against a model of the
machine, long before the machine itself is standing on a factory floor. This project exists to show
what that looks like on a machine close enough to a real one that the answer counts for something.

And that last part is the whole reason it exists. There are plenty of virtual commissioning demos.
Most are a conveyor with three boxes on it, or a rendered animation in a slide deck. You cannot test
a control program against either: they show that a picture can move, not that a program is correct.

So this project takes the opposite approach:

- **A real machine, with real processes.** A two-level pallet conveyor and five processing stations
  that identify, mark, inspect, transfer, press, check and cap a two-slot workpiece. 83 devices,
  7 functional groups.
- **A real control program drives it.** Not a script inside the model — an actual PLC program,
  talking to fieldbus terminals, that has no idea it is running against a twin.
- **The awkward parts are kept.** Stations that interlock. Grippers whose cylinder limit does not
  prove they are holding anything. Resets that deadlock the whole group if you write them wrong.
  These are what a real commissioning finds, so a model that removes them proves nothing.

## Honest simulation, and why it is the hard part

A simulation your control program knows about is not a test.

If the model is driven by the same logic being tested, or the sensors always agree, or cylinders move
instantly and nothing ever jams, then every program passes — including the broken ones. That is how a
demo can look impressive and be worthless.

The structure here is built to prevent that:

- The control program talks to **fieldbus terminals**, exactly as it would on the real machine. The
  twin sits behind the simulated side of the bus. Nothing about the program changes when it runs
  against steel.
- What the machine *does* is written down as a **contract**, separately from any one PLC's
  implementation of it — so you can check whether a program actually satisfies it, rather than
  checking whether it runs.
- The description of the machine is **generated from the twin**, so the documentation cannot quietly
  drift away from the thing it describes.

## Who it is for

- **Controls engineers** who want a serious machine to write and test PLC code against, without
  owning one.
- **Students and people learning automation** who want to see how a real line is structured,
  sequenced and recovered — the interlocks and the failure handling, not just the happy path.
- **Anyone evaluating virtual commissioning** who wants to judge it on a real example.

You need a PC. You do not need a machine, a lab, or a licence server to start.

> New to the abbreviations? [05 · Glossary](05-glossary.md) explains PLC, MIL/SIL/HIL, fieldbus,
> PackML and the rest in plain language.

## The ways to run it

| Mode | | The machine is driven by | You need |
|---|---|---|---|
| **MIL** | Model in the Loop | C# sequences inside Unity — an abstract animation of the process | Nothing but the twin |
| **SIL** | Software in the Loop | A real PLC program on an **emulated** runtime — TwinCAT on this PC, PLCSIM Advanced | The runtime |
| **HIL** | Hardware in the Loop | The same PLC program on **real controller hardware** | The controller |

**SIL and HIL are the same setup.** The twin, the twin device layer and the control program are
identical; only where the PLC executes changes. That is the property that makes a virtual
commissioning result worth anything — you validate in SIL and the program moves to hardware
unchanged.

MIL is for seeing the machine and understanding the process. It proves nothing about a control
program, and it is not meant to.

See [02 · Setup](02-setup.md) for all three.

## Any control system

The twin is one thing; the control system that drives it is another. Swapping it is meant to be
straightforward, and the twin contains nothing vendor-shaped.

| Platform | Status |
|---|---|
| **Beckhoff / TwinCAT** | Working today — control program, twin device layer, web HMI |
| **Siemens / TIA** | In progress. The Unity scene is ready; the PLC program is not written |
| **Anything else** | Planned — **and this is where help is most wanted** |

Everything needed to implement another one already exists: the machine's structure is published as
machine-readable JSON, and its behaviour as a platform-neutral contract. The setups are drawn out in
[04 · Architecture](04-architecture.md), and contributions are very welcome —
see [CONTRIBUTING.md](../CONTRIBUTING.md).

## How the repository is organised

| Module | Path | Role |
|---|---|---|
| **Unity twin** | `Unity/` | The digital twin of the machinery, on Open Commissioning |
| **Beckhoff** | `Beckhoff/` | TwinCAT 3 implementation. Active and complete |
| **Siemens** | `Siemens/` | TIA port. Work in progress |

Each vendor module is a **separate, optional repository** you clone into the main repo's root, where
its path is gitignored so the two do not collide. Take only the platform you use. Nothing in the
main repository depends on a vendor module being present, and each module carries a committed copy
of the machine's structure so it also builds on its own.

Which modules exist and which versions pair with this twin is in
[COMPATIBILITY.md](../COMPATIBILITY.md).

## Where the documentation lives

The pages here describe **the machine and the twin**. Anything about a particular control platform —
how to install it, how its projects are arranged — is documented by that platform's own repository,
and these pages link out to it.

Within that, the machine is described in two halves:

| | Where | Written by |
|---|---|---|
| **What the machine is made of** — every device, its type, its address | [the machine pages](context/machine.md) | generated from the Unity twin, so it cannot drift |
| **How the machine behaves** — sequences, interlocks, faults, recovery | [the behaviour contracts](reference/transport-behaviour.md) | by hand, and they apply to every control platform equally |

Because the first half is generated, editing one of those pages achieves nothing — the next build
overwrites it. [04 · Architecture](04-architecture.md) explains why it is built that way.

## Where to go next

| You want to | Read |
|---|---|
| Look up an abbreviation | [05 · Glossary](05-glossary.md) |
| Run the demo | [02 · Setup](02-setup.md), then [03 · Usage](03-usage.md) |
| Understand how the twin is built | [04 · Architecture](04-architecture.md) |
| Connect your own control system | [Other control platforms](04-architecture.md#7-other-control-platforms), then [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Know what the machine is made of | [The machine](context/machine.md) |
| Know how it behaves | [Behaviour contracts](reference/transport-behaviour.md) |
| Run it on TwinCAT | [Beckhoff documentation](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/README.md) |

## Credits

**The machine itself comes from [Villette Oh](https://grabcad.com/villette.oh-1).** The CAD model of
the laser welding and assembly system — [*Laser Welding & Assembly System (PSA
OPCV)*](https://grabcad.com/library/laser-welding-assembly-system-psa-opcv-1), published on GrabCAD —
is what every shape in this twin was built from. Without it there would be no machine to model, only
another demo with three boxes on a conveyor. Thank you.

**Thanks to Andreas Fast** for the Siemens expertise, and for the PLC project architecture and
design that this project's control side is built on.

**Built on [Open Commissioning](https://github.com/OpenCommissioning)** by SpiraTec AG — the
`com.open-commissioning.core` and `com.open-commissioning.ui` Unity packages, and the OC Assistant
TwinCAT tooling. It is the foundation the whole twin stands on.

Also used:

| | |
|---|---|
| [`com.pilar.context`](https://github.com/Preliy/unity-pilar-context) | the engineering context carried by each part of the twin |
| [Unity-URP-Outline](https://github.com/CristianQiu/Unity-URP-Outline) | selection outlines |
| [UniTask](https://github.com/Cysharp/UniTask) | async sequences |
| [NaughtyAttributes](https://github.com/dbrizov/NaughtyAttributes) | editor tooling |

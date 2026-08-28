# Glossary

Automation is full of abbreviations. Here is what the ones used in these pages mean, in plain
language. Nothing here is specific to this project unless it says so.

## The big idea

**Virtual commissioning** — testing a machine's control program against a simulation of the machine,
before the real one exists or while it is still being built. The point is to find the mistakes early,
when fixing one costs an afternoon instead of a week on site.

**Digital twin** — a model of a real machine that behaves like the real machine: parts move, sensors
switch, cylinders take time to travel. In this project the twin is built in **Unity** and is what you
see on screen.

**MIL · SIL · HIL** — the three ways to run a twin, and the difference is only *what drives it*:

| | Stands for | What drives the machine |
|---|---|---|
| **MIL** | Model in the Loop | Scripts inside the model itself. An animation — good for looking at the machine, proves nothing about a control program |
| **SIL** | Software in the Loop | A real control program, running on emulated controller software on your PC |
| **HIL** | Hardware in the Loop | The same control program, running on real controller hardware |

## Control systems

**PLC** — Programmable Logic Controller. The industrial computer that runs a machine: it reads the
sensors, decides what to do, and switches the motors and valves. Every real production machine has
one.

**Control program** — the software running on the PLC. In this project it is the thing being tested.

**Control platform** — a whole controls ecosystem: the controller, its programming software and its
fieldbus. Beckhoff/TwinCAT and Siemens/TIA are two. This project keeps one **module** per platform.

**PackML** — a widely used standard for how a machine's states are named and how it moves between
them (stopped, starting, executing, aborting, resetting …). The operator panel buttons in this
machine follow it.

**ST** — Structured Text, the text programming language most PLC programs on this machine are
written in. It looks a little like Pascal.

**FB** — Function Block. A reusable block of PLC code with its own memory, roughly what other
languages call a class instance. One cylinder in the machine is served by one function block.

**GVL** — Global Variable List. A named list of variables a PLC program shares across its parts.

**HMI** — Human Machine Interface. The screen an operator uses to run the machine.

## Signals and buses

**I/O** — Inputs and Outputs. The machine's senses and muscles: an input is a sensor telling the PLC
something, an output is the PLC switching something on.

**Fieldbus** — the network that carries I/O between the PLC and the terminals out on the machine.
The important part of this project is that the control program talks to a fieldbus, exactly as it
would on the real machine, and never talks to the simulation directly.

**EtherCAT** — a fast fieldbus, made by Beckhoff, used by the TwinCAT setup here.

**PROFINET** — a fast fieldbus, widely used with Siemens controllers.

**ADS** — Automation Device Specification. Beckhoff's way for two programs on a PC to exchange data.
Unity uses it to talk to the simulation project.

**Process image** — the block of memory holding the current value of every input and output, updated
once per PLC cycle.

**Cycle time** — how often the PLC runs its program from top to bottom. 1 ms here. Everything the
machine does happens in those steps.

**Bit mapping** — which individual bit of a byte carries which signal. A camera might report "ready"
on bit 0 and "busy" on bit 1 of the same byte, so the mapping is the only thing that says what a
value means. The machine pages state it as a table per device.

## Products this project uses

**Open Commissioning (OC)** — the open-source framework this twin is built on: a Unity package of
machine components, a TwinCAT library, and the OC Assistant tool that keeps the two in step. By
SpiraTec AG. See [github.com/OpenCommissioning](https://github.com/OpenCommissioning).

**OC Assistant** — the tool that synchronises the Unity scene and the simulation project: the
hierarchy, the components, their metadata and the interface GVLs. It also scans a fieldbus and
creates the emulation unit for it.

**TwinCAT** — Beckhoff's control software for a PC. Here it does two jobs: it hosts the simulation
project, and it can also run the control program being tested.

**TIA Portal** — Siemens' engineering software for their controllers.

**PLCSIM Advanced** — Siemens' emulator: a Siemens PLC running as software on a PC.

**Unity** — the real-time 3D engine the twin is built in.

**CAD** — Computer Aided Design. The 3D drawings of the real machine, which is where this twin's
shapes come from.

## Words used in this project

**FG** — *Funktionsgruppe*, functional group. One self-contained part of the machine, such as the
conveyor or the press station. This machine has seven: `FG_System`, `FG_Transport`, and `FG_01` to
`FG_05`.

**Station** — one working position on the conveyor, where a pallet is stopped so a group can work on
it.

**Index unit** — the transport station that stops a pallet, lifts it to hold the part still, asks a
functional group to run, and only releases the pallet when the group reports it has finished.

**Pallet** — the carrier that travels around the conveyor with the workpiece on it. This one has two
slots.

**Device** — one addressable thing in the machine: a cylinder, a sensor, a drive, a lamp.

**Device type** — the *kind* of device, such as `Cylinder` or `SensorBinary`. One page describes each
type; every device in the machine is an instance of one.

**Simulation unit** (also *emulation unit*) — the TwinCAT project holding one function block per twin
device, and the emulated fieldbus. It sits between Unity and the control program, in every setup,
whichever vendor's controller is being tested.

**Twin PLC path** — the address the twin uses for a device, such as `MAIN.FG_01.P_Camera`. A control
platform usually spells the same device differently, so the two are never mixed on one page.

**Behaviour contract** — a written description of what the machine must do: the sequences, the
interlocks, the fault codes and the recovery. It belongs to the machine, not to any one control
platform, so every platform running this line has to honour the same one.

**ContextNode** — the engineering description carried by a part of the twin, as key/value entries in
the Unity scene. Some keys are synced from the project (`oc.plcPath`, `oc.deviceType`); the rest are
authored by a human and say what the part is *for*. Everything generated downstream comes from them.

**Knowledge base** — the generated machine description in [`context/`](context/): what exists, where,
and of what type. Generated from the twin, so it cannot drift; never edited by hand.

**Handoff** — [`context/.machine.json`](context/.machine.json), the machine's structure as
schema-versioned JSON. It is what a control platform builds against, and each module keeps its own
committed copy so it builds without this repository present.

**Module** — one control platform's realisation of this machine: a separate, optional repository
cloned into this one's root, holding that platform's projects and its own documentation.

**Prefab** — Unity's word for a reusable object saved once and placed many times. The whole machine
is one prefab, which is why every scene shows the same machine.

**Scene** — one Unity file you open and press Play on. There is one per control platform, plus the
MIL one.

**†** — on a generated machine page, marks something that belongs to *one* control platform's
example rather than to the machine itself. Today only the operator panel is marked.

**PSA OPCV** — the name of the original machine this twin was modelled from, carried over from the
CAD model it was built out of.

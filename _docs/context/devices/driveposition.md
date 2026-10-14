<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# DrivePosition

**A positioned axis: told where to be, it travels there at its own speed and reports where it actually is and whether it is moving.**

Twin device type · twin FB `FB_Sercos_VC` · **2 instances** in FG_Transport · Unity component `OC.Components.DrivePosition`

## What it is

A servo axis — in this machine, the carriage of each lift unit, which it carries between the lower
and upper conveyor levels. Unlike a cylinder it has no end positions of its own: any position along
its travel is a valid target, and which positions *matter* is decided by the control program.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `ControlData` | Target position, in the twin's units (mm) |
| `StatusData` | Actual position, in the twin's units (mm) |
| `Status.6` | Moving |
| `Status.7` | Initialisation pulse — one second, after the device was restored from a metadata snapshot |

No control bit is used. The target position is the whole of the command.

## How the twin models it

Each cycle the axis moves towards the target at a constant `Speed` (per instance, units per second)
— no acceleration ramp, no following error. With `Speed` at zero it jumps to the target at once.
The twin is a **follower**: it does not close a position loop, plan a profile or know about
referencing. Whatever position the simulation side sends, it goes to.

## Watch out

**The twin's zero is not the control program's zero.** The twin starts at its own zero, which here
is the lower conveyor level. The control program only knows a position once it has referenced the
axis on a sensor, and its zero is wherever that sensor is — so the same carriage reads different
numbers on the two sides. A position is meaningful only after referencing, and comparing it with the
twin's `StatusData` needs the offset.

**The component has no travel limits.** Nothing in `DrivePosition` stops at the end of travel; the
limit sensors beside it report, they do not restrain. Keeping the axis inside its travel is the
control program's job — which is exactly what a twin is there to prove.

**`Status.7` is not a health bit.** It is a one-second pulse after a metadata restore, and it must not
be wired as "drive ready".

## In this machine

Lift servo drive. Positions the carriage between the lower and upper conveyor levels.

**Signal** — Position-controlled. Referenced on B_AxisMin, which reads 0 mm; the lower conveyor level is at 10 mm and the upper at 364 mm.

There are **2** of them, in FG_Transport:

| Device | Twin PLC path | Group |
|---|---|---|
| `Y_Lift` | `MAIN.FG_Transport.Lift01_Y_Lift` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Lift02_Y_Lift` | FG_Transport |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/driveposition.md)
- **Siemens** — _no knowledge base published yet_

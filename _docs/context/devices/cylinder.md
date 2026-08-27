<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# Cylinder

**A pneumatic cylinder. Travels between a retracted and an extended end position, taking real time to get there, and reports when it arrives.**

Twin device type · twin FB `FB_Cylinder` · **35 instances** in FG_01, FG_03, FG_04, FG_05, FG_Transport · Unity component `OC.Components.Cylinder`

## What it is

The workhorse of the machine: 35 of the 83 devices are cylinders. Stoppers, lifts, grippers, gates
and the press are all cylinders. A real one is driven by air through one or two solenoid valves and
usually has a sensor at each end of its stroke telling the PLC it has arrived.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Retract — drive towards the retracted end |
| `Control.1` | Extend — drive towards the extended end |
| `Status.0` | At the retracted end |
| `Status.1` | At the extended end |

**Both status bits are false while it is travelling.** That is the whole point of simulating it:
movement takes time, so a program that assumes an instant arrival fails here exactly as it would on
the real machine.

## How the twin models it

Travel is a stroke completed over a configured time — half a second by default, separately settable
for each direction — mapped onto the part's actual movement through a motion curve. The two end
positions are set per instance, so the same component drives a 10 mm gripper jaw and a full lift
stroke.

Three valve types, set per instance:

| Type | Behaviour with no command |
|---|---|
| **Double acting** | Stays where it is. Moves only while exactly one of the two control bits is set — set both, and it does not move |
| **Single acting, spring retracts** | Returns to the retracted end |
| **Single acting, spring extends** | Returns to the extended end |

## Watch out

- **An end-position bit is not proof of what the cylinder is holding.** Gripper jaws closed on
  nothing reach the extended end *sooner* than jaws closed on a part, and the bit is true either way.
  Only a dedicated part sensor says a part is held.
- **A de-energised double solenoid does not hold a gripped part in this twin.** The scene wires the
  cylinder's *moving* signal to the gripper's grip, so dropping the command drops the part. Grips
  are re-asserted every cycle for exactly this reason — see
  [the transport behaviour contract](../../reference/transport-behaviour.md).

## In this machine

There are **35** of them, in FG_01, FG_03, FG_04, FG_05, FG_Transport:

| Device | Twin PLC path | Group | Role / Signal |
|---|---|---|---|
| `Y_Gate1` | `MAIN.FG_01.Y_Gate1` | FG_01 | Guard gate 1. Must be closed before the FG_01 laser may fire. |
| `Y_Gate2` | `MAIN.FG_01.Y_Gate2` | FG_01 | Guard gate 2. Must be closed before the FG_01 laser may fire. |
| `Y_Gripper` | `MAIN.FG_01.Y_Gripper` | FG_01 | Double solenoid with both limits read. EXTENDED clamps the payload for marking and reading; retracted releases. |
| `Y_Platform` | `MAIN.FG_01.Y_Platform` | FG_01 | Double solenoid with both limits read. Service positioning of the laser head. Never actuated during the production cycle. |
| `Y_ReaderWindow` | `MAIN.FG_01.Y_ReaderWindow` | FG_01 | Double solenoid with both limits read. EXTENDED opens the window for the read; retracted shields the optics and is home. |
| `Y_AxisR1` | `MAIN.FG_03.Y_AxisR1` | FG_03 | Double solenoid with both limits read. Rotary. Retracted is 0 deg and the receiving orientation; extended is 180 deg and the placing one. |
| `Y_AxisX1` | `MAIN.FG_03.Y_AxisX1` | FG_03 | Double solenoid with both limits read. MAX is raised; arm 1 rises once and stays up for the whole cycle. |
| `Y_AxisX2` | `MAIN.FG_03.Y_AxisX2` | FG_03 | Double solenoid with both limits read. MAX is the transfer position, min is home over slot 1. |
| `Y_AxisY1` | `MAIN.FG_03.Y_AxisY1` | FG_03 | Double solenoid with both limits read. MAX is the transfer position, min is home over slot 2. |
| `Y_AxisY2` | `MAIN.FG_03.Y_AxisY2` | FG_03 | Double solenoid with both limits read. The axis factor is inverted, so MAX is LOWERED. |
| `Y_Gripper1` | `MAIN.FG_03.Y_Gripper1` | FG_03 | Double solenoid with both limits read. EXTENDED grips. The limit proves the jaws moved, NOT that they caught anything - only B_Detect1 says that. |
| `Y_Gripper2` | `MAIN.FG_03.Y_Gripper2` | FG_03 | Double solenoid with both limits read. EXTENDED grips. The limit proves the jaws moved, NOT that they caught anything - only B_Detect2 says that. |
| `Y_AxisZ` | `MAIN.FG_04.Y_AxisZ` | FG_04 | Double solenoid with both limits read. EXTENDED presses down onto the part; retracted is clear. A double solenoid so an abort leaves it where it is. |
| `Y_AxisR` | `MAIN.FG_05.Y_AxisR` | FG_05 | Double solenoid with both limits read. Rotary. Extended is the fitting orientation, retracted is home. |
| `Y_AxisX` | `MAIN.FG_05.Y_AxisX` | FG_05 | Double solenoid with both limits read. MAX is over the pallet, min is over the cap feed. |
| `Y_AxisZ1` | `MAIN.FG_05.Y_AxisZ1` | FG_05 | Double solenoid with both limits read. EXTENDED lowers the cap onto the part on the pallet side. |
| `Y_AxisZ2` | `MAIN.FG_05.Y_AxisZ2` | FG_05 | Double solenoid with both limits read. EXTENDED lowers to the cap at the pick position on the feed side. |
| `Y_CapsSourceStopper` | `MAIN.FG_05.Y_CapsSourceStopper` | FG_05 | Double solenoid with both limits read. EXTENDED BLOCKS the feed path and the queue accumulates against it. The opposite sense to a transport stopper. |
| `Y_Gripper` | `MAIN.FG_05.Y_Gripper` | FG_05 | Double solenoid with both limits read. EXTENDED grips the cap. The limit proves the jaws moved, NOT that they caught one - only B_Detect says that. |
| `Y_Lift` | `MAIN.FG_Transport.Index01_Y_Lift` | FG_Transport | Double solenoid with both limits read. EXTENDED raises the carriage and fixes the pallet clear of the belt; retracted is home. |
| `Y_Stopper` | `MAIN.FG_Transport.Index01_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Lift` | `MAIN.FG_Transport.Index02_Y_Lift` | FG_Transport | Double solenoid with both limits read. EXTENDED raises the carriage and fixes the pallet clear of the belt; retracted is home. |
| `Y_Stopper` | `MAIN.FG_Transport.Index02_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Lift` | `MAIN.FG_Transport.Index03_Y_Lift` | FG_Transport | Double solenoid with both limits read. EXTENDED raises the carriage and fixes the pallet clear of the belt; retracted is home. |
| `Y_Stopper` | `MAIN.FG_Transport.Index03_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Lift` | `MAIN.FG_Transport.Index04_Y_Lift` | FG_Transport | Double solenoid with both limits read. EXTENDED raises the carriage and fixes the pallet clear of the belt; retracted is home. |
| `Y_Stopper` | `MAIN.FG_Transport.Index04_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Lift` | `MAIN.FG_Transport.Index05_Y_Lift` | FG_Transport | Double solenoid with both limits read. EXTENDED raises the carriage and fixes the pallet clear of the belt; retracted is home. |
| `Y_Stopper` | `MAIN.FG_Transport.Index05_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Lift` | `MAIN.FG_Transport.Lift01_Y_Lift` | FG_Transport | Double solenoid with both limits read. Moves the carriage between the lower and upper conveyor levels. |
| `Y_Lift` | `MAIN.FG_Transport.Lift02_Y_Lift` | FG_Transport | Double solenoid with both limits read. Moves the carriage between the lower and upper conveyor levels. |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper01_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper02_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper03_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper04_Y_Stopper` | FG_Transport | Double solenoid with both limits read. RETRACTED (min) holds the pallet; EXTENDING (max) releases it - the blade drops out of the way. |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/cylinder.md)
- **Siemens** — _no knowledge base published yet_

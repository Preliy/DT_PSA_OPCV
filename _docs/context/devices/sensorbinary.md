<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# SensorBinary

**A presence sensor. Reports whether something is inside its beam — one bit, no commands.**

Twin device type · twin FB `FB_SensorBinary` · **25 instances** in FG_01, FG_05, FG_Transport · Unity component `OC.Components.SensorBinary`

## What it is

A light barrier or proximity switch: the machine's eyes. It is how the control program knows a
pallet has arrived at a station or has left it again.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Status.0` | Something is detected |

No control bits. The PLC cannot command a sensor, only read it.

## How the twin models it

The sensor is a real volume in the 3D scene — a thin beam of a settable length, or a box fitted to
the geometry — and it switches when a part physically enters it. Nothing tells the sensor a part is
there; it sees one because one is there. That is what makes a mis-timed release or a part left
behind show up in the twin the way it would on the machine.

Each instance can be inverted, for a sensor whose real-world contact is normally closed.

## In this machine

There are **25** of them, in FG_01, FG_05, FG_Transport:

| Device | Twin PLC path | Group | Role / Signal |
|---|---|---|---|
| `B_SafetyGate1` | `MAIN.FG_01.B_SafetyGate1` | FG_01 | Monitors guard gate 1 for the FG_01 laser interlock. |
| `B_SafetyGate2` | `MAIN.FG_01.B_SafetyGate2` | FG_01 | Monitors guard gate 2 for the FG_01 laser interlock. |
| `B_Part` | `MAIN.FG_05.B_Part` | FG_05 | Binary presence sensor. On the FEED: a cap has arrived at the pick position. Once the gripper lifts one away it reports the NEXT one. |
| `B_Detect` | `MAIN.FG_Transport.Index01_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Index01_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Index02_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Index02_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Index03_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Index03_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Index04_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Index04_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Index05_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Index05_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Lift01_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Lift01_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Lift02_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Lift02_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Stopper01_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Stopper01_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Stopper02_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Stopper02_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Stopper03_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Stopper03_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |
| `B_Detect` | `MAIN.FG_Transport.Stopper04_B_Detect` | FG_Transport | Binary presence sensor. Active while a pallet is at this station. Occupied and CanAccept are computed from it. |
| `B_Exit` | `MAIN.FG_Transport.Stopper04_B_Exit` | FG_Transport | Binary presence sensor. Its RISING EDGE clears the transfer latch, in every PackML state. Read the edge, never the level. |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/sensorbinary.md)
- **Siemens** — _no knowledge base published yet_

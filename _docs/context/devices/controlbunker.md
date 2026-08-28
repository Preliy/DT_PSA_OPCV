<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# ControlBunker

**The cap feeder: a vibrating bunker and a short conveyor that bring caps to the pick position, switched by two bits.**

Twin device type · twin FB `FB_DeviceByte` · **1 instance** in FG_05 · Unity component `Preliy.Demo.ControlBunker`

## What it is

A parts feeder, of the kind that sits beside an assembly station and keeps a supply of small parts
coming. A vibration table shakes caps out of a bunker onto a narrow conveyor, which carries them to
where a gripper can pick one up. It is project-specific: no Open Commissioning component covers it,
so it is a small script on top of a plain byte link.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `ControlData.0` | Bunker on — run the vibration table |
| `ControlData.1` | Conveyor on — run the caps conveyor |

**No status bits.** The feeder does not tell the PLC anything: not whether it is running, not whether
it has caps left. Whether a cap is actually at the pick position is answered by a separate sensor.

## Watch out

**A feeder is not a sequenced device.** It is switched on and left running while the station works —
it does not run "one cap at a time" and there is nothing to wait for. See
[the FG_05 behaviour contract](../../reference/fg-05-behaviour.md).

## In this machine

Cap bunker. Feeds small caps onto the short conveyor that presents them at the pick position.

**Signal** — Two bool outputs from the PLC and no status bits - the bunker reports nothing back. MIL turns both on together for as long as it is enabled.

Every instance carries the same bit mapping:

| Symbol | Meaning |
|---|---|
| `ControlData.0` | enables the vibration table that feeds the bunker |
| `ControlData.1` | enables the short caps conveyor that carries them to the pick position |

2 of 8 control bits used. The status byte is unused.

There is **1** of them, in FG_05:

| Device | Twin PLC path | Group |
|---|---|---|
| `Y_CapsSource` | `MAIN.FG_05.Y_CapsSource` | FG_05 |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/controlbunker.md)
- **Siemens** — _no knowledge base published yet_

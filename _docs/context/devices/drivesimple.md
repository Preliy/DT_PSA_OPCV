<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# DriveSimple

**A conveyor motor: run forwards, run backwards, or stop. Reports the speed it actually reached and whether it is moving.**

Twin device type · twin FB `FB_Drive` · **4 instances** in FG_Transport · Unity component `OC.Components.DriveSimple`

## What it is

The motors that move pallets: the conveyor belts on both levels, and the short belt on each lift
carriage. Not a positioning axis — it has no target position and no idea where anything is. It runs
until it is told to stop, and something else, usually a sensor, decides when that is.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Run forwards |
| `Control.1` | Run backwards |
| `Status.6` | Moving |
| `StatusData` | Actual speed |

Setting both direction bits, or neither, commands a stop.

## How the twin models it

The speed ramps towards the commanded direction at a configured acceleration rather than jumping to
it, and the resulting speed drives everything standing on the belt. Each instance has its own speed
and acceleration.

## Watch out

**A running belt is not a moving pallet.** The motor reports its own speed, and nothing else. Whether
a pallet actually arrived is a sensor's answer — which is exactly the mistake a twin is there to
catch.

## In this machine

**Signal** — Simple drive: forward and backward run bits out, one drive-active bit back. No speed reference and no encoder.

There are **4** of them, in FG_Transport:

| Device | Twin PLC path | Group |
|---|---|---|
| `M_Conveyor` | `MAIN.FG_Transport.Lift01_M_Conveyor` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Lift02_M_Conveyor` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Transport01_M_Conveyor` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Transport02_M_Conveyor` | FG_Transport |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/drivesimple.md)
- **Siemens** — _no knowledge base published yet_

<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# LinkByte

**A plain byte in each direction, with no behaviour of its own — the way to give the PLC a device Open Commissioning has no component for.**

Twin device type · twin FB `FB_DeviceByte` · **1 instance** in FG_01 · Unity component `OC.Components.LinkByte`

## What it is

Sometimes the machine has something that is not a cylinder, a sensor or a drive: a laser module, a
feeder, a piece of third-party equipment with its own protocol. LinkByte is the generic answer — eight
control bits down, eight status bits up, and whatever they mean is decided by how the scene is wired.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `ControlData.0` … `ControlData.7` | Whatever the scene wires each bit to |
| `StatusData.0` … `StatusData.7` | Whatever the scene reports back |

Because the meaning is per instance, it is stated per instance: look for the **Bit mapping** section
on the group page that owns the device.

## How the twin models it

Each control bit raises an event when it changes, and those events are wired in the Unity inspector
to whatever should happen — start an animation, enable a conveyor, fire a laser. Status bits are set
by whatever in the scene knows the answer.

## Watch out

**A LinkByte promises nothing.** A cylinder reports arrival because the component measures it; a
LinkByte reports only what someone wired to it. If a bit has no status wired back, the PLC gets no
confirmation the thing happened — which is a fact about the real device as often as it is about the
model.

## In this machine

**Signal** — One control bit out enables the laser module; held high for 1 s it applies the mark. NO status bits - the PLC gets no confirmation that it fired.

There is **1** of them, in FG_01:

| Device | Twin PLC path | Group |
|---|---|---|
| `Y_LaserMark` | `MAIN.FG_01.Y_LaserMark` | FG_01 |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/linkbyte.md)
- **Siemens** — _no knowledge base published yet_

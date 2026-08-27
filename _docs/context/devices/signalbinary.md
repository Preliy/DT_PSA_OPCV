<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# SignalBinary

**One bit to the PLC that is worked out somewhere else in the twin, rather than measured by a sensor of its own.**

Twin device type · twin FB `FB_SensorBinary` · **4 instances** in FG_03, FG_04, FG_05 · Unity component `OC.Components.SignalBinary`

## What it is

It looks like a sensor to the control program — the same single status bit, the same function block
— but there is no beam anywhere. It publishes a value another component in the scene computed.

Use it for a **verdict** rather than an observation: "the press bottomed out with nothing seated
under it" is a conclusion drawn from a cylinder position and a sensor together, not something any one
sensor can see.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Status.0` | The signal is true |

## How the twin models it

It is pointed at another component in the scene that produces a boolean, and mirrors it. In this
machine the source is usually a small project script, such as the one that decides whether the press
seated a part.

## In this machine

There are **4** of them, in FG_03, FG_04, FG_05:

| Device | Twin PLC path | Group | Role / Signal |
|---|---|---|---|
| `B_Detect1` | `MAIN.FG_03.B_Detect1` | FG_03 | Grip witness for arm 1. Active while gripper 1 actually holds the part. |
| `B_Detect2` | `MAIN.FG_03.B_Detect2` | FG_03 | Grip witness for arm 2. Active while gripper 2 actually holds the part. |
| `B_NIO` | `MAIN.FG_04.B_NIO` | FG_04 | A VERDICT, not a sensor reading. Active means the press bottomed with nothing correctly seated. Only meaningful at the bottom limit with the hold expired. |
| `B_Detect` | `MAIN.FG_05.B_Detect` | FG_05 | Grip witness in the jaws. Active while this unit carries a cap. NOT the same question as B_Part. |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/signalbinary.md)
- **Siemens** — _no knowledge base published yet_

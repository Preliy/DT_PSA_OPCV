<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# The machine

![The machine](../images/Machine_Overview.png)

*The line seen from the front - FG_System, FG_Transport and FG_01 to FG_05 assembled together.*

## Function

Demo assembly line on a Bosch TS style two level pallet conveyor. Pallets carrying a two slot workpiece circulate through five processing groups on the upper level.

## ProcessFlow

Lower level accumulates pallets and feeds them left to Lift 1, which raises each pallet to the upper level. Stoppers and sensors release one pallet at a time between FG_01 and FG_05. After FG_05 the pallet reaches Lift 2, which returns it to the lower conveyor where the part travels right and is destroyed.

## Layout

Two conveyor levels. The lower accumulates and returns, the upper carries FG_01 to FG_05. Lift 1 raises pallets at one end, Lift 2 lowers them at the other. Each group has its own Index unit that stops and lifts the pallet.

## Functional groups

| Group | Control PLC path | Symbols | Behaviour | Function |
|---|---|---:|---|---|
| [FG_System](fg-system.md) | `MAIN.Machine.FG_System` | 10 | [contract](../reference/fg-system-safety.md) | Cell infrastructure - safety enclosure, interlocked doors, operator panel, signal tower and monitors. |
| [FG_Transport](fg-transport.md) | `MAIN.Machine.FG_Transport` | 42 | [contract](../reference/transport-behaviour.md) | Two level pallet conveyor in the Bosch TS style. |
| [FG_01](fg-01.md) | `MAIN.Machine.FG_01` | 9 | [contract](../reference/fg-01-behaviour.md) | Identifies the payload and applies a laser mark. |
| [FG_02](fg-02.md) | `MAIN.Machine.FG_02` | 1 | [contract](../reference/fg-02-behaviour.md) | Optical inspection. |
| [FG_03](fg-03.md) | `MAIN.Machine.FG_03` | 9 | [contract](../reference/fg-03-behaviour.md) | Transfers the part from slot 1 to slot 2 of the pallet, flipping it 180 degrees on the way. |
| [FG_04](fg-04.md) | `MAIN.Machine.FG_04` | 2 | [contract](../reference/fg-04-behaviour.md) | Presses the part home into its slot and checks that it seated correctly. |
| [FG_05](fg-05.md) | `MAIN.Machine.FG_05` | 10 | [contract](../reference/fg-05-behaviour.md) | Fits a cap from the bunker onto the part carried on the pallet. |

**83 twin devices** across 7 groups - see [plc-symbols.md](plc-symbols.md). Each group's page carries its own hierarchy, components and Unity detail, and links to the control implementation in each vendor module.

## Scenes

One machine, one prefab - `Unity/Assets/Demo_1/Prefabs/Machine_1.prefab` - instanced by every scene under `Unity/Assets/Demo_1/Scenes/`. Each scene adds its vendor's operator panel, and that is the only thing they disagree about.

| Scene | Vendor | Symbols | |
|---|---|---:|---|
| `VC_Demo_1_Beckhoff_1` | Beckhoff | 83 | **reference for these pages** |
| `VC_Demo_1_Siemens_1` | Siemens | 83 |  |

15 node(s) differ and are marked † wherever they appear - all of them under an operator panel. Unmarked is the machine.

## Control implementations

This repository is master for **structure**. Each vendor module is master for how that structure is realised in a control platform, and keeps its own knowledge base:

- **Beckhoff** (Beckhoff TwinCAT 3) — [the machine in Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/machine.md)
- **Siemens** (Siemens TIA Portal) — [DT_PSA_OPCV_Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens), _no knowledge base published yet_

## How the groups drive each other

**Every processing group is served by an Index unit in `FG_Transport`.** The Index stops the pallet, lifts it to fix the payload, and only then asks the group to run; the pallet does not move until the group answers. The three invariants that coupling has to preserve, and the step chain that enforces them, are in [`transport-behaviour.md`](../reference/transport-behaviour.md).

Scene wiring measured **2026-08-23T17:11:57Z** from the live Editor, not inferred from naming.

```
Index01     -> Index02  -- serves FG_01
Index02     -> Index03  -- serves FG_02
Index03     -> Index04  -- serves FG_03
Index04     -> Index05  -- serves FG_04
Index05     -> Stopper04  -- serves FG_05
Stopper04   -> Lift02
Lift02      -> Stopper01  (lowers)
Stopper01   -> Stopper02
Stopper02   -> Lift01
Lift01      -> Stopper03  (raises)
Stopper03   -> Index01
```

11 stations in a closed ring - the last returns to the first.

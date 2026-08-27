# Reference — authoring ContextNode entries

## Key vocabulary in use

Keys are **free-form**. Nothing validates them. This table is the convention this project follows so
the exported tree stays consistent enough for a downstream consumer to rely on — keep to it unless
the machine gives you a reason not to, and record any new key you introduce here.

| Tier | Keys | Notes |
|---|---|---|
| `machine` | `Purpose`, `ProcessFlow`, `Layout` | What the line produces, the order stations act in |
| `group` | `Function`, `Process`, `Interfaces`, `Safety` | `Interfaces` = what it hands off to / receives from |
| `assembly` | `Function`, `Role`, `PlcTree`, `BitLayout` | `Role` is instance-specific; see the prefab rule |
| `device` | `Function`, `Signal`, `BitLayout` | Keep short. `Signal` = what the PLC reads/writes here |

`BitLayout` started as a `PanelSampler` key and now also serves any device whose PLC interface is a
packed byte rather than a single value — `Y_Camera` and `Y_CapsSource`. Use it when the bit
assignment is the fact worth recording, and keep `Signal` for what the device does with those bits.
A device that uses a single bit needs `Signal` alone — `Y_LaserMark` carries no `BitLayout`.

In `Demo_1` today: `Function` 131, `Role` 25, `PlcTree` 14, `Signal` 13, `Process` 11, `Interfaces` 6,
`Safety` 3, `BitLayout` 2, and `Purpose` / `ProcessFlow` / `Layout` once each on the root.

`PlcTree` earns its place only for the **negative** case — "carries no OC `Hierarchy`, so it opens no
level in the PLC path". Sync cannot express that, because the absence of `oc.hierarchyRole` is not a
statement. Do **not** use it to say a node *is* a group or a sampler: `oc.hierarchyRole` already says
so and keeps itself correct.

## Three trees, not one

Tiers describe *documentation granularity*. Two paths describe position, and they are different trees:

- **`scenePath`** — the Unity transform hierarchy, arranged for the scene and the CAD import.
- **`topologyPath`** — the `ContextNode` tree, the structure a human authored. Levels you never
  annotated are simply absent from it, and a target with no node has no topology path at all.

Because every one of the 132 targets in `Demo_1` carries a node, the two currently coincide. They
diverge the moment an un-annotated level appears between two nodes — that gap is information, saying
the intervening levels carry no meaning worth documenting.

The PLC's own tree is a **third** axis, and it lives in the same entry list as your writing — under
the `oc.` prefix, written there by `context_sync`. Nothing in the package interprets those keys.

**Never write a prefixed key yourself.** `context_set` refuses them outright: the next sync would
revert the edit, so a hand-written value is a lie with a timer on it. Your own dotted keys
(`Motor.Speed`) are fine — only a prefix matching an installed provider is reserved.

## Reading Open Commissioning's entries

| Key | Value | Meaning | Demo_1 |
|---|---|---|---|
| `oc.plcPath` | `MAIN.FG_01.P_Reader` | Position in the PLC symbol tree | 132 |
| `oc.hierarchyRole` | `group` | Opens a level in the PLC path, joined with `.` | 7 |
| | `sampler` | Opens **no** level; prefixes its children instead, joined with `_` | 13 |
| `oc.deviceType` | `SensorBinary` | The `IDevice` component's type. Present on devices only | 93 |
| `oc.aggregatedBy` | a panel name | A `PanelSampler` folded this device into its own single symbol | 10 |
| `oc.simulationDevice` | `true` | The device exchanges nothing with the PLC and no sampler explains why | 3 |

An `oc.plcPath` proves nothing on its own: every target has one, including pure structure.

## OC component semantics

Standard behaviour — do not re-read the OC package to describe these.

| Component | Means |
|---|---|
| `Cylinder` | Pneumatic actuator, two end positions. Usually drives one or more `Axis` children. |
| `SensorBinary` | Binary presence/position sensor. Reports true when its beam/volume is occupied. |
| `Axis` | Kinematic joint. **Not a PLC device** — it is animated by its parent actuator. |
| `DriveSimple` | Motor with on/off + direction, no position feedback. |
| `TransportLinear` | Conveyor surface that moves payloads placed on it. |
| `TagReader` / `DataReader` | Optical device reading an ID / data payload off a part. |
| `Lock` | Safety interlock on a door. |
| `Button` / `SwitchRotary` | Operator input on a panel or E-stop. |
| `Lamp` | Signal lamp (tower, indicator). |
| `PanelSampler` | Groups an HMI panel's child buttons/lamps under one PLC symbol. |
| `Gripper` | Grasps and carries a payload. |
| `Source` / `Sink` | Spawns / consumes payloads — simulation boundary, not real hardware. |
| `LinkByte` / `SignalBinary` | Raw PLC value link with no physical behaviour of its own. |

Only 12 OC types are `IDevice` and therefore tier `device`. `Demo_1` uses all 12:

`Cylinder` 35, `SensorBinary` 28, `Button` 8, `Lock` 6, `Lamp` 4, `DriveSimple` 4, `TagReader` 2,
`PanelSampler` 2, `SwitchRotary` 1, `LinkByte` 1, `SignalBinary` 1, `ControlBunker` 1 — 93 total.

Note `DataReader` is **not** an `IDevice`, which is why `FG_02/P_Camera` reaches the PLC only through
its child lamp.

## The PLC project tree is defined by Hierarchy, not by transform parenting

`OC.Communication.Hierarchy` is what builds the project tree. A node's PLC path comes from walking up
the chain of `Hierarchy` components to the `Client`; transforms without one are skipped entirely.
There are two modes, and they behave very differently:

| `oc.hierarchyRole` | Meaning | Path effect |
|---|---|---|
| `group` | `Hierarchy` with `IsNameSampler` false | Opens a level, joined with `.` |
| `sampler` | `Hierarchy` with `IsNameSampler` true | Opens **no** level; prefixes children, joined with `_` |
| *(absent)* | No `Hierarchy` | Invisible to the PLC — Unity grouping only |

In `Demo_1` that gives **7 groups** (`FG_01`…`FG_05`, `FG_System`, `FG_Transport`), **13 name
samplers** (the 5 Index units, 4 Stoppers, 2 Lifts, 2 Transports — which is why `FG_Transport` is flat
as `MAIN.FG_Transport.Index01_B_Detect`), and **18 Unity-only wrappers** (`Laser Unit`,
`Barcode Reader`, `Doors`, the `Axis_*` kinematics). Both the group set and the device set match
the scene's `_Project_Tree.xml` exactly.

When a structural node has no `Hierarchy`, say so in a `PlcTree` entry — otherwise a reader will
assume it is a PLC level.

## PanelSampler aggregates children into one symbol

`PanelSampler` holds an ordered `_components` list, **disables each child's own communication**, and
exposes a single `FB_Panel` DWORD instead. Its `LateUpdate` packs each child's status bits into that
link at a running index and unpacks control bits back, so the PLC addresses the whole panel through
one symbol. Used for operator panels and signal towers.

The bit layout is therefore derivable from the scene, and **reordering `_components` changes the PLC
bit assignment** — which is why both panels carry a `BitLayout` entry recording the order. Read it
with:

```bash
unity command eval --code 'var sb=new System.Text.StringBuilder();
foreach (var p in UnityEngine.Object.FindObjectsByType<OC.Interactions.PanelSampler>(
    UnityEngine.FindObjectsInactive.Include, UnityEngine.FindObjectsSortMode.None)) {
  sb.Append(p.gameObject.name).Append(": "); int i=0;
  foreach (var c in p.Components) { if (c==null) continue;
    sb.Append("bit").Append(i).Append("=").Append(c.gameObject.name).Append(" ");
    i+=c.AllocatedBitLength; } }
return sb.ToString();'
```

## Carrying an IDevice is not the same as being a PLC symbol

A node is a real PLC symbol when it carries `oc.deviceType` and **neither** `oc.aggregatedBy` nor
`oc.simulationDevice`. Both of the latter are inferred from a disabled `Link`, which OC overloads —
splitting them is what makes either claim truthful, and downstream code generation must skip both.

**83 of the 180 nodes are PLC symbols**, matching the scene's `_Project_Tree.xml` exactly.
The 13 that are not:

| Count | Nodes | Key | Why |
|---|---|---|---|
| 7 | 6 `Control Panel` buttons + the `OP MODE` switch | `oc.aggregatedBy: H_ControlPanel` | Folded into one `FB_Panel` symbol |
| 3 | signal tower `RED` / `YELLOW` / `GREEN` | `oc.aggregatedBy: H_SignalTower` | Folded into one `FB_Panel` symbol |
| 2 | `Y_Gate1/SimSensor`, `Y_Gate2/SimSensor` | `oc.simulationDevice` | Simulation-only end position feedback |
| 1 | `FG_04/B_NIO/Sensor` | `oc.simulationDevice` | Feeds `PartPressDetector` locally; the PLC sees `B_NIO` |

Say so in the entry when a device is not a PLC symbol. Note also that such devices may share a
resolved `oc.plcPath` — both gate `SimSensor`s resolve to `MAIN.FG_Transport.SimSensor` — which is
harmless precisely because neither becomes a symbol. Among the 80 real symbols there are no
duplicates, and there must never be.

## Project-specific behaviour scripts

Read these to ground a `Function` or `Role` entry. All are `Preliy.Demo.*` under
`Unity/Assets/Demo_1/Scripts/`.

| Script | Drives |
|---|---|
| `SequenceUnit1` … `SequenceUnit5` | One per functional group `FG_01`…`FG_05` |
| `SequenceConveyor` | The `FG_Transport` conveyor loop |
| `SequenceTransferIndex` | A `TS Index Unit` station (5 instances) |
| `SequenceTransferStopper` | A `Stopper Unit` (4 instances) |
| `SequenceTransferLift` | A `TU Lift` (2 instances) |
| `SequenceGate` | A `Gate Typ 1` |
| `SequenceBunker` / `ControlBunker` | The `FG_05` cap feeder |
| `PartPressDetector` | NIO detection on `FG_04/B_NIO` |

These implement `ISimulationBehaviour`; `SimulationBehaviourManager` on `Project` enables them all
when its `_enable` flag is set. Each `SequenceUnitN` seizes its cylinders (`Override.Value = true`)
on enable and releases them on disable — that is the MIL↔PLC handover.

Station handoff: `SequenceTransferIndex` raises `ReadyForOperation` → the station's
`SequenceUnitN.Execute()` → its `OperationComplete` calls back into the Index unit's
`set_OperationDone(true)`, which releases the pallet.

## High-leverage prefab assets

Author type-level context on these once; every instance inherits it. Remember the asset text must be
true of *every* instance — never name one.

| Prefab | Instances | Root components |
|---|---|---|
| `TS Index Unit` | 5 | `Hierarchy`, `SequenceTransferIndex` |
| `Stopper Unit` | 4 | `Hierarchy`, `SequenceTransferStopper` |
| `TU Lift` | 2 | `Hierarchy`, `SequenceTransferLift` |
| `TU Linear Typ 1` / `TU Linear Base` | 2 / many | `Hierarchy`, `TransportLinear`, `DriveSimple` |
| `Gate Typ 1` | 4 | `Cylinder`, `SequenceGate` |
| `Safety Lock Typ 1` | 6 | `Lock` |
| `Door Typ 1` / `Door Typ 2` | 2 / 4 | `Door` |
| `Camera Typ 1` / `2` / `3` | 1 each | `TagReader` / `DataReader` / `TagReader` |
| `Emergency Switch Typ 1` | 2 | `Button` |
| `Signal Tower Typ 1` | 1 | `PanelSampler` + 3 `Lamp` |
| `Control Panel` | 1 | `PanelSampler` + 6 buttons + 1 switch |

## Worked example

The point of this example is not the machine — it is the *shape* of the reasoning.

Target `Project/FG_01/Barcode Reader/P_Reader` — tier `device`, components `Rigidbody`, `TagReader`,
`oc.plcPath` `MAIN.FG_01.P_Reader`.

What the project already tells you: it is a `TagReader`, it sits inside the `Barcode Reader` assembly
in `FG_01`, and `SequenceUnit1` drives that group. Reading `SequenceUnit1.Operation()` gives the
actual order of events:

```
gripper extends -> laser ON (1 s) -> laser OFF -> reader window opens
-> read (1 s) -> window closes -> gripper retracts -> OperationComplete
```

So the read happens **after** marking, not before — it verifies the mark rather than gating it. This
is exactly why step 3 of the skill is mandatory: the plausible-sounding assumption ("read the tag,
then mark accordingly") is the opposite of what the code does, and an agent that skipped the source
would have written it backwards with total confidence.

What only the user can tell you: what is actually encoded in the mark, and what happens when the
verification read fails.

Resulting entries:

```bash
unity command context_set --target "Project/FG_01/Barcode Reader/P_Reader" \
  --key "Function" \
  --value "Verification read after laser marking. The reader window opens once the mark is complete and the code is read back to confirm it is legible before the pallet is released."

unity command context_set --target "Project/FG_01/Barcode Reader/P_Reader" \
  --key "Signal" \
  --value "PLC reads the decoded string. In MIL, SequenceUnit1 holds the window open for 1 s and does not branch on the result."
```

Note what the `Function` value does **not** say: "This is a tag reader component." The component list
already carries that, and `oc.deviceType` says it again. Note also that `Signal` is explicit about MIL
not branching on the read — do not describe intent the code does not implement.

## Verifying a write

```bash
unity command context_get --target "Project/FG_01/Barcode Reader/P_Reader"   # read back through a different command
unity command save_all
unity command context_audit --format json                                    # updated coverage
```

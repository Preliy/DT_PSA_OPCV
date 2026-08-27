# FG_05 — the behaviour contract

Capping. Fits a cap from the bunker onto the part carried on the pallet. Written from the shipped ST;
**the PLC is master for behaviour**.

Source: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/15 FG_05/FG_05.TcPOU`.

**The reset and resume model is in [`gripper-station-reset.md`](gripper-station-reset.md) §5.**

---

## Components

Ten symbols. Six cylinders, all `FB_DoubleSolenoidFeedback`.

| Group | Instances | FB |
|---|---|---|
| Cap handling unit | `Y_AxisX`, `Y_AxisZ1`, `Y_AxisZ2`, `Y_AxisR`, `Y_Gripper` | `FB_DoubleSolenoidFeedback` |
| | `B_Detect` | `FB_DigitalSensor` |
| Cap feed | `Y_CapsSourceStopper` | `FB_DoubleSolenoidFeedback` |
| | `Y_CapsSource` (ControlBunker) | `FB_AbstractBunker` |
| | `B_Part` | `FB_DigitalSensor` |
| Vision | `P_Camera` | `FB_AbstractCamera` |

### `B_Part` and `B_Detect` answer different questions

The names are close enough to invite the mistake.

| Sensor | Where | Says |
|---|---|---|
| `B_Part` | on the **feed** | a cap has arrived at the pick position. Step 10 waits for it; once the gripper lifts a cap away it is reporting the **next** one |
| `B_Detect` | inside the **jaws** | this unit is carrying a cap. Steps 70 and 120 confirm against it, and it decides whether `Resetting` may open the gripper at all |

A cylinder limit cannot stand in for `B_Detect`: jaws that close on nothing reach `.Extended` sooner
than jaws that close on a cap, so `.Extended` is true either way.

## The bunker is not part of the pallet cycle

> Getting this wrong stalls the station permanently.

`SequenceBunker.cs` turns both bits on in `OnEnable` and off in `OnDisable` — it is a **continuously
running feed**, not a step. Driven from inside `Execute` it would stop between pallets, no cap would
ever be waiting when the next pallet arrived, and step 10 would block on `B_Part` for ever.

`Y_CapsSource` is therefore commanded from `CyclicLogic`, through the `DriveBunker` action, **on mode
and state only**.

`Y_CapsSourceStopper` is **held, never indexed**. An accumulating feed needs nothing more: the queue
pushes the next cap against the engaged stopper as soon as the gripper takes the one in front. It is
commanded to its blocking position and left there for the whole cycle.

**It is commanded at `Resetting` step 0**, before anything homes — not at the end of the reset. Its
de-energised position does not block, and the feed runs throughout `Resetting` and `Idle`, so a late
command would let caps spill past the pick position while the axes travel. `Execute` step 10
re-asserts it.

> **EXTENDED blocks the path.** Settled 2026-08-22 by refactoring the device in the twin, and the
> PLC follows: both call sites are `Extend()` and both waits are on `.Extended`.
>
> **This is the opposite sense to the nine transport stoppers**, where retracted holds — see the
> correction register in [`transport-behaviour.md`](transport-behaviour.md) §6. That register was
> derived from the `TS Index Unit` and `Stopper Unit` prefabs, and this device comes from neither, so
> the two facts do not contradict each other. Do not "correct" one to match the other.

## The camera reads the assembly, not the cap

`P_Camera` is mounted on the feed side but looks across at the pallet. The key it reads is the
**assembly's `CapsID`**, so the read answers *"which cap does this assembly want"*, and the station
fits a cap only to an assembly of the type it is set up for. An empty pallet reads 0.

FG_01, FG_02 and FG_05 run the identical `FB_AbstractCamera` under the identical name over the
identical four status bits. The only difference between the three stations is which payload key their
twin reads and what value it has to be — here `CapsID`, expected **810**. The comparison is made in
`SIM_1`'s `FB_Camera` against a value set in this group's `Mapping` action, not in the control PLC;
the shared mechanism and the full datum table are in
[`fg-02-behaviour.md`](fg-02-behaviour.md#what-is-actually-compared).

> **The read is first, and that placement is load-bearing.** `Index05` has already stopped and lifted
> the pallet before this group is triggered, so the assembly is in view from the first scan and there
> is nothing to wait for. Reading here means a NOK aborts **before the gripper has taken anything** —
> cap still in the feed, handling unit empty and home. Read after the pick instead and an abort
> strands a cap in the air above the part.

## Production cycle

`Execute`, mode `Production`.

| Step | Action | Advances on | Timeout |
|---:|---|---|---|
| 0 | derive entry from `B_Detect`; camera on, trigger cleared | — | wrong park position → **fault 4** |
| 10 | `Y_CapsSourceStopper.Extend` (hold — extended blocks) | `B_Part.Active` **and** `SettleTimer` 500 ms | |
| 20 | wait for camera | `P_Camera.Ready` | `ReadyTimer` 2 s → **fault 2** |
| 30 | `Trigger` | `DeviceBusy` **or** `ResultValid` | `ShotTimer` 3 s → **fault 3** |
| 40 | read verdict | `ResultOK` — else **fault 1** | `ShotTimer` → **fault 3** |
| 50 | `ClearTrigger` | — | |
| 60 | `Y_AxisZ2.Extend` — down on the bunker side | `.Extended` | |
| 70 | `Y_Gripper.Extend` — grip the cap | `.Extended` **and** `B_Detect.Active` | `GripTimer` 500 ms → **fault 5** |
| 80 | `Y_AxisZ2.Retract` — lift clear | `.Retracted` | |
| 90 | `Y_AxisX.Extend` — traverse to the pallet | `.Extended` | |
| 100 | `Y_AxisR.Extend` — rotate, in the air and clear | `.Extended` | |
| 110 | `Y_AxisZ1.Extend` — lower onto the part | `.Extended` | |
| 120 | `Y_Gripper.Retract` — release | `.Retracted` **and** `NOT B_Detect.Active` | `ReleaseTimer` 500 ms → **fault 6** |
| 130 | `Y_AxisZ1.Retract` — up, clear of the pallet | `.Retracted` | |
| 140 | `Y_AxisX.Retract` — back over the feed | `.Retracted` | |
| 150 | `Y_AxisR.Retract` — rotate home | `.Retracted` | |
| 160 | camera off, `ChangeState(Complete)` | — | |

**Where the cycle starts is derived, not remembered** — step 0 reads `B_Detect` and the park position
rather than trusting a stored flag.

Both grip confirmations are two-part: the cylinder limit **and** the sensor. `GripTimer` and
`ReleaseTimer` are armed on the limit being reached, so the 500 ms budget covers the sensor
answering, not the stroke.

## Fault codes

`ST_FG_05_Capping_Status`, published as `HMI.Capping.FaultCode`. Codes 1–3 are the camera's, shared
in shape with FG_01 and FG_02.

| Code | Meaning |
|---:|---|
| 1 | this station does not cap that assembly (`ResultOK` false) |
| 2 | the camera never became `Ready` |
| 3 | the shot never completed |
| 4 | started with a cap held by a unit that is not at its safe position |
| 5 | pick failed — jaws closed but `B_Detect` never confirmed |
| 6 | release failed — jaws opened but `B_Detect` never cleared |

An abort means `Index05` never receives `OperationDone` and raises its own fault 3 on the operation
timeout. There is no reject station on this line.

## Safety

No authored `Safety` section for this group. The cell chain (`Machine.SafetyOk` → `AbortImmediate`)
applies.

> **A de-energised double solenoid does not hold a gripped cap in the twin.** `CyclicLogic`
> re-asserts the grip every scan in every state but `Execute`. `Aborting` and `Stopping` leave the
> **axes** alone — not the grip.

## Related

- [`gripper-station-reset.md`](gripper-station-reset.md) — the reset model, safe positions, resume
- [`fg-03-behaviour.md`](fg-03-behaviour.md) — the same model with two arms
- [`fg-01-behaviour.md`](fg-01-behaviour.md), [`fg-02-behaviour.md`](fg-02-behaviour.md) — the same camera protocol

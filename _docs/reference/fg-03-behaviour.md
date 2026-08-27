# FG_03 — the behaviour contract

Slot 1 → slot 2 transfer with a 180° flip. Written from the shipped ST; **the PLC is master for
behaviour**.

Source: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/13 FG_03/FG_03.TcPOU`.

**The reset and resume model is in [`gripper-station-reset.md`](gripper-station-reset.md) §4** — safe
positions, the snapshot rule, the handover tie-break. This page is what the group *is* and what its
production cycle does.

---

## Components

Nine symbols. Seven cylinders, all `FB_DoubleSolenoidFeedback` — two coils and two limits each — plus
two grip sensors.

| Arm | Axes | Gripper | Grip sensor |
|---|---|---|---|
| **Arm 1** — the placing arm | `Y_AxisX1`, `Y_AxisY1`, `Y_AxisR1` | `Y_Gripper1` | `B_Detect1` |
| **Arm 2** — the picking arm | `Y_AxisX2`, `Y_AxisY2` | `Y_Gripper2` | `B_Detect2` |

## The two arms name their axes the opposite way round

> **Every earlier version of this module had arm 1 wrong because of it.**

Confirmed against the twin's `Axis` components, which is the only place it is written down:

| Axis | Direction | Detail |
|---|---|---|
| `Y_AxisX1` | **vertical** | translates local Y, factor +0.001; max = raised |
| `Y_AxisY1` | **horizontal** | translates local Z, factor +0.001; max = transfer position, min = home over slot 2 |
| `Y_AxisX2` | **horizontal** | translates local X, factor +0.001; max = transfer position, min = home over slot 1 |
| `Y_AxisY2` | **vertical** | translates local Y, factor **−0.001** — sign inverted, so a rising cylinder value *descends*; max = lowered |

Two further traps in the same family:

- **Arm 1 never lowers to place.** `X1` rises at step 60 and stays at max for the whole cycle. The
  180° flip on `R1` is what carries the part down into slot 2 — which is why no lowering step
  appears, and why looking for one makes the sequence read as though a step were missing.
- **`R1` retracted (0°) is home and the receiving orientation; extended (180°) is the placing
  orientation.** It turns **only** at the transfer position: over slot 2 the sweep would go through
  whatever is in the slot. That is why step 140 traverses back before step 150 turns.

## Production cycle

Full step table in [`gripper-station-reset.md`](gripper-station-reset.md) §4. Three sub-sequences
with a safe position between them:

| Sub | Steps | Does | Ends at |
|---:|---|---|---|
| 1 | 20–40 | pick out of slot 1 | **SAFE A** — `X2` min, `Y2` min, arm 2 raised at home, holding |
| 2 | 50–90 | the transfer | **SAFE B** — `X1` max, `Y1` max, `R1` min, arm 1 raised at the transfer position, holding, not yet rotated |
| 3 | 100–170 | flip, place, home | — |

**Exactly one moment has both arms on the same part.** Step 80 waits for `B_Detect1` before step 90
commands `Y_Gripper2.Retract`, so the part is never held by nobody. The twin's `SequenceUnit3.cs`
separates those two motions with a 0.2 s dwell instead, which *assumes* the grip happened rather than
confirming it.

**Arm 2 goes home at step 100 before the rotate**, not in parallel with it, so the rotating part can
never meet arm 2 standing at the transfer position.

### Why the MIL dwells are gone

`SequenceUnit3.cs` interleaves all fourteen motions with 0.2 s waits because the twin's animation has
no limit switches to wait on. **They are the animation's substitute for feedback, not a process
requirement.** This module waits on `.Extended` / `.Retracted` at every step, exactly as FG_01 waits
on its gate limits. The one dwell kept is the 0.5 s settle at the head of the cycle, which has no
sensor behind it.

## Two rules that cost a part to learn

> **A cylinder limit is not a grip witness.** Jaws closed on *nothing* reach `.Extended` sooner than
> jaws closed on a part, so `.Extended` is true either way. Only `B_Detect1` / `B_Detect2` say a part
> is held.

> **A de-energised double solenoid does not hold a gripped part in the twin.** True of the real
> valve, false here — the `Gripper` releases the moment its cylinder moves at all. Arm 1 dropped a
> part mid-reset before this was understood. `CyclicLogic` now re-asserts the grip every scan in
> **every state but `Execute`**.

Both grip sensors are `GripSensor.cs` reading the OC `Gripper`'s `IsPicked` — the gripper's own record
of what it picked up, not an independent look into the jaws. **They cannot report a part the gripper
has silently lost.** On real hardware these would be beams; the PLC code is written the same either
way, but a diagnosis leaning on *"the sensor would have seen it"* is leaning on the optimistic
witness.

## Fault codes

`ST_FG_03_Transfer_Status`, published as `HMI.Transfer.FaultCode`. Table in
[`gripper-station-reset.md`](gripper-station-reset.md) §7.

| Code | Meaning |
|---:|---|
| 1 | `Resetting` could not separate the two grippers at the handover; nothing was moved |
| 2 | pick failed |
| 3 | handover failed |
| 4 | release failed inside `Execute` |
| 5 | started with a part held by an arm that is not at its safe position |

`HMI.Transfer.ResumePoint` is published alongside and is **not** a fault — it is which sub-sequence
the next Start would enter (1 full cycle, 2 handover, 3 place), derived every scan from the live
sensors so the panel shows what pressing Start would do.

## Safety

**No `Safety` section is authored for this group in the twin.** The handover interlock above is
derived from the sequence itself, not from a safety statement, and is recorded as such. No other
permissive is invented here. The cell chain (`Machine.SafetyOk` → `AbortImmediate`) applies.

## Non-production states

`Aborting` and `Stopping` command **no axis motion** — a part is likely hanging in a gripper, and
moving an arm is what tears it. They leave the axes alone; `CyclicLogic` keeps the grip asserted.

`Resetting` parks whatever is held at its safe position **without opening the gripper**, and the next
Start resumes from there — step 0 derives the entry point from the two grip sensors. So an E-Stop
mid-cycle costs a reset and a start, not a scrapped part and not a trip into the cell.

The pallet stays clamped by `Index03` throughout, so the resumed cycle finishes the job and `Index03`
gets its `OperationDone` as usual — **provided the operator is quicker than `Index03`'s own operation
timeout**, which nothing in this group can extend.

## Related

- [`gripper-station-reset.md`](gripper-station-reset.md) — the reset model, safe positions, resume, the twin drop mechanism
- [`fg-05-behaviour.md`](fg-05-behaviour.md) — the same model with one gripper
- [`transport-behaviour.md`](transport-behaviour.md) — the Index↔group handshake

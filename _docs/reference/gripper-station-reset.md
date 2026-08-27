# How FG_03 and FG_05 reset with a part in the gripper

Hand-written. Written from the shipped ST in `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/13 FG_03/FG_03.TcPOU` and
`Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/15 FG_05/FG_05.TcPOU`. Where those disagree with anything here, they win —
the PLC is master for behaviour.

This is the station-level companion to `transport-behaviour.md`, which owns the same subject
for `FG_Transport`. The rules it establishes are not restated here, they are **applied**:
a reset terminates on time and on its own cylinders, and readiness is derived, never
remembered.

## 1. The problem

`FB_DoubleSolenoidFeedback` reports where the cylinder is, not what it is holding. Worse,
**jaws that close on nothing reach their extended limit sooner than jaws that close on a
part** — so `.Extended` is not a weak grip witness, it is a misleading one. Until the grip
sensors arrived, neither group could tell a successful pick from a miss, and neither reset
could tell an empty gripper from a full one.

So both `Resetting` methods homed the axes and then opened the grippers unconditionally.
The obvious cost was a dropped part. The expensive one was FG_03-specific:

> An E-Stop inside the handover window — `Execute` steps 80..90 — leaves **both grippers
> holding the same part**. The old reset raised both arms, rotated R1, and traversed the two
> arms apart while they were still clamped on it.

That is the failure the sensors exist to remove. A dropped part is a scrapped part; two arms
pulling against each other is a damaged machine.

## 2. The sensors

| Signal | PLC path | Twin mechanism |
|---|---|---|
| `B_Detect1` | `MAIN.Machine.FG_03.B_Detect1` | `SignalBinary` + `GripSensor.cs` → `Y_Gripper1/Gripper.IsPicked` |
| `B_Detect2` | `MAIN.Machine.FG_03.B_Detect2` | `SignalBinary` + `GripSensor.cs` → `Y_Gripper2/Gripper.IsPicked` |
| `B_Detect` | `MAIN.Machine.FG_05.B_Detect` | `SignalBinary` + `GripSensor.cs` → `Y_Gripper/Gripper.IsPicked` |

All three are `FB_DigitalSensor` in `PLC_1` and `FB_SensorBinary` in `SIM_1`. Channels:
`FG_03_EL1809_1` 15 and 16 — which fills that terminal — and `FG_05_EL1809_1` 14.

**All three are the optimistic witness, and that is worth knowing when diagnosing.** FG_03's
two started as `SensorBinary` beam sensors and were changed to `GripSensor` on 2026-08-21 to
match FG_05. `IsPicked` is the OC gripper component's own record of what it picked up, not an
independent look into the jaws, so **none of the three can report a part the gripper has
silently lost** — only one it never took or never let go of. On real hardware these would be
beams. The PLC code is written the same either way, but a diagnosis that leans on "the sensor
would have seen it" is leaning on the wrong half of the pair.

**`B_Detect` is not `B_Part`.** `B_Part` is on the feed and says a cap has arrived at the
pick position; once the gripper lifts one away it is reporting the *next* cap. `B_Detect` is
in the jaws and says this unit is carrying one. Two questions, adjacent names, and the
FG_05 block header says so at the declaration for exactly that reason.

## 3. The rule: sample once, branch, never wait

```
Resetting step 0:   _Held1 := B_Detect1.Active;    // and never read again
                    _Held2 := B_Detect2.Active;
```

A live sensor read inside a waiting step would break the reset contract just as surely as
waiting on the index unit did in `FG_Transport`: a part that never clears the beam would
park the group in `Resetting` for ever, and every station behind it with it. A **snapshot
cannot fail to arrive**. Every step in every route then waits on the module's own cylinders,
bounded by the `ExtendTime`/`RetractTime` budgets set in `Initialize`, so a jam alarms out of
the state instead of sitting in it.

The one place a sensor is read after step 0 is immediately *after* a gripper reports
`Retracted` — one sample, to decide whether to latch a fault. It is never a wait condition.

## 4. FG_03 — safe positions, and a cycle that resumes

**A reset does not undo the cycle and it does not finish it.** It moves whatever is held to a
position it can be held at indefinitely, and the next Start picks the cycle up from there.

### First: the two arms name their axes the opposite way round

Every earlier version of this page and of `FG_03.TcPOU` had arm 1 wrong. Confirmed against the
twin's `Axis` components, which is the only place it is written down:

| Symbol | Role | Unity `_direction` | factor | max means |
|---|---|---|---|---|
| `Y_AxisX1` | arm 1 **vertical** | 1 = Y | `+0.001` | raised |
| `Y_AxisY1` | arm 1 **horizontal** | 2 = Z | `+0.001` | at the transfer position |
| `Y_AxisX2` | arm 2 **horizontal** | 0 = X | `+0.001` | at the transfer position |
| `Y_AxisY2` | arm 2 **vertical** | 1 = Y | `−0.001` | **lowered** — the sign is inverted |

**Arm 1 never lowers to place.** `X1` rises once at step 60 and stays at max for the whole
cycle. The 180° flip on `R1` is what carries the part down into slot 2. Reading the sequence
expecting a lowering step is what makes it look as though one is missing.

**`R1` turns only at the transfer position.** Over slot 2 the sweep goes straight through
whatever is in the slot, which is why step 140 traverses back before step 150 turns.

### The cycle

```
     20  Y2.Extend    arm 2 down into slot 1
     30  G2.Extend    grip                        + B_Detect2
     40  Y2.Retract   lift                                      -> SAFE A
     50  X2.Extend    arm 2 across to the transfer
     60  X1.Extend    arm 1 up   (first cycle only; it stays up)
     70  Y1.Extend    arm 1 across to the transfer
     80  G1.Extend    grip - both hold            + B_Detect1
     90  G2.Retract   arm 2 lets go               + NOT B_Detect2   -> SAFE B
    100  X2.Retract   arm 2 home
    110  R1.Extend    THE FLIP - and the placing move
    120  Y1.Retract   across to slot 2
    130  G1.Retract   release                     + NOT B_Detect1
    140  Y1.Extend    clear of the placed part
    150  R1.Retract   rotate home
    160  Y1.Retract   home over slot 2
```

Arm 2 goes home at 100 *before* the rotate rather than in parallel with it, so the rotating
part can never meet arm 2 standing at the transfer position.

### The safe positions

| | State | Left by | Resumes at |
|---|---|---|---|
| **SAFE A** | `X2` min, `Y2` min, part in gripper 2 | step 40 | step 50 |
| **SAFE B** | `X1` max, `Y1` max, `R1` min, part in gripper 1 | step 90 | step 100 |

**Both are states the cycle already rests at**, so a resume is the cycle simply carrying on and
nothing had to be inserted to make either position real.

**Arm 1's safe position is not its home.** Home is `Y1` min, over slot 2 — which is the *place*
position. A part parked there hovers exactly where it is about to be put down, and is still the
wrong way up. The transfer position is where arm 1 legitimately stands holding a part.

### Resetting

| Step | |
|---|---|
| `0` | sample both sensors; both held → `10`, otherwise → `100` |
| `10` | **both hold.** Arm 1 has priority: arm 2 lets go where the arms stand, as step 90 does. → `100`. If arm 2 will not let go: fault 1, → `900`, **nothing moves at all** |
| `100` | both arms up — `X1.Extend` for arm 1, `Y2.Retract` for arm 2 |
| `110` | arm 1 across to the transfer position — SAFE B, and the only place `R1` may turn |
| `120` | `R1` home |
| `130` | arm 2 home — SAFE A |
| `140` | arm 1 stays at the transfer position if carrying; goes home over slot 2 if not |
| `150` | open the **empty** grippers, and only those |

Step 110 runs whether or not anything is held, because step 120 needs to turn and the transfer
position is the only place it may. Traversing there with a rotated part is step 120 in reverse;
turning there with a part held is step 110's own move. Both are moves the cycle already makes.

**No gripper holding a part is ever opened** — and, since §9, it is not merely left alone
either: `CyclicLogic` holds it closed. Step 150 waits only on the cylinders it actually drove.

### Resuming

`Execute` step 0 derives the entry point from the two grip sensors and from nothing else — no
stored step index, no "was I interrupted" flag. This is `transport-behaviour.md` §1 applied to a
sequence rather than to an interface.

```
B_Detect1 -> 100      B_Detect2 -> 50      neither -> 10
```

It also **checks the arm is at its safe position** — `X1` and `Y1` both *extended* for arm 1,
`X2` and `Y2` both *retracted* for arm 2. Note that those are opposite tests for the same
physical idea, which is the axis-naming trap again. A part held anywhere else means the entry
point would be a guess, so it raises fault 5 and aborts rather than moving.

`HMI.Transfer.ResumePoint` publishes the same derivation every scan, computed from the live
sensors in `PublishStatus` — **not** copied from `Resetting`'s `_Held1`/`_Held2`, which are that
state's private snapshot and stale everywhere else.

### What the resume costs

The pallet stays clamped by Index03 for the whole interruption, so a resumed cycle finishes the
job and Index03 gets its `OperationDone` as usual. **Index03's own operation timeout is the
limit** — if the operator takes longer than that to Clear, Reset and Start, Index03 raises its
fault 3 and the station has to be recovered from the transport side too.

A part in a gripper used to be an illegal starting condition and is now a legal one, so the
"refuse to start dirty" net is gone and the sensors have to be right. Fault 5 is what is left of
it: it no longer asks *whether* a part is held, only whether it is held somewhere the cycle can
be resumed from.

## 5. FG_05 — the same model, one gripper

One gripper, so one safe position and one resume point.

```
SAFE   X MAX, Z1 min, Z2 min, R min, cap in the gripper
```

**This one the cycle really does pass through.** It is exactly the state `Execute` step 90
leaves — Z2 up from step 80, Z1 never lowered yet, R not yet turned, and the traverse across to
the pallet just finished. So the resume entry is step 100 and nothing had to be inserted to
make the position real, unlike FG_03's arm 1.

| Step | `Resetting` |
|---|---|
| `0` | `Y_CapsSourceStopper.Extend` — block the feed; disable the camera; sample `B_Detect` into `_Held` |
| `10` | both vertical strokes up |
| `20` | R home always; X to **max if carrying**, min if empty |
| `30` | wait for the stopper `.Extended`; open the gripper only if it is empty |

**The feed is blocked at step 0, not at step 30.** The stopper's de-energised position no longer
blocks — extended does — and `DriveBunker` keeps the feed running right through `Resetting` and
`Idle`, so commanding it at the end of the reset would let caps spill past the pick position for
the whole of the axis homing. The command latches, so step 30 only waits on `.Extended` and the
state still terminates on this unit's own travel budget.

`Execute` step 0 then resumes at 100 if a cap is held and the unit is at `X` max with both `Z`
retracted, and raises fault 4 if a cap is held anywhere else.

**A resume skips the camera entirely, and that is correct rather than a shortcut.** The read
identifies the *assembly*, it happened at steps 20..50 before the cap was ever picked, and it
came back OK — a NOK aborts before the pick. The pallet has not moved since. Re-reading would
ask a question that has already been answered.

### Why not put the cap somewhere

Worth recording, because every obvious answer is wrong:

| | |
|---|---|
| Back on the feed | The pick position is not empty. The stopper is held, so the next cap advanced into place the moment this one was lifted. Releasing there jams the feed. |
| Onto the part | A reset does not deliver product, and finishing the placement means knowing Index05 still has a pallet clamped underneath — the "reset waits on another unit" mistake. |
| Open in the air | What the original code did. The cap falls. |
| Keep it and stop | What the version before this did: park, raise code 4, make an operator fish the cap out. Safe, but it turned every E-Stop into a trip into the cell for a cap that was never in danger. |

Parking at the safe position costs none of that. The cap is held clear over the pallet, the
unit can stand there indefinitely, and the placement it was three moves away from is still
three moves away.

## 6. `Execute` confirms every grip and every release

This is what makes the reset snapshot worth trusting. Each check waits on the cylinder limit
first, then on the sensor, bounded by its own `TON` — a separate timer per step, because
adjacent confirming steps (FG_03's 80 and 90) would never let a shared timer's `IN` drop.
The timer is armed only once the cylinder is at its limit: the stroke already has the
cylinder's own travel timeout, and `T#500MS` covers only the part settling in or falling out.

| Group | Step | Confirms | Fault |
|---|---|---|---|
| FG_03 | 0 | both jaws empty before starting | 5 |
| FG_03 | 30 | pick caught the part | 2 |
| FG_03 | 80 | **arm 1 has it before arm 2 lets go** | 3 |
| FG_03 | 90 | the part left arm 2's jaws — also what makes arm 2's traverse home safe | 4 |
| FG_03 | 130 | the part left arm 1's jaws | 4 |
| FG_05 | 0 | jaws empty before starting | 4 |
| FG_05 | 70 | the cap is in the jaws | 5 |
| FG_05 | 120 | the cap left the jaws | 6 |

FG_03 step 80 is the one that matters most. The module header always claimed the part is
"never held by nobody", and until now that claim rested on `Y_Gripper1.Extended` — a bit that
is true whether or not the jaws caught anything. Step 90 earns its place too: arm 2 traverses
away at step 100, so a part that never left its jaws would be dragged straight off arm 1.

## 7. Fault codes

Raised with `AbortImmediate()` from `Execute`, latched without aborting from `Resetting`, and
cleared in `Clearing` — the fault is cleared by the act of clearing, not by the condition
going away, because a part jammed in a gripper is still jammed after the sensor stops being
interesting.

**FG_03**, `HMI.Transfer.FaultCode`, `ST_FG_03_Transfer_Status` — the group's first fault code:

| Code | Meaning |
|---|---|
| 1 | `Resetting` could not separate the two grippers at the handover; nothing was moved |
| 2 | pick failed |
| 3 | handover failed |
| 4 | release failed inside `Execute` |
| 5 | started with a part held by an arm that is not at its safe position |

`ResumePoint` is published alongside. It is not a fault — it is which sub-sequence the next
Start will enter (1 full cycle, 2 handover, 3 place), derived every scan from the live
sensors so the panel shows what pressing Start would do.

**FG_05**, `HMI.Capping.FaultCode`, `ST_FG_05_Capping_Status` — 1..3 were already the camera's
and are unchanged:

| Code | Meaning |
|---|---|
| 4 | started with a cap held by a unit that is not at its safe position |
| 5 | pick failed |
| 6 | release failed |

## 8. Open items

- ~~`B_Detect1` sits above the R1 rotary joint~~ — **closed 2026-08-21.** It was a beam
  sensor parented to `Axis_Y1`, above the rotary joint, so it would have gone blind in one of
  the two R1 orientations. Replacing it with `GripSensor` removed the problem rather than
  fixing the parenting: `IsPicked` is read off the `Gripper` component itself and does not
  care where the sensor node hangs or which way the arm is turned.
- ~~`Y_CapsSourceStopper`'s polarity is an assumption~~ — **closed 2026-08-22.** The device was
  refactored in the twin and **EXTENDED now blocks the path**; both PLC call sites — `Execute`
  step 10 and `Resetting` step 30 — are `Extend()` and both waits are on `.Extended`. This is the
  opposite sense to the nine transport stoppers, and deliberately so; see
  [`fg-05-behaviour.md`](fg-05-behaviour.md#the-bunker-is-not-part-of-the-pallet-cycle).

## 9. The twin drops a held part if the gripper cylinder moves

**Observed 2026-08-21: FG_03 arm 1 let go of its part in the middle of a reset**, in code that
never commands `Y_Gripper1`. The step logic was not at fault; the premise underneath it was.

### The scene wiring

`Y_Gripper1`, `Y_Gripper2` and FG_05's `Y_Gripper` each have their `OC.Components.Cylinder`
wired to the child `OC.MaterialFlow.Gripper`:

| Cylinder event | Target |
|---|---|
| `OnLimitMaxEvent` | `Gripper.Pick(bool)` |
| `OnLimitMinEvent` | `Gripper.Place(bool)` |
| `OnActiveChanged` | `Gripper.Place(bool)` |

`GripperBase.Place(bool place)` is `if (place) Place(); else Pick();` — so a **`TRUE`** on any of
those release-side events drops the payload. And `Cylinder.UpdateState()` sets

```csharp
_isActive.Value = !Math.FastApproximately(_target.Value, _value.Value, 1e-1f);
```

— `IsActive` means **the cylinder is moving**. So `OnActiveChanged(TRUE)` → `Place()` → the part
is released the instant the gripper cylinder travels at all.

**The payload is held only while that cylinder is at its max limit and standing still.**

### What that invalidates

Every comment in both modules used to justify no-motion `Aborting` and `Stopping`, and an
uncommanded gripper in `Resetting`, with *"a de-energised double solenoid holds its position"*.
That is correct for the real valve and **wrong for the twin**: nothing about the twin's grip
survives the cylinder being allowed to drift. Leaving a full gripper uncommanded across
`Clearing` and `Resetting` was enough to lose the part.

### The fix

Both modules re-assert the grip in `CyclicLogic`, **before `SUPER^.CyclicLogic()`**:

```iecst
IF _CurrentState <> E_PMLState.ePMLState_Execute THEN
    IF B_Detect1.Active THEN Y_Gripper1.Extend(); END_IF
    IF B_Detect2.Active THEN Y_Gripper2.Extend(); END_IF
END_IF
```

- **Before `SUPER^`** is what makes it an interlock rather than a suggestion — it overwrites
  whatever a state method asked for on the previous scan. Same shape as the lift carriage
  interlock in `transport-behaviour.md` §3.
- **`HMICommunication` runs inside `SUPER^`**, so it still gets the last word and an operator
  can jog a gripper open in Manual.
- **`Execute` is excluded** because it is the only state allowed to put a part down.
- It commands no *motion*: the jaws are already closed, so `Extend()` on them is a no-op at the
  valve. It only refuses to let anything else open them.

### The rule

**Never leave a grip uncommanded and expect it to hold.** If a part must stay gripped, command
the grip. This is a twin-versus-hardware divergence, so it will not show up in reasoning about
the real valve — only in the running cell.

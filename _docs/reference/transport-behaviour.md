# FG_Transport — the behaviour contract

How the transport ring actually sequences, interlocks and recovers. **The PLC is master for
behaviour**, so this page is written from the shipped ST and every rule below can be pointed at a
line of it.

**This file is curated, not generated.** No tool writes it. `_docs/context/` is the opposite —
derived from the twin and rebuilt wholesale — so the never-hand-edit rule applies there, not here.
That is also why this page has to exist: anything under `context/` that the build did not write is
deleted, so behaviour knowledge cannot live there at all.

Source of every claim: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/10 FG_Transport/`.

---

## What this page is master of, and what it is not

| Domain | Master | Where it lives |
|---|---|---|
| **Structure** — which devices exist, their PLC paths, device types, I/O, terminal channels | the Unity twin | the machine pages (generated) |
| **Behaviour** — sequences, handshake, interlocks, fault codes, reset | **the PLC** | this page |

The MIL C# under `Unity/Assets/Demo_1/Scripts/MIL/` is **the twin's animation**, not the behavioural
contract. It still drives the twin acceptably standalone, but it implements the *older* design: no
transfer latch, no check that the lift is at a level before running its carriage belt, and no reset
path at all. Reading a handshake out of it today reproduces bugs that have been fixed.

The MIL's own vocabulary differs from the PLC's, and both names turn up in the scene. Use this
table to read one as the other:

| MIL (twin) | PLC | Note |
|---|---|---|
| `Ready` | `CanAccept` | derived, not stored |
| `Busy` | `Occupied` | derived; `Busy` is taken by `FB_BaseFB` and means something else |
| `SendPayload()` | `SendToNext` → `PayloadIncoming` | only a lift consumes it |
| `Done` | *(removed)* | the successor detects the pallet on its own sensor |

The three invariants still hold and are still the reason the Index steps are ordered as they are;
they are marked in the step table below.

---

## 1. The interface is derived, not assigned

Two properties are the whole readiness contract, and both are **property getters computed on every
read**:

```iecst
Occupied  := B_Detect.Active OR <transfer latch>;
CanAccept := <at home / blocking> AND NOT B_Detect.Active
                                 AND NOT <transfer latch>
                                 AND (_FaultCode = 0);
```

| Unit | `CanAccept` | `Occupied` |
|---|---|---|
| Stopper | `FB_TransferStopper.TcPOU:429` | `:378` |
| Index | `FB_TransferIndex.TcPOU:504` | `:434` |
| Lift | `FB_TransferLift.TcPOU:201` (`AtHome`, derived from the carriage position — §3) | `:614` |

**Why derived matters.** The previous design stored `_Ready` and `_Occupied` and only maintained them
inside `Execute`. Every other PackML state either wiped them or left them stale, which meant a reset
that homed a lift with a pallet still aboard came back announcing an empty lift — and the upstream
stopper released a second pallet into it. A getter cannot go stale, is correct in every state and
every mode, and needs no second reset-only channel bolted alongside it.

There is no `_Ready` and no `_Occupied` variable anywhere in these three blocks. The step chains
*act*; they do not define the interface.

**One channel wires the ring**, `FG_Transport.TcPOU:423-433`:

```iecst
Lift01.NextCanAccept    := Stopper03.CanAccept;
Stopper03.NextCanAccept := Index01.CanAccept;
…
Stopper02.NextCanAccept := Lift01.CanAccept;
```

`WireRing` is the only place the chain order exists — no station knows what follows it, which is what
lets one FB serve five index units. `FG_Transport.TcPOU:414`: **"The wiring is the authority."**

### The Index station cycle

`FB_TransferIndex.Execute`, one chain for all five instances. The three invariants are marked where
the code enforces them.

| Step | Action | Advances on | Fault |
|---:|---|---|---|
| 0 | home: `Y_Stopper.Retract` (blocking), `Y_Lift.Retract`, handshake flags cleared | — | |
| 10 | confirm blocking position from the real switch | limits | **1** no block |
| 20 | idle and empty — the normal resting condition | `B_Detect` | |
| 30 | **invariant 1** — `Y_Lift.Extend` while the stopper still blocks | `.Extended` | **2** lift did not raise |
| 40 | `_ReadyForOperation := TRUE`; wait for the group | `_OperationDone` | **3** group did not finish |
| 50 | **invariant 2** — operation complete, so `Y_Lift.Retract` | `.Retracted` | **4** lift did not lower |
| 60 | **invariant 3** — successor can accept; arm `_Transferring` | `NextCanAccept` | |
| 70 | `Y_Stopper.Extend` — release | `.Extended` | **5** no release |
| 80 | confirm the pallet actually left | `B_Exit` rising edge | **6** never reached exit |

The unit clears `_OperationDone` itself once it sees it, so a group never has to reset anything. An
Index with `bypass` set skips the call and dwells 1 s instead — useful for a station whose group does
not exist yet.

---

## 2. The transfer latch — the only memory in the interface

A payload crossing a station boundary is invisible to sensors: a pallet drawn half onto a lift
carriage has not reached `B_Detect` yet. That single case needs memory, and it is one plain `BOOL`
per direction, initialising `FALSE`.

| Unit | Latch | Armed at | Cleared by |
|---|---|---|---|
| Stopper | `_Transferring` (`:61`) | commit to release, `:247` | rising edge of `B_Exit`, `:185-188` |
| Index | `_Transferring` (`:63`) | commit to release, `:296` | rising edge of `B_Exit`, `:196-199` |
| Lift | `_LoadingIn` (`:55`) | belt starts drawing in, `:372` | rising edge of `B_Detect`, `:255-257` |
| Lift | `_UnloadingOut` (`:56`) | commit to push off, `:418` | rising edge of `B_Exit`, `:258-260` |

On the stopper and index the latch **is** `SendToNext` (`:511`, `:608`) — handing over and being
mid-crossing are the same fact, so keeping them as one variable means they cannot disagree.

### Three rules that are not obvious, and each cost a failure to learn

**a. Clear on an edge, never a level.** `B_Exit` may still be made by the *previous* pallet when the
next release commits, which would clear the latch instantly and drop `Occupied` while a pallet was
about to cross. `R_TRIG` instances at `FB_TransferStopper.TcPOU:67`, `FB_TransferIndex.TcPOU:69`,
`FB_TransferLift.TcPOU:62-63`.

**b. The witness may not be a live command.** An earlier version qualified the clear with
`Y_Stopper.Extended` (stopper) and `M_Conveyor.RunForward/Backward` (lift). `Stopping` and `Aborting`
retract the cylinder and stop the belt immediately, so a stop during a crossing **destroyed the very
witness the clearing rule depended on** — the latch could never go `FALSE` again, the station sat in
`Resetting` for ever, and every predecessor with it. A sensor edge is the only witness a stop cannot
erase.

**c. Arm only when the ending sensor is clear.** A latch armed while its ending sensor is already
made will never see a rising edge and stays `TRUE` for ever. Hence `B_Detect` is tested *first* at the
lift's `Execute` step 20 (`:363-372`), and `_UnloadingOut := NOT B_Exit.Active` at step 60 (`:418`).

**d. Arm once, on the transition — never inside the waiting step.** `CyclicLogic` clears the latch
before the state method runs, so a step that re-asserts it every scan re-sets it on the very scan it
was cleared. Both commits are on the transition into the pushing step, not inside it.

---

## 3. The lift — carriage axis and invariants

### The carriage is a positioned axis

The lift carriage is driven by a **servo axis** (`Y_Lift`), not a cylinder. It has no end-position
switches; where it stands is read from its position, measured from a reference.

| Fact | Value |
|---|---|
| Reference | `B_AxisMin`, at the bottom of travel. Referencing sets the position there to **0 mm** |
| Lower conveyor level | **10 mm** |
| Upper conveyor level | **364 mm** |
| At a level | referenced **and** within ±1 mm of the level (`AtLevel`, `:182`) |
| Travel limits | `B_AxisMin` and `B_AxisMax`. A made limit sensor forbids motion further in its own direction — in every state and mode — and always allows motion away from it (`:288-289`). Once referenced, software position limits of −2 / 370 mm apply as well |

**`AtHome` and `AtFar` are derived from the position every time they are read**, like every other
readiness fact here. Lift01 (`ReverseDirection = FALSE`) loads at the lower level and delivers to the
upper; Lift02 is the mirror image. **An axis that is not referenced is at no level** — so until a
reset has referenced it, the belt guard below stays shut and `CanAccept` stays `FALSE`. That is
deliberate: an unreferenced position is a number, not a fact.

### The Lift station cycle

`FB_TransferLift.Execute`, Production mode. Like the ring, it loops and never completes.

| Step | Action | Advances on | Fault |
|---:|---|---|---|
| 0 | belt off. A pallet aboard → step 40; otherwise command the home level | — | |
| 10 | wait for the carriage at the home level and at rest | `AtHome` | **1** no home |
| 20 | pallet aboard → 40; announced by the predecessor → belt draws in, arm `_LoadingIn` | `PayloadIncoming` | |
| 30 | belt running inwards | `B_Detect` | **2** pallet never arrived aboard |
| 40 | settle | 500 ms | |
| 50 | command the far level — issued once | move accepted | **3** travel failed |
| 55 | wait for the carriage at the far level and at rest; then **explicitly** to 60 | `AtFar` | **3** travel failed |
| 60 | successor can accept; arm `_UnloadingOut` if `B_Exit` is clear | `NextCanAccept` | |
| 70 | belt pushes out | `B_Exit` | **4** pallet never left |
| 80 | belt off, back to 0 | — | |

A level move is **issued once and then watched**, never re-issued every scan: the motion command is
fire-and-forget, and the arrival test is the derived position, not the command's own status.

**Steps are numbered by target, not by `+ 10`, once the chain is not a plain decade.** Step 55 used
to advance with `+ 10` like its neighbours and landed on 65, a step that does not exist — the lift
stood at the far level with the pallet aboard and the belt off, with no fault and no timeout.

### The invariants

**The carriage belt may only run while the carriage is at a level.** Between levels the belt drives
the pallet into a fixed edge. Enforced in `CyclicLogic` for every state and every mode — including
Manual, where the operator jogs the belt by hand — at `FB_TransferLift.TcPOU:279`:

```iecst
IF NOT (AtHome OR AtFar) THEN
    M_Conveyor.RunForward := FALSE;
    M_Conveyor.RunBackward := FALSE;
END_IF
```

**A crossing can only *start* at a level, so a set latch is proof the carriage is in position.** This
is what makes `Resetting` safe: with a latch set it may run the belt without testing the axis; with no
latch set nothing spans the gap, so the axis is free to move. The whole reset routing rests on it.

A second guard above it (`:268-272`) restricts the belt to `Execute` and `Resetting`. Note that guard
runs **before** `SUPER^.CyclicLogic()`, so it does not merely veto the output for a scan — it erases
the request the state method set on the previous scan, before the drive evaluates it. A state left out
of that condition cannot move a conveyor at all, however plainly its code commands one. The same shape
guards the main conveyors at `FG_Transport.TcPOU:151`.

**A stop halts the carriage where it stands; an abort also takes the power off it.** `Stopping` is
orderly and `Resetting` resumes from wherever the carriage halted. `Aborting` — the safety chain's
answer — must not rely on a servo holding position under power, so it removes the power once the
axis is at rest, and does not wait for rest on an axis that is in error. `Resetting` powers the axis
again before it moves it.

---

## 4. The reset model — accumulation

A reset re-establishes **where the pallets are**. It does not deliver anything.

1. The group runs both main conveyors in the production direction for the whole of `Resetting`
   (`FG_Transport.TcPOU:338`).
2. Every stopper and index blocks and never releases; the index also lowers its lift.
3. Loose pallets travel up against the blocking stoppers and **accumulate** where a detect sensor can
   see them.
4. Each station waits a fixed `_AccumulateTime` (5 s, `FB_TransferStopper.TcPOU:86`,
   `FB_TransferIndex.TcPOU:99`, `FB_TransferLift.TcPOU:91`), then clears its transfer latch and
   completes. After that, each station's state is simply what its sensor says.

Arming lines: `FB_TransferStopper.TcPOU:494`, `FB_TransferIndex.TcPOU:594`,
`FB_TransferLift.TcPOU:802`.

The lift additionally finishes any interrupted crossing first — direction from the latch, belt only,
axis untouched — then powers the axis, **references it only if it has no reference**, and moves to
the home level (`FB_TransferLift.Resetting`, steps 30–40). The reference survives every PackML
state, so in practice only the first reset after a power-up references; every later one goes
straight to the home level.

> **The rule this produced: a reset must terminate on time and on its own actuators. Never on another
> unit, and never on an event that may not arrive.**

**Referencing is the one place a reset waits on a sensor**, and it stays inside the rule: the sensor
is the lift's own `B_AxisMin`, the decision to reference is a branch on the axis' own state sampled
once, and the whole of it — powering, referencing — is bounded by one timeout (40 s, a full stroke at
search speed). A reference sensor that never makes is fault **9**, not a hang.

Both violations of that rule were shipped and both deadlocked:

- The lift waited for its successor to report `CanAccept` before handing over during a reset. But a
  stopper *never releases during a reset* by design, so a stopper holding a pallet could never become
  free — the lift sat at the hand-over step with the whole group behind it. **A reset must not depend
  on another unit doing something the reset forbids it from doing.**
- The stopper waited for an in-flight pallet to clear `B_Exit` before blocking, and the clearing rule
  needed a cylinder position that `Stopping` had already destroyed. See §2b.

`_AccumulateTime` must exceed the time a pallet needs to reach a stopper from mid-span. 5 s is a
starting value, tuned against the twin, not a derived one.

---

## 5. Fault codes

Raised with `ChangeState(E_PMLCommand.ePMLCommand_Hold)`, cleared in `Clearing`, published as
`HMI.Station.FaultCode`. A non-zero code also forces `CanAccept` false, so a faulted station stops the
ring behind it rather than accepting pallets it cannot move.

| Code | Stopper | Index | Lift |
|---|---|---|---|
| 1 | no block | no home | no home |
| 2 | no release | lift did not raise | pallet never arrived aboard |
| 3 | pallet never reached exit | group did not finish | travel failed |
| 4 | — | lift did not lower | pallet never left |
| 5 | — | no release | *reset:* pallet never came aboard |
| 6 | — | pallet never reached exit | *reset:* pallet never left |
| 9 | — | — | *reset:* carriage axis not referenced — timeout or axis error |

> **Known drift:** the `ST_Transfer*_Status.TcDUT` header comments still list the pre-reset code sets
> (`ST_TransferStopper_Status` and `ST_TransferIndex_Status`). The FB declarations are current; the
> DUT comments are not. Harmless — they are comments — but fix them when next in those files.
> `ST_TransferLift_Status` was brought up to date with the servo axis.
>
> Lift codes 7 and 8 are declared in the `FaultCode` comment and never raised: they belonged to a
> reset that delivered the pallet, which deadlocked and was removed (§4).

---

## 6. Correction register — where the twin's prose is wrong

The PLC is master for behaviour, so these are corrections *to the twin*, recorded here until the
authored entries are fixed in the scene.

**Stopper polarity — nine authored `Function` entries are backwards.**

> **RETRACTED (min) HOLDS THE PALLET. EXTENDING (max) RELEASES IT.**

Asserted at `FB_TransferStopper.TcPOU:20-22` and `FB_TransferIndex.TcPOU:28`, and confirmed by the
twin's own geometry: `Cylinder._limits = {0, 20}` with axis `_factor: -0.001` on the
`TS Stopper Typ 1` prefab, so max is the stopper *down*. The MIL agrees —
`SequenceTransferStopper.Idle()` calls `_stopper.MoveToMin()` to block.

Two authoring sites, both prefab overrides; all nine exported entries inherited from them.
**Corrected 2026-08-19** in the prefabs, re-exported, and rebuilt into the digest:

| Prefab | Affects | State |
|---|---|---|
| `Unity/Assets/Demo_1/Prefabs/TS Index Unit.prefab` | `Index01..05/Y_Stopper` (5) | fixed |
| `Unity/Assets/Demo_1/Prefabs/Stopper Unit.prefab` | `Stopper01..04/Y_Stopper` (4) | fixed |

This entry is kept as a worked example of the correction path, not as an outstanding defect: the twin
authored it one way, the PLC and the twin's own geometry said the other, and the PLC won. That is the
authority split doing its job.

Related and **correct** — do not "fix" it: `fg-01.md:103,111` says the FG_01 gates are *"the opposite
sense to the transport stoppers"*. Gate extended = closed = restrictive; stopper retracted = holding =
restrictive. Genuinely opposite. That sentence only *reads* wrong while the stopper prose is wrong.

**Two `Role` entries name the wrong successor.** Lift01's prose says it feeds `Index01`; the wiring
feeds `Stopper03`. Index05's says it releases towards `Lift02`; the wiring goes to `Stopper04`. Both
skip the intervening stopper. The measured ring in `machine.md` shows the real order;
`FG_Transport.TcPOU:412-414` settles it — the wiring is the authority.

---

## 7. Reading order for a new group

1. This page — the handshake contract and the reset model.
2. [The machine](../context/machine.md) — the measured ring order and which Index serves which group.
3. [SPT framework](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/spt-framework.md)
   — the framework, and the official build order that says to code Auto mode **last**.
4. The group's own page — what its devices *are*.

Do not take a station handshake from a MIL coroutine. They describe the twin's animation, and the
design they describe is the one this page replaced.

---

## Related

- [`spt-framework.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/spt-framework.md) — SPT V3.9 API, state machine, build order
- [`plc-io-exceptions.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/plc-io-exceptions.md) — signals unlinked on purpose
- [`../context/machine.md`](../context/machine.md) — the measured ring order and the Index→group couplings

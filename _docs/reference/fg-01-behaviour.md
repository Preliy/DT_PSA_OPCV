# FG_01 — the behaviour contract

Identify and mark. Written from the shipped ST; **the PLC is master for behaviour**, so where this
disagrees with an authored `Function` entry in the twin, this wins.

Source: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/11 FG_01/FG_01.TcPOU`.

---

## Components

Nine, all SPT components — no bare coils, no GVL.

| Instance | FB | Twin device |
|---|---|---|
| `Y_Gripper`, `Y_Platform`, `Y_ReaderWindow` | `FB_DoubleSolenoidFeedback` | Cylinder |
| `Y_Gate1`, `Y_Gate2` | `FB_SingleSolenoidFeedback` | Cylinder |
| `B_SafetyGate1`, `B_SafetyGate2` | `FB_DigitalSensor` | SensorBinary |
| `P_Camera` | `FB_AbstractCamera` | DataReader |
| `Y_LaserMark` | `FB_AbstractLightSource` | LinkByte |

`P_Camera` was `P_Reader`. Not a rename — the twin device became a `DataReader` with a real
vision-sensor protocol, so this station now drives the same FB as FG_02 over the same four status
bits. The old reader's single `Result` bit was an echo of its own trigger. Its function block and
DUTs were **deleted 2026-08-22** once nothing referenced them.

> **This station does not verify its own mark.** `P_Camera` reads the payload key `SerialNumber`
> (expected **60**, carried by `Assembly Part 1`); the laser writes a *different* datum, `LaserMark`,
> and **FG_02** is what reads that back. The read happens after the laser fires, which invites the
> assumption that it is a verification. It is not — it is identification. A pallet with no part reads
> 0 and fails. The comparison itself lives in `SIM_1`'s `FB_Camera`, against a value set in that
> group's `Mapping` action — see [`fg-02-behaviour.md`](fg-02-behaviour.md) for the shared mechanism
> and the datum table.

`Y_Platform` positions the laser head in **service only** and is never actuated by the cycle.

## Production cycle

`Execute`, mode `Production`. Steps of 10; the whole chain is one `CASE`.

| Step | Action | Advances on | Timeout |
|---:|---|---|---|
| 0 | laser off, camera **on**, trigger cleared | — | |
| 10 | `Y_Gate1.Extend` + `Y_Gate2.Extend` together | both `.Extended` **and** both `B_SafetyGate*.Active` | component travel, 3 s |
| 20 | `Y_Gripper.Extend` | — | |
| 30 | settle | `ClampSettleTimer` 500 ms, armed on `Y_Gripper.Extended` | |
| 40 | `Y_LaserMark.Enable` | `MarkTimer` 1 s, then `Disable` | |
| 50 | `Y_ReaderWindow.Extend` | — | |
| 60 | wait for camera | `P_Camera.Ready` | `ReadyTimer` 2 s → **fault 2** |
| 70 | `P_Camera.Trigger` | `DeviceBusy` **or** `ResultValid` | `ShotTimer` 3 s → **fault 3** |
| 80 | read verdict, latch `_LastResultOK` | `ResultOK` — else **fault 1** | `ShotTimer` → **fault 3** |
| 90 | `ClearTrigger` (tells the camera its verdict was read) | — | |
| 100 | `Y_ReaderWindow.Retract` | `.Retracted` | |
| 110 | `Y_Gripper.Retract` | `.Retracted` | |
| 120 | both gates `Retract` | both `.Retracted` **and** both `B_SafetyGate*` clear | |
| 130 | camera off, `ChangeState(Complete)` | — | |

Two ordering rules that are load-bearing:

- **The camera is powered at step 0, not at the read.** It has the whole gate-clamp-mark sequence to
  come `Ready` in, so the 2 s at step 60 is a grace period on top, not a cold-start budget.
- **`ReadyTimer` is armed on `Y_ReaderWindow.Extended`, not on the step.** Step 50 extends and
  advances on the same scan, so step 60 waits on two things. Arming on the step alone would let a
  slow window burn the camera's budget and raise fault 2 — *"the camera is not answering"* — for a
  pneumatic fault. The window reports its own travel timeout.

`Maintenance` and `Manual` run no group sequence. `Y_Platform` and `P_Camera` stay reachable through
each component's own HMI control.

## Fault codes

`ST_FG_01_Identify_Status`. Raised with `AbortImmediate()`, cleared in `Clearing`, published as
`HMI.Identify.FaultCode`.

| Code | Meaning |
|---:|---|
| 1 | the part is not the one this station expects (`ResultOK` false) |
| 2 | the camera never became `Ready` |
| 3 | the shot never completed |

**A wrong serial number aborts the group.** `Index01` then never receives `OperationDone` and raises
its own fault 3 on the operation timeout — the same shape FG_02 uses on a NOK. There is no reject
station on this line, so a part that does not belong stops the pallet where it is and asks for a
human.

## Safety — the laser interlock

> **An entry check and an abort path, by design.** The gates are closed and proven before the cycle
> is allowed to reach the laser, and they cannot open during it: the only step that opens them is
> step 120, eight steps after the burst has finished. A live per-scan permissive was considered and
> is deliberately not implemented.

What the code does:

- **On entry** — step 10 will not advance until `Y_Gate1.Extended AND Y_Gate2.Extended AND
  B_SafetyGate1.Active AND B_SafetyGate2.Active`. Closed for a gate is its **extended** limit, the
  opposite sense to a transport stopper.
- **By sequence position** — the reader window is still retracted (shielding the optics) at step 40,
  because it does not open until step 50.
- **By abort** — E-Stop in any mode, or a guard door in `Production`, clears `Machine.SafetyOk`;
  `Machine.EnforceSafety` calls `AbortImmediate()`, and FG_01's `Aborting` step 0 calls
  `Y_LaserMark.Disable()`.

What the code does **not** do: re-check the gates on every scan of the 1 s burst.
`Y_LaserMark.Enable()` at step 40 carries no permissive term, and `FB_AbstractLightSource.Enable()`
is one line — `OutputData.0 := TRUE;`. **This is accepted.** FG_01 shuts the cell before it does
anything else, the gates are pneumatic cylinders held at their extended limit, and any real loss of
the safety chain reaches the laser through the abort path within a scan.

Note the FG_01 gates are *not* part of `Machine.SafetyOk`, which covers only the two E-stops and the
six enclosure doors. This interlock is this group's own, and the cell chain is what backs it.

## Non-production states

| State | Leaves the station | Why |
|---|---|---|
| `Aborting` | laser off, camera off, **window shielded, grip kept** | releasing a clamped payload on abort would drop it |
| `Stopping` | laser off, camera off, window shielded, **grip kept** | so the cycle resumes after a reset without re-fixturing |
| `Resetting` | laser off, camera off, window shielded → grip released → gates opened | home is *nothing energised*; gates last, and only once the payload is free |
| `Clearing` | `_FaultCode := 0`, then every component `Reset()` | the fault clears by the act of clearing, not by the condition going away — a wrong part is still wrong after the camera stops reporting it |

`Resetting` terminates on its own cylinders and on nothing else, per the rule in
[`transport-behaviour.md`](transport-behaviour.md) §4.

## Travel timeouts

Set in `Initialize`, in ms. They alarm on a jam; they do not pace the cycle.

| Component | Extend / Retract |
|---|---|
| `Y_Gripper`, `Y_ReaderWindow` | 2000 |
| `Y_Platform` | 3000 |
| `Y_Gate1`, `Y_Gate2` | 3000 (longer stroke) |

## Related

- [`transport-behaviour.md`](transport-behaviour.md) — the Index↔group handshake and the reset rule
- [`spt-framework.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/spt-framework.md) — SPT V3.9 state machine and build order
- [`fg-02-behaviour.md`](fg-02-behaviour.md) — the same camera protocol, one station on

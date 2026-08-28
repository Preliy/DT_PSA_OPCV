# FG_04 — the behaviour contract

Press and seat check. Written from the shipped ST; **the PLC is master for behaviour**.

Source: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/14 FG_04/FG_04.TcPOU`.

---

## Components

| Instance | FB | Twin device |
|---|---|---|
| `Y_AxisZ` | `FB_DoubleSolenoidFeedback` | Cylinder |
| `B_NIO` | `FB_DigitalSensor` | SignalBinary |

**The press is a double solenoid on purpose.** An abort mid-stroke leaves it where it is, rather
than letting a spring drive it further into the part.

## `B_NIO` is a verdict, not a sensor reading

The twin's seating sensor is **not a PLC symbol at all** — its `Link` is disabled. It feeds
`PartPressDetector` inside Unity, which publishes the conclusion here as one bit: *the press reached
its bottom limit and nothing was correctly seated underneath it.*

So the bit is only meaningful **at the bottom of the stroke with the hold expired**, and that is the
only place this module reads it. Reading `B_NIO` anywhere else in the cycle is meaningless.

## Production cycle

`Execute`, mode `Production`.

| Step | Action | Advances on |
|---:|---|---|
| 0 | — | immediately |
| 10 | let the pallet settle on the index lift | `SettleTimer` 500 ms |
| 20 | `Y_AxisZ.Extend` — down onto the part | `.Extended` |
| 30 | hold at the bottom, then read the verdict | `HoldTimer` 1 s, then `B_NIO.Active` → **fault 1**, else advance |
| 40 | `Y_AxisZ.Retract` — clear before the index lowers | `.Retracted` |
| 50 | `ChangeState(Complete)` | — |

`HoldTimer` is armed on `(SequenceState = 30) AND Y_AxisZ.Extended`, so the hold begins at the bottom
limit rather than at the step.

**The 1 s hold is a timer because it is a process requirement with no sensor behind it.** The part is
being seated and nothing reports *"seated"* — only `B_NIO` reports the opposite.

`Maintenance` and `Manual` run no group sequence; `Y_AxisZ` is jogged through its own solenoid HMI
command struct whenever `HMIPermissions` has granted control.

## Fault codes

`ST_FG_04_Press_Status`, published as `HMI.Press.FaultCode`. One code.

| Code | Meaning |
|---:|---|
| 1 | NIO — the press bottomed and nothing was correctly seated under it |

**An NIO aborts the group.** `AbortImmediate()` runs, `Index04` never receives `OperationDone`, and
raises its own fault 3 — *"group did not finish"* — when its operation timeout expires. That path
already exists in `FB_TransferIndex` and needed nothing added. The consequence is intended: there is
no reject station on this line, so a bad press stops the pallet where it is and asks for a human.

## Safety

No authored `Safety` section and no group permissive. The cell chain (`Machine.SafetyOk` →
`AbortImmediate`) applies, and it is what makes the abort behaviour below matter.

## Non-production states

> **A press held down on a part is the hazardous state of this station.** It is loaded against the
> workpiece and against the pallet under it, and the index lift is holding both.

| State | Leaves the station |
|---|---|
| `Aborting` | **retracts the press** — not a no-motion abort |
| `Stopping` | retracts the press, same reason |
| `Resetting` | retracts the press; home is press up |
| `Clearing` | `_FaultCode := 0`, then `Y_AxisZ.Reset()` and `B_NIO.Reset()` |

Retracting is the safe direction and the one that lets the pallet be got out by hand afterwards.

Every one of those strokes is bounded by `Y_AxisZ.RetractTime`, so a jammed press **alarms out of the
state rather than parking in it** — an abort that waits on a limit that may never arrive is exactly
the failure mode [`transport-behaviour.md`](transport-behaviour.md) §4 warns about.

`Clearing` sets the fault to zero before resetting components: a bad part is still a bad part after
the press has lifted, and the operator has to have taken it out.

## Travel timeouts

`Y_AxisZ.ExtendTime` = `RetractTime` = 2000 ms. On a press, alarming on a jam is what a timeout is
actually for.

## Related

- [`transport-behaviour.md`](transport-behaviour.md) — the Index↔group handshake, and the Index fault 3 this group's abort provokes

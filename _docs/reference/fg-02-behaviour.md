# FG_02 — the behaviour contract

Optical inspection. Written from the shipped ST; **the PLC is master for behaviour**.

Source: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/12 FG_02/FG_02.TcPOU`.

---

## Components

One: `P_Camera : FB_AbstractCamera`, twin device `Y_Camera` (LinkByte). Nothing in this group moves.

The twin side is `FB_Camera` in `SIM_1`. Both halves have to agree on the bit layout and nothing
checks it for you.

## The camera handshake

Two signals out, four back. This is a real protocol, not a status bit echoing a trigger.

| Out | Back | Meaning |
|---|---|---|
| `Enable` | `Ready` | permission to trigger |
| `Trigger` | `DeviceBusy` | the shot is running |
| | `ResultValid` | a verdict is on the wire, and stays there until the trigger is released |
| | `ResultOK` | the verdict |

What that buys is diagnosis: the station can tell *"the camera never answered"* from *"the shot never
completed"* from *"the part is bad"*. The previous interface had one status bit wired straight from
the trigger and could report none of the three — which is why the old sequence was a fixed 1 s dwell
that could not fail.

### What is actually compared

**The twin does not evaluate anything.** It echoes enable and trigger and hands over the datum it
read; `Ready`, `DeviceBusy`, `ResultValid` and `ResultOK` are all synthesised in `SIM_1`'s
`FB_Camera`, which compares the datum against an expected value **set in that group's `Mapping`
action**. Change the expectation there, not in the control PLC.

| Station | Payload key read | Expected | Written by |
|---|---|---:|---|
| FG_01 | `SerialNumber` | 60 | the part itself (`Assembly Part 1`) |
| **FG_02** | **`LaserMark`** | **240** | the FG_01 laser |
| FG_05 | `CapsID` | 810 | the part itself |

**FG_02 is the station that verifies the mark**, not FG_01. FG_01 fires the laser and then reads
`SerialNumber` — it never checks its own work. An unmarked part reads `LaserMark` = 0 here and
fails.

## Production cycle

`Execute`, mode `Production`.

| Step | Action | Advances on | Timeout |
|---:|---|---|---|
| 0 | `P_Camera.Disable` | — | |
| 10 | `Enable` | `Ready` | `ReadyTimer` 2 s → **fault 2** |
| 20 | `Trigger` | `DeviceBusy` **or** `ResultValid` | `ShotTimer` 3 s → **fault 3** |
| 30 | read verdict, latch `_LastResultOK` | `ResultOK` — else **fault 1** | `ShotTimer` → **fault 3** |
| 40 | `Disable` (clears the trigger first) | — | |
| 50 | `ChangeState(Complete)` | — | |

**`ResultValid` counts as an acknowledgement at step 20.** A fast camera can raise and drop
`DeviceBusy` inside one scan, so waiting only on `DeviceBusy` would hang on exactly the device that
answered quickest.

`ShotTimer` deliberately spans steps 20 **and** 30: the split between *acknowledged* and *answered*
is the station's business, but the camera's total response time is one number and is what an
operator would be told. Same budgets as FG_01 — it is the same device.

`Maintenance` and `Manual` run no group sequence; the camera stays reachable through
`FB_AbstractCamera.HMICommunication` whenever `HMIPermissions` has granted control.

## Fault codes

`ST_FG_02_Inspection_Status`, published as `HMI.Inspection.FaultCode`.

| Code | Meaning |
|---:|---|
| 1 | the part is bad (`ResultOK` false) |
| 2 | the camera never became `Ready` |
| 3 | the shot never completed |

**A NOK aborts the group.** `Index02` never receives `OperationDone` and raises its own fault 3 on
the operation timeout, exactly as FG_04 does on `B_NIO`. There is no reject station on this line, so
a bad part stops the pallet where it is and asks for a human.

## Safety

**No `Safety` section is authored for this group in the twin, and no permissive is written in the
PLC.** That is a gap in the twin, not permission to invent one. The station has no moving parts and
no hazardous output; the cell-level chain (`Machine.SafetyOk` → `AbortImmediate`) still applies.

## Non-production states

Every one of `Aborting`, `Stopping`, `Resetting` is the same two steps: `P_Camera.Disable()`, then
complete. `Disable()` drops the trigger before the enable, so a shot is never left armed on a device
that is losing power on the next line.

Home position for this group is *nothing energised*. There is no mechanism to bring back to a known
place, so `Resetting` terminates on its own call and on nothing else — the rule from
[`transport-behaviour.md`](transport-behaviour.md) §4.

`Clearing` sets `_FaultCode := 0` first, then waits for `P_Camera.Reset()`. The fault clears by the
act of clearing: a bad part is still a bad part after the camera has stopped reporting it, and the
operator has to have taken it out.

## Related

- [`fg-01-behaviour.md`](fg-01-behaviour.md) — the same camera protocol, one station back
- [`transport-behaviour.md`](transport-behaviour.md) — the Index↔group handshake and the reset rule

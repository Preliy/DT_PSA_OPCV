# FG_System — the safety contract

Cell infrastructure: the enclosure, the six interlocked doors, the two emergency stops and the signal
tower. It processes no parts. Written from the shipped ST; **the PLC is master for behaviour**.

Sources: `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/01 FG_System/FG_System.TcPOU`, `Beckhoff/TwinCAT_1/PLC/PLC_1/Modules/00 Machine/Machine.TcPOU`.

---

## The authority split inside safety

> **FG_System publishes two facts about the machinery and applies no policy to them.**

| Level | Owns | Members |
|---|---|---|
| `FG_System` | the facts | `GuardsSecure`, `EmergencyStopActive` |
| `Machine` | the policy | `SafetyOk`, `EnforceSafety` |

Only the machine owns the PackML mode, and an equipment module that knows what
`ePMLUnitMode_Production` implies has reached past its level. That is why the mode test lives in
`Machine.SafetyOk` and not here.

Both facts are **property getters, computed on every read** — never stored flags. Same rule the
transport stations follow for `CanAccept` and `Occupied`, for the same reason: a remembered readiness
flag maintained in one state is stale in all the others.

```iecst
EmergencyStopActive := SS_EStop1.Active OR SS_EStop2.Active;

GuardsSecure := B_SafetyDoor11.Secure AND ... AND B_SafetyDoor23.Secure;
```

`Secure` is **shut AND locked**. Closed alone is not enough.

## The policy — `Machine.SafetyOk`

```iecst
SafetyOk := NOT FG_System.EmergencyStopActive
        AND ( (_CurrentMode <> ePMLUnitMode_Production) OR FG_System.GuardsSecure );
```

**Mode is the gate, and the two inputs are gated differently on purpose:**

| Input | Acts in | Why |
|---|---|---|
| Emergency stops | **every mode** | a mushroom is the one input that is never mode-dependent, and Manual is precisely the mode where somebody is inside the cell jogging a cylinder |
| Guard doors | **Production only**, every state | Maintenance and Manual ignore them — that is what those modes are for, and it is the only way into the cell, because the locks are commanded throughout Production |

`Machine.EnforceSafety` calls `AbortImmediate()` whenever `SafetyOk` is false, **except** in
`Aborting`, `Aborted` and `Clearing`:

| Excluded state | Why |
|---|---|
| `Aborting` / `Aborted` | re-issuing `AbortImmediate()` every scan overwrites the command that would leave `Aborted`, so the machine could never recover. This is a deadlock, and the exclusion is the fix. |
| `Clearing` | we are in `Clearing` *because* safety broke. Aborting out of it makes clearing impossible. |

This is the path that disables FG_01's laser and retracts FG_04's press: the machine aborts, and the
base `Aborting` carries the abort down to every registered submodule.

## The lock policy

```iecst
_DoorsRequestedLocked := (_MachineMode = ePMLUnitMode_Production);
```

Sealed in Production, free in Maintenance and Manual. That is the whole rule.

It is what makes *"closed and locked in every Production state"* reachable at all: the locks are
already commanded at power-up, long before any reset, so **a reset never has to wait for them**.

> **The consequence is deliberate: an operator in Production cannot open a door at all.** Getting
> into the cell means selecting Maintenance or Manual, which drops every lock.

A door has 3 s (`LockTime`) to confirm its lock before raising its own fault 1.

## Indication

**The tower shows the MACHINE's state, not this module's.** `Machine.Execute` deliberately does not
call `SUPER^.Execute()`, so a registered submodule never follows the machine into `Execute` — a tower
driven from `FG_System.CurrentState` would sit dark through all of production. The machine hands its
state down every scan through `SetMachineIndication(State, Mode)`.

`SetMachineIndication` **must** be called before the machine's `SUPER^.CyclicLogic()`, which is what
calls this module's `CyclicLogic`. Otherwise the lock policy and the tower both act on last scan's
state.

### The E-stop lamps

| Condition | Lamp |
|---|---|
| not latched | dark |
| latched | solid |
| latched **and** machine in `Clearing` | **flashing** |

The flashing case is the one that earns its keep. `Clearing` stalls until the safety chain is whole
again, so with two mushrooms on the cell an operator staring at a machine that will not clear needs
to know **which** one is still down. Solid-on-both says a mushroom is latched; flashing says *that is
what is blocking you right now*.

Phase comes from `H_SignalTower.Flash` (1 Hz, `FlashTime` 500 ms), re-exposed as `IndicationFlash`,
so the mushroom lamps, the red tower lamp and the panel's RESET button blink together rather than
against each other.

`DriveEStopLamps()` runs **before** `SUPER^.CyclicLogic()`, because `FB_IlluminatedButton` copies
`Lamp` to its coil inside its own `CyclicLogic`; setting `Lamp` after would put it a scan behind.

The decision lives in this module and not in `FB_IlluminatedButton` on purpose: **a component must
not know which PackML state the machine is in.** It exposes `Lamp`; the module that knows writes it.

## No state methods are overridden

Deliberate. `NoStateTasksToComplete` defaults TRUE and is re-armed on every state change, so each of
the base's transition states self-completes on the scan it is entered. An infrastructure module has
nothing to sequence, and a step chain here would only be one more thing for the machine's `Resetting`
to wait on.

## Components and I/O

Nine registered components. **Forgetting one is silent** — its `CyclicLogic` would simply never be
called, and a door would report neither closed nor locked for ever.

| Component | FB | Count |
|---|---|---:|
| `B_SafetyDoor11..13`, `B_SafetyDoor21..23` | `FB_SafetyDoor` | 6 |
| `SS_EStop1`, `SS_EStop2` | `FB_IlluminatedButton` | 2 |
| `H_SignalTower` | `FB_SignalTower` | 1 |

22 DI + 20 DO. Six doors contribute two inputs and one coil each; the two mushrooms one input and one
lamp coil each; the tower four coils. **The panel's own eight inputs and eight lamps belong to
`MAIN.ControlSource_Panel`, not to this module.**

Each mushroom is one component carrying signal bit and lamp bit together — they are one device.

> **Both mushrooms are read normally closed — TRUE while healthy, FALSE while latched.** That is
> how the real hardware is wired, and getting it the other way round has the worst failure mode
> available: a cut cable would read as "no emergency stop". So it is the sense every control
> platform reads against, and the **twin inverts to match it** rather than the reverse — the twin's
> `FB_Button` reports `bValue` TRUE while *pressed*, and the simulation layer negates it on the way
> into the process image. A platform that reads the twin directly, without that inversion, must
> invert on its own side instead; either way the mushroom input arrives NC.
>
> The consequence is deliberate: **with no process image at all** — the simulation not running, the
> fieldbus down — both inputs read 0, which under NC means latched, and the machine will not leave
> `Aborted`. That is fail-safe, not a fault.
>
> How Beckhoff realises it is in [`plc-io-exceptions.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/plc-io-exceptions.md).

## Related

- [`transport-behaviour.md`](transport-behaviour.md) — the derived-not-stored rule this module follows
- [`fg-01-behaviour.md`](fg-01-behaviour.md) — the laser interlock, which is FG_01's own and **not** part of `SafetyOk`
- [`state-lamp.md`](state-lamp.md) — the signal tower's state-to-colour mapping
- [`plc-io-exceptions.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/plc-io-exceptions.md) — signals unlinked on purpose

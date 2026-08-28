# Signal tower and panel-lamp state table

The indication contract for `H_SignalTower` and the `H_ControlPanel` button lamps: which lamp is on,
and whether it is solid or flashing, for every PackML state.

**This file is curated, not generated.** It once lived under `context/`, which is the one place it
could not survive: that directory is rebuilt wholesale from the twin and anything the build did not
write is deleted. It lives here instead, alongside the other hand-written references, where the
never-hand-edit rule does not apply.

`S` — solid colour. `F` — flashing.

| Condition / Indication | Aborting | Clearing | Aborted | Completed | Stopped | Stopping | Resetting | Idle | Starting | Execute | Completing | Holding | Held (No Production) | Unholding | Suspending | Suspended | Unsuspending | Output |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Abnormal Stop | F | F | F |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Red Lamp Flashing |
| Controlled Stop |  |  |  | S | S | S | S |  |  |  |  |  |  |  |  |  |  | Red Lamp Solid |
| Starved Upstream |  |  |  |  |  |  |  |  |  |  |  |  |  |  | F | F |  | Amber Lamp Flashing |
| Blocked Downstream |  |  |  |  |  |  |  |  |  |  |  |  |  |  | S | S |  | Amber Lamp Solid |
| Low Material | F | F | F | F | F | F | F | F | F | F | F |  |  | F | F | F | F | Blue Lamp Flashing |
| Material Exhausted |  |  |  |  |  |  |  |  |  |  |  | S | S |  |  |  |  | Blue Lamp Solid |
| Ready to Start |  |  |  |  |  |  |  | F |  |  |  |  |  |  |  |  |  | Green Lamp Flashing |
| Running |  |  |  |  |  |  |  |  | S | S | S |  |  | S |  |  | S | Green Lamp Solid |
| Starting / Restarting |  |  |  |  |  |  |  |  | F |  |  |  |  | F |  |  | F | Horn |
| Ready to Start |  |  |  |  |  |  |  | F |  |  |  |  |  |  |  |  |  | Start Button Flashing |
| Running |  |  |  |  |  |  |  |  | S | S | S |  |  | S | S | S | S | Start Button Solid |
| Ready to Reset |  |  | F | F | F |  |  |  |  |  |  |  |  |  |  |  |  | Reset Button Flashing |

## Reading it against this project

Two translations are needed before this becomes ST, and both are easy to get wrong:

- **`Completed` here is `Complete` in the PLC.** This project runs SPT V3.9, where the state is
  `E_PMLState.ePMLState_Complete`; `Completed` is the V4 spelling and occurs **0** times in the
  shipped binary. See [`spt-framework.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/spt-framework.md).
- **The rows are independent conditions, not a priority ladder.** Red comes from the state, amber
  from starvation/blocking, blue from material and green from the state. Two lamps can be lit at
  once — Low Material is flagged as flashing blue across almost every state, including the ones that
  also light red or green.

## What FG_System implements

| Row | Status |
|---|---|
| Abnormal Stop, Controlled Stop, Ready to Start, Running | **implemented** — driven from the machine's `CurrentState` |
| Start Button Flashing / Solid, Reset Button Flashing | **implemented** — panel lamp bits, same flash phase |
| Starved Upstream, Blocked Downstream | **input exposed, never TRUE** — no starvation or blocking source exists in the machine yet |
| Low Material, Material Exhausted | **input exposed, never TRUE** — there is no material model |
| Horn | **not implemented** — the twin carries no horn device |

The unimplemented rows are present as `BOOL` inputs on `FB_SignalTower` defaulting `FALSE`, so the
table can be completed later without touching the lamp logic.

## Bit layout

Verified 2026-08-20 against the live `PanelSampler._components` lists:

| Symbol | Bits |
|---|---|
| `H_SignalTower` `ControlData` | 0 RED, 1 YELLOW, 2 BLUE, 3 GREEN |
| `H_ControlPanel` `StatusData` (pressed) / `ControlData` (lamp) | 0 START, 1 RESET, 2 STOP, 3 CLEAR, 4 ABORT, 5 PRODUCTION, 6 MAINTANANCE, 7 MANUAL |

Note the tower has **four** lamps, not three, and GREEN is bit **3**. The twin's authored prose said
three lamps with GREEN at bit 2 until it was corrected on 2026-08-20.

## Related

- [`spt-framework.md`](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/reference/spt-framework.md) — the V3.9 ⇄ V4 differences, including the `Complete` /
  `Completed` split
- [`../context/fg-system.md`](../context/fg-system.md) — the devices themselves

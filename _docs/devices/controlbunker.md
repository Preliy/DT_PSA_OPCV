# ControlBunker

Component: Preliy.Demo.ControlBunker
Package:   this project — Unity/Assets/Demo_1/Scripts/ControlBunker.cs
Summary:   The cap feeder: a vibrating bunker and a short conveyor that bring caps to the pick position, switched by two bits.
Control:   ControlData
Status:    —

## What it is

A parts feeder, of the kind that sits beside an assembly station and keeps a supply of small parts
coming. A vibration table shakes caps out of a bunker onto a narrow conveyor, which carries them to
where a gripper can pick one up. It is project-specific: no Open Commissioning component covers it,
so it is a small script on top of a plain byte link.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `ControlData.0` | Bunker on — run the vibration table |
| `ControlData.1` | Conveyor on — run the caps conveyor |

**No status bits.** The feeder does not tell the PLC anything: not whether it is running, not whether
it has caps left. Whether a cap is actually at the pick position is answered by a separate sensor.

## Watch out

**A feeder is not a sequenced device.** It is switched on and left running while the station works —
it does not run "one cap at a time" and there is nothing to wait for. See
[the FG_05 behaviour contract](../../reference/fg-05-behaviour.md).

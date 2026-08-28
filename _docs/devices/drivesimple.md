# DriveSimple

Component: OC.Components.DriveSimple
Package:   com.open-commissioning.core
Summary:   A conveyor motor: run forwards, run backwards, or stop. Reports the speed it actually reached and whether it is moving.
Control:   Control
Status:    Status

## What it is

The motors that move pallets: the conveyor belts on both levels, and the short belt on each lift
carriage. Not a positioning axis — it has no target position and no idea where anything is. It runs
until it is told to stop, and something else, usually a sensor, decides when that is.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Run forwards |
| `Control.1` | Run backwards |
| `Status.6` | Moving |
| `StatusData` | Actual speed |

Setting both direction bits, or neither, commands a stop.

## How the twin models it

The speed ramps towards the commanded direction at a configured acceleration rather than jumping to
it, and the resulting speed drives everything standing on the belt. Each instance has its own speed
and acceleration.

## Watch out

**A running belt is not a moving pallet.** The motor reports its own speed, and nothing else. Whether
a pallet actually arrived is a sensor's answer — which is exactly the mistake a twin is there to
catch.

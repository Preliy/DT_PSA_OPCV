# SensorBinary

Component: OC.Components.SensorBinary
Package:   com.open-commissioning.core
Summary:   A presence sensor. Reports whether something is inside its beam — one bit, no commands.
Control:   —
Status:    Status

## What it is

A light barrier or proximity switch: the machine's eyes. It is how the control program knows a
pallet has arrived at a station or has left it again.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Status.0` | Something is detected |

No control bits. The PLC cannot command a sensor, only read it.

## How the twin models it

The sensor is a real volume in the 3D scene — a thin beam of a settable length, or a box fitted to
the geometry — and it switches when a part physically enters it. Nothing tells the sensor a part is
there; it sees one because one is there. That is what makes a mis-timed release or a part left
behind show up in the twin the way it would on the machine.

Each instance can be inverted, for a sensor whose real-world contact is normally closed.

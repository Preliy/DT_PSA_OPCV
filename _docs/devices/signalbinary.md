# SignalBinary

Component: OC.Components.SignalBinary
Package:   com.open-commissioning.core
Summary:   One bit to the PLC that is worked out somewhere else in the twin, rather than measured by a sensor of its own.
Control:   —
Status:    Status

## What it is

It looks like a sensor to the control program — the same single status bit, the same function block
— but there is no beam anywhere. It publishes a value another component in the scene computed.

Use it for a **verdict** rather than an observation: "the press bottomed out with nothing seated
under it" is a conclusion drawn from a cylinder position and a sensor together, not something any one
sensor can see.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Status.0` | The signal is true |

## How the twin models it

It is pointed at another component in the scene that produces a boolean, and mirrors it. In this
machine the source is usually a small project script, such as the one that decides whether the press
seated a part.

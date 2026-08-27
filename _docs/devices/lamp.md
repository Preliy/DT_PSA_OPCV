# Lamp

Component: OC.Interactions.Lamp
Package:   com.open-commissioning.core
Summary:   An indicator light: one bit down from the PLC, nothing back.
Control:   Control
Status:    —

## What it is

A signal-tower segment or a panel indicator. It carries no information *to* the control program at
all — it exists so the program can say something to the person standing in front of the machine.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Light on |

Like a button, a lamp takes **one bit**, and lamps are normally packed into a panel rather than
addressed one at a time.

## How the twin models it

The bit switches the emissive colour of the lamp object in the scene, and its dot on the on-screen
panel. Which colour means what is a decision of the control program, not of the lamp — this machine's
mapping is in [the state lamp page](../../reference/state-lamp.md).

# Button

Component: OC.Interactions.Button
Package:   com.open-commissioning.core
Summary:   A push button with a lamp in it. One bit up to the PLC saying it is pressed, one bit back down driving its light.
Control:   Control
Status:    Status

## What it is

What an operator actually touches: start, stop, reset, an emergency stop mushroom. The lamp is
driven by the PLC, not by the button, so the panel shows what the program believes rather than what
the operator just did.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Status.0` | Pressed |
| `Control.0` | Light the button's lamp |

A button takes **one bit** in each direction. That matters when several are packed into a panel — see
[PanelSampler](panelsampler.md).

## How the twin models it

Two kinds, set per instance:

| Type | What a click does |
|---|---|
| **Momentary** | Goes true, and back to false about a tenth of a second later |
| **Latching** | Stays true until it is clicked again — the behaviour of an emergency stop mushroom |

Buttons appear both as 3D objects in the scene and as controls on the on-screen operator panel; both
drive the same bit.

## Watch out

**A latching button does not release itself.** Clicking an emergency stop in the twin leaves the cell
in emergency stop until you click it a second time, exactly like twisting the real mushroom back out.

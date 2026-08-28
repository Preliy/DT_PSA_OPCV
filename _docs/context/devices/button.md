<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# Button

**A push button with a lamp in it. One bit up to the PLC saying it is pressed, one bit back down driving its light.**

Twin device type · twin FB `FB_Button` · **2 instances** in FG_System · Unity component `OC.Interactions.Button`

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

## In this machine

**Signal** — One input and one lamp coil, as a single device. Active while the mushroom is latched.

There are **2** of them, in FG_System:

| Device | Twin PLC path | Group |
|---|---|---|
| `SS_EStop1` | `MAIN.FG_System.SS_EStop1` | FG_System |
| `SS_EStop2` | `MAIN.FG_System.SS_EStop2` | FG_System |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/button.md)
- **Siemens** — _no knowledge base published yet_

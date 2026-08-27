<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# Lamp

**An indicator light: one bit down from the PLC, nothing back.**

Twin device type · Unity component `OC.Interactions.Lamp` · **no device of its own in this machine** - every instance is folded into another device, so it carries no PLC address. Its group page shows which bit each one is.

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

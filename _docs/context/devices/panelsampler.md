<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# PanelSampler

**Not a device: a collector. Packs up to 32 buttons and lamps into a single 32-bit word in each direction, so a whole operator panel costs the PLC one address.**

Twin device type · twin FB `FB_Panel` · **2 instances** in FG_System · Unity component `OC.Interactions.PanelSampler`

## What it is

An operator panel has a dozen buttons and lights on it. Giving each one its own PLC address is
wasteful and tedious, so the panel is sampled: every control it lists is packed, bit by bit, into one
32-bit status word going up and one 32-bit control word coming down.

## What the PLC sees

One **32-bit word each way**. Bit *n* of the status word is the *n*-th listed control's status bit;
bit *n* of the control word is written back to that same control. In practice, for a panel of push
buttons: the status word says which buttons are pressed, and the control word lights their lamps.

Which control sits on which bit is a property of one particular panel, so it is stated on that
panel's own device — see the **Bit mapping** section of the group page that owns it.

## How the twin models it

The panel holds an ordered list of controls. Each declares how many bits it needs — a button one, a
lamp one — and they are allocated in list order from bit 0. At startup the panel **switches off each
listed control's own PLC link** and takes it over; a sampled button is no longer a device the PLC can
address by itself. It also builds the on-screen operator panel from the same list.

## Watch out

- **The list order *is* the bit assignment.** Reordering the list in Unity silently moves every
  signal to a different bit, and a control program written against the old order keeps running and
  does the wrong things.
- **32 bits is the ceiling.** A panel that asks for more is rejected at startup and reports nothing
  at all.

## In this machine

There are **2** of them, in FG_System:

| Device | Twin PLC path | Group | Role / Signal |
|---|---|---|---|
| `H_ControlPanel` † | `MAIN.FG_System.H_ControlPanel` | FG_System | PanelSampler. Disables its children's individual communication and exposes one aggregated FB_Panel DWORD, packing their status bits in and unpacking control bits back. |
| `H_SignalTower` | `MAIN.FG_System.H_SignalTower` | FG_System | PanelSampler. Aggregates the four tower lamps into one FB_Panel DWORD, with the lamps own links disabled. Same packing mechanism as the control panel. |

† **From the reference scene only.** Every scene instances the same `Machine_1` prefab, but each adds its own vendor's operator panel, so this row is `VC_Demo_1_Beckhoff_1`'s and another scene spells it differently. The machine is what is *un*marked; a marked row is an example. Each vendor's own is on its page below.

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/panelsampler.md)
- **Siemens** — _no knowledge base published yet_

# PanelSampler

Component: OC.Interactions.PanelSampler
Package:   com.open-commissioning.core
Summary:   Not a device: a collector. Packs up to 32 buttons and lamps into a single 32-bit word in each direction, so a whole operator panel costs the PLC one address.
Control:   ControlData
Status:    StatusData

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

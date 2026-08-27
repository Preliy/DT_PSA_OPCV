# DataReader

Component: Preliy.Demo.DataReader
Package:   this project — Unity/Assets/Demo_1/Scripts/DataReader.cs
Summary:   A code reader or camera: on command, reads a number carried by the part in front of it and hands it to the PLC.
Control:   Control
Status:    Status

## What it is

The station that answers "which part is this?". In the real cell it is a camera or a barcode
scanner; the part carries an identity, and the reader turns it into a number the control program can
act on. This machine has three of them — one identifies, one inspects, one checks a cap.

Open Commissioning ships a data reader of its own; this project uses a variant of it that adds the
PLC handshake below.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Enable |
| `Control.1` | Trigger — read now |
| `Status.0` | Enabled, echoed back |
| `Status.1` | Triggered, echoed back |
| `StatusData` | The value read, as a 64-bit number |

The Unity component drives exactly these. The **result-valid and result-OK bits** a control program
waits on are added by the reader's function block in the simulation project, on top of this — so the
full protocol a PLC sees is the one written on the device's own page and in
[the FG_01 behaviour contract](../../reference/fg-01-behaviour.md).

## How the twin models it

The reader is a volume in the scene, like a sensor. A part carries named data with it, and the reader
is configured with the name of the field to read. On a trigger it looks up that field on whatever
part is currently in front of it; dropping the trigger clears the result. If nothing is there, or the
part carries no such field, the read fails and is logged — it does not invent a value.

## Watch out

**A result is only meaningful while the part is still there.** The value is cleared when the trigger
drops or the part leaves, so a program that triggers and reads the answer three steps later may find
it gone.

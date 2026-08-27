<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# Lock

**A safety door interlock. Holds one or more doors locked, and reports separately whether they are shut and whether they are locked.**

Twin device type · twin FB `FB_Lock` · **6 instances** in FG_System · Unity component `OC.Interactions.Lock`

## What it is

A guard door on the cell enclosure with a solenoid interlock: the PLC energises the lock, and the
door cannot be opened until it lets go. It is the boundary between an operator and a moving machine.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Lock — hold the doors locked |
| `Status.0` | Every door it owns is shut |
| `Status.1` | Every door it owns is locked |

## Watch out

**Shut and locked are two different facts, and the machine is only safe when both are true.** A door
can be pushed to and not latched. Treating "shut" as "safe" is a mistake this twin will let you make
and the real machine will not forgive. The policy that acts on these bits is in
[the safety chain](../../reference/fg-system-safety.md).

## How the twin models it

One lock can own several doors: the reported bits are "all of them", not "any of them". The doors
are real hinged objects and can be dragged open with the mouse while the machine runs, which is how
you test what your program does when someone opens a guard mid-cycle.

## In this machine

**Signal** — Two inputs back - closed and locked - and one lock coil out. Secure means BOTH: closed alone is not enough.

There are **6** of them, in FG_System:

| Device | Twin PLC path | Group |
|---|---|---|
| `B_SafetyDoor11` | `MAIN.FG_System.B_SafetyDoor11` | FG_System |
| `B_SafetyDoor12` | `MAIN.FG_System.B_SafetyDoor12` | FG_System |
| `B_SafetyDoor13` | `MAIN.FG_System.B_SafetyDoor13` | FG_System |
| `B_SafetyDoor21` | `MAIN.FG_System.B_SafetyDoor21` | FG_System |
| `B_SafetyDoor22` | `MAIN.FG_System.B_SafetyDoor22` | FG_System |
| `B_SafetyDoor23` | `MAIN.FG_System.B_SafetyDoor23` | FG_System |

## Control implementations

The twin is master for **structure**, and that is all this page states. Which control function block each instance becomes, its process-image members and its published HMI struct is the control platform's own knowledge base:

- [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/context/devices/lock.md)
- **Siemens** — _no knowledge base published yet_

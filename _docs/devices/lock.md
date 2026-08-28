# Lock

Component: OC.Interactions.Lock
Package:   com.open-commissioning.core
Summary:   A safety door interlock. Holds one or more doors locked, and reports separately whether they are shut and whether they are locked.
Control:   Control
Status:    Status

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

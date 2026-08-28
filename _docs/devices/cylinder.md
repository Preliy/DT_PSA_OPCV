# Cylinder

Component: OC.Components.Cylinder
Package:   com.open-commissioning.core
Summary:   A pneumatic cylinder. Travels between a retracted and an extended end position, taking real time to get there, and reports when it arrives.
Control:   Control
Status:    Status

## What it is

The workhorse of the machine: 35 of the 83 devices are cylinders. Stoppers, lifts, grippers, gates
and the press are all cylinders. A real one is driven by air through one or two solenoid valves and
usually has a sensor at each end of its stroke telling the PLC it has arrived.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `Control.0` | Retract — drive towards the retracted end |
| `Control.1` | Extend — drive towards the extended end |
| `Status.0` | At the retracted end |
| `Status.1` | At the extended end |

**Both status bits are false while it is travelling.** That is the whole point of simulating it:
movement takes time, so a program that assumes an instant arrival fails here exactly as it would on
the real machine.

## How the twin models it

Travel is a stroke completed over a configured time — half a second by default, separately settable
for each direction — mapped onto the part's actual movement through a motion curve. The two end
positions are set per instance, so the same component drives a 10 mm gripper jaw and a full lift
stroke.

Three valve types, set per instance:

| Type | Behaviour with no command |
|---|---|
| **Double acting** | Stays where it is. Moves only while exactly one of the two control bits is set — set both, and it does not move |
| **Single acting, spring retracts** | Returns to the retracted end |
| **Single acting, spring extends** | Returns to the extended end |

## Watch out

- **An end-position bit is not proof of what the cylinder is holding.** Gripper jaws closed on
  nothing reach the extended end *sooner* than jaws closed on a part, and the bit is true either way.
  Only a dedicated part sensor says a part is held.
- **A de-energised double solenoid does not hold a gripped part in this twin.** The scene wires the
  cylinder's *moving* signal to the gripper's grip, so dropping the command drops the part. Grips
  are re-asserted every cycle for exactly this reason — see
  [the transport behaviour contract](../../reference/transport-behaviour.md).

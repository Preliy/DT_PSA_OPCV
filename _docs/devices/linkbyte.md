# LinkByte

Component: OC.Components.LinkByte
Package:   com.open-commissioning.core
Summary:   A plain byte in each direction, with no behaviour of its own — the way to give the PLC a device Open Commissioning has no component for.
Control:   ControlData
Status:    StatusData

## What it is

Sometimes the machine has something that is not a cylinder, a sensor or a drive: a laser module, a
feeder, a piece of third-party equipment with its own protocol. LinkByte is the generic answer — eight
control bits down, eight status bits up, and whatever they mean is decided by how the scene is wired.

## What the PLC sees

| Symbol | Meaning |
|---|---|
| `ControlData.0` … `ControlData.7` | Whatever the scene wires each bit to |
| `StatusData.0` … `StatusData.7` | Whatever the scene reports back |

Because the meaning is per instance, it is stated per instance: look for the **Bit mapping** section
on the group page that owns the device.

## How the twin models it

Each control bit raises an event when it changes, and those events are wired in the Unity inspector
to whatever should happen — start an animation, enable a conveyor, fire a laser. Status bits are set
by whatever in the scene knows the answer.

## Watch out

**A LinkByte promises nothing.** A cylinder reports arrival because the component measures it; a
LinkByte reports only what someone wired to it. If a bit has no status wired back, the PLC gets no
confirmation the thing happened — which is a fact about the real device as often as it is about the
model.

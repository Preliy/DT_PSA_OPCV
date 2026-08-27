# Documentation

Everything about the machine and the Unity twin. Start at [Introduction](01-introduction.md), or at
the [Glossary](05-glossary.md) if the abbreviations are new to you.

Anything specific to a control platform is documented by the platform's own repository, because each
control module is self-contained and optional.

## Getting started

| Page | Answers |
|---|---|
| [01 · Introduction](01-introduction.md) | What this project is for, who it is for, and how it is organised |
| [02 · Setup](02-setup.md) | Getting it running — on its own, then with your control system |
| [03 · Usage](03-usage.md) | Running the application: navigation, the user interface, hot keys |
| [04 · Architecture](04-architecture.md) | How the digital twin is built and how it talks to a PLC |
| [05 · Glossary](05-glossary.md) | Every abbreviation on these pages, in plain language |

## The machine

What the machine *is*: every functional group, every station, every device, with drawings. **These
pages are generated from the Unity twin**, so they cannot drift away from the thing they describe.

| Page | Answers |
|---|---|
| [How fresh is this?](context/PROVENANCE.md) | Which scene, which export, how many devices — read it before trusting the rest |
| [The machine](context/machine.md) | What it is, which groups exist, and the circulation ring |
| [Devices and PLC paths](context/plc-symbols.md) | Every twin device: name, PLC path, device type, group |
| [`.machine.json`](context/.machine.json) | The same structure as machine-readable JSON — what you build a new platform against |
| [Device types](context/devices/) | One page per kind of device: what a cylinder, a sensor or an interlock is, which bit means what, and what will catch you out |

One page per functional group, each with its hierarchy, its figure and its devices:

[FG_System](context/fg-system.md) · [FG_Transport](context/fg-transport.md) ·
[FG_01](context/fg-01.md) · [FG_02](context/fg-02.md) · [FG_03](context/fg-03.md) ·
[FG_04](context/fg-04.md) · [FG_05](context/fg-05.md)

## How it behaves

What the machine *does*: sequences, the station handshake, interlocks, fault codes and recovery.
These are **machine-level contracts** — any control platform that runs this line has to honour them,
whatever it is written in.

| Page | Answers |
|---|---|
| [Transport](reference/transport-behaviour.md) | How FG_Transport sequences, interlocks and recovers — the station contract, the transfer latch, the reset model |
| [FG_01](reference/fg-01-behaviour.md) | Identify and mark: the camera handshake, the step chain, and what the laser interlock does and does not enforce |
| [FG_02](reference/fg-02-behaviour.md) | Optical inspection: the four-bit camera protocol and why a NOK stops the pallet |
| [FG_03](reference/fg-03-behaviour.md) | Slot 1 → slot 2 transfer: the axis-naming trap, the handover, the three sub-sequences |
| [FG_04](reference/fg-04-behaviour.md) | Press and seat check: why the verdict bit is a verdict, and why every stop retracts the press |
| [FG_05](reference/fg-05-behaviour.md) | Capping: the continuously-running bunker, and why the read comes first |
| [Safety](reference/fg-system-safety.md) | The safety chain: who owns the facts, who owns the policy, and the lock rule |
| [Gripper station reset](reference/gripper-station-reset.md) | How FG_03 and FG_05 reset with a part in the gripper |
| [State lamp](reference/state-lamp.md) | The signal tower's state-to-colour mapping |

**No functional group runs on its own.** Each is served by an Index unit in FG_Transport that fixes
the pallet, triggers the group, and waits for it to report done before releasing. A group designed
without that handshake is designed wrong — start with [Transport](reference/transport-behaviour.md).

## The control platforms

Each control platform is a separate repository and documents itself, including its own wiki.

| Platform | Documentation | Wiki |
|---|---|---|
| **Beckhoff / TwinCAT** | [Setup, usage, and how the PLC projects are organised](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/README.md) | [DT_PSA_OPCV_Beckhoff/wiki](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/wiki) |
| **Anything else** | Planned — see [Other control platforms](04-architecture.md#7-other-control-platforms) | — |

Which module version pairs with this twin is in [COMPATIBILITY.md](../COMPATIBILITY.md); the
declaration itself is [`_workflow/config/modules.json`](../_workflow/config/modules.json).

## The curated sources

These are hand-written **inputs** to the generated pages rather than pages in their own right.
Edit these; never edit anything under `context/`.

| File | Feeds |
|---|---|
| [`devices/`](devices/) | one file per device type → [the device pages](context/devices/). The build fails if the twin has a device type this directory does not describe |
| [`ImageDescription.md`](ImageDescription.md) | each figure's scope, caption and numbered callouts → the group pages |
| [`DeviceDescription-SPEC.md`](DeviceDescription-SPEC.md) | nothing. It is the **contract** `devices/` implements: the format, the rules, and which fact belongs where |

## The figures

`images/` holds the rendered views of the machine. Every callout on every figure is checked against
the twin when these pages are built, so a picture cannot quietly outlive the device it points at.
The source of truth for each figure — its scope, caption and numbered callouts — is
[`ImageDescription.md`](ImageDescription.md).

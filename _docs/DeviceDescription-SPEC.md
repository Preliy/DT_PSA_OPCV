# Device descriptions — the contract

**This page is the specification. The descriptions themselves live in
[`devices/`](devices/), one file per device type.** Nothing here describes a device; it says what
a device description is, what belongs in one, and what the build does with it.

## The three places a device fact can live, and why

A device fact belongs in exactly one of these, and putting it in the wrong one is the mistake this
page exists to prevent.

| | Where | Written by | Example |
|---|---|---|---|
| What a **type** is | `_docs/devices/<type>.md` — **hand-written** | You | A cylinder takes real time to travel, and both status bits are false while it does |
| What an **instance** does here | A `ContextNode` in the Unity scene | You, in Unity | `Y_Stopper` retracted holds the pallet |
| The **rendered page** | `_docs/context/devices/<type>.md` — **generated** | `build_knowledge.py` | Both of the above, plus the instance table |

A device **type** is a Unity component. What it is, what it does and which bit means what are
properties of the component and are identical on every machine that uses it — so they are written
once per type, rather than 35 times over on 35 cylinders.

**`_docs/context/devices/` is not a copy you may edit.** The build sweeps that directory and
deletes anything it did not write. It embeds the source file verbatim and then adds what only the
export knows: the instance count, the groups, the Unity component, the table of every instance with
its twin PLC path and its authored role, and the links to each vendor's page. That is why the two
look alike — one is the input to the other.

**The build fails if a type in the scene has no file here.** A new device type is a device type
somebody has to describe.

## The format

One file per type, at `_docs/devices/<type-in-lowercase>.md`:

```
# <DeviceType>            exactly as the twin spells it — this heading is the authority,
                          not the filename

Component: <namespace-qualified Unity class>
Package:   <which package it comes from>
Summary:   <one sentence, rendered directly under the page title>
Control:   <the link member the PLC writes — Control, ControlData, or — for none>
Status:    <the link member the PLC reads  — Status,  StatusData,  or — for none>

<free markdown — headings, tables, whatever the type needs>
```

The filename is only a filename; the `# ` heading is what names the type, so casing like
`SensorBinary` survives a lowercase file called `sensorbinary.md`.

**`Control:` and `Status:` are not decoration — the build spells the bit tables from them.** A
device that carries a plain link addresses its bits as `Control.0` and `Status.1`; one that carries
a data link — a byte, a DWORD, a LWORD — addresses them as `ControlData.0` and `StatusData.1`.
Getting that wrong makes every generated bit table name an address that does not exist, so take it
from the component source, where it is the member the code actually calls `GetBit` and `SetBit` on.

## What a good description contains

The existing files are the worked examples; [`devices/cylinder.md`](devices/cylinder.md) is the
fullest. Four sections carry their weight:

| Section | Answers |
|---|---|
| **What it is** | What the real-world thing is, in a sentence a controls engineer would recognise |
| **What the PLC sees** | The bit table. Every symbol the control program can read or write |
| **How the twin models it** | What is simulated and what is not — the part that decides whether a program that passes here would pass on the machine |
| **Watch out** | The trap. What looks true and is not |

**Watch out is the section that earns the page.** "A gripper's cylinder limit is not a grip
witness" is worth more than any amount of restating what the bits are called.

## Rules

- **Never write a control-platform fact here.** Function blocks, terminal channels, `.tmc`
  details and HMI structs belong to a vendor module. This page describes the *twin* component.
- **Never invent the "why".** Bit meanings are readable from the component source — read them.
  Process intent is not; ask. A plausible invented explanation is worse than none, because it will
  be believed.
- **Take the facts from the component, not from memory.** The Open Commissioning components are in
  `Unity/Library/PackageCache/com.open-commissioning.core@*/Runtime/`; the two project-specific ones
  are in `Unity/Assets/Demo_1/Scripts/`.
- **Control and status, throughout.** *Control* is what the PLC writes and the twin obeys. *Status*
  is what the twin reports and the PLC reads. Every device also has an **Override** switch in the
  Unity inspector: with it on, the device ignores the control side so you can drive it by hand.

# Machine description

What the machine is, where each fact about it is written down, and how to read those pages.

**This page is a guide, not the description itself.** The description is
[generated from the Unity twin](05-engineering-workflow.md) and lives in
[`context/`](context/); the behaviour is hand-written and lives in [`reference/`](reference/).
Nothing about the machine is restated here, deliberately — a hand-typed copy of a generated fact is
a copy that goes stale.

## 1. The vocabulary

The machine is described at four levels, and every page you will read is at one of them.

| | What it is |
|---|---|
| **The machine** | The whole line: one Unity prefab, instanced by every scene |
| **Functional group** — `FG` | *Funktionsgruppe*. One self-contained part of the machine — the conveyor, or one processing station. There are seven: `FG_System`, `FG_Transport`, and `FG_01` to `FG_05` |
| **Module / station** | One working position inside a group — an index unit, a lift, a stopper, a gripper. Many are prefabs used several times over |
| **Device** | One addressable thing: a cylinder, a sensor, a drive, a lamp. Each has a device **type** and a **twin PLC path** |

Two of those distinctions carry weight:

- **A device type is not a device.** `Cylinder` is a type, with one page describing what its bits
  mean and what will catch you out; `MAIN.FG_01.Y_Gripper` is an instance of it. Read the type page
  once, then the instances are just addresses.
- **`FG_System` and `FG_Transport` are not stations.** `FG_Transport` is the conveyor that carries
  every pallet; `FG_System` is the machine-level layer — the operator panel, the signal tower, the
  safety chain.

## 2. The one thing to know before reading anything

**No functional group runs on its own.**

Each of `FG_01` to `FG_05` is served by an **Index unit** in `FG_Transport` that stops the pallet,
fixes it in place, triggers the group, and only releases the pallet when the group reports it has
finished. The groups do not talk to each other; they talk to transport.

A group designed without that handshake is designed wrong, and it is the single most common way a
first control implementation goes astray. The ring — which index feeds which group, in which order —
is in [the machine page](context/machine.md); the step chain and its invariants are in
[transport-behaviour.md](reference/transport-behaviour.md).

## 3. Two halves, two owners

| | Answers | Where | Written by |
|---|---|---|---|
| **Structure** | What the machine is made of — every device, its type, its address, its place in the hierarchy | [`context/`](context/) | a generator, from the twin |
| **Behaviour** | What it has to *do* — sequences, the station handshake, interlocks, fault codes, recovery | [`reference/`](reference/) | a human, once, for every platform |

Structure is generated because it can be read out of the twin, so those pages cannot drift away from
the machine. Behaviour cannot be read out of anything — a sequence is a decision — so it is written
by hand, once, platform-neutrally. Every control platform running this line honours the same
contracts.

A group's page in `context/` links to its contract in `reference/`, and that link is the boundary
between the two.

**Realisation is the third thing, and it is not here.** How one particular PLC spells all of this —
its function blocks, its terminal channels, its HMI — belongs to that platform's own repository. Each
group page links out to it. See [04 · PLC connectivity](04-plc-connectivity.md).

## 4. How to read a group page

Every `fg-*.md` page has the same shape:

| Section | What it gives you |
|---|---|
| **Function / Process** | What this group is for, in the words of someone who knows the machine |
| **Figure** | A rendered view with numbered callouts, each resolved against the twin when the page was built |
| **Devices** | Every device in the group: name, twin PLC path, device type |
| **Bit mapping** | For devices whose interface is a byte, which bit means what |
| **Hierarchy** | The tree, as the twin holds it |
| **Unity** | Notes about the model itself — what a component does here, and where the twin's own prose is known to be wrong |
| **Control implementations** | A link out, one per control platform |

Two conventions run through all of them:

- **`†` means "this is one vendor's example, not the machine".** The pages are rendered from one
  reference scene, so the operator panel you see is that vendor's. Anything marked `†` is not
  identical in every scene — never take machine-level code or documentation from a marked row.
- **The twin path is not the control path.** The twin says `MAIN.FG_01.P_Camera`; TwinCAT says
  `MAIN.Machine.FG_01.P_Camera`. These pages state the **twin** path; the verified control path is
  on the platform's page, where it can be checked against a real type model.

## 5. The pages

### Start here

| Page | Answers |
|---|---|
| [How fresh is this?](context/PROVENANCE.md) | Which scene, which export, which commit, how many devices — **read it before trusting the rest** |
| [The machine](context/machine.md) | What it is, which groups exist, and the circulation ring |
| [Devices and PLC paths](context/plc-symbols.md) | Every twin device in one table: name, twin PLC path, device type, group |
| [`.machine.json`](context/.machine.json) | The same structure as machine-readable JSON — what you build a new control platform against |
| [Device types](context/devices/) | One page per kind of device: what it is, which bit means what, what will catch you out |

### The functional groups

One page per group — its hierarchy, its figure, its devices — and beside it the contract that says
how it must behave.

| Group | What it is | Structure | Behaviour |
|---|---|---|---|
| **FG_System** | The machine-level layer: operator panel, signal tower, safety | [fg-system](context/fg-system.md) | [safety](reference/fg-system-safety.md) · [state lamp](reference/state-lamp.md) |
| **FG_Transport** | The two-level pallet conveyor, and the index units that serve every group | [fg-transport](context/fg-transport.md) | [transport](reference/transport-behaviour.md) |
| **FG_01** | Identify and mark | [fg-01](context/fg-01.md) | [fg-01](reference/fg-01-behaviour.md) |
| **FG_02** | Optical inspection | [fg-02](context/fg-02.md) | [fg-02](reference/fg-02-behaviour.md) |
| **FG_03** | Slot-to-slot transfer | [fg-03](context/fg-03.md) | [fg-03](reference/fg-03-behaviour.md) · [gripper reset](reference/gripper-station-reset.md) |
| **FG_04** | Press and seat check | [fg-04](context/fg-04.md) | [fg-04](reference/fg-04-behaviour.md) |
| **FG_05** | Capping | [fg-05](context/fg-05.md) | [fg-05](reference/fg-05-behaviour.md) · [gripper reset](reference/gripper-station-reset.md) |

### The behaviour contracts in full

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

## 6. Where the figures come from

[`images/`](images/) holds the rendered views of the machine. Every callout on every figure is
checked against the twin when these pages are built, so a picture cannot quietly outlive the device
it points at. The source of truth for each figure — its scope, caption and numbered callouts — is
[`ImageDescription.md`](ImageDescription.md); a figure is added by editing that file, never by
pasting an image into a generated page.

## 7. If a page is wrong

A page under `context/` disagreeing with the machine is a bug worth reporting — but **not one that
can be fixed by editing the page**, which the next build overwrites. Where each kind of correction
goes is in [05 · Engineering workflow](05-engineering-workflow.md), and the shortest version is: fix
the twin, or fix the contract.

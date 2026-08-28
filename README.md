# DT_PSA_OPCV — Digital Twin for Laser Welding & Assembly System (PSA OPCV)

**A real production line, in software. Connect your PLC and run it.**

[![Release](https://img.shields.io/github/v/release/Preliy/DT_PSA_OPCV?sort=semver)](https://github.com/Preliy/DT_PSA_OPCV/releases)
[![Vendor compatibility](https://img.shields.io/github/actions/workflow/status/Preliy/DT_PSA_OPCV/compatibility.yml?branch=master&label=vendor%20compatibility)](COMPATIBILITY.md)
[![Wiki](https://img.shields.io/github/actions/workflow/status/Preliy/DT_PSA_OPCV/wiki.yml?branch=master&label=wiki)](https://github.com/Preliy/DT_PSA_OPCV/wiki)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub-EA4AAA.svg)](https://github.com/sponsors/Preliy)
[![Buy me a coffee](https://img.shields.io/badge/support-buy%20me%20a%20coffee-FFDD00.svg)](https://buymeacoffee.com/preliy)

![The machine](_docs/images/Machine_Overview.png)

## Welcome

A Unity-based digital twin of a laser welding and assembly system, built for **virtual
commissioning**. The twin runs on **Open Commissioning Core** and the **Open Commissioning UI
framework**; **TwinCAT** is the simulation unit — it hosts the behaviour models and emulates the
real-time industrial fieldbus, so the twin and a control program meet over EtherCAT exactly as a
real cell does.

Pallets circulate on a two-level conveyor. Five stations work on the part as it passes: one
identifies it and marks it with a laser, one inspects it optically, one moves it between pallet
slots and flips it over, one presses it home and checks it seated, and the last fits a cap. Doors
interlock. Stations wait for each other. Things go wrong, and have to be reset properly.

**The difference is what drives it.** Your own PLC program can take over and run the whole machine —
and it cannot tell that the machine is not real.

## The goal

Virtual commissioning means testing a control program against a model of the machine, long before
the machine is standing on a factory floor. This project exists to make that testable on a machine
close enough to a real one that the answer counts for something — and to publish everything needed
to run it from **any** control platform, not one.

So there are three deliverables, and they are kept apart on purpose:

| | |
|---|---|
| **A machine worth testing against** | A two-level pallet conveyor and five processing stations, modelled from real CAD, with the awkward parts kept |
| **A written specification of it** | What it is made of, published as machine-readable JSON; what it must do, published as platform-neutral [behaviour contracts](_docs/reference/transport-behaviour.md) |
| **One module per control platform** | Each realises the same specification in its own tooling, in its own repository |

## Why this one is different

Most virtual commissioning demos are three boxes on a conveyor belt, or an animation in a slide deck.
They look nice. You cannot learn much from them, and you certainly cannot test a control program
against one.

A model that is too kind is worse than no model at all. If the sensors always agree, if nothing ever
jams, if the simulation quietly helps the program along — then every program passes, including the
broken ones.

So this machine is built to be honest. It has the awkward parts that real machines have, the ones
that catch people out during real commissioning. If your program runs this line properly, that
actually tells you something.

## A community project

This is an independent, community-run open-source project. **It is not affiliated with, endorsed by,
sponsored by or supported by** any of the automation, engine or framework vendors whose products it
works with, nor by the manufacturer of the machine it is modelled on. No vendor has reviewed it and
none is responsible for it.

Product and company names are used only to say what the software talks to, and remain the property
of their owners. EtherCAT® is a registered trademark and patented technology, licensed by Beckhoff
Automation GmbH, Germany.

**The machine itself is vendor-neutral.** It is described once — the same device list, the same
behaviour contracts — in a form that belongs to no controller. A control platform is then just one
implementation of that description, kept in its own repository. The ones here exist because someone
sat down and built them, and yours can be next.

It is also, plainly, a simulation. It is published under [GPL-3.0](LICENSE) with no warranty of any
kind, and a program that runs correctly here has not thereby been validated for safety, for
certification, or for use on real machinery.

## Three ways to run it

| | What happens |
|---|---|
| **Watch it** | The machine runs by itself, like an animation. [Download the Windows build](https://github.com/Preliy/DT_PSA_OPCV/releases/latest) and run it — no Unity, no PLC, nothing to install |
| **Test your program** | Your PLC program runs on your PC and drives the machine |
| **Test your hardware** | The same program runs on a real controller and drives the machine |

The second and third are the same setup — the only difference is where your PLC is. What you prove
on your desk still holds on the hardware.

## Who it is for

- **Controls engineers** who want a serious machine to write and test code against, without owning
  one.
- **Students and people learning automation**, who want to see how a real line is actually put
  together — the interlocks and the recovery, not just the happy path.
- **Anyone curious about virtual commissioning** who wants to judge it on a real example.

You need a PC. That is all.

## Getting it

The twin is one repository. Each **control platform is a separate, optional repository** you clone
into this one's root — take only the platform you use:

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV

# optional - only if you want to run it on this platform
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff
```

The module paths are gitignored here, so the two repositories do not collide: inside `Beckhoff/`
everything is a normal checkout on a normal branch, and `git status` in the main repo never mentions
it. Nothing to initialise, nothing to keep in sync by hand.

Then follow [Setup](_docs/01-setup.md) — what you need, and how to get the machine running.

### Control platforms

<!-- BEGIN GENERATED - do not edit between the markers. -->
| Module | Platform | Version | Status |
|---|---|---|---|
| [Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff) | Beckhoff TwinCAT 3 | 1.0.0 | current |
| [Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens) | Siemens TIA Portal | 0.1.0 | not a consumer |
<!-- END GENERATED -->

Which module version pairs with which twin — and how a stale one is caught — is in
[COMPATIBILITY.md](COMPATIBILITY.md). The **vendor compatibility** badge above is that check
running weekly: green means every declared module still pairs with this twin.

## Bring your own control system

The machine belongs to no vendor. Beckhoff runs it today because that is what was built first.
Siemens is on the way. Anything else is wide open — and that is where help is most welcome.

Everything you would need is already written down: [what the machine is made
of](_docs/context/machine.md), and [exactly how it is supposed to
behave](_docs/reference/transport-behaviour.md). So you are building against a specification, not
guessing.

If you would like to bring your platform to it, we would love to hear from you.

**→ [Connecting a PLC](_docs/04-plc-connectivity.md)** · **→ [CONTRIBUTING.md](CONTRIBUTING.md)**

## Where to start

| | |
|---|---|
| [**Setup**](_docs/01-setup.md) | What you need, and getting it running |
| [**Using the application**](_docs/02-using-the-application.md) | Moving around, and the controls |
| [**How it works**](_docs/03-how-it-works.md) | The architecture, and why it is built this way |
| [**PLC connectivity**](_docs/04-plc-connectivity.md) | The platforms that run it, and how to add yours |
| [**Engineering workflow**](_docs/05-engineering-workflow.md) | How the machine describes itself, and where PLC code comes from |
| [**The machine**](_docs/06-machine-description.md) | Every station and device, with drawings |
| [**Glossary**](_docs/07-glossary.md) | PLC, MIL/SIL/HIL, fieldbus — every abbreviation in plain language |
| [**Full documentation**](_docs/README.md) | Everything else |

The same pages are browsable as a [Wiki](https://github.com/Preliy/DT_PSA_OPCV/wiki). Each control
platform keeps its own — the TwinCAT one is
[here](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/wiki) — and the two cross-link.

## Contributing

Contributions are genuinely wanted — a new control platform, a missing setup step, a bug you hit, or
a correction to something we got wrong.

| | |
|---|---|
| **Connect another control system** | Rockwell, CODESYS, B&R, Omron, your own soft PLC. You implement against a published specification rather than guessing — see [PLC connectivity](_docs/04-plc-connectivity.md) |
| **Get HIL working** | Everything here was validated on an emulated runtime. Real controller hardware uses the same mechanism, but nobody has captured the steps |
| **Fill a setup gap** | A step that fails on a fresh machine is worth reporting even if you cannot fix it |
| **Correct the record** | If a page disagrees with the machine, one of the two is wrong and we want to know which |

Start with [CONTRIBUTING.md](CONTRIBUTING.md), and the [Code of Conduct](CODE_OF_CONDUCT.md) applies
to everyone taking part.

## Support this project

This is built and maintained in spare time, and it stays free and GPL-3.0 either way. If it saved
you a commissioning week, or you just want to keep it moving:

- **[❤ GitHub Sponsors](https://github.com/sponsors/Preliy)** — one-off or monthly, through GitHub
- **[☕ Buy me a coffee](https://buymeacoffee.com/preliy)** — one-off, no account needed

Not sponsoring costs you nothing — a bug report, a fixed setup step or a new control platform is
worth just as much. See [Contributing](#contributing) above.

## License

[GPL-3.0](LICENSE) — Copyright © 2026 Viktor Gaponenko.

Use it, learn from it, build on it. If you share a modified version, it stays open for the next
person.

## Credits

### The machine — [Villette Oh](https://grabcad.com/villette.oh-2)

This twin has a real machine behind it because someone drew one and gave it away. The CAD model —
[**Laser Welding & Assembly System (PSA
OPCV)**](https://grabcad.com/library/laser-welding-assembly-system-psa-opcv-1), published on
GrabCAD — is where every shape here comes from. Without it this would be one more demo with three
boxes on a conveyor. Thank you.

### [Open Commissioning](https://github.com/OpenCommissioning)

The framework the whole twin stands on: the `com.open-commissioning.core` and
`com.open-commissioning.ui` Unity packages, the OC TwinCAT library, and the OC Assistant tooling.

**Thanks to Andreas Fast** for the Siemens expertise, and for the PLC project architecture and
design that this project's control side is built on.

### Also used

| | |
|---|---|
| [`com.pilar.context`](https://github.com/Preliy/unity-pilar-context) | the engineering context carried by each part of the twin |
| [Unity-URP-Outline](https://github.com/CristianQiu/Unity-URP-Outline) | selection outlines |
| [UniTask](https://github.com/Cysharp/UniTask) | async sequences |
| [NaughtyAttributes](https://github.com/dbrizov/NaughtyAttributes) | editor tooling |

Every third-party component, with its version and licence, is listed in
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

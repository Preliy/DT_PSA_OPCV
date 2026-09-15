# DT_PSA_OPCV — Digital Twin for Laser Welding & Assembly System

**A real production line, in software. Connect your PLC and run it.**

[![Release](https://img.shields.io/github/v/release/Preliy/DT_PSA_OPCV?sort=semver)](https://github.com/Preliy/DT_PSA_OPCV/releases)
[![Vendor compatibility](https://img.shields.io/github/actions/workflow/status/Preliy/DT_PSA_OPCV/compatibility.yml?branch=master&label=vendor%20compatibility)](COMPATIBILITY.md)
[![Wiki](https://img.shields.io/github/actions/workflow/status/Preliy/DT_PSA_OPCV/wiki.yml?branch=master&label=wiki)](https://github.com/Preliy/DT_PSA_OPCV/wiki)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub-EA4AAA.svg)](https://github.com/sponsors/Preliy)
[![Buy me a coffee](https://img.shields.io/badge/support-buy%20me%20a%20coffee-FFDD00.svg)](https://buymeacoffee.com/preliy)

![The machine](_docs/images/Machine_Overview.png)

## What is it?

A Unity digital twin of a laser welding and assembly line, built for **virtual commissioning** on
[Open Commissioning](https://github.com/OpenCommissioning). Your PLC program connects over EtherCAT
and drives the machine exactly as it would drive a real one.

Pallets circulate on a two-level conveyor through five stations: identify and laser-mark, optical
inspection, part transfer, press and seat check, and capping. Doors interlock, stations wait for
each other, and things go wrong and have to be reset properly — just like on a real line.

## Who is it for?

- **Goal** — test a control program against a realistic machine long before the real one exists,
  from any control platform.
- **Why** — most virtual commissioning demos are too kind: nothing jams, the sensors always agree,
  so even a broken program passes. This machine keeps the awkward parts. If your program runs it,
  that means something.
- **Community driven** — an independent open-source project. The machine is described once, in a
  vendor-neutral way, and each control platform lives in its own repository.

It is made for **controls engineers** who want a serious machine to code against, **students** learning
how a real line is put together, and **anyone curious** about virtual commissioning.

## Getting started

**Just want to watch it run?** [Download the Windows build](https://github.com/Preliy/DT_PSA_OPCV/releases/latest) —
nothing to install.

**Want to connect your PLC?** Clone the twin, plus the platform you use:

```bash
git clone https://github.com/Preliy/DT_PSA_OPCV.git
cd DT_PSA_OPCV


# optional: add a control platform, e.g. Beckhoff
git clone https://github.com/Preliy/DT_PSA_OPCV_Beckhoff.git Beckhoff
```

Then follow the **[Setup guide](_docs/01-setup.md)**. Everything else is in the
**[Documentation](_docs/README.md)**, also browsable as a **[Wiki](https://github.com/Preliy/DT_PSA_OPCV/wiki)**.

## Supported platforms

| Platform | Repository | Status |
|---|---|---|
| Beckhoff TwinCAT 3 | [DT_PSA_OPCV_Beckhoff](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff) | ✅ Done |
| Siemens TIA Portal | [DT_PSA_OPCV_Siemens](https://github.com/Preliy/DT_PSA_OPCV_Siemens) | 🚧 Work in progress |

Which module version pairs with which twin is in [COMPATIBILITY.md](COMPATIBILITY.md).

## Contributing

This project grows through discussion. Have an idea, a question or a better way to do something?
Open an issue or start a discussion — let's iterate on it together and make the machine better.

Directions where help is very welcome:

- **New devices** — drives, barcode readers, and other components real lines use
- **Another control platform** — Rockwell, CODESYS, B&R, Omron… built against a published
  specification, see [PLC connectivity](_docs/04-plc-connectivity.md)
- **Hardware-in-the-loop** — running the same program on a real controller
- **Setup gaps, bugs and corrections** — a report is worth as much as a fix

Start with [CONTRIBUTING.md](CONTRIBUTING.md). The [Code of Conduct](CODE_OF_CONDUCT.md) applies to everyone.

## Support the project

Built in spare time, and free forever. If it helped you, you can keep it moving:

- **[❤ GitHub Sponsors](https://github.com/sponsors/Preliy)** — one-off or monthly
- **[☕ Buy me a coffee](https://buymeacoffee.com/preliy)** — one-off, no account needed

## Credits

- **[Villette Oh](https://grabcad.com/villette.oh-2)** — the CAD model
  [Laser Welding & Assembly System (PSA OPCV)](https://grabcad.com/library/laser-welding-assembly-system-psa-opcv-1),
  where every shape of this machine comes from. Thank you.
- **[Andreas Fast](https://www.linkedin.com/in/automation-fast-andreas/)** — PLC project architecture and Digital Twin development and validation.
- **[Open Commissioning](https://github.com/OpenCommissioning)** — the framework the twin stands on.
- Also used: [`com.pillar.context`](https://github.com/Preliy/unity-pillar-context),
  [Unity-URP-Outline](https://github.com/CristianQiu/Unity-URP-Outline),
  [UniTask](https://github.com/Cysharp/UniTask),
  [NaughtyAttributes](https://github.com/dbrizov/NaughtyAttributes) — full list in
  [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## License

[GPL-3.0](LICENSE) — Copyright © 2026 Viktor Gaponenko. Use it, learn from it, build on it; if you
share a modified version, it stays open for the next person.

Trademarks, non-affiliation and safety: see [NOTICE.md](NOTICE.md).

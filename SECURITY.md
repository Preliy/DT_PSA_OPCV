# Security policy

## What this project is

DT_PSA_OPCV is a **simulation**. It is a Unity digital twin of a machine, a set of generated
documents describing it, and a small amount of Python that builds those documents. It has no
server, no user accounts, no database and no network service of its own.

The one place it talks to anything is **ADS**, on a machine you control, to a PLC runtime you
started — Unity to TwinCAT over a link you configured. That connection is unauthenticated by
design, because that is what ADS is on an engineering network. **Do not expose an ADS route, a
TwinCAT runtime or this twin to an untrusted network.** That is a property of the protocol and
the commissioning setup, not a defect in this project, and there is no fix here for it.

## Supported versions

The newest release is supported. Older tags are kept for reference only — a fix lands on
`master` and ships in the next release rather than being backported.

## Reporting a vulnerability

Please report privately rather than opening a public issue:

- **Preferred** — [open a private security advisory](https://github.com/Preliy/DT_PSA_OPCV/security/advisories/new)
  on this repository.
- **Or** — email <viktor.gaponenko@pm.com> with `DT_PSA_OPCV` in the subject.

Say what you found, how to reproduce it, and what it lets someone do. A proof of concept helps
more than a description.

You can expect an acknowledgement within a week. If the report is valid you will be credited in
the release notes unless you would rather not be.

## What is in scope

- The Python tooling in `_workflow/tools/` — the wiki builder, the publisher, the compatibility
  check. These run in GitHub Actions with a repository token, so a way to make one of them write
  or push something it should not is worth reporting.
- The GitHub Actions workflows in `.github/workflows/` — token scope, injection through an
  untrusted input, anything that lets a pull request obtain write access.
- The Unity project, for anything that executes code a user did not intend to run.

## What is not in scope

- **An unauthenticated ADS connection.** See above.
- A control program written against this twin behaving unsafely. The twin is a model; the
  behaviour contracts in `_docs/reference/` say what a program must honour, and honouring them
  is the program's job.
- Anything in a **vendor module** — `DT_PSA_OPCV_Beckhoff` and the rest are separate
  repositories with their own policies. Report there.
- Third-party dependencies. Report those upstream; tell us if this project's use of one makes
  the problem worse.

## Control platforms

Each vendor module is its own repository and carries its own `SECURITY.md`. A finding in a
TwinCAT project, a PLC program or an HMI belongs there, not here.

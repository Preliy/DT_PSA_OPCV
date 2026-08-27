# Usage

How to run the twin and drive it. For installing the toolchain, see [02 · Setup](02-setup.md).

## 1. Starting the application

### From a packaged build

1. Download the `.zip` archive.
2. Extract it on your local machine.
3. Start the `.exe` from the archive folder.

### From the Unity Editor

Open the project in Unity and load the scene for the control platform you are using:

| Scene | Use it for |
|---|---|
| `VC_Demo_1_MIL` | **MIL** — the twin on its own, no PLC. Needs nothing else installed |
| `VC_Demo_1_Beckhoff_1` | Running against the TwinCAT PLC. Adds the Beckhoff operator panel |
| `VC_Demo_1_Siemens_1` | The Siemens variant. Adds that vendor's panel — the PLC side is not written yet |

Scenes live in `Unity/Assets/Demo_1/Scenes/`.

## 2. Navigation

### 2.1 Camera control

| Input | Does |
|---|---|
| **Right click + drag** | Rotate the view |
| **Middle click + drag** | Pan the view |
| **Scroll wheel** | Zoom in / out |
| **Right click + WASD** | Move the camera forward, backward and sideways |
| **Right click + Q/E** | Move the camera down / up |

### 2.2 Selection

**Left click** on an object to select it. Selection has to be enabled first — turn on **Interaction
Mode** in the left side panel.

### 2.3 Interacting with the UI

**Left click** buttons, sliders and other UI elements.

## 3. User interface

![The application window](images/UI_MainPage.png)

The interface has three main operating modules, numbered in the picture above.

### 1–9 · Left side panel

| # | Tool | Does |
|---:|---|---|
| 1 | **Interaction Mode** | Activates selection of and interaction with objects in the scene |
| 2 | **Hide Menu** | Show or hide the geometry of specific parts of the model |
| 3 | **Material Flow** | Show or hide the material flow collision bodies |
| 4 | **Label Menu** | Show or hide the labels in the scene |
| 5 | **Camera Menu** | Jumps the camera to a predefined position |
| 6 | **Settings Menu** | Show or hide the scene settings |
| 7 | **Macros** | Project-defined action buttons |
| 8 | **Console Menu** | Show or hide the scene console |
| 9 | **Save / Load** | Save and restore the component layout |

### 10 · Time panel

Pause the application, or use the time factor slider to change the simulation speed. The panel also
shows the elapsed run time.

### Industrial panel

Shows or hides the predefined industrial HMIs — the operator panel and the monitors modelled on the
machine itself.

## 4. Hot keys

| Key | Does |
|---|---|
| **Selection + F** | Jumps the camera to the selected object in the scene |
| **F12** | Switch between full screen and windowed mode |
| **ESC** | Exit the application |

## 5. MIL, SIL and HIL

This matters more than it looks, because MIL and the other two do not implement the same
machine.

### MIL — the twin on its own

Load `VC_Demo_1_MIL`. No control system is involved: C# coroutines under
`Unity/Assets/Demo_1/Scripts/MIL/` drive the devices directly, so the line runs by itself.

Useful for showing the machine, checking geometry, or working on the twin with nothing else
installed.

> **Do not read the machine's behaviour out of the MIL scripts.** They are the twin's *animation*
> and implement an **older contract** — no transfer latch, no check that a lift is at a level before
> running its carriage belt, and no reset path at all. A handshake copied from them reproduces bugs
> that have already been fixed. The behaviour that counts is written down in
> the [behaviour contracts](reference/transport-behaviour.md), and the control program
> is master for it.

### SIL and HIL — a control system drives it

Load the scene for your control platform, with its runtime up. The twin's devices bind over the
transport to a project holding one function block per device; that project exchanges I/O with the
control program across a fieldbus. **Nothing in Unity decides what the machine does** — every motion
is commanded by the PLC, and the twin only reports its sensors back.

The setup is identical whether the PLC runs on an emulated runtime (**SIL**) or on real
controller hardware (**HIL**) — only where it executes changes.

Operate the machine from the on-screen control panel, or from the platform's own HMI. **Each
platform's panel is different**, and so is the startup procedure:

| Platform | How to run it |
|---|---|
| **Beckhoff / TwinCAT** | [Beckhoff usage guide](https://github.com/Preliy/DT_PSA_OPCV_Beckhoff/blob/master/_docs/02-usage.md) |
| **Siemens / TIA** | Not yet — the control side does not exist |
| **Your own** | [Other control platforms](04-architecture.md#7-other-control-platforms) |

## 6. What you are looking at

Every device on screen has a name and a PLC path, and both are documented:

- The figure and device table for each group — [the machine pages](context/)
- Every twin device in one table — [devices and PLC paths](context/plc-symbols.md)
- Turn on **Label Menu** (tool 4) to see the names in the scene itself.

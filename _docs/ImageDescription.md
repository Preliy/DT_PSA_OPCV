# About this file

Source for every figure rendered into the knowledge base. The documentation build parses it and
renders the images and their legends into `_docs/context/`.

**Every callout is checked against the twin.** A name that does not resolve, or resolves twice, fails
the build — so a figure can never quietly drift away from the machine it shows.

Each block is:

```
# <Image file name>
Scope:      machine | <group> | <group>/<module> | ui
Represents: <instance>, <instance>          (optional - module detail views only)
Caption:    <one sentence, rendered under the image>

1. <callout>            — <optional note>
2. ...
```

A callout is resolved inside its scope's subtree, in this order:

1. an exact relative scene path — `Y_CapsSource/M_Conveyor`
2. a node name that is unique in the subtree — `M_Conveyor` inside `Lift01`
3. a unique `oc.plcPath` leaf — `Transport01_M_Conveyor`

`Scope: ui` marks a figure of the application interface rather than the machine. It is used in
`_docs/` only and is never resolved against the twin.

**Not every image in `images/` is a figure.** The architecture diagrams — `OC_Base_*.svg`, embedded
by hand in [`04-plc-connectivity.md`](04-plc-connectivity.md) — show how the setup is wired, not what the
machine contains, so they have no callouts to resolve and are deliberately absent from this file.

They are **self-theming SVGs**: a light drawing plus one `@media (prefers-color-scheme: dark)`
stylesheet that swaps each colour, so a single file reads correctly in both themes. That shape is
deliberate — a `<picture>` block or a `#gh-dark-mode-only` suffix renders in the repository and
breaks in the wiki, because the wiki build rewrites a markdown image link into a raw-content URL
and only ever sees the markdown. Keep any replacement a plain markdown image for the same reason.

They are committed artifacts with no generator in this repository. Editing one means redoing that
merge by hand, or rebuilding it from whatever drawing tool it came from.

---

# Machine_Overview.png
Scope: machine
Caption: The line seen from the front - FG_System, FG_Transport and FG_01 to FG_05 assembled together.

# Group_System_Overview.png
Scope: FG_System
Caption: The FG_System group and the machine main frame, isolated.

1. SS_EStop1
2. SS_EStop2
3. H_ControlPanel
4. H_SignalTower
5. B_SafetyDoor11
6. B_SafetyDoor12
7. B_SafetyDoor13
8. B_SafetyDoor21
9. B_SafetyDoor22
10. B_SafetyDoor23

# Group_Transport_Overview.png
Scope: FG_Transport
Caption: The two level pallet conveyor, isolated. Callouts name the transport modules; each module type has its own detail view below.

1. Lift01
2. Lift02
3. Transport01_M_Conveyor
4. Transport02_M_Conveyor
5. Stopper01
6. Stopper02
7. Stopper03
8. Stopper04
9. Index01
10. Index02
11. Index03
12. Index04
13. Index05

# Modul_Lift_Overview.png
Scope: FG_Transport/Lift01
Represents: Lift01, Lift02
Caption: The lift module, isolated. Raises or lowers a pallet between the two conveyor levels and runs it off the carriage.

1. Y_Lift
2. M_Conveyor
3. B_Detect
4. B_Exit

# Modul_Index_Overview.png
Scope: FG_Transport/Index01
Represents: Index01, Index02, Index03, Index04, Index05
Caption: The index module, isolated. Stops a pallet and lifts it to fix the payload while its functional group runs.

1. Y_Stopper
2. Y_Lift
3. B_Detect
4. B_Exit

# Modul_Stopper_Overview.png
Scope: FG_Transport/Stopper01
Represents: Stopper01, Stopper02, Stopper03, Stopper04
Caption: The stopper module, isolated. Holds and releases a pallet without lifting it.

1. Y_Stopper
2. B_Detect
3. B_Exit

# Group_1_Overview.png
Scope: FG_01
Caption: The FG_01 identify and mark station, isolated.

1. Y_Gate1
2. Y_Gate2
3. Y_ReaderWindow
4. Y_Platform
5. B_SafetyGate1
6. B_SafetyGate2
7. Y_LaserMark
8. Y_Gripper
9. P_Camera

# Group_2_Overview.png
Scope: FG_02
Caption: The FG_02 optical inspection station, isolated.

1. P_Camera

# Group_3_Overview.png
Scope: FG_03
Caption: The FG_03 transfer station, isolated. Two gantries move the part from pallet slot 1 to slot 2.

1. Y_AxisX1
2. Y_AxisY1
3. Y_AxisR1
4. Y_Gripper1
5. B_Detect1
6. Y_AxisX2
7. Y_AxisY2
8. Y_Gripper2
9. B_Detect2

# Group_4_Overview.png
Scope: FG_04
Caption: The FG_04 press station, isolated.

1. Y_AxisZ
2. B_NIO

# Group_5_Overview.png
Scope: FG_05
Caption: The FG_05 capping station, isolated, with the cap bunker on the left.

1. Y_AxisX
2. Y_AxisZ1
3. Y_AxisZ2
4. Y_AxisR
5. Y_Gripper
6. B_Detect
7. Y_CapsSourceStopper
8. P_Camera
9. Y_CapsSource
10. Y_CapsSource/M_Conveyor
11. B_Part

# UI_MainPage.png
Scope: ui
Caption: The runtime application window. The left side panel runs down the left edge; the time panel sits at the top.

1. Interaction Mode — activate selection of and interaction with objects in the scene
2. Hide Menu        — show or hide the geometry of specific parts of the model
3. Material Flow    — show or hide the material flow collision bodies
4. Label Menu       — show or hide the labels in the scene
5. Camera Menu      — jump the camera to a predefined position
6. Settings Menu    — show or hide the scene settings
7. Macros           — project defined action buttons
8. Console Menu     — show or hide the scene console
9. Save / Load      — save and restore the component layout
10. Time Panel      — pause the application, or use the time factor slider to change simulation speed

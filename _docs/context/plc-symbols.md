<!-- GENERATED from the Unity twin - do not edit. The build sweeps this directory and deletes anything it did not write; see _workflow/README.md. -->
<!-- Source: Unity/Assets/StreamingAssets/<Scene>_Context.json (structure and prose) and <Scene>_Project_Tree.xml (the device list), for every exported vendor scene. Edit the scene's ContextNodes, then re-run refreshing-project-knowledge. The control side is on the vendor page linked from here. -->

# PLC symbols

Every device that is a real PLC symbol: it carries `oc.deviceType` and **neither** `oc.aggregatedBy` **nor** `oc.simulationDevice`. 83 of them.

Devices excluded by that test are listed under their group's own page, so nobody generates a symbol for a panel button or a simulation-only device.

| Symbol | PLC path | Device type | FB type | Group |
|---|---|---|---|---|
| `B_SafetyGate1` | `MAIN.FG_01.B_SafetyGate1` | SensorBinary | `FB_SensorBinary` | FG_01 |
| `B_SafetyGate2` | `MAIN.FG_01.B_SafetyGate2` | SensorBinary | `FB_SensorBinary` | FG_01 |
| `P_Camera` | `MAIN.FG_01.P_Camera` | DataReader | `FB_Camera` | FG_01 |
| `Y_Gate1` | `MAIN.FG_01.Y_Gate1` | Cylinder | `FB_Cylinder` | FG_01 |
| `Y_Gate2` | `MAIN.FG_01.Y_Gate2` | Cylinder | `FB_Cylinder` | FG_01 |
| `Y_Gripper` | `MAIN.FG_01.Y_Gripper` | Cylinder | `FB_Cylinder` | FG_01 |
| `Y_LaserMark` | `MAIN.FG_01.Y_LaserMark` | LinkByte | `FB_DeviceByte` | FG_01 |
| `Y_Platform` | `MAIN.FG_01.Y_Platform` | Cylinder | `FB_Cylinder` | FG_01 |
| `Y_ReaderWindow` | `MAIN.FG_01.Y_ReaderWindow` | Cylinder | `FB_Cylinder` | FG_01 |
| `P_Camera` | `MAIN.FG_02.P_Camera` | DataReader | `FB_Camera` | FG_02 |
| `B_Detect1` | `MAIN.FG_03.B_Detect1` | SignalBinary | `FB_SensorBinary` | FG_03 |
| `B_Detect2` | `MAIN.FG_03.B_Detect2` | SignalBinary | `FB_SensorBinary` | FG_03 |
| `Y_AxisR1` | `MAIN.FG_03.Y_AxisR1` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_AxisX1` | `MAIN.FG_03.Y_AxisX1` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_AxisX2` | `MAIN.FG_03.Y_AxisX2` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_AxisY1` | `MAIN.FG_03.Y_AxisY1` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_AxisY2` | `MAIN.FG_03.Y_AxisY2` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_Gripper1` | `MAIN.FG_03.Y_Gripper1` | Cylinder | `FB_Cylinder` | FG_03 |
| `Y_Gripper2` | `MAIN.FG_03.Y_Gripper2` | Cylinder | `FB_Cylinder` | FG_03 |
| `B_NIO` | `MAIN.FG_04.B_NIO` | SignalBinary | `FB_SensorBinary` | FG_04 |
| `Y_AxisZ` | `MAIN.FG_04.Y_AxisZ` | Cylinder | `FB_Cylinder` | FG_04 |
| `B_Detect` | `MAIN.FG_05.B_Detect` | SignalBinary | `FB_SensorBinary` | FG_05 |
| `B_Part` | `MAIN.FG_05.B_Part` | SensorBinary | `FB_SensorBinary` | FG_05 |
| `P_Camera` | `MAIN.FG_05.P_Camera` | DataReader | `FB_Camera` | FG_05 |
| `Y_AxisR` | `MAIN.FG_05.Y_AxisR` | Cylinder | `FB_Cylinder` | FG_05 |
| `Y_AxisX` | `MAIN.FG_05.Y_AxisX` | Cylinder | `FB_Cylinder` | FG_05 |
| `Y_AxisZ1` | `MAIN.FG_05.Y_AxisZ1` | Cylinder | `FB_Cylinder` | FG_05 |
| `Y_AxisZ2` | `MAIN.FG_05.Y_AxisZ2` | Cylinder | `FB_Cylinder` | FG_05 |
| `Y_CapsSource` | `MAIN.FG_05.Y_CapsSource` | ControlBunker | `FB_DeviceByte` | FG_05 |
| `Y_CapsSourceStopper` | `MAIN.FG_05.Y_CapsSourceStopper` | Cylinder | `FB_Cylinder` | FG_05 |
| `Y_Gripper` | `MAIN.FG_05.Y_Gripper` | Cylinder | `FB_Cylinder` | FG_05 |
| `B_SafetyDoor11` | `MAIN.FG_System.B_SafetyDoor11` | Lock | `FB_Lock` | FG_System |
| `B_SafetyDoor12` | `MAIN.FG_System.B_SafetyDoor12` | Lock | `FB_Lock` | FG_System |
| `B_SafetyDoor13` | `MAIN.FG_System.B_SafetyDoor13` | Lock | `FB_Lock` | FG_System |
| `B_SafetyDoor21` | `MAIN.FG_System.B_SafetyDoor21` | Lock | `FB_Lock` | FG_System |
| `B_SafetyDoor22` | `MAIN.FG_System.B_SafetyDoor22` | Lock | `FB_Lock` | FG_System |
| `B_SafetyDoor23` | `MAIN.FG_System.B_SafetyDoor23` | Lock | `FB_Lock` | FG_System |
| `H_ControlPanel` † | `MAIN.FG_System.H_ControlPanel` | PanelSampler | `FB_Panel` | FG_System |
| `H_SignalTower` | `MAIN.FG_System.H_SignalTower` | PanelSampler | `FB_Panel` | FG_System |
| `SS_EStop1` | `MAIN.FG_System.SS_EStop1` | Button | `FB_Button` | FG_System |
| `SS_EStop2` | `MAIN.FG_System.SS_EStop2` | Button | `FB_Button` | FG_System |
| `B_Detect` | `MAIN.FG_Transport.Index01_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Index01_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Index01_Y_Lift` | Cylinder | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Index01_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Index02_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Index02_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Index02_Y_Lift` | Cylinder | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Index02_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Index03_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Index03_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Index03_Y_Lift` | Cylinder | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Index03_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Index04_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Index04_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Index04_Y_Lift` | Cylinder | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Index04_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Index05_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Index05_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Index05_Y_Lift` | Cylinder | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Index05_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Lift01_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Lift01_B_Exit` | SensorBinary | `?` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Lift01_M_Conveyor` | DriveSimple | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Lift01_Y_Lift` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Lift02_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Lift02_B_Exit` | SensorBinary | `?` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Lift02_M_Conveyor` | DriveSimple | `?` | FG_Transport |
| `Y_Lift` | `MAIN.FG_Transport.Lift02_Y_Lift` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Stopper01_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Stopper01_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper01_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Stopper02_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Stopper02_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper02_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Stopper03_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Stopper03_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper03_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `B_Detect` | `MAIN.FG_Transport.Stopper04_B_Detect` | SensorBinary | `FB_SensorBinary` | FG_Transport |
| `B_Exit` | `MAIN.FG_Transport.Stopper04_B_Exit` | SensorBinary | `?` | FG_Transport |
| `Y_Stopper` | `MAIN.FG_Transport.Stopper04_Y_Stopper` | Cylinder | `?` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Transport01_M_Conveyor` | DriveSimple | `?` | FG_Transport |
| `M_Conveyor` | `MAIN.FG_Transport.Transport02_M_Conveyor` | DriveSimple | `?` | FG_Transport |

† **From the reference scene only.** Every scene instances the same `Machine_1` prefab, but each adds its own vendor's operator panel, so this row is `VC_Demo_1_Beckhoff_1`'s and another scene spells it differently. The machine is what is *un*marked; a marked row is an example. Each vendor's own is on its page below.

## Per group

| Group | Symbols |
|---|---:|
| [FG_System](fg-system.md) | 10 |
| [FG_Transport](fg-transport.md) | 42 |
| [FG_01](fg-01.md) | 9 |
| [FG_02](fg-02.md) | 1 |
| [FG_03](fg-03.md) | 9 |
| [FG_04](fg-04.md) | 2 |
| [FG_05](fg-05.md) | 10 |

## Per device type

The interface a device type presents - its control function block, its process-image members and its bit layout - is on the type's own page, not repeated on every instance.

| Device type | Instances |
|---|---:|
| [Button](devices/button.md) | 2 |
| [ControlBunker](devices/controlbunker.md) | 1 |
| [Cylinder](devices/cylinder.md) | 35 |
| [DataReader](devices/datareader.md) | 3 |
| [DriveSimple](devices/drivesimple.md) | 4 |
| [LinkByte](devices/linkbyte.md) | 1 |
| [Lock](devices/lock.md) | 6 |
| [PanelSampler](devices/panelsampler.md) | 2 |
| [SensorBinary](devices/sensorbinary.md) | 25 |
| [SignalBinary](devices/signalbinary.md) | 4 |

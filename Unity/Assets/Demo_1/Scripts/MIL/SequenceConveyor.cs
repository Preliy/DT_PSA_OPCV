using OC.Components;
using UnityEngine;

namespace Preliy.Demo
{
    public class SequenceConveyor : SimulationBehaviour
    {
        [SerializeField]
        private DriveSimple _driveTop;
        [SerializeField]
        private DriveSimple _driveDown;

        private void OnEnable()
        {
            _driveTop.Override.Value = true;
            _driveDown.Override.Value = true;
            _driveTop.Backward.Value = true;
            _driveDown.Backward.Value = true;
        }
        
        private void OnDisable()
        {
            _driveTop.Override.Value = false;
            _driveDown.Override.Value = false;
            _driveTop.Backward.Value = false;
            _driveDown.Backward.Value = false;
        }
    }
}

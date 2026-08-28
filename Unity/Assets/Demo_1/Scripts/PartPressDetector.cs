using OC.Components;
using UnityEngine;

namespace Preliy.Demo
{
    public class PartPressDetector : MonoBehaviour
    {
        [SerializeField]
        private SensorBinary _sensorBinary;
        [SerializeField]
        private Cylinder _cylinder;
        [SerializeField]
        private SignalBinary _signal;
        
        private void Update()
        {
            _signal.Signal.Value = !_sensorBinary.Value.Value && _cylinder.OnLimitMax.Value;
        }
    }
}



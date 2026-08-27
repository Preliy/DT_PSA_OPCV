using OC;
using OC.Components;
using OC.MaterialFlow;
using UnityEngine;

namespace Preliy.Demo
{
    public class GripSensor : MonoBehaviour, IMeasurement<bool>
    {
        public IPropertyReadOnly<bool> Value => _value;
        
        [SerializeField]
        private Gripper _gripper;
        [SerializeField]
        private Property<bool> _value = new (false);

        private void FixedUpdate()
        {
            _value.Value = _gripper.IsPicked.Value;
        }
    } 
}



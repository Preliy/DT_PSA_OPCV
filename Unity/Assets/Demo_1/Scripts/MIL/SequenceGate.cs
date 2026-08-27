using OC.Components;
using UnityEngine;

namespace Preliy.Demo
{
    public class SequenceGate : SimulationBehaviour
    {
        public bool Collision
        {
            get => _collision;
            set => _collision = value;
        }

        [SerializeField]
        private bool _collision;
        [SerializeField]
        private Cylinder _gate;

        private void OnEnable()
        {
            _gate.Override.Value = true;
        }

        private void OnDisable()
        {
            _gate.Override.Value = false;
            _gate.JogPlus = false;
            _gate.JogMinus = false;
        }

        private void Update()
        {
            _gate.JogPlus = _collision;
        }
    }
}

using OC.Scripts.System;
using UnityEngine;

namespace Preliy.Demo
{
    public abstract class SimulationBehaviour : MonoBehaviour, ISimulationBehaviour
    {
        public bool Enable
        {
            get => enabled;
            set => enabled = value;
        }
    }
}

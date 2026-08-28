using UnityEngine;

namespace Preliy.Demo
{
    public class SequenceBunker : SimulationBehaviour
    {
        [SerializeField]
        private ControlBunker _controlBunker;

        private void OnEnable()
        {
            _controlBunker.ConveyorOn = true;
            _controlBunker.BunkerOn = true;
        }
        
        private void OnDisable()
        {
            _controlBunker.ConveyorOn = false;
            _controlBunker.BunkerOn = false;
        }
    }
}

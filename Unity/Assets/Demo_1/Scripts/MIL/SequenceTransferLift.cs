using System.Collections;
using OC;
using OC.Components;
using UnityEngine;

namespace Preliy.Demo
{
    public class SequenceTransferLift : SequenceBase
    {
        [Header("Settings")] 
        [SerializeField]
        private bool _reverseDirection;
        
        [Header("References")]
        [SerializeField]
        private DriveSimple _conveyor;
        [SerializeField]
        private Cylinder _lift;
        [SerializeField]
        private SensorBinary _sensorDetect;
        [SerializeField]
        private SensorBinary _sensorExit;

        protected override void OnEnable()
        {
            _conveyor.Override.Value = true;
            _lift.Override.Value = true;
            base.OnEnable();
        }

        protected override void OnDisable()
        {
            base.OnDisable();
            _conveyor.Override.Value = false;
            _lift.Override.Value = false;
        }

        public override void SendPayload() => ChangeState(WaitForPayload);

        protected override IEnumerator Idle()
        {
            if (_reverseDirection)
            {
                yield return _lift.MoveToMax();
            }
            else
            {
                yield return _lift.MoveToMin();
            }
            
            _conveyor.Backward.Value = false;
            _conveyor.Forward.Value = false;
            
            _ready = true;
            _busy = false;
            _done = false;
        }

        private IEnumerator WaitForPayload()
        {
            _ready = false;
            _conveyor.Backward.Value = true;
            yield return new WaitUntil(() => _sensorDetect.Value.Value);
            _busy = true;
            _conveyor.Backward.Value = false;
            yield return new WaitForSeconds(0.5f);
            ChangeState(MoveLift);
        }

        private IEnumerator MoveLift()
        {
            if (_reverseDirection)
            {
                yield return _lift.MoveToMin();
            }
            else
            {
                yield return _lift.MoveToMax();
            }
            
            ChangeState(Occupied);
        }

        private IEnumerator Occupied()
        {
            yield return new WaitUntil(() => _nextSequence != null && _nextSequence.Ready);
            ChangeState(TransferToNext);
        }

        private IEnumerator TransferToNext()
        {
            _conveyor.Forward.Value = true;
            yield return new WaitUntil(() => _sensorExit.Value.Value);
            
            _done = true;
            ChangeState(Idle);
        }
    }
}

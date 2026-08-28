using System.Collections;
using OC;
using OC.Components;
using UnityEngine;

namespace Preliy.Demo
{
    public class SequenceTransferStopper : SequenceBase
    {
        [Header("References")]
        [SerializeField]
        private Cylinder _stopper;
        [SerializeField]
        private SensorBinary _sensorDetect;
        [SerializeField]
        private SensorBinary _sensorExit;

        protected override void OnEnable()
        {
            _stopper.Override.Value = true;
            base.OnEnable();
        }

        protected override void OnDisable()
        {
            base.OnDisable();
            _stopper.Override.Value = false;
        }

        public override void SendPayload() => ChangeState(Idle);

        protected override IEnumerator Idle()
        {
            yield return _stopper.MoveToMin();
            _ready = true;
            _busy = false;
            _done = false;
            yield return new WaitUntil(() => _sensorDetect.Value.Value);
            ChangeState(Occupied);
        }

        private IEnumerator Occupied()
        {
            _ready = false;
            _busy = true;
            yield return new WaitUntil(() => _nextSequence != null && _nextSequence.Ready);
            _nextSequence.SendPayload();
            ChangeState(TransferToNext);
        }

        private IEnumerator TransferToNext()
        {
            yield return _stopper.MoveToMax();
            yield return new WaitUntil(() => _sensorExit.Value.Value);
            _done = true;
            ChangeState(Idle);
        }
    }
}

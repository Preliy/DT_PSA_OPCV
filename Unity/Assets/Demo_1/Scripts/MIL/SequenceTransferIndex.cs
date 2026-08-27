using System.Collections;
using OC;
using OC.Components;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceTransferIndex : SequenceBase
    {
        public bool OperationDone
        {
            get => _operationDone;
            set => _operationDone = value;
        }
        
        [Header("References")]
        [SerializeField]
        private Cylinder _stopper;
        [SerializeField]
        private Cylinder _index;
        [SerializeField]
        private SensorBinary _sensorDetect;
        [SerializeField]
        private SensorBinary _sensorExit;

        [Header("Settings")] 
        [SerializeField]
        private bool _bypass;

        [Header("Operations")] 
        [SerializeField]
        private bool _operationDone;
        
        [SerializeField]
        public UnityEvent ReadyForOperation;

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
            yield return _index.MoveToMin();
            _ready = true;
            _busy = false;
            _done = false;
            yield return new WaitUntil(() => _sensorDetect.Value.Value);
            ChangeState(Index);
        }
        
        private IEnumerator Index()
        {
            _ready = false;
            _busy = true;
            yield return _index.MoveToMax();
            
            if (!_bypass)
            {
                ReadyForOperation?.Invoke();
                yield return new WaitUntil(() => _operationDone);
                _operationDone = false;
            }
            else
            {
                yield return new WaitForSeconds(1f);
            }
            
            yield return _index.MoveToMin();
            ChangeState(Occupied);
        }

        private IEnumerator Occupied()
        {
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

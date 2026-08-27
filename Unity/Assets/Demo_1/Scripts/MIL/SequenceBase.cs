using System;
using System.Collections;
using UnityEngine;

namespace Preliy.Demo
{
    public abstract class SequenceBase : SimulationBehaviour
    {
        public bool Busy => _busy;
        public bool Ready => _ready;
        public bool Done => _done;

        [Header("State")]
        [SerializeField]
        private string _stateName;

        [Header("Status")]
        [SerializeField]
        protected bool _busy;
        [SerializeField]
        protected bool _ready;
        [SerializeField]
        protected bool _done;

        [Header("Topology")]
        [SerializeField]
        protected SequenceBase _nextSequence;

        [Header("Debug")]
        [SerializeField]
        private bool _log;

        private Coroutine _driverRoutine;
        private Func<IEnumerator> _requestedState;
        private string _lastStateName;

        // ReSharper disable Unity.PerformanceAnalysis
        protected void ChangeState(Func<IEnumerator> state)
        {
            _requestedState = state;
            _stateName = state.Method.Name;

            if (_log) Debug.Log($"Change state {_lastStateName} > {_stateName}", this);

            _lastStateName = _stateName;

            if (_driverRoutine == null && Enable)
            {
                _driverRoutine = StartCoroutine(Driver());
            }
        }

        private IEnumerator Driver()
        {
            while (true)
            {
                var state = _requestedState;
                _requestedState = null;

                yield return state();

                // State finished without requesting a transition -> re-enter it (loop).
                if (_requestedState == null)
                {
                    _requestedState = state;
                }

                yield return null; // guarantee forward progress even if a state never yields
            }
        }

        protected virtual void OnEnable()
        {
            ChangeState(Idle);
        }

        protected virtual void OnDisable()
        {
            if (_driverRoutine != null)
            {
                StopCoroutine(_driverRoutine);
                _driverRoutine = null;
            }
            _requestedState = null;
            _ready = false;
            _busy = false;
            _done = false;
        }

        protected abstract IEnumerator Idle();

        public abstract void SendPayload();
    }
}

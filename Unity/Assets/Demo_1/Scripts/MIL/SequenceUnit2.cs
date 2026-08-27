using System.Collections;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceUnit2 : SimulationBehaviour
    {
        [Header("Status")]
        [SerializeField]
        private bool _busy;

        [Header("References")]
        [SerializeField]
        private DataReader _dataReader;

        public UnityEvent OperationComplete;

        private void OnDisable()
        {
            StopAllCoroutines();
            _busy = false;
        }

        public void Execute()
        {
            if (!Enable) return;
            StopAllCoroutines();
            StartCoroutine(Operation());
        }

        private IEnumerator Operation()
        {
            _busy = true;
            _dataReader.Trigger.Value = true;
            yield return new WaitForSeconds(2f);
            _dataReader.Trigger.Value = false;
            _busy = false;
            OperationComplete.Invoke();
        }
    }
}

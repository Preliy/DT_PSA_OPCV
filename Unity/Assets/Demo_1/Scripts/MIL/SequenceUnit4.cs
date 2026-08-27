using System.Collections;
using OC;
using OC.Components;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceUnit4 : SimulationBehaviour
    {
        [Header("Status")]
        [SerializeField]
        private bool _busy;

        [Header("References")]
        [SerializeField]
        private Cylinder _z1;


        public UnityEvent OperationComplete;

        private void OnEnable()
        {
            _z1.Override.Value = true;
        }

        private void OnDisable()
        {
            StopAllCoroutines();
            _busy = false;
            _z1.Override.Value = false;
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
            yield return new WaitForSeconds(0.5f);

            yield return _z1.MoveToMax();
            yield return new WaitForSeconds(1f);
            yield return _z1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            
            _busy = false;
            OperationComplete.Invoke();
        }

    }
    
}



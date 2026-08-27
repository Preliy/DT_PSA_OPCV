using System.Collections;
using OC;
using OC.Components;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceUnit5 : SimulationBehaviour
    {
        [Header("Status")]
        [SerializeField]
        private bool _busy;

        [Header("References")]
        [SerializeField]
        private Cylinder _x1;
        [SerializeField]
        private Cylinder _z1;
        [SerializeField]
        private Cylinder _z2;
        [SerializeField]
        private Cylinder _r1;
        [SerializeField]
        private Cylinder _gripper;
        [SerializeField]
        private SensorBinary _part;
        [SerializeField] 
        private Cylinder _capStopper;
        
        
        public UnityEvent OperationComplete;
        
        private void OnEnable()
        {
            _x1.Override.Value = true;
            _z1.Override.Value = true;
            _z2.Override.Value = true;
            _r1.Override.Value = true;
            _gripper.Override.Value = true;
            _capStopper.Override.Value = true;
            _capStopper.JogPlus = true;
            _capStopper.JogMinus = false;
        }

        private void OnDisable()
        {
            StopAllCoroutines();
            _busy = false;
            _x1.Override.Value = false;
            _z1.Override.Value = false;
            _z2.Override.Value = false;
            _r1.Override.Value = false;
            _gripper.Override.Value = false;
            _capStopper.Override.Value = false;
            _capStopper.JogPlus = false;
            _capStopper.JogMinus = true;
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
            yield return new WaitUntil(() => _part.Value.Value);
            yield return new WaitForSeconds(0.5f);

            yield return _z2.MoveToMax();
            yield return new WaitForSeconds(0.4f);
            yield return _gripper.MoveToMax();
            yield return new WaitForSeconds(0.4f);
            yield return _z2.MoveToMin();
            
            yield return new WaitForSeconds(0.2f);
            yield return _x1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _r1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _z1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _gripper.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _z1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _x1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _r1.MoveToMin();
            
            _busy = false;
            OperationComplete.Invoke();
        }

    }
    
}



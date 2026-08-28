using System.Collections;
using OC;
using OC.Components;
using OC.Interactions;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceUnit3 : SimulationBehaviour
    {
        [Header("Status")]
        [SerializeField]
        private bool _busy;

        [Header("References")]
        [SerializeField]
        private Cylinder _x1;
        [SerializeField]
        private Cylinder _y1;
        [SerializeField]
        private Cylinder _r1;
        [SerializeField]
        private Cylinder _gripper1;
        [SerializeField]
        private Cylinder _x2;
        [SerializeField]
        private Cylinder _y2;
        [SerializeField]
        private Cylinder _gripper2;
        
        public UnityEvent OperationComplete;
        
        private void OnEnable()
        {
            _x1.Override.Value = true;
            _y1.Override.Value = true;
            _r1.Override.Value = true;
            _gripper1.Override.Value = true;
            _x2.Override.Value = true;
            _y2.Override.Value = true;
            _gripper2.Override.Value = true;
        }

        private void OnDisable()
        {
            StopAllCoroutines();
            _busy = false;
            _x1.Override.Value = false;
            _y1.Override.Value = false;
            _r1.Override.Value = false;
            _gripper1.Override.Value = false;
            _x2.Override.Value = false;
            _y2.Override.Value = false;
            _gripper2.Override.Value = false;
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

            yield return _y2.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _gripper2.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _y2.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _x2.MoveToMax();
            
            yield return new WaitForSeconds(0.2f);
            yield return _x1.MoveToMax(); 
            yield return new WaitForSeconds(0.2f);
            yield return _y1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _gripper1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _gripper2.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _r1.MoveToMax();
            yield return new WaitForSeconds(0.2f);
            yield return _x2.MoveToMin();
            
            yield return new WaitForSeconds(0.2f);
            yield return _x1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _gripper1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _y1.MoveToMin();
            yield return new WaitForSeconds(0.2f);
            yield return _r1.MoveToMin();
            
            
            _busy = false;
            OperationComplete.Invoke();
        }

    }
    
}



using System.Collections;
using OC;
using OC.Components;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    public class SequenceUnit1 : SimulationBehaviour
    {
        [Header("Status")]
        [SerializeField]
        private bool _busy;

        [Header("References")]
        [SerializeField]
        private Cylinder _platform;
        [SerializeField]
        private Cylinder _gripper;
        [SerializeField]
        private Cylinder _readerWindow;
        [SerializeField]
        private LinkByte _laser;
        [SerializeField]
        private Cylinder _gate1;
        [SerializeField]
        private Cylinder _gate2;

        public UnityEvent OperationComplete;

        private void OnEnable()
        {
            _platform.Override.Value = true;
            _gripper.Override.Value = true;
            _readerWindow.Override.Value = true;
            _gate1.Override.Value = true;
            _gate2.Override.Value = true;
        }

        private void OnDisable()
        {
            StopAllCoroutines();
            _busy = false;
            _platform.Override.Value = false;
            _gripper.Override.Value = false;
            _readerWindow.Override.Value = false;
            _gate1.Override.Value = false;
            _gate2.Override.Value = false;
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
            yield return _gate1.MoveToMax();//Start parallel
            yield return _gate2.MoveToMax();//Start parallel
            yield return new WaitForSeconds(0.5f);
            yield return _gripper.MoveToMax();
            yield return new WaitForSeconds(0.5f);
            _laser.OnBit0Changed.Invoke(true);  
            yield return new WaitForSeconds(1);
            _laser.OnBit0Changed.Invoke(false);
            yield return _readerWindow.MoveToMax();
            yield return new WaitForSeconds(1);
            yield return _readerWindow.MoveToMin();
            yield return _gripper.MoveToMin();
            yield return new WaitForSeconds(0.5f);
            yield return _gate1.MoveToMin();//Start parallel
            yield return _gate2.MoveToMin();//Start parallel
            yield return new WaitForSeconds(0.5f);
            _busy = false;
            OperationComplete.Invoke();
        }

        
    }
    
}



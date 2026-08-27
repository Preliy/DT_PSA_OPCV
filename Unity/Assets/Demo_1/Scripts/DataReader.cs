using System;
using System.Globalization;
using OC;
using OC.Communication;
using OC.Components;
using OC.MaterialFlow;
using UnityEngine;
using UnityEngine.Events;

namespace Preliy.Demo
{
    [SelectionBase]
    [DisallowMultipleComponent]
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(BoxCollider))]
    public class DataReader : Detector, IDevice, IMeasurement<ulong>, IInteractable
    {
        public Type ReferenceType => typeof(DataReader);
        public Link Link => _link;
        public IProperty<bool> Override => _override;
        public IPropertyReadOnly<ulong> Value => _value;
        public IProperty<bool> Trigger => _trigger;

        [SerializeField]
        protected Property<bool> _override = new (false);
        [SerializeField]
        protected Property<bool> _enabled = new (true);
        [SerializeField]
        protected Property<bool> _trigger = new (false);
        [SerializeField]
        protected Property<string> _string = new ("");
        [SerializeField]
        protected Property<ulong> _value = new ();
        [SerializeField]
        private string _key;
        [SerializeField] 
        private bool _auto;
        [SerializeField]
        private LinkDataLWord _link = new("FB_Reader");
        
        public UnityEvent<ulong> OnValueChangedEvent;
        public UnityEvent<bool> OnTriggerChangedEvent;
        
        private PayloadBase _payloadBase;
        private BoxCollider _collider;
        private Rigidbody _rigidbody;
        
        private new void OnEnable()
        {
            base.OnEnable();
            _value.OnValueChanged += OnValueChanged;
            _trigger.OnValueChanged += OnTriggerChanged;
        }

        private new void OnDisable()
        {
            base.OnDisable();
            _value.OnValueChanged -= OnValueChanged;
            _trigger.OnValueChanged -= OnTriggerChanged;
        }

        private void Start()
        {
            _link.Initialize(this);
            Initialize();
        }

        private void FixedUpdate()
        {
            LinkHandShake();
        }

        protected void OnValidate()
        {
            _value.OnValidate();
            _trigger.OnValidate();
        }

        protected override void OnPayloadEnterAction(PayloadBase payloadBase)
        {
            base.OnPayloadEnterAction(payloadBase);
            _payloadBase = payloadBase;
            if (_auto)
            {
                _trigger.Value = false;
                _trigger.Value = true;
            }
        }
        
        protected override void OnPayloadExitAction(PayloadBase payloadBase)
        {
            base.OnPayloadExitAction(payloadBase);
            _payloadBase = null;
            if (_auto) _trigger.Value = false;
        }
        
        private void OnTriggerChanged(bool trigger)
        {
            if (trigger)
            {
                if (TryGetValue(out var result, true))
                {
                    _value.Value = result;
                }
            }
            else
            {
                Clear();
            }
            
            OnTriggerChangedEvent?.Invoke(trigger);
        }

        public void Clear()
        {
            _string.Value = "";
            _value.Value = 0;
        }
        
        public bool TryGetValue(out ulong value, bool log = false)
        {
            try
            {
                if (_payloadBase == null) throw new Exception("Payload is null!");
                if (!_payloadBase.TryGetComponent(out PayloadData payloadData)) throw new Exception("PayloadData component is null!");
                if (TryGetValue(payloadData, _key, out var rawResult))
                {
                    if (!ulong.TryParse(rawResult, NumberStyles.Integer, CultureInfo.InvariantCulture,
                            out ulong result)) throw new Exception("Value is not parsable in ulong!");
                    value = result;
                    return true;
                }
                
                throw new Exception("Value is not found!");
            }
            catch (Exception exception)
            {
                if (log) OC.Logging.Logger.LogError(exception.Message, this);
                value = 0;
                return false;
            }
        }
        
        private void OnValueChanged(ulong value)
        {
            OnValueChangedEvent?.Invoke(value);
        }
        
        private void Initialize()
        {
            if (_collider == null) _collider = GetComponent<BoxCollider>();
            if (_rigidbody == null) _rigidbody = GetComponent<Rigidbody>();
            
            _collider.isTrigger = true;
            _rigidbody.isKinematic = true;
            _rigidbody.useGravity = false;
        }

        private void LinkHandShake()
        {
            if (!_link.Connected) return;
            if (!_override)
            {
                _enabled.Value = _link.Control.GetBit(0);
                _trigger.Value = _link.Control.GetBit(1);
            }
            
            _link.Status.SetBit(0, _enabled.Value);
            _link.Status.SetBit(1, _trigger.Value);
            _link.StatusData = (long)_value.Value;
        }
        
        //Need to be fixed in OC Package (temp method wrapper)
        private bool TryGetValue(PayloadData payloadData, string key, out string value)
        {
            try
            {
                var metadata = payloadData.Data.Find(item => item.Key == key);
                if (metadata == null)
                {
                    value = "";
                    return false;
                }
                
                value = metadata.Value;
                return true;
            }
            catch (Exception _)
            {
                value = "";
                return false;
            }
        }
    }
}
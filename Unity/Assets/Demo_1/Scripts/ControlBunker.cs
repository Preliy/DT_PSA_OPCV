using OC;
using OC.Communication;
using OC.Components;
using OC.MaterialFlow;
using UnityEngine;
using UnityEngine.Events;
using Random = UnityEngine.Random;

namespace Preliy.Demo
{
    public class ControlBunker : MonoComponent, IDevice
    {
        public bool ConveyorOn
        {
            get => _conveyorOn;
            set => _conveyorOn = value;
        }

        public bool BunkerOn
        {
            get => _bunkerOn;
            set => _bunkerOn = value;
        }

        public Link Link => _link;
        public IProperty<bool> Override => _override;
        
        [Header("Control")]
        [SerializeField]
        protected Property<bool> _override = new (false);

        [SerializeField]
        private bool _conveyorOn;
        [SerializeField]
        private bool _bunkerOn;
        
        [Header("Settings")]
        [SerializeField] 
        private float _speed = 100f;
        [SerializeField]
        private Vector2 _sourceTimeRange = new(0, 2);
        
        [Header("References")]
        [SerializeField]
        private Source _source;
        [SerializeField]
        private TransportLinear _transport;
        
        [SerializeField]
        private LinkDataByte _link = new("FB_DeviceByte");
        
        private float _spawnTimer;
        private bool _wasBlocked;
        
        public UnityEvent<bool> OnBunkerOnChanged;
        public UnityEvent<bool> OnConveyorOnChanged;
        
        private void Start()
        {
            Link.Initialize(this);
            ResetSpawnTimer();
        }

        private void Update()
        {
            if (_link.Connected && !_override.Value)
            {
                _bunkerOn = _link.ControlData.GetBit(0); 
                _conveyorOn = _link.ControlData.GetBit(1);
            }
            
            OnBunkerOnChanged?.Invoke(_bunkerOn);
            OnConveyorOnChanged?.Invoke(_conveyorOn);
            
            _transport.Target.Value = _conveyorOn ? _speed : 0;
            CreatePart();
        }

        private void CreatePart()
        {
            if (!_bunkerOn) return;
            
            if (_source.Collision.Value)
            {
                _wasBlocked = true;
                return;
            }

            if (_wasBlocked)
            {
                ResetSpawnTimer();
                _wasBlocked = false;
            }

            _spawnTimer -= Time.deltaTime;

            if (_spawnTimer <= 0f)
            {
                _source.Create();
                ResetSpawnTimer();
            }
        }
        
        private void ResetSpawnTimer()
        {
            _spawnTimer = Random.Range(_sourceTimeRange.x, _sourceTimeRange.y);
        }
    }
}
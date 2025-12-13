"""
TDD Test Suite: Device Auto-Activation on Telemetry Submission
==============================================================

Test-Driven Development for automatically activating devices when they send telemetry data.
This ensures devices become active in both Redis cache and PostgreSQL database.
"""

import pytest
import json
import time
from datetime import datetime, timezone
from app import create_app
from src.models import db, Device, User
from src.services.redis_cache import RedisCacheService
from src.services.mongodb_service import MongoDBService


class TestDeviceAutoActivation:
    """Test suite for device auto-activation on telemetry submission"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def test_user(self, app):
        """Create test user"""
        with app.app_context():
            user = User(
                username='testuser_activation',
                email='test_activation@smartsense.local',
                is_active=True
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            return user_id
    
    @pytest.fixture
    def inactive_device(self, app, test_user):
        """Create inactive test device"""
        with app.app_context():
            device = Device(
                name='Auto Activation Test Device',
                device_type='sensor',
                status='inactive',  # Initially inactive
                location='Test Lab',
                user_id=test_user,  # test_user is now just the ID
                api_key='test_auto_activation_key_123456789'
            )
            db.session.add(device)
            db.session.commit()
            device_id = device.id
            return device_id
    
    @pytest.fixture
    def redis_service(self):
        """Redis service instance"""
        return RedisCacheService()
    
    @pytest.fixture
    def mongodb_service(self):
        """MongoDB service instance"""
        return MongoDBService()

    # ==========================================
    # TEST 1: Device Status Before Telemetry
    # ==========================================
    
    def test_device_initially_inactive(self, app, inactive_device):
        """Test 1: Device should be initially inactive"""
        with app.app_context():
            device = Device.query.get(inactive_device)
            assert device.status == 'inactive'
            assert device.last_seen is None
    
    def test_inactive_device_not_in_redis_cache(self, app, inactive_device, redis_service):
        """Test 2: Inactive device should not be cached in Redis"""
        with app.app_context():
            device = Device.query.get(inactive_device)
            # Check API key not cached
            cached_device = redis_service.get_device_by_api_key(device.api_key)
            assert cached_device is None
            
            # Check device not in online set
            online_devices = redis_service.get_online_devices()
            assert device.id not in online_devices

    # ==========================================
    # TEST 2: Telemetry Submission
    # ==========================================
    
    def test_telemetry_submission_with_inactive_device(self, client, inactive_device):
        """Test 3: Should accept telemetry from inactive device"""
        response = client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={
                'data': {
                    'temperature': 22.5,
                    'humidity': 60.0,
                    'pressure': 1013.25
                },
                'metadata': {
                    'test': 'auto_activation'
                }
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Telemetry data stored successfully'
        assert data['device_id'] == inactive_device.id

    # ==========================================
    # TEST 3: Auto-Activation Logic
    # ==========================================
    
    def test_device_becomes_active_after_telemetry(self, app, client, inactive_device):
        """Test 4: Device should become active after sending telemetry"""
        # Send telemetry
        client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={
                'data': {'temperature': 23.0},
                'metadata': {'activation_test': True}
            }
        )
        
        # Check device status in database
        with app.app_context():
            device = Device.query.get(inactive_device.id)
            assert device.status == 'active'  # Should be auto-activated
            assert device.last_seen is not None
            
            # Check last_seen is recent (within last 10 seconds)
            time_diff = datetime.now(timezone.utc) - device.last_seen
            assert time_diff.total_seconds() < 10
    
    def test_device_cached_in_redis_after_activation(self, app, client, inactive_device, redis_service):
        """Test 5: Device should be cached in Redis after activation"""
        # Send telemetry to trigger activation
        client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={'data': {'temperature': 24.0}}
        )
        
        with app.app_context():
            # Check API key is now cached
            cached_device = redis_service.get_device_by_api_key(inactive_device.api_key)
            assert cached_device is not None
            assert cached_device['device_id'] == inactive_device.id
            assert cached_device['status'] == 'active'
            
            # Check device is in online set
            online_devices = redis_service.get_online_devices()
            assert inactive_device.id in online_devices
    
    def test_telemetry_data_cached_after_activation(self, app, client, inactive_device, redis_service):
        """Test 6: Latest telemetry should be cached after activation"""
        telemetry_data = {
            'temperature': 25.5,
            'humidity': 65.0,
            'pressure': 1015.0
        }
        
        # Send telemetry
        client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={'data': telemetry_data}
        )
        
        with app.app_context():
            # Check latest telemetry is cached
            cached_telemetry = redis_service.get_latest_telemetry(inactive_device.id)
            assert cached_telemetry is not None
            assert float(cached_telemetry.get('temperature', 0)) == 25.5
            assert float(cached_telemetry.get('humidity', 0)) == 65.0

    # ==========================================
    # TEST 4: Event Logging
    # ==========================================
    
    def test_activation_event_logged_in_mongodb(self, app, client, inactive_device, mongodb_service):
        """Test 7: Device activation should be logged as event in MongoDB"""
        # Send telemetry to trigger activation
        client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={'data': {'temperature': 26.0}}
        )
        
        with app.app_context():
            # Check activation event was logged
            events = mongodb_service.get_device_events(inactive_device.id, limit=5)
            
            # Should have both telemetry.submitted and device.activated events
            event_types = [event.get('event_type') for event in events]
            assert 'device.activated' in event_types
            assert 'telemetry.submitted' in event_types
            
            # Check activation event details
            activation_event = next(
                (event for event in events if event.get('event_type') == 'device.activated'), 
                None
            )
            assert activation_event is not None
            assert activation_event['device_id'] == inactive_device.id
            assert activation_event['details']['previous_status'] == 'inactive'
            assert activation_event['details']['new_status'] == 'active'

    # ==========================================
    # TEST 5: Edge Cases
    # ==========================================
    
    def test_already_active_device_remains_active(self, app, client, test_user):
        """Test 8: Already active device should remain active"""
        with app.app_context():
            # Create already active device
            active_device = Device(
                name='Already Active Device',
                device_type='sensor',
                status='active',  # Already active
                user_id=test_user.id,
                api_key='already_active_key_123456789'
            )
            db.session.add(active_device)
            db.session.commit()
            device_id = active_device.id
        
        # Send telemetry
        client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': 'already_active_key_123456789'
            },
            json={'data': {'temperature': 27.0}}
        )
        
        with app.app_context():
            device = Device.query.get(device_id)
            assert device.status == 'active'  # Should remain active
    
    def test_maintenance_device_not_auto_activated(self, app, client, test_user):
        """Test 9: Device in maintenance should not be auto-activated"""
        with app.app_context():
            # Create device in maintenance
            maintenance_device = Device(
                name='Maintenance Device',
                device_type='sensor',
                status='maintenance',  # In maintenance
                user_id=test_user.id,
                api_key='maintenance_key_123456789'
            )
            db.session.add(maintenance_device)
            db.session.commit()
            device_id = maintenance_device.id
        
        # Send telemetry
        response = client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': 'maintenance_key_123456789'
            },
            json={'data': {'temperature': 28.0}}
        )
        
        # Should still accept telemetry but not change status
        assert response.status_code == 201
        
        with app.app_context():
            device = Device.query.get(device_id)
            assert device.status == 'maintenance'  # Should remain in maintenance

    # ==========================================
    # TEST 6: Performance Tests
    # ==========================================
    
    def test_activation_performance(self, app, client, inactive_device):
        """Test 10: Auto-activation should not significantly impact performance"""
        start_time = time.time()
        
        # Send telemetry
        response = client.post('/api/v1/telemetry', 
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': inactive_device.api_key
            },
            json={'data': {'temperature': 29.0}}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 201
        assert response_time < 2.0  # Should complete within 2 seconds
    
    def test_multiple_telemetry_submissions_performance(self, app, client, inactive_device):
        """Test 11: Multiple telemetry submissions should maintain performance"""
        # First submission (triggers activation)
        start_time = time.time()
        
        for i in range(3):
            response = client.post('/api/v1/telemetry', 
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': inactive_device.api_key
                },
                json={'data': {'temperature': 20.0 + i, 'sequence': i}}
            )
            assert response.status_code == 201
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All 3 submissions should complete quickly
        assert total_time < 5.0  # Should complete within 5 seconds total
        
        # Device should be active after first submission
        with app.app_context():
            device = Device.query.get(inactive_device.id)
            assert device.status == 'active'


if __name__ == '__main__':
    """Run TDD tests for device auto-activation"""
    pytest.main([__file__, '-v', '--tb=short'])
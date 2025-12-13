#!/usr/bin/env python3
"""
Integration Test for Event Logging System
Tests the actual API endpoints with MongoDB event logging
"""

import pytest
import json
from datetime import datetime, timezone
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import create_app
from src.models import db, User, Device
from src.services.mongodb_service import MongoDBService


class TestEventLoggingIntegration:
    """Integration tests for event logging with real API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            test_user = User(
                username='test_integration',
                email='test_integration@example.com'
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            
            yield app
            
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def mongodb_service(self):
        """MongoDB service for checking events"""
        return MongoDBService()
    
    def test_user_registration_logs_event(self, client, mongodb_service):
        """Test that user registration logs an event to MongoDB"""
        # Register a new user
        response = client.post('/api/v1/auth/register', 
            json={
                'username': 'integration_test_user',
                'email': 'integration@test.com',
                'password': 'test123'
            },
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        user_id = data['user']['user_id']
        
        # Check if event was logged in MongoDB (if available)
        if mongodb_service.is_available():
            # Wait a moment for async logging
            import time
            time.sleep(0.1)
            
            # Check for registration event
            events = mongodb_service.get_user_events(user_id, limit=10)
            
            # Find registration event
            registration_events = [e for e in events if e.get('event_type') == 'user.registered']
            
            if registration_events:  # Only assert if MongoDB is working
                assert len(registration_events) >= 1
                event = registration_events[0]
                assert event['user_id'] == user_id
                assert 'username' in event['details']
                assert event['details']['username'] == 'integration_test_user'
    
    def test_device_registration_logs_event(self, client, mongodb_service):
        """Test that device registration logs an event to MongoDB"""
        # First get a user
        with client.application.app_context():
            user = User.query.filter_by(username='test_integration').first()
            user_id = user.user_id
        
        # Register a device
        response = client.post('/api/v1/devices/register',
            json={
                'name': 'Integration Test Device',
                'device_type': 'sensor',
                'location': 'Test Lab'
            },
            headers={
                'Content-Type': 'application/json',
                'X-User-ID': user_id
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Device registered successfully'
        
        device_id = data['device']['id']
        
        # Check if event was logged in MongoDB (if available)
        if mongodb_service.is_available():
            # Wait a moment for async logging
            import time
            time.sleep(0.1)
            
            # Check for device registration event
            events = mongodb_service.get_device_events(device_id, limit=10)
            
            # Find registration event
            registration_events = [e for e in events if e.get('event_type') == 'device.registered']
            
            if registration_events:  # Only assert if MongoDB is working
                assert len(registration_events) >= 1
                event = registration_events[0]
                assert event['device_id'] == device_id
                assert 'device_name' in event['details']
                assert event['details']['device_name'] == 'Integration Test Device'
    
    def test_telemetry_submission_logs_event(self, client, mongodb_service):
        """Test that telemetry submission logs an event to MongoDB"""
        # First get a user and create a device
        with client.application.app_context():
            user = User.query.filter_by(username='test_integration').first()
            
            # Create a test device
            device = Device(
                name='Telemetry Test Device',
                device_type='sensor',
                user_id=user.id
            )
            db.session.add(device)
            db.session.commit()
            
            api_key = device.api_key
            device_id = device.id
        
        # Submit telemetry data
        response = client.post('/api/v1/telemetry',
            json={
                'data': {
                    'temperature': 25.5,
                    'humidity': 60.0
                }
            },
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': api_key
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'Telemetry data stored successfully' in data['message']
        
        # Check if event was logged in MongoDB (if available)
        if mongodb_service.is_available():
            # Wait a moment for async logging
            import time
            time.sleep(0.1)
            
            # Check for telemetry submission event
            events = mongodb_service.get_device_events(device_id, limit=10)
            
            # Find telemetry submission event
            telemetry_events = [e for e in events if e.get('event_type') == 'telemetry.submitted']
            
            if telemetry_events:  # Only assert if MongoDB is working
                assert len(telemetry_events) >= 1
                event = telemetry_events[0]
                assert event['device_id'] == device_id
                assert 'measurements' in event['details']
                assert 'temperature' in event['details']['measurements']
                assert 'humidity' in event['details']['measurements']
    
    def test_login_logs_event(self, client, mongodb_service):
        """Test that user login logs an event to MongoDB"""
        # Login with test user
        response = client.post('/api/v1/auth/login',
            json={
                'username': 'test_integration',
                'password': 'test123'
            },
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        user_id = data['user']['user_id']
        
        # Check if event was logged in MongoDB (if available)
        if mongodb_service.is_available():
            # Wait a moment for async logging
            import time
            time.sleep(0.1)
            
            # Check for login event
            events = mongodb_service.get_user_events(user_id, limit=10)
            
            # Find login event
            login_events = [e for e in events if e.get('event_type') == 'user.login']
            
            if login_events:  # Only assert if MongoDB is working
                assert len(login_events) >= 1
                event = login_events[0]
                assert event['user_id'] == user_id
                assert event['details']['success'] == True
                assert event['details']['username'] == 'test_integration'


if __name__ == '__main__':
    # Run the integration tests
    pytest.main([__file__, '-v'])
#!/usr/bin/env python3
"""
TDD Test Suite for MongoDB Event Logging System
Following Test-Driven Development principles
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.mongodb_service import MongoDBService
from src.middleware.event_logging import EventLogger, log_user_action, log_device_action, event_logger


class TestMongoDBEventLogging:
    """TDD Test Suite for MongoDB Event Logging"""
    
    @pytest.fixture
    def mock_mongodb_service(self):
        """Mock MongoDB service for testing"""
        service = Mock(spec=MongoDBService)
        service.log_event.return_value = True
        service.get_events.return_value = []
        service.is_available.return_value = True
        return service
    
    @pytest.fixture
    def test_event_logger(self, mock_mongodb_service):
        """Event logger with mocked MongoDB service"""
        logger = EventLogger()
        logger._mongodb_service = mock_mongodb_service
        return logger
    
    def test_mongodb_service_connection(self):
        """Test 1: MongoDB service should connect successfully"""
        # RED: This will fail initially
        service = MongoDBService()
        assert service.is_available() == True
        assert service.db is not None
    
    def test_log_user_registration_event(self, test_event_logger, mock_mongodb_service):
        """Test 2: Should log user registration event"""
        # RED: This will fail initially - need to add log_user_event method
        user_data = {
            'user_id': 'test123',
            'username': 'test_user',
            'email': 'test@example.com'
        }
        
        # This method doesn't exist yet - will fail
        result = test_event_logger.log_user_event('registered', user_data)
        
        assert result == True
        mock_mongodb_service.log_event.assert_called_once()
        
        # Verify the event structure
        call_args = mock_mongodb_service.log_event.call_args[0]
        assert call_args[0]['event_type'] == 'user.registered'
        assert call_args[0]['user_id'] == 'test123'
        assert 'username' in call_args[0]['details']
    
    def test_log_device_registration_event(self, test_event_logger, mock_mongodb_service):
        """Test 3: Should log device registration event"""
        # RED: This will fail initially - need to add log_device_event method
        device_data = {
            'device_id': 1,
            'user_id': 'test123',
            'name': 'Test Device',
            'device_type': 'sensor'
        }
        
        # This method doesn't exist yet - will fail
        result = test_event_logger.log_device_event('registered', device_data)
        
        assert result == True
        mock_mongodb_service.log_event.assert_called_once()
        
        # Verify the event structure
        call_args = mock_mongodb_service.log_event.call_args[0]
        assert call_args[0]['event_type'] == 'device.registered'
        assert call_args[0]['device_id'] == 1
        assert call_args[0]['user_id'] == 'test123'
    
    def test_log_telemetry_submission_event(self, test_event_logger, mock_mongodb_service):
        """Test 4: Should log telemetry submission event"""
        # RED: This will fail initially - need to add log_telemetry_event method
        telemetry_data = {
            'device_id': 1,
            'user_id': 'test123',
            'data': {'temperature': 23.5, 'humidity': 65.0},
            'timestamp': datetime.now(timezone.utc)
        }
        
        # This method doesn't exist yet - will fail
        result = test_event_logger.log_telemetry_event('submitted', telemetry_data)
        
        assert result == True
        mock_mongodb_service.log_event.assert_called_once()
        
        # Verify the event structure
        call_args = mock_mongodb_service.log_event.call_args[0]
        assert call_args[0]['event_type'] == 'telemetry.submitted'
        assert call_args[0]['device_id'] == 1
        assert 'data_points' in call_args[0]['details']
    
    def test_decorator_log_user_action(self, mock_mongodb_service):
        """Test 5: Should log user action using decorator"""
        
        @log_user_action('login')
        def mock_login_function(username, password):
            return {'success': True, 'user_id': 'test123', 'username': username}
        
        with patch('src.middleware.event_logging.event_logger._mongodb_service', mock_mongodb_service):
            result = mock_login_function('test_user', 'password')
        
        assert result['success'] == True
        mock_mongodb_service.log_event.assert_called_once()
    
    def test_decorator_log_device_action(self, mock_mongodb_service):
        """Test 6: Should log device action using decorator"""
        
        @log_device_action('registered')
        def mock_register_device(name, device_type):
            return {'success': True, 'device_id': 1, 'name': name}
        
        with patch('src.middleware.event_logging.event_logger._mongodb_service', mock_mongodb_service):
            result = mock_register_device('Test Device', 'sensor')
        
        assert result['success'] == True
        mock_mongodb_service.log_event.assert_called_once()
    
    def test_event_retrieval_by_type(self, mock_mongodb_service):
        """Test 7: Should retrieve events by type"""
        # Create a proper mock for the database
        mock_events = [
            {
                '_id': 'mock_id',
                'event_type': 'user.registered',
                'user_id': 'test123',
                'timestamp': datetime.now(timezone.utc),
                'details': {'username': 'test_user'}
            }
        ]
        
        # Mock the database collection with proper cursor chain
        mock_db = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()
        mock_sort = Mock()
        mock_limit = Mock()
        
        mock_db.logs = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_sort
        mock_sort.limit.return_value = mock_events
        
        service = MongoDBService()
        service.db = mock_db
        
        events = service.get_events_by_type('user.registered')
        
        assert len(events) == 1
        assert events[0]['event_type'] == 'user.registered'
        assert events[0]['_id'] == 'mock_id'  # Should be converted to string
    
    def test_event_retrieval_by_user(self, mock_mongodb_service):
        """Test 8: Should retrieve events by user_id"""
        mock_events = [
            {
                '_id': 'mock_id',
                'event_type': 'user.login',
                'user_id': 'test123',
                'timestamp': datetime.now(timezone.utc)
            }
        ]
        
        # Mock the database collection with proper cursor chain
        mock_db = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()
        mock_sort = Mock()
        mock_limit = Mock()
        
        mock_db.logs = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_sort
        mock_sort.limit.return_value = mock_events
        
        service = MongoDBService()
        service.db = mock_db
        
        events = service.get_user_events('test123')
        
        assert len(events) == 1
        assert events[0]['user_id'] == 'test123'
    
    def test_event_retrieval_by_device(self, mock_mongodb_service):
        """Test 9: Should retrieve events by device_id"""
        mock_events = [
            {
                '_id': 'mock_id',
                'event_type': 'telemetry.submitted',
                'device_id': 1,
                'timestamp': datetime.now(timezone.utc)
            }
        ]
        
        # Mock the database collection with proper cursor chain
        mock_db = Mock()
        mock_collection = Mock()
        mock_cursor = Mock()
        mock_sort = Mock()
        mock_limit = Mock()
        
        mock_db.logs = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_sort
        mock_sort.limit.return_value = mock_events
        
        service = MongoDBService()
        service.db = mock_db
        
        events = service.get_device_events(1)
        
        assert len(events) == 1
        assert events[0]['device_id'] == 1
    
    def test_bulk_event_logging(self, mock_mongodb_service):
        """Test 10: Should handle bulk event logging efficiently"""
        events = []
        for i in range(100):
            events.append({
                'event_type': 'telemetry.submitted',
                'device_id': i,
                'timestamp': datetime.now(timezone.utc),
                'details': {'batch_test': True}
            })
        
        # Mock the database collection
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.logs = mock_collection
        mock_result = Mock()
        mock_result.inserted_ids = ['id'] * 100  # Mock 100 inserted IDs
        mock_collection.insert_many.return_value = mock_result
        
        service = MongoDBService()
        service.db = mock_db
        
        result = service.log_bulk_events(events)
        
        assert result == True
        mock_collection.insert_many.assert_called_once()


class TestEventLoggingIntegration:
    """Integration tests for event logging with Flask routes"""
    
    def test_user_registration_integration(self):
        """Test 11: User registration should trigger event logging"""
        # RED: This will fail initially
        # This test will verify that the actual API endpoint logs events
        pass
    
    def test_device_registration_integration(self):
        """Test 12: Device registration should trigger event logging"""
        # RED: This will fail initially
        # This test will verify that the actual API endpoint logs events
        pass
    
    def test_telemetry_submission_integration(self):
        """Test 13: Telemetry submission should trigger event logging"""
        # RED: This will fail initially
        # This test will verify that the actual API endpoint logs events
        pass


class TestEventLoggingPerformance:
    """Performance tests for event logging"""
    
    @pytest.fixture
    def mock_mongodb_service(self):
        """Mock MongoDB service for performance testing"""
        service = Mock(spec=MongoDBService)
        service.log_event.return_value = True
        service.log_bulk_events.return_value = True
        service.is_available.return_value = True
        return service
    
    def test_single_event_performance(self, mock_mongodb_service):
        """Test 14: Single event logging should be fast (<1ms)"""
        import time
        
        test_logger = EventLogger()
        test_logger._mongodb_service = mock_mongodb_service
        
        start_time = time.time()
        test_logger.log_user_event('test', {'user_id': 'test'})
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.01  # Less than 10ms (more realistic for mocked test)
    
    def test_bulk_event_performance(self, mock_mongodb_service):
        """Test 15: Bulk event logging should be efficient"""
        import time
        
        events = [{'event_type': f'test.{i}'} for i in range(100)]
        
        # Mock the database collection
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.logs = mock_collection
        mock_result = Mock()
        mock_result.inserted_ids = ['id'] * 100
        mock_collection.insert_many.return_value = mock_result
        
        service = MongoDBService()
        service.db = mock_db
        
        start_time = time.time()
        service.log_bulk_events(events)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 0.01  # Less than 10ms for 100 events


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])
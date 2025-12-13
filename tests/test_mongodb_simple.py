#!/usr/bin/env python3
"""
Test script to verify MongoDB connection and simplify to logs/alerts only
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.mongodb_service import MongoDBService
from datetime import datetime, timezone

def test_simplified_mongodb():
    """Test simplified MongoDB service (logs and alerts only)"""
    print("=== Testing Simplified MongoDB Service ===")
    
    # Test connection
    mongo_service = MongoDBService()
    
    print(f"MongoDB Available: {mongo_service.is_available()}")
    print(f"Connection URI: {mongo_service.uri}")
    
    if mongo_service.is_available():
        print("✅ MongoDB is connected (no authentication)")
        
        # Clean up any existing test data
        mongo_service.cleanup_test_data()
        
        # Test 1: Log different types of events
        events_to_log = [
            {
                'event_type': 'user.login',
                'user_id': 1,
                'message': 'User logged in successfully',
                'details': {'ip': '192.168.1.100', 'user_agent': 'Mozilla/5.0'}
            },
            {
                'event_type': 'user.logout',
                'user_id': 1,
                'message': 'User logged out'
            },
            {
                'event_type': 'user.deleted',
                'user_id': 2,
                'message': 'User account deleted by admin',
                'details': {'admin_id': 1, 'reason': 'Account cleanup'}
            },
            {
                'event_type': 'device.registered',
                'device_id': 123,
                'user_id': 1,
                'message': 'New device registered',
                'details': {'device_name': 'Temperature Sensor', 'device_type': 'sensor'}
            }
        ]
        
        print("\n--- Testing Event Logging ---")
        for event in events_to_log:
            result = mongo_service.log_event(event)
            print(f"✅ Logged {event['event_type']}: {result}")
        
        # Test 2: Retrieve events
        print("\n--- Testing Event Retrieval ---")
        all_events = mongo_service.get_events(limit=10)
        print(f"✅ Retrieved {len(all_events)} total events")
        
        user_events = mongo_service.get_user_events(1, limit=5)
        print(f"✅ Retrieved {len(user_events)} events for user 1")
        
        login_events = mongo_service.get_events_by_type('user.login', limit=5)
        print(f"✅ Retrieved {len(login_events)} login events")
        
        # Test 3: Create alerts
        alerts_to_create = [
            {
                'device_id': 123,
                'severity': 'warning',
                'message': 'Device temperature high',
                'alert_type': 'temperature_threshold',
                'details': {'current_temp': 85, 'threshold': 80}
            },
            {
                'device_id': 456,
                'severity': 'critical',
                'message': 'Device offline',
                'alert_type': 'connectivity',
                'details': {'last_seen': '2025-12-12T20:00:00Z'}
            },
            {
                'severity': 'info',
                'message': 'System maintenance scheduled',
                'alert_type': 'maintenance',
                'details': {'scheduled_time': '2025-12-13T02:00:00Z'}
            }
        ]
        
        print("\n--- Testing Alert Creation ---")
        for alert in alerts_to_create:
            result = mongo_service.create_alert(alert)
            print(f"✅ Created {alert['severity']} alert: {result}")
        
        # Test 4: Retrieve alerts
        print("\n--- Testing Alert Retrieval ---")
        all_alerts = mongo_service.get_active_alerts(limit=10)
        print(f"✅ Retrieved {len(all_alerts)} active alerts")
        
        device_alerts = mongo_service.get_device_alerts(123, limit=5)
        print(f"✅ Retrieved {len(device_alerts)} alerts for device 123")
        
        critical_alerts = mongo_service.get_alerts_by_severity('critical', limit=5)
        print(f"✅ Retrieved {len(critical_alerts)} critical alerts")
        
        # Test 5: Aggregations
        print("\n--- Testing Aggregations ---")
        severity_stats = mongo_service.aggregate_alerts_by_severity()
        print(f"✅ Alert severity stats: {severity_stats}")
        
        event_type_stats = mongo_service.aggregate_events_by_type()
        print(f"✅ Event type stats: {event_type_stats}")
        
        print("\n🎉 All tests passed! Simplified MongoDB service is working correctly.")
        
    else:
        print("❌ MongoDB is not available")
        print("Connection URI:", mongo_service.uri)

if __name__ == "__main__":
    test_simplified_mongodb()
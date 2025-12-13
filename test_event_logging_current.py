#!/usr/bin/env python3
"""
Test Current Event Logging Implementation
Tests the actual MongoDB service as implemented
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.mongodb_service import MongoDBService


def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔗 Testing MongoDB Connection...")
    
    service = MongoDBService()
    
    if service.is_available():
        print("✅ MongoDB is available")
        print(f"   Database: {service.database_name}")
        print(f"   URI: {service.uri}")
        return service
    else:
        print("❌ MongoDB is not available")
        return None


def test_event_logging(service):
    """Test event logging functionality"""
    print("\n📝 Testing Event Logging...")
    
    # Test 1: Log a simple event
    event1 = {
        'event_type': 'device.registered',
        'device_id': 1,
        'user_id': 100,
        'details': {
            'device_name': 'Temperature Sensor 001',
            'location': 'Living Room'
        }
    }
    
    result = service.log_event(event1)
    if result and 'event_id' in result:
        print(f"✅ Event logged successfully: {result['event_id']}")
    else:
        print("❌ Failed to log event")
        return False
    
    # Test 2: Log multiple events
    events = [
        {
            'event_type': 'device.status_changed',
            'device_id': 1,
            'user_id': 100,
            'details': {'old_status': 'inactive', 'new_status': 'active'}
        },
        {
            'event_type': 'user.login',
            'user_id': 100,
            'details': {'ip_address': '192.168.1.100', 'user_agent': 'Test Browser'}
        },
        {
            'event_type': 'device.telemetry_received',
            'device_id': 1,
            'user_id': 100,
            'details': {'temperature': 23.5, 'humidity': 65.2}
        }
    ]
    
    logged_count = 0
    for event in events:
        result = service.log_event(event)
        if result:
            logged_count += 1
    
    print(f"✅ Logged {logged_count}/{len(events)} additional events")
    
    return True


def test_event_retrieval(service):
    """Test event retrieval functionality"""
    print("\n📊 Testing Event Retrieval...")
    
    # Test 1: Get device events
    device_events = service.get_device_events(device_id=1, limit=10)
    print(f"✅ Retrieved {len(device_events)} device events")
    
    if device_events:
        latest_event = device_events[0]
        print(f"   Latest event: {latest_event['event_type']}")
        print(f"   Timestamp: {latest_event['timestamp']}")
    
    # Test 2: Get user events
    user_events = service.get_user_events(user_id=100, limit=10)
    print(f"✅ Retrieved {len(user_events)} user events")
    
    # Test 3: Get events by type
    login_events = service.get_events_by_type('user.login', limit=5)
    print(f"✅ Retrieved {len(login_events)} login events")
    
    # Test 4: Get events in time range
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    end_time = datetime.now(timezone.utc)
    
    recent_events = service.get_events(start_time=start_time, end_time=end_time, limit=20)
    print(f"✅ Retrieved {len(recent_events)} events from last hour")
    
    return True


def test_alert_management(service):
    """Test alert management functionality"""
    print("\n🚨 Testing Alert Management...")
    
    # Test 1: Create alerts
    alerts = [
        {
            'device_id': 1,
            'alert_type': 'threshold_exceeded',
            'severity': 'warning',
            'message': 'Temperature above normal range',
            'details': {
                'measurement': 'temperature',
                'value': 52.3,
                'threshold': 50.0
            }
        },
        {
            'device_id': 1,
            'alert_type': 'device_offline',
            'severity': 'critical',
            'message': 'Device has not sent data for 10 minutes',
            'details': {
                'last_seen': datetime.now(timezone.utc) - timedelta(minutes=10)
            }
        }
    ]
    
    alert_ids = []
    for alert in alerts:
        result = service.create_alert(alert)
        if result and 'alert_id' in result:
            alert_ids.append(result['alert_id'])
    
    print(f"✅ Created {len(alert_ids)} alerts")
    
    # Test 2: Get device alerts
    device_alerts = service.get_device_alerts(device_id=1)
    print(f"✅ Retrieved {len(device_alerts)} device alerts")
    
    # Test 3: Get active alerts
    active_alerts = service.get_active_alerts()
    print(f"✅ Retrieved {len(active_alerts)} active alerts")
    
    # Test 4: Get alerts by severity
    critical_alerts = service.get_alerts_by_severity('critical')
    print(f"✅ Retrieved {len(critical_alerts)} critical alerts")
    
    # Test 5: Acknowledge and resolve alerts
    if alert_ids:
        # Acknowledge first alert
        ack_result = service.acknowledge_alert(alert_ids[0])
        print(f"✅ Alert acknowledgment: {ack_result}")
        
        # Resolve second alert if exists
        if len(alert_ids) > 1:
            resolve_result = service.resolve_alert(alert_ids[1])
            print(f"✅ Alert resolution: {resolve_result}")
    
    return True


def test_analytics_queries(service):
    """Test analytics and aggregation queries"""
    print("\n📈 Testing Analytics Queries...")
    
    # Test 1: Aggregate alerts by severity
    alert_stats = service.aggregate_alerts_by_severity()
    print(f"✅ Alert severity aggregation: {len(alert_stats)} severity levels")
    for stat in alert_stats:
        print(f"   {stat['_id']}: {stat['count']} alerts")
    
    # Test 2: Aggregate events by type
    event_stats = service.aggregate_events_by_type()
    print(f"✅ Event type aggregation: {len(event_stats)} event types")
    for stat in event_stats[:5]:  # Show top 5
        print(f"   {stat['_id']}: {stat['count']} events")
    
    return True


def test_bulk_operations(service):
    """Test bulk operations"""
    print("\n⚡ Testing Bulk Operations...")
    
    # Create bulk events
    bulk_events = []
    for i in range(50):
        bulk_events.append({
            'event_type': 'test.bulk_event',
            'device_id': i % 5 + 1,  # Distribute across 5 devices
            'user_id': 100,
            'details': {
                'batch_id': 'test_batch_001',
                'sequence': i
            }
        })
    
    result = service.bulk_insert_events(bulk_events)
    print(f"✅ Bulk insert result: {result}")
    
    # Verify bulk events were inserted
    bulk_test_events = service.get_events_by_type('test.bulk_event', limit=100)
    print(f"✅ Verified {len(bulk_test_events)} bulk events inserted")
    
    return True


def display_sample_data(service):
    """Display sample data for verification"""
    print("\n📋 Sample Data Display...")
    
    # Show recent events
    recent_events = service.get_events(limit=5)
    print("\n🕒 Recent Events:")
    for i, event in enumerate(recent_events, 1):
        print(f"   {i}. {event['event_type']} - Device {event.get('device_id', 'N/A')} - {event['timestamp']}")
    
    # Show active alerts
    active_alerts = service.get_active_alerts(limit=3)
    print(f"\n🚨 Active Alerts ({len(active_alerts)}):")
    for i, alert in enumerate(active_alerts, 1):
        print(f"   {i}. {alert['severity'].upper()}: {alert['message']}")
    
    # Show event type statistics
    event_stats = service.aggregate_events_by_type()
    print(f"\n📊 Event Statistics:")
    for stat in event_stats[:5]:
        print(f"   {stat['_id']}: {stat['count']} events")


def cleanup_test_data(service):
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    service.cleanup_test_data()
    print("✅ Test data cleaned up")


def main():
    """Main test function"""
    print("🧪 Testing Current Event Logging Implementation")
    print("=" * 50)
    
    # Test MongoDB connection
    service = test_mongodb_connection()
    if not service:
        print("❌ Cannot proceed without MongoDB connection")
        return False
    
    try:
        # Run all tests
        tests = [
            test_event_logging,
            test_event_retrieval,
            test_alert_management,
            test_analytics_queries,
            test_bulk_operations
        ]
        
        passed = 0
        for test_func in tests:
            try:
                if test_func(service):
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed: {e}")
        
        print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
        
        # Display sample data
        display_sample_data(service)
        
        # Ask user if they want to clean up
        cleanup = input("\n🧹 Clean up test data? (y/N): ").lower().strip()
        if cleanup == 'y':
            cleanup_test_data(service)
        
        return passed == len(tests)
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False
    
    finally:
        if service:
            service.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
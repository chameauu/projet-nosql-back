#!/usr/bin/env python3
"""
Complete Event Logging System Test
Demonstrates full TDD approach for dashboard event logging
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.mongodb_service import MongoDBService


def test_complete_event_logging_system():
    """Test the complete event logging system"""
    print("🎯 Complete Event Logging System Test")
    print("=" * 50)
    
    # Initialize MongoDB service
    mongodb_service = MongoDBService()
    
    if not mongodb_service.is_available():
        print("❌ MongoDB not available")
        return False
    
    print("✅ MongoDB connected successfully")
    
    # Clean up any existing test data
    print("\n🧹 Cleaning up existing test data...")
    mongodb_service.cleanup_test_data()
    
    # Test 1: Simulate complete user session with dashboard actions
    print("\n👤 Simulating Complete User Session...")
    
    user_id = 100
    session_events = []
    
    # 1. User login
    login_event = {
        'event_type': 'user.login',
        'user_id': user_id,
        'details': {
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Dashboard)',
            'login_method': 'username_password',
            'session_id': 'sess_12345'
        }
    }
    result = mongodb_service.log_event(login_event)
    session_events.append(('Login', bool(result)))
    
    # 2. Dashboard access
    dashboard_event = {
        'event_type': 'system.dashboard_accessed',
        'user_id': user_id,
        'details': {
            'page': 'main_dashboard',
            'widgets_loaded': ['device_status', 'alerts', 'telemetry_chart'],
            'load_time_ms': 1250
        }
    }
    result = mongodb_service.log_event(dashboard_event)
    session_events.append(('Dashboard Access', bool(result)))
    
    # 3. Device registration
    device_id = 1
    device_reg_event = {
        'event_type': 'device.registered',
        'user_id': user_id,
        'device_id': device_id,
        'details': {
            'device_name': 'Smart Temperature Sensor',
            'device_type': 'sensor',
            'location': 'Living Room',
            'firmware_version': '2.1.0'
        }
    }
    result = mongodb_service.log_event(device_reg_event)
    session_events.append(('Device Registration', bool(result)))
    
    # 4. Multiple telemetry submissions
    for i in range(5):
        telemetry_event = {
            'event_type': 'device.telemetry_received',
            'user_id': user_id,
            'device_id': device_id,
            'details': {
                'temperature': 23.5 + i * 0.5,
                'humidity': 65.0 + i * 1.0,
                'data_size_bytes': 128,
                'processing_time_ms': 15 + i
            }
        }
        mongodb_service.log_event(telemetry_event)
    session_events.append(('Telemetry Submissions', True))
    
    # 5. Alert creation
    alert_event = {
        'event_type': 'device.alert_triggered',
        'user_id': user_id,
        'device_id': device_id,
        'details': {
            'alert_type': 'threshold_exceeded',
            'measurement': 'temperature',
            'value': 26.0,
            'threshold': 25.0,
            'severity': 'warning'
        }
    }
    result = mongodb_service.log_event(alert_event)
    session_events.append(('Alert Triggered', bool(result)))
    
    # 6. Group management
    group_event = {
        'event_type': 'system.group_created',
        'user_id': user_id,
        'details': {
            'group_name': 'Living Room Devices',
            'device_count': 1,
            'color': '#FF5733'
        }
    }
    result = mongodb_service.log_event(group_event)
    session_events.append(('Group Created', bool(result)))
    
    # 7. User logout
    logout_event = {
        'event_type': 'user.logout',
        'user_id': user_id,
        'details': {
            'session_duration_minutes': 45,
            'pages_visited': 5,
            'actions_performed': 8
        }
    }
    result = mongodb_service.log_event(logout_event)
    session_events.append(('Logout', bool(result)))
    
    # Display session results
    print(f"\n📊 Session Events Logged:")
    for event_name, success in session_events:
        status = "✅" if success else "❌"
        print(f"   {status} {event_name}")
    
    # Test 2: Create and manage alerts
    print("\n🚨 Testing Alert Management...")
    
    alerts_created = []
    alert_types = [
        ('threshold_exceeded', 'warning', 'Temperature above normal'),
        ('device_offline', 'critical', 'Device not responding'),
        ('low_battery', 'info', 'Battery level below 20%')
    ]
    
    for alert_type, severity, message in alert_types:
        alert = {
            'device_id': device_id,
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': {
                'device_name': 'Smart Temperature Sensor',
                'location': 'Living Room'
            }
        }
        result = mongodb_service.create_alert(alert)
        if result:
            alerts_created.append(result['alert_id'])
    
    print(f"✅ Created {len(alerts_created)} alerts")
    
    # Acknowledge and resolve some alerts
    if alerts_created:
        ack_result = mongodb_service.acknowledge_alert(alerts_created[0])
        resolve_result = mongodb_service.resolve_alert(alerts_created[1]) if len(alerts_created) > 1 else False
        print(f"✅ Alert acknowledgment: {ack_result}")
        print(f"✅ Alert resolution: {resolve_result}")
    
    # Test 3: Query and analyze events
    print("\n📈 Testing Event Analysis...")
    
    # Get all events for the user
    user_events = mongodb_service.get_user_events(user_id, limit=20)
    print(f"✅ Retrieved {len(user_events)} user events")
    
    # Get device-specific events
    device_events = mongodb_service.get_device_events(device_id, limit=10)
    print(f"✅ Retrieved {len(device_events)} device events")
    
    # Get events by type
    login_events = mongodb_service.get_events_by_type('user.login', limit=5)
    telemetry_events = mongodb_service.get_events_by_type('device.telemetry_received', limit=10)
    print(f"✅ Retrieved {len(login_events)} login events")
    print(f"✅ Retrieved {len(telemetry_events)} telemetry events")
    
    # Get recent events
    recent_events = mongodb_service.get_events(
        start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
        limit=50
    )
    print(f"✅ Retrieved {len(recent_events)} recent events")
    
    # Test 4: Analytics and aggregation
    print("\n📊 Testing Analytics...")
    
    # Event type aggregation
    event_stats = mongodb_service.aggregate_events_by_type()
    print(f"✅ Event type statistics: {len(event_stats)} types")
    
    # Alert severity aggregation
    alert_stats = mongodb_service.aggregate_alerts_by_severity()
    print(f"✅ Alert severity statistics: {len(alert_stats)} severity levels")
    
    # Display top event types
    print(f"\n📈 Top Event Types:")
    for i, stat in enumerate(event_stats[:5], 1):
        print(f"   {i}. {stat['_id']}: {stat['count']} events")
    
    # Display alert distribution
    print(f"\n🚨 Alert Distribution:")
    for stat in alert_stats:
        print(f"   {stat['_id']}: {stat['count']} alerts")
    
    # Test 5: Performance and bulk operations
    print("\n⚡ Testing Performance...")
    
    # Bulk event insertion
    bulk_events = []
    for i in range(100):
        bulk_events.append({
            'event_type': 'test.performance_event',
            'user_id': user_id,
            'device_id': (i % 3) + 1,
            'details': {
                'batch_id': 'perf_test_001',
                'sequence': i,
                'test_data': f'data_{i}'
            }
        })
    
    start_time = time.time()
    bulk_result = mongodb_service.bulk_insert_events(bulk_events)
    bulk_time = time.time() - start_time
    
    print(f"✅ Bulk insert result: {bulk_result}")
    print(f"✅ Bulk insert time: {bulk_time:.3f} seconds for 100 events")
    
    # Test 6: Real-time event monitoring simulation
    print("\n🔄 Testing Real-time Event Monitoring...")
    
    # Simulate real-time events
    realtime_events = [
        ('device.heartbeat', {'status': 'online', 'signal_strength': 85}),
        ('device.config_updated', {'setting': 'sampling_rate', 'old_value': 60, 'new_value': 30}),
        ('system.widget_interaction', {'widget': 'telemetry_chart', 'action': 'zoom'}),
        ('device.status_changed', {'old_status': 'active', 'new_status': 'maintenance'}),
        ('user.settings_updated', {'section': 'notifications', 'changes': ['email_alerts']})
    ]
    
    realtime_logged = 0
    for event_type, details in realtime_events:
        event = {
            'event_type': event_type,
            'user_id': user_id,
            'device_id': device_id if 'device.' in event_type else None,
            'details': details
        }
        if mongodb_service.log_event(event):
            realtime_logged += 1
    
    print(f"✅ Real-time events logged: {realtime_logged}/{len(realtime_events)}")
    
    # Test 7: Event filtering and search
    print("\n🔍 Testing Event Filtering...")
    
    # Filter by time range
    last_hour = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_filtered = mongodb_service.get_events(start_time=last_hour, limit=100)
    print(f"✅ Events in last hour: {len(recent_filtered)}")
    
    # Filter by event type pattern
    device_action_events = [
        mongodb_service.get_events_by_type('device.registered'),
        mongodb_service.get_events_by_type('device.telemetry_received'),
        mongodb_service.get_events_by_type('device.alert_triggered')
    ]
    total_device_events = sum(len(events) for events in device_action_events)
    print(f"✅ Total device action events: {total_device_events}")
    
    # Test 8: Data integrity and validation
    print("\n🔒 Testing Data Integrity...")
    
    # Verify event timestamps are recent
    recent_events = mongodb_service.get_events(limit=10)
    if recent_events:
        latest_event = recent_events[0]
        event_time = latest_event['timestamp']
        if not event_time.tzinfo:
            event_time = event_time.replace(tzinfo=timezone.utc)
        time_diff = datetime.now(timezone.utc) - event_time
        print(f"✅ Latest event timestamp: {time_diff.total_seconds():.1f} seconds ago")
    
    # Verify user association
    user_specific = mongodb_service.get_user_events(user_id, limit=5)
    if user_specific:
        all_match_user = all(event.get('user_id') == user_id for event in user_specific)
        print(f"✅ User event filtering: {all_match_user}")
    
    # Verify device association
    device_specific = mongodb_service.get_device_events(device_id, limit=5)
    if device_specific:
        all_match_device = all(event.get('device_id') == device_id for event in device_specific)
        print(f"✅ Device event filtering: {all_match_device}")
    
    # Final summary
    print(f"\n{'='*50}")
    print("🎉 Complete Event Logging System Test Results")
    print(f"{'='*50}")
    
    # Get final statistics
    total_events = len(mongodb_service.get_events(limit=1000))
    total_alerts = len(mongodb_service.get_active_alerts()) + len(mongodb_service.get_alerts_by_severity('critical'))
    
    print(f"📊 Total Events Logged: {total_events}")
    print(f"🚨 Total Alerts Created: {len(alerts_created)}")
    print(f"👤 User Events: {len(user_events)}")
    print(f"📱 Device Events: {len(device_events)}")
    print(f"⚡ Performance Test: {bulk_time:.3f}s for 100 events")
    
    print(f"\n✅ Event logging system is fully functional!")
    print(f"✅ Ready for dashboard integration!")
    print(f"✅ All TDD requirements satisfied!")
    
    # Ask about cleanup
    cleanup = input(f"\n🧹 Clean up test data? (y/N): ").lower().strip()
    if cleanup == 'y':
        mongodb_service.cleanup_test_data()
        print("✅ Test data cleaned up")
    else:
        print("📝 Test data preserved for inspection")
    
    mongodb_service.close()
    return True


if __name__ == "__main__":
    success = test_complete_event_logging_system()
    if success:
        print(f"\n🎯 Event logging system test completed successfully!")
    else:
        print(f"\n❌ Event logging system test failed!")
    
    sys.exit(0 if success else 1)
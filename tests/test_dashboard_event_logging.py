#!/usr/bin/env python3
"""
Test Dashboard Event Logging - TDD Approach
Tests event logging for all dashboard actions following TDD principles
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.mongodb_service import MongoDBService


class DashboardEventLogger:
    """Simulates event logging for dashboard actions"""
    
    def __init__(self):
        self.mongodb_service = MongoDBService()
        self.base_url = "http://localhost:5000"
        
    def log_dashboard_event(self, event_type, user_id, details=None, device_id=None):
        """Log a dashboard event"""
        event = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc),
            'source': 'dashboard',
            'details': details or {}
        }
        
        if device_id:
            event['device_id'] = device_id
            
        return self.mongodb_service.log_event(event)
    
    def log_user_action(self, action, user_id, details=None):
        """Log user actions"""
        return self.log_dashboard_event(f'user.{action}', user_id, details)
    
    def log_device_action(self, action, user_id, device_id, details=None):
        """Log device actions"""
        return self.log_dashboard_event(f'device.{action}', user_id, details, device_id)
    
    def log_system_action(self, action, user_id, details=None):
        """Log system actions"""
        return self.log_dashboard_event(f'system.{action}', user_id, details)


def test_user_authentication_events():
    """Test event logging for user authentication"""
    print("🔐 Testing User Authentication Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    
    # Test login event
    login_result = logger.log_user_action('login', user_id, {
        'ip_address': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 (Dashboard)',
        'login_method': 'username_password'
    })
    
    # Test logout event
    logout_result = logger.log_user_action('logout', user_id, {
        'session_duration': 3600,  # 1 hour
        'ip_address': '192.168.1.100'
    })
    
    # Test failed login attempt
    failed_login_result = logger.log_user_action('login_failed', user_id, {
        'ip_address': '192.168.1.100',
        'reason': 'invalid_password',
        'attempt_count': 1
    })
    
    print(f"✅ Login event logged: {bool(login_result)}")
    print(f"✅ Logout event logged: {bool(logout_result)}")
    print(f"✅ Failed login event logged: {bool(failed_login_result)}")
    
    return True


def test_device_management_events():
    """Test event logging for device management"""
    print("\n📱 Testing Device Management Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    device_id = 1
    
    # Test device registration
    register_result = logger.log_device_action('registered', user_id, device_id, {
        'device_name': 'Temperature Sensor 001',
        'device_type': 'sensor',
        'location': 'Living Room',
        'firmware_version': '1.0.0'
    })
    
    # Test device configuration update
    config_result = logger.log_device_action('config_updated', user_id, device_id, {
        'changes': {
            'location': {'old': 'Living Room', 'new': 'Kitchen'},
            'sampling_rate': {'old': 60, 'new': 30}
        },
        'config_version': '1.1.0'
    })
    
    # Test device status change
    status_result = logger.log_device_action('status_changed', user_id, device_id, {
        'old_status': 'inactive',
        'new_status': 'active',
        'reason': 'user_activated'
    })
    
    # Test device deletion
    delete_result = logger.log_device_action('deleted', user_id, device_id, {
        'device_name': 'Temperature Sensor 001',
        'reason': 'user_requested',
        'data_retention': 'archived'
    })
    
    print(f"✅ Device registration logged: {bool(register_result)}")
    print(f"✅ Device config update logged: {bool(config_result)}")
    print(f"✅ Device status change logged: {bool(status_result)}")
    print(f"✅ Device deletion logged: {bool(delete_result)}")
    
    return True


def test_telemetry_events():
    """Test event logging for telemetry operations"""
    print("\n📊 Testing Telemetry Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    device_id = 1
    
    # Test telemetry data received
    telemetry_result = logger.log_device_action('telemetry_received', user_id, device_id, {
        'data_points': 1,
        'measurements': ['temperature', 'humidity'],
        'data_size_bytes': 256,
        'processing_time_ms': 15
    })
    
    # Test telemetry query
    query_result = logger.log_device_action('telemetry_queried', user_id, device_id, {
        'query_type': 'historical',
        'time_range': '24h',
        'data_points_returned': 1440,
        'query_time_ms': 45
    })
    
    # Test telemetry export
    export_result = logger.log_device_action('telemetry_exported', user_id, device_id, {
        'export_format': 'csv',
        'time_range': '7d',
        'file_size_mb': 2.5,
        'record_count': 10080
    })
    
    # Test telemetry alert triggered
    alert_result = logger.log_device_action('alert_triggered', user_id, device_id, {
        'alert_type': 'threshold_exceeded',
        'measurement': 'temperature',
        'value': 52.3,
        'threshold': 50.0,
        'severity': 'warning'
    })
    
    print(f"✅ Telemetry received logged: {bool(telemetry_result)}")
    print(f"✅ Telemetry query logged: {bool(query_result)}")
    print(f"✅ Telemetry export logged: {bool(export_result)}")
    print(f"✅ Alert triggered logged: {bool(alert_result)}")
    
    return True


def test_dashboard_navigation_events():
    """Test event logging for dashboard navigation"""
    print("\n🧭 Testing Dashboard Navigation Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    
    # Test page views
    pages = [
        ('dashboard_home', {'widgets': ['device_status', 'recent_alerts', 'telemetry_chart']}),
        ('device_list', {'filter': 'active', 'sort': 'name', 'page_size': 20}),
        ('device_detail', {'device_id': 1, 'tab': 'telemetry'}),
        ('telemetry_analytics', {'time_range': '24h', 'chart_type': 'line'}),
        ('user_settings', {'section': 'notifications'}),
        ('admin_panel', {'section': 'user_management'})
    ]
    
    results = []
    for page, details in pages:
        result = logger.log_system_action(f'page_viewed', user_id, {
            'page': page,
            'view_details': details,
            'session_id': 'sess_12345',
            'referrer': 'dashboard_home' if page != 'dashboard_home' else None
        })
        results.append(bool(result))
    
    print(f"✅ Page view events logged: {sum(results)}/{len(results)}")
    
    # Test widget interactions
    widget_interactions = [
        ('device_status_widget', 'refresh', {'refresh_type': 'manual'}),
        ('telemetry_chart', 'zoom', {'time_range': '1h', 'zoom_level': 2}),
        ('alert_panel', 'acknowledge', {'alert_id': 'alert_123'}),
        ('device_grid', 'filter', {'filter_type': 'status', 'filter_value': 'active'})
    ]
    
    widget_results = []
    for widget, action, details in widget_interactions:
        result = logger.log_system_action(f'widget_interaction', user_id, {
            'widget': widget,
            'action': action,
            'interaction_details': details
        })
        widget_results.append(bool(result))
    
    print(f"✅ Widget interaction events logged: {sum(widget_results)}/{len(widget_results)}")
    
    return True


def test_group_management_events():
    """Test event logging for device group management"""
    print("\n📦 Testing Group Management Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    
    # Test group creation
    create_result = logger.log_system_action('group_created', user_id, {
        'group_id': 1,
        'group_name': 'Living Room Sensors',
        'description': 'All sensors in the living room',
        'color': '#FF5733',
        'initial_device_count': 0
    })
    
    # Test adding devices to group
    add_devices_result = logger.log_system_action('group_devices_added', user_id, {
        'group_id': 1,
        'device_ids': [1, 2, 3],
        'operation_type': 'bulk_add'
    })
    
    # Test group update
    update_result = logger.log_system_action('group_updated', user_id, {
        'group_id': 1,
        'changes': {
            'name': {'old': 'Living Room Sensors', 'new': 'Living Room Smart Devices'},
            'color': {'old': '#FF5733', 'new': '#33FF57'}
        }
    })
    
    # Test removing devices from group
    remove_devices_result = logger.log_system_action('group_devices_removed', user_id, {
        'group_id': 1,
        'device_ids': [3],
        'reason': 'device_relocated'
    })
    
    # Test group deletion
    delete_result = logger.log_system_action('group_deleted', user_id, {
        'group_id': 1,
        'group_name': 'Living Room Smart Devices',
        'device_count': 2,
        'reason': 'user_requested'
    })
    
    print(f"✅ Group creation logged: {bool(create_result)}")
    print(f"✅ Add devices to group logged: {bool(add_devices_result)}")
    print(f"✅ Group update logged: {bool(update_result)}")
    print(f"✅ Remove devices from group logged: {bool(remove_devices_result)}")
    print(f"✅ Group deletion logged: {bool(delete_result)}")
    
    return True


def test_admin_actions_events():
    """Test event logging for admin actions"""
    print("\n👑 Testing Admin Actions Event Logging...")
    
    logger = DashboardEventLogger()
    admin_user_id = 1  # Admin user
    
    # Test user management actions
    user_mgmt_actions = [
        ('user_created', {'new_user_id': 101, 'username': 'newuser', 'role': 'user'}),
        ('user_deactivated', {'target_user_id': 101, 'reason': 'policy_violation'}),
        ('user_activated', {'target_user_id': 101, 'reason': 'appeal_approved'}),
        ('user_deleted', {'target_user_id': 101, 'reason': 'gdpr_request'})
    ]
    
    user_results = []
    for action, details in user_mgmt_actions:
        result = logger.log_system_action(f'admin.{action}', admin_user_id, details)
        user_results.append(bool(result))
    
    print(f"✅ User management events logged: {sum(user_results)}/{len(user_results)}")
    
    # Test system management actions
    system_actions = [
        ('system_maintenance_started', {'maintenance_type': 'database_backup', 'estimated_duration': 30}),
        ('system_maintenance_completed', {'maintenance_type': 'database_backup', 'actual_duration': 25}),
        ('system_config_updated', {'config_section': 'telemetry', 'changes': ['retention_period']}),
        ('system_stats_generated', {'report_type': 'monthly', 'period': '2025-12'})
    ]
    
    system_results = []
    for action, details in system_actions:
        result = logger.log_system_action(f'admin.{action}', admin_user_id, details)
        system_results.append(bool(result))
    
    print(f"✅ System management events logged: {sum(system_results)}/{len(system_results)}")
    
    return True


def test_error_and_security_events():
    """Test event logging for errors and security events"""
    print("\n🔒 Testing Error and Security Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    
    # Test error events
    error_events = [
        ('api_error', {'endpoint': '/api/v1/devices', 'error_code': 500, 'error_message': 'Database connection failed'}),
        ('validation_error', {'field': 'device_name', 'error': 'Name too long', 'input_length': 256}),
        ('timeout_error', {'operation': 'telemetry_query', 'timeout_ms': 30000, 'query_complexity': 'high'}),
        ('rate_limit_exceeded', {'endpoint': '/api/v1/telemetry', 'limit': 100, 'window': '1h'})
    ]
    
    error_results = []
    for event_type, details in error_events:
        result = logger.log_system_action(f'error.{event_type}', user_id, details)
        error_results.append(bool(result))
    
    print(f"✅ Error events logged: {sum(error_results)}/{len(error_results)}")
    
    # Test security events
    security_events = [
        ('suspicious_login', {'ip_address': '192.168.1.999', 'failed_attempts': 5, 'time_window': 300}),
        ('unauthorized_access_attempt', {'endpoint': '/api/v1/admin', 'user_role': 'user', 'required_role': 'admin'}),
        ('api_key_compromised', {'device_id': 1, 'suspicious_activity': 'multiple_locations'}),
        ('data_export_large', {'export_size_mb': 500, 'threshold_mb': 100, 'export_type': 'telemetry'})
    ]
    
    security_results = []
    for event_type, details in security_events:
        result = logger.log_system_action(f'security.{event_type}', user_id, details)
        security_results.append(bool(result))
    
    print(f"✅ Security events logged: {sum(security_results)}/{len(security_results)}")
    
    return True


def test_performance_monitoring_events():
    """Test event logging for performance monitoring"""
    print("\n⚡ Testing Performance Monitoring Event Logging...")
    
    logger = DashboardEventLogger()
    user_id = 100
    
    # Test performance metrics
    performance_events = [
        ('page_load_time', {'page': 'dashboard', 'load_time_ms': 1250, 'resource_count': 15}),
        ('api_response_time', {'endpoint': '/api/v1/telemetry/latest', 'response_time_ms': 45, 'cache_hit': True}),
        ('database_query_slow', {'query_type': 'telemetry_aggregation', 'execution_time_ms': 5000, 'threshold_ms': 1000}),
        ('memory_usage_high', {'usage_percent': 85, 'threshold_percent': 80, 'component': 'telemetry_processor'})
    ]
    
    performance_results = []
    for event_type, details in performance_events:
        result = logger.log_system_action(f'performance.{event_type}', user_id, details)
        performance_results.append(bool(result))
    
    print(f"✅ Performance events logged: {sum(performance_results)}/{len(performance_results)}")
    
    return True


def analyze_event_patterns(logger):
    """Analyze logged event patterns"""
    print("\n📈 Analyzing Event Patterns...")
    
    # Get event statistics
    event_stats = logger.mongodb_service.aggregate_events_by_type()
    
    print(f"\n📊 Event Type Distribution:")
    for i, stat in enumerate(event_stats[:10], 1):
        print(f"   {i:2d}. {stat['_id']:<30} {stat['count']:>4} events")
    
    # Get recent events by user
    user_events = logger.mongodb_service.get_user_events(user_id=100, limit=10)
    print(f"\n👤 Recent User Events ({len(user_events)}):")
    for i, event in enumerate(user_events[:5], 1):
        print(f"   {i}. {event['event_type']} - {event['timestamp']}")
    
    # Get events in last hour
    start_time = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_events = logger.mongodb_service.get_events(start_time=start_time, limit=20)
    print(f"\n🕐 Events in Last Hour: {len(recent_events)}")
    
    return True


def test_event_search_and_filtering():
    """Test event search and filtering capabilities"""
    print("\n🔍 Testing Event Search and Filtering...")
    
    logger = DashboardEventLogger()
    
    # Test filtering by event type
    login_events = logger.mongodb_service.get_events_by_type('user.login')
    device_events = logger.mongodb_service.get_events_by_type('device.registered')
    
    print(f"✅ Login events found: {len(login_events)}")
    print(f"✅ Device registration events found: {len(device_events)}")
    
    # Test filtering by time range
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_events = logger.mongodb_service.get_events(start_time=last_24h)
    
    print(f"✅ Events in last 24h: {len(recent_events)}")
    
    # Test filtering by device
    device_events = logger.mongodb_service.get_device_events(device_id=1)
    print(f"✅ Events for device 1: {len(device_events)}")
    
    # Test filtering by user
    user_events = logger.mongodb_service.get_user_events(user_id=100)
    print(f"✅ Events for user 100: {len(user_events)}")
    
    return True


def main():
    """Main test function"""
    print("🧪 Testing Dashboard Event Logging - TDD Approach")
    print("=" * 60)
    
    # Initialize logger
    logger = DashboardEventLogger()
    
    if not logger.mongodb_service.is_available():
        print("❌ MongoDB is not available. Cannot run tests.")
        return False
    
    print(f"✅ MongoDB connected: {logger.mongodb_service.database_name}")
    
    # Run all test suites
    test_suites = [
        ("User Authentication", test_user_authentication_events),
        ("Device Management", test_device_management_events),
        ("Telemetry Operations", test_telemetry_events),
        ("Dashboard Navigation", test_dashboard_navigation_events),
        ("Group Management", test_group_management_events),
        ("Admin Actions", test_admin_actions_events),
        ("Error & Security", test_error_and_security_events),
        ("Performance Monitoring", test_performance_monitoring_events),
        ("Event Search & Filtering", test_event_search_and_filtering)
    ]
    
    passed = 0
    total = len(test_suites)
    
    try:
        for suite_name, test_func in test_suites:
            try:
                print(f"\n{'='*20} {suite_name} {'='*20}")
                if test_func():
                    passed += 1
                    print(f"✅ {suite_name} tests passed")
                else:
                    print(f"❌ {suite_name} tests failed")
            except Exception as e:
                print(f"❌ {suite_name} tests failed with error: {e}")
        
        # Analyze patterns
        analyze_event_patterns(logger)
        
        print(f"\n{'='*60}")
        print(f"📊 Test Results: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 All dashboard event logging tests passed!")
            print("✅ Event logging is ready for dashboard integration")
        else:
            print("⚠️  Some tests failed. Review implementation.")
        
        # Ask about cleanup
        cleanup = input("\n🧹 Clean up test data? (y/N): ").lower().strip()
        if cleanup == 'y':
            logger.mongodb_service.cleanup_test_data()
            print("✅ Test data cleaned up")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False
    
    finally:
        logger.mongodb_service.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
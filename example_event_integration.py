#!/usr/bin/env python3
"""
Example: Event Logging Integration
Shows how to integrate event logging into existing API routes
"""

from flask import Flask, request, jsonify, Blueprint
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from middleware.event_logging import (
    log_user_action, log_device_action, log_system_action, log_api_call,
    log_login, log_logout, log_device_registration, log_telemetry_received,
    log_error_event, log_performance_event
)

# Create example blueprint
example_bp = Blueprint('example', __name__, url_prefix='/api/v1/example')


# Example 1: User Authentication with Event Logging
@example_bp.route('/auth/login', methods=['POST'])
@log_user_action('login', {'method': 'api_endpoint'})
def login():
    """Example login endpoint with event logging"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Simulate authentication logic
    if username and password:
        user_id = 100  # Simulated user ID
        
        # Log successful login
        log_login(user_id, success=True, details={
            'username': username,
            'login_method': 'username_password'
        })
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'Login successful'
        }), 200
    else:
        # Log failed login
        log_login(None, success=False, details={
            'username': username,
            'reason': 'missing_credentials'
        })
        
        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401


# Example 2: Device Registration with Event Logging
@example_bp.route('/devices/register', methods=['POST'])
@log_device_action('registered', {'source': 'api'})
def register_device():
    """Example device registration with event logging"""
    data = request.get_json()
    user_id = int(request.headers.get('X-User-ID', 100))
    
    # Simulate device registration
    device_id = 123  # Simulated device ID
    device_name = data.get('name', 'Unknown Device')
    device_type = data.get('device_type', 'sensor')
    
    # Log device registration
    log_device_registration(user_id, device_id, {
        'device_name': device_name,
        'device_type': device_type,
        'location': data.get('location'),
        'firmware_version': data.get('firmware_version')
    })
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'message': 'Device registered successfully'
    }), 201


# Example 3: Telemetry Submission with Event Logging
@example_bp.route('/telemetry', methods=['POST'])
@log_api_call('telemetry.submitted', include_request_data=True)
def submit_telemetry():
    """Example telemetry submission with event logging"""
    data = request.get_json()
    device_id = 123  # From API key lookup
    user_id = 100   # From device ownership
    
    # Simulate telemetry processing
    telemetry_data = data.get('data', {})
    
    # Log telemetry received
    log_telemetry_received(user_id, device_id, {
        'measurements': list(telemetry_data.keys()),
        'data_points': len(telemetry_data),
        'timestamp': data.get('timestamp')
    })
    
    return jsonify({
        'success': True,
        'message': 'Telemetry data received'
    }), 200


# Example 4: Device Status Update with Event Logging
@example_bp.route('/devices/<int:device_id>/status', methods=['PUT'])
@log_device_action('status_updated')
def update_device_status(device_id):
    """Example device status update with event logging"""
    data = request.get_json()
    user_id = int(request.headers.get('X-User-ID', 100))
    
    old_status = 'active'  # Simulated current status
    new_status = data.get('status', 'active')
    
    # The decorator will automatically log the device action
    # Additional custom logging can be done here if needed
    
    return jsonify({
        'success': True,
        'device_id': device_id,
        'old_status': old_status,
        'new_status': new_status
    }), 200


# Example 5: User Dashboard Access with Event Logging
@example_bp.route('/dashboard', methods=['GET'])
@log_system_action('dashboard_accessed', {'page': 'main'})
def dashboard():
    """Example dashboard access with event logging"""
    user_id = int(request.headers.get('X-User-ID', 100))
    
    # Simulate dashboard data preparation
    dashboard_data = {
        'devices': 5,
        'active_alerts': 2,
        'recent_telemetry': 100
    }
    
    return jsonify({
        'success': True,
        'data': dashboard_data
    }), 200


# Example 6: Error Handling with Event Logging
@example_bp.route('/devices/<int:device_id>/error-demo', methods=['GET'])
def error_demo(device_id):
    """Example error handling with event logging"""
    user_id = int(request.headers.get('X-User-ID', 100))
    
    try:
        # Simulate an error condition
        if device_id == 999:
            raise ValueError("Device not found")
        
        return jsonify({'device_id': device_id, 'status': 'ok'}), 200
        
    except ValueError as e:
        # Log the error event
        log_error_event('device_not_found', {
            'device_id': device_id,
            'error_message': str(e)
        }, user_id=user_id)
        
        return jsonify({
            'success': False,
            'error': 'Device not found'
        }), 404


# Example 7: Performance Monitoring with Event Logging
@example_bp.route('/devices/<int:device_id>/analytics', methods=['GET'])
def device_analytics(device_id):
    """Example analytics endpoint with performance monitoring"""
    import time
    start_time = time.time()
    
    user_id = int(request.headers.get('X-User-ID', 100))
    
    # Simulate analytics processing
    time.sleep(0.1)  # Simulate processing time
    
    processing_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Log performance metric
    log_performance_event('analytics_processing_time', processing_time, 
                         threshold=100.0, user_id=user_id, 
                         details={'device_id': device_id})
    
    return jsonify({
        'device_id': device_id,
        'analytics': {'uptime': 99.5, 'avg_temp': 23.2},
        'processing_time_ms': processing_time
    }), 200


# Example 8: Bulk Operations with Event Logging
@example_bp.route('/devices/bulk-update', methods=['POST'])
@log_system_action('bulk_device_update')
def bulk_device_update():
    """Example bulk operation with event logging"""
    data = request.get_json()
    user_id = int(request.headers.get('X-User-ID', 100))
    device_ids = data.get('device_ids', [])
    
    # Simulate bulk update
    updated_count = len(device_ids)
    
    # The decorator logs the system action automatically
    # Additional details can be logged here
    
    return jsonify({
        'success': True,
        'updated_devices': updated_count,
        'device_ids': device_ids
    }), 200


def create_test_app():
    """Create a test Flask app with event logging examples"""
    app = Flask(__name__)
    app.register_blueprint(example_bp)
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Event Logging Integration Examples',
            'endpoints': [
                '/api/v1/example/auth/login',
                '/api/v1/example/devices/register',
                '/api/v1/example/telemetry',
                '/api/v1/example/devices/<id>/status',
                '/api/v1/example/dashboard',
                '/api/v1/example/devices/<id>/error-demo',
                '/api/v1/example/devices/<id>/analytics',
                '/api/v1/example/devices/bulk-update'
            ]
        })
    
    return app


def test_integration():
    """Test the event logging integration"""
    print("🧪 Testing Event Logging Integration Examples")
    print("=" * 50)
    
    app = create_test_app()
    
    with app.test_client() as client:
        # Test 1: Login
        print("\n1. Testing Login Event Logging...")
        response = client.post('/api/v1/example/auth/login', 
                             json={'username': 'testuser', 'password': 'password'},
                             headers={'X-User-ID': '100'})
        print(f"   Login response: {response.status_code}")
        
        # Test 2: Device Registration
        print("\n2. Testing Device Registration Event Logging...")
        response = client.post('/api/v1/example/devices/register',
                             json={'name': 'Test Sensor', 'device_type': 'temperature'},
                             headers={'X-User-ID': '100'})
        print(f"   Device registration response: {response.status_code}")
        
        # Test 3: Telemetry Submission
        print("\n3. Testing Telemetry Event Logging...")
        response = client.post('/api/v1/example/telemetry',
                             json={'data': {'temperature': 23.5, 'humidity': 65}},
                             headers={'X-API-Key': 'device123'})
        print(f"   Telemetry response: {response.status_code}")
        
        # Test 4: Dashboard Access
        print("\n4. Testing Dashboard Access Event Logging...")
        response = client.get('/api/v1/example/dashboard',
                            headers={'X-User-ID': '100'})
        print(f"   Dashboard response: {response.status_code}")
        
        # Test 5: Error Handling
        print("\n5. Testing Error Event Logging...")
        response = client.get('/api/v1/example/devices/999/error-demo',
                            headers={'X-User-ID': '100'})
        print(f"   Error demo response: {response.status_code}")
        
        # Test 6: Performance Monitoring
        print("\n6. Testing Performance Event Logging...")
        response = client.get('/api/v1/example/devices/123/analytics',
                            headers={'X-User-ID': '100'})
        print(f"   Analytics response: {response.status_code}")
        
        print("\n✅ All integration tests completed!")
        print("📝 Events have been logged to MongoDB")
        print("🔍 Check MongoDB logs collection to verify events")


if __name__ == "__main__":
    test_integration()
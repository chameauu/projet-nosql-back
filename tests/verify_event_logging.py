#!/usr/bin/env python3
"""
Verify Event Logging Integration
"""

import sys
import os
import requests
import time
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.mongodb_service import MongoDBService

def test_complete_flow():
    """Test the complete event logging flow"""
    print("🧪 Testing Complete Event Logging Flow")
    print("=" * 50)
    
    # Initialize MongoDB service
    mongodb = MongoDBService()
    
    if not mongodb.is_available():
        print("❌ MongoDB not available - skipping test")
        return
    
    print("✅ MongoDB is available")
    
    # Get initial event count
    initial_count = mongodb.db.logs.count_documents({})
    print(f"Initial event count: {initial_count}")
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    
    user_data = {
        'username': f'verify_test_{int(time.time())}',
        'email': f'verify_{int(time.time())}@test.com',
        'password': 'test123'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/v1/auth/register',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            print("✅ User registration successful")
            user_info = response.json()
            user_id = user_info['user']['user_id']
            print(f"   User ID: {user_id}")
            
            # Wait a moment for event logging
            time.sleep(0.5)
            
            # Check for registration event
            reg_events = list(mongodb.db.logs.find({
                'event_type': 'user.registered',
                'user_id': user_id
            }))
            
            if reg_events:
                print("✅ Registration event found in MongoDB!")
                event = reg_events[0]
                print(f"   Event details: {event.get('details', {})}")
            else:
                print("❌ Registration event NOT found in MongoDB")
                
                # Check all recent events
                recent_events = list(mongodb.db.logs.find().sort('timestamp', -1).limit(5))
                print(f"   Recent events ({len(recent_events)}):")
                for event in recent_events:
                    print(f"     - {event.get('event_type')} at {event.get('timestamp')}")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during user registration: {e}")
    
    # Test 2: Register a device
    print("\n2. Testing device registration...")
    
    if 'user_id' in locals():
        device_data = {
            'name': f'Verify Device {int(time.time())}',
            'device_type': 'sensor',
            'location': 'Test Lab'
        }
        
        try:
            response = requests.post(
                'http://localhost:5000/api/v1/devices/register',
                json=device_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-User-ID': user_id
                }
            )
            
            if response.status_code == 201:
                print("✅ Device registration successful")
                device_info = response.json()
                device_id = device_info['device']['id']
                api_key = device_info['device']['api_key']
                print(f"   Device ID: {device_id}")
                
                # Wait a moment for event logging
                time.sleep(0.5)
                
                # Check for device registration event
                dev_events = list(mongodb.db.logs.find({
                    'event_type': 'device.registered',
                    'device_id': device_id
                }))
                
                if dev_events:
                    print("✅ Device registration event found in MongoDB!")
                    event = dev_events[0]
                    print(f"   Event details: {event.get('details', {})}")
                else:
                    print("❌ Device registration event NOT found in MongoDB")
                
                # Test 3: Submit telemetry
                print("\n3. Testing telemetry submission...")
                
                telemetry_data = {
                    'data': {
                        'temperature': 25.5,
                        'humidity': 60.0
                    }
                }
                
                try:
                    response = requests.post(
                        'http://localhost:5000/api/v1/telemetry',
                        json=telemetry_data,
                        headers={
                            'Content-Type': 'application/json',
                            'X-API-Key': api_key
                        }
                    )
                    
                    if response.status_code == 201:
                        print("✅ Telemetry submission successful")
                        
                        # Wait a moment for event logging
                        time.sleep(0.5)
                        
                        # Check for telemetry event
                        tel_events = list(mongodb.db.logs.find({
                            'event_type': 'telemetry.submitted',
                            'device_id': device_id
                        }))
                        
                        if tel_events:
                            print("✅ Telemetry event found in MongoDB!")
                            event = tel_events[0]
                            print(f"   Event details: {event.get('details', {})}")
                        else:
                            print("❌ Telemetry event NOT found in MongoDB")
                    else:
                        print(f"❌ Telemetry submission failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                        
                except Exception as e:
                    print(f"❌ Error during telemetry submission: {e}")
                    
            else:
                print(f"❌ Device registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during device registration: {e}")
    
    # Final summary
    print("\n" + "=" * 50)
    final_count = mongodb.db.logs.count_documents({})
    new_events = final_count - initial_count
    print(f"Final event count: {final_count}")
    print(f"New events created: {new_events}")
    
    if new_events > 0:
        print("✅ Event logging system is working!")
    else:
        print("❌ No new events were created")
    
    # Show recent events
    print("\nRecent events:")
    recent_events = list(mongodb.db.logs.find().sort('timestamp', -1).limit(5))
    for i, event in enumerate(recent_events, 1):
        print(f"  {i}. {event.get('event_type')} at {event.get('timestamp')}")
        if event.get('details'):
            print(f"     Details: {event.get('details')}")

if __name__ == '__main__':
    test_complete_flow()
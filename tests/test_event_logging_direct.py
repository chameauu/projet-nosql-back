#!/usr/bin/env python3
"""
Direct test of event logging functionality
"""

import sys
import os
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.mongodb_service import MongoDBService
from src.middleware.event_logging import EventLogger

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    
    mongodb_service = MongoDBService()
    
    if mongodb_service.is_available():
        print("✅ MongoDB is available")
        
        # Test logging an event
        test_event = {
            'event_type': 'test.connection',
            'timestamp': datetime.now(timezone.utc),
            'details': {'test': True}
        }
        
        result = mongodb_service.log_event(test_event)
        if result:
            print("✅ Event logged successfully:", result)
        else:
            print("❌ Failed to log event")
            
        # Check if event was stored
        events = mongodb_service.get_events_by_type('test.connection')
        print(f"✅ Found {len(events)} test events")
        
    else:
        print("❌ MongoDB is not available")

def test_event_logger():
    """Test EventLogger class"""
    print("\nTesting EventLogger...")
    
    event_logger = EventLogger()
    
    # Test user event
    result = event_logger.log_user_event('test', {
        'user_id': 'test123',
        'username': 'test_user'
    })
    
    if result:
        print("✅ User event logged successfully")
    else:
        print("❌ Failed to log user event")
    
    # Test device event
    result = event_logger.log_device_event('test', {
        'device_id': 1,
        'user_id': 'test123',
        'name': 'Test Device'
    })
    
    if result:
        print("✅ Device event logged successfully")
    else:
        print("❌ Failed to log device event")

def check_existing_events():
    """Check for existing events in MongoDB"""
    print("\nChecking existing events...")
    
    mongodb_service = MongoDBService()
    
    if mongodb_service.is_available():
        # Check total events
        try:
            # Use the db directly to count documents
            total_events = mongodb_service.db.logs.count_documents({})
            print(f"Total events in database: {total_events}")
            
            # Get recent events
            recent_events = list(mongodb_service.db.logs.find().sort("timestamp", -1).limit(5))
            print(f"Recent events: {len(recent_events)}")
            
            for event in recent_events:
                print(f"  - {event.get('event_type', 'unknown')} at {event.get('timestamp', 'unknown')}")
                
        except Exception as e:
            print(f"Error checking events: {e}")
    else:
        print("MongoDB not available")

if __name__ == '__main__':
    print("🧪 Testing Event Logging System")
    print("=" * 50)
    
    test_mongodb_connection()
    test_event_logger()
    check_existing_events()
    
    print("\n" + "=" * 50)
    print("✅ Event logging test complete!")
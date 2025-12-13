"""
MongoDB Service - Simplified
Handles only logs and alerts collections (no authentication)
"""

import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from bson import ObjectId

logger = logging.getLogger(__name__)


class MongoDBService:
    """Simplified service for managing logs and alerts in MongoDB"""
    
    def __init__(self):
        """Initialize MongoDB connection (no authentication)"""
        self.uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/iotflow')
        self.database_name = os.getenv('MONGODB_DATABASE', 'iotflow')
        
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            # Ensure indexes
            self._ensure_indexes()
            
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def _ensure_indexes(self):
        """Ensure indexes exist for logs and alerts only"""
        try:
            # Event logs indexes
            self.db.logs.create_index([("device_id", ASCENDING), ("timestamp", DESCENDING)])
            self.db.logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            self.db.logs.create_index([("event_type", ASCENDING), ("timestamp", DESCENDING)])
            self.db.logs.create_index([("timestamp", DESCENDING)])
            
            # Alerts indexes
            self.db.alerts.create_index([("device_id", ASCENDING), ("status", ASCENDING)])
            self.db.alerts.create_index([("severity", ASCENDING), ("created_at", DESCENDING)])
            self.db.alerts.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
            
            logger.info("MongoDB indexes ensured for logs and alerts")
        except Exception as e:
            logger.error(f"Error ensuring indexes: {e}")
    
    def is_available(self) -> bool:
        """Check if MongoDB is available"""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB not available: {e}")
            return False
    
    # Event Logging
    
    def log_event(self, event: Dict) -> Optional[Dict]:
        """Log an event to the logs collection"""
        try:
            event['timestamp'] = event.get('timestamp', datetime.now(timezone.utc))
            
            result = self.db.logs.insert_one(event)
            return {'event_id': str(result.inserted_id)}
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return None
    
    def log_bulk_events(self, events: List[Dict]) -> bool:
        """Log multiple events efficiently"""
        try:
            if not events:
                return True
            
            # Ensure all events have timestamps
            for event in events:
                event['timestamp'] = event.get('timestamp', datetime.now(timezone.utc))
            
            result = self.db.logs.insert_many(events)
            return len(result.inserted_ids) == len(events)
        except Exception as e:
            logger.error(f"Error logging bulk events: {e}")
            return False
    
    def get_device_events(self, device_id: int, limit: int = 100) -> List[Dict]:
        """Get device events from logs"""
        try:
            events = list(self.db.logs.find(
                {"device_id": device_id}
            ).sort("timestamp", DESCENDING).limit(limit))
            
            for event in events:
                event['_id'] = str(event['_id'])
            return events
        except Exception as e:
            logger.error(f"Error getting device events: {e}")
            return []
    
    def get_user_events(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user events from logs"""
        try:
            events = list(self.db.logs.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit))
            
            for event in events:
                event['_id'] = str(event['_id'])
            return events
        except Exception as e:
            logger.error(f"Error getting user events: {e}")
            return []
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict]:
        """Get events by type from logs"""
        try:
            events = list(self.db.logs.find(
                {"event_type": event_type}
            ).sort("timestamp", DESCENDING).limit(limit))
            
            for event in events:
                event['_id'] = str(event['_id'])
            return events
        except Exception as e:
            logger.error(f"Error getting events by type: {e}")
            return []
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get events within time range from logs"""
        try:
            query = {}
            if start_time or end_time:
                query['timestamp'] = {}
                if start_time:
                    query['timestamp']['$gte'] = start_time
                if end_time:
                    query['timestamp']['$lte'] = end_time
            
            events = list(self.db.logs.find(query).sort("timestamp", DESCENDING).limit(limit))
            
            for event in events:
                event['_id'] = str(event['_id'])
            return events
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    # Alert Management
    
    def create_alert(self, alert: Dict) -> Optional[Dict]:
        """Create an alert"""
        try:
            alert['created_at'] = datetime.now(timezone.utc)
            alert['acknowledged'] = alert.get('acknowledged', False)
            alert['status'] = alert.get('status', 'active')
            
            result = self.db.alerts.insert_one(alert)
            return {'alert_id': str(result.inserted_id)}
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None
    
    def get_alert(self, alert_id: str) -> Optional[Dict]:
        """Get alert by ID"""
        try:
            if not ObjectId.is_valid(alert_id):
                return None
            
            alert = self.db.alerts.find_one({"_id": ObjectId(alert_id)})
            if alert:
                alert['_id'] = str(alert['_id'])
            return alert
        except Exception as e:
            logger.error(f"Error getting alert: {e}")
            return None
    
    def get_device_alerts(self, device_id: int, limit: int = 100) -> List[Dict]:
        """Get device alerts"""
        try:
            alerts = list(self.db.alerts.find(
                {"device_id": device_id}
            ).sort("created_at", DESCENDING).limit(limit))
            
            for alert in alerts:
                alert['_id'] = str(alert['_id'])
            return alerts
        except Exception as e:
            logger.error(f"Error getting device alerts: {e}")
            return []
    
    def get_active_alerts(self, limit: int = 100) -> List[Dict]:
        """Get active alerts"""
        try:
            alerts = list(self.db.alerts.find(
                {"status": "active"}
            ).sort("created_at", DESCENDING).limit(limit))
            
            for alert in alerts:
                alert['_id'] = str(alert['_id'])
            return alerts
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            if not ObjectId.is_valid(alert_id):
                return False
            
            result = self.db.alerts.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": {"acknowledged": True, "acknowledged_at": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            if not ObjectId.is_valid(alert_id):
                return False
            
            result = self.db.alerts.update_one(
                {"_id": ObjectId(alert_id)},
                {"$set": {"status": "resolved", "resolved_at": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    def get_alerts_by_severity(self, severity: str, limit: int = 100) -> List[Dict]:
        """Get alerts by severity"""
        try:
            alerts = list(self.db.alerts.find(
                {"severity": severity}
            ).sort("created_at", DESCENDING).limit(limit))
            
            for alert in alerts:
                alert['_id'] = str(alert['_id'])
            return alerts
        except Exception as e:
            logger.error(f"Error getting alerts by severity: {e}")
            return []
    
    # Utility Methods
    
    def aggregate_alerts_by_severity(self) -> List[Dict]:
        """Aggregate alerts by severity"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            return list(self.db.alerts.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error aggregating alerts by severity: {e}")
            return []
    
    def aggregate_events_by_type(self) -> List[Dict]:
        """Aggregate events by type"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            return list(self.db.logs.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error aggregating events by type: {e}")
            return []
    
    def bulk_insert_events(self, events: List[Dict]) -> bool:
        """Bulk insert events"""
        try:
            for event in events:
                event['timestamp'] = event.get('timestamp', datetime.now(timezone.utc))
            
            self.db.logs.insert_many(events)
            return True
        except Exception as e:
            logger.error(f"Error bulk inserting events: {e}")
            return False
    
    def cleanup_test_data(self):
        """Cleanup test data (logs and alerts only)"""
        try:
            self.db.logs.delete_many({})
            self.db.alerts.delete_many({})
            logger.info("Test data cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up test data: {e}")
    
    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()

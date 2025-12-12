# 📊 MongoDB Queries Reference - IoTFlow Project

**Database**: `iotflow`  
**Authentication**: Required (`iotflow:iotflowpass`)  
**Collections**: 6 main collections for event logging and analytics

---

## 🔧 Connection Commands

### Basic Connection
```bash
# Connect to MongoDB with authentication
docker exec -it iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin

# One-line query execution
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "QUERY_HERE"
```

### Database Selection
```javascript
// Switch to iotflow database
use iotflow;

// Show current database
db.getName();

// List all collections
show collections;
db.getCollectionNames();
```

---

## 📋 Database Overview Queries

### 1. Database Statistics
```javascript
// Database stats
db.stats();

// Collection counts
db.getCollectionNames().forEach(function(collection) {
    print(collection + ': ' + db[collection].countDocuments());
});

// Database size info
db.runCommand({dbStats: 1, scale: 1024*1024}); // Size in MB
```

### 2. Collection Information
```javascript
// List all collections with details
db.runCommand("listCollections").cursor.firstBatch.forEach(
    function(collection) {
        print("Collection: " + collection.name);
    }
);

// Get collection stats
db.event_logs.stats();
db.device_configs.stats();
```

---

## 📝 Event Logs Collection Queries

### Basic Event Queries
```javascript
// Count all events
db.event_logs.countDocuments();

// Get latest 10 events
db.event_logs.find().sort({timestamp: -1}).limit(10).pretty();

// Get all event types
db.event_logs.distinct("event_type");

// Count events by type
db.event_logs.aggregate([
    {$group: {_id: "$event_type", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);
```

### Device-Specific Events
```javascript
// Events for specific device
db.event_logs.find({device_id: 1}).sort({timestamp: -1}).pretty();

// Count events per device
db.event_logs.aggregate([
    {$group: {_id: "$device_id", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// Latest event per device
db.event_logs.aggregate([
    {$sort: {device_id: 1, timestamp: -1}},
    {$group: {
        _id: "$device_id",
        latest_event: {$first: "$$ROOT"}
    }}
]);
```

### User-Specific Events
```javascript
// Events for specific user
db.event_logs.find({user_id: 4}).sort({timestamp: -1}).pretty();

// Count events per user
db.event_logs.aggregate([
    {$group: {_id: "$user_id", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// User activity summary
db.event_logs.aggregate([
    {$match: {user_id: {$exists: true}}},
    {$group: {
        _id: "$user_id",
        total_events: {$sum: 1},
        event_types: {$addToSet: "$event_type"},
        first_activity: {$min: "$timestamp"},
        last_activity: {$max: "$timestamp"}
    }}
]);
```

### Time-Based Event Queries
```javascript
// Events from last hour
db.event_logs.find({
    timestamp: {$gte: new Date(Date.now() - 60*60*1000)}
}).sort({timestamp: -1});

// Events from last 24 hours
db.event_logs.find({
    timestamp: {$gte: new Date(Date.now() - 24*60*60*1000)}
}).sort({timestamp: -1});

// Events from specific date range
db.event_logs.find({
    timestamp: {
        $gte: ISODate("2025-12-12T00:00:00Z"),
        $lte: ISODate("2025-12-12T23:59:59Z")
    }
}).sort({timestamp: -1});

// Events by hour of day
db.event_logs.aggregate([
    {$group: {
        _id: {$hour: "$timestamp"},
        count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
]);
```

### Event Type Analysis
```javascript
// Telemetry submission events
db.event_logs.find({event_type: "telemetry.submitted"}).count();

// Device registration events
db.event_logs.find({event_type: "device.registered"}).pretty();

// User registration events
db.event_logs.find({event_type: "user.registered"}).pretty();

// Group creation events
db.event_logs.find({event_type: "group.created"}).pretty();

// Error events (if any)
db.event_logs.find({event_type: {$regex: "error"}}).pretty();
```

---

## ⚙️ Device Configs Collection Queries

### Basic Config Queries
```javascript
// Count all device configs
db.device_configs.countDocuments();

// Get all device configs
db.device_configs.find().pretty();

// Get config for specific device
db.device_configs.findOne({device_id: 1});

// Get configs for specific user
db.device_configs.find({user_id: 4}).pretty();
```

### Config Analysis
```javascript
// Latest config updates
db.device_configs.find().sort({updated_at: -1}).limit(5).pretty();

// Configs by version
db.device_configs.aggregate([
    {$group: {_id: "$config_version", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// Devices with custom settings
db.device_configs.find({settings: {$exists: true, $ne: {}}}).pretty();
```

---

## 🚨 Alerts Collection Queries

### Basic Alert Queries
```javascript
// Count all alerts
db.alerts.countDocuments();

// Get all active alerts
db.alerts.find({status: "active"}).sort({created_at: -1}).pretty();

// Get alerts by severity
db.alerts.find({severity: "critical"}).pretty();
db.alerts.find({severity: "warning"}).pretty();

// Unacknowledged alerts
db.alerts.find({acknowledged: false}).sort({created_at: -1}).pretty();
```

### Alert Analysis
```javascript
// Alerts by severity count
db.alerts.aggregate([
    {$group: {_id: "$severity", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// Alerts by device
db.alerts.aggregate([
    {$group: {_id: "$device_id", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// Alert resolution time analysis
db.alerts.aggregate([
    {$match: {status: "resolved", resolved_at: {$exists: true}}},
    {$project: {
        device_id: 1,
        resolution_time: {
            $subtract: ["$resolved_at", "$created_at"]
        }
    }},
    {$group: {
        _id: null,
        avg_resolution_time: {$avg: "$resolution_time"},
        min_resolution_time: {$min: "$resolution_time"},
        max_resolution_time: {$max: "$resolution_time"}
    }}
]);
```

---

## 📊 Analytics Collection Queries

### Basic Analytics Queries
```javascript
// Count all analytics reports
db.analytics.countDocuments();

// Latest analytics reports
db.analytics.find().sort({generated_at: -1}).limit(10).pretty();

// Reports by type
db.analytics.aggregate([
    {$group: {_id: "$report_type", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);

// Reports for specific device
db.analytics.find({device_id: 1}).sort({generated_at: -1}).pretty();
```

---

## 👤 User Preferences Collection Queries

### Basic Preferences Queries
```javascript
// Count user preferences
db.user_preferences.countDocuments();

// Get all user preferences
db.user_preferences.find().pretty();

// Get preferences for specific user
db.user_preferences.findOne({user_id: 4});

// Users with custom preferences
db.user_preferences.find({
    $or: [
        {theme: {$exists: true}},
        {notifications: {$exists: true}},
        {dashboard_layout: {$exists: true}}
    ]
}).pretty();
```

---

## 🏷️ Device Metadata Collection Queries

### Basic Metadata Queries
```javascript
// Count device metadata entries
db.device_metadata.countDocuments();

// Get all device metadata
db.device_metadata.find().pretty();

// Get metadata for specific device
db.device_metadata.findOne({device_id: 1});

// Devices with tags
db.device_metadata.find({tags: {$exists: true, $ne: []}}).pretty();
```

### Tag-Based Queries
```javascript
// Find devices by tag
db.device_metadata.find({tags: "sensor"}).pretty();
db.device_metadata.find({tags: "living-room"}).pretty();

// All unique tags
db.device_metadata.distinct("tags");

// Tag usage count
db.device_metadata.aggregate([
    {$unwind: "$tags"},
    {$group: {_id: "$tags", count: {$sum: 1}}},
    {$sort: {count: -1}}
]);
```

### Location-Based Queries
```javascript
// Devices with location data
db.device_metadata.find({
    "location.coordinates": {$exists: true}
}).pretty();

// Devices near a point (requires 2dsphere index)
db.device_metadata.find({
    location: {
        $near: {
            $geometry: {type: "Point", coordinates: [2.3522, 48.8566]}, // Paris
            $maxDistance: 1000 // 1km
        }
    }
});
```

---

## 🔍 Advanced Aggregation Queries

### Cross-Collection Analysis
```javascript
// Device activity summary (events + metadata)
db.event_logs.aggregate([
    {$match: {device_id: {$exists: true}}},
    {$group: {
        _id: "$device_id",
        total_events: {$sum: 1},
        event_types: {$addToSet: "$event_type"},
        first_seen: {$min: "$timestamp"},
        last_seen: {$max: "$timestamp"}
    }},
    {$lookup: {
        from: "device_metadata",
        localField: "_id",
        foreignField: "device_id",
        as: "metadata"
    }},
    {$sort: {total_events: -1}}
]);

// User engagement analysis
db.event_logs.aggregate([
    {$match: {user_id: {$exists: true}}},
    {$group: {
        _id: "$user_id",
        total_events: {$sum: 1},
        unique_devices: {$addToSet: "$device_id"},
        activity_span: {
            $subtract: [
                {$max: "$timestamp"},
                {$min: "$timestamp"}
            ]
        }
    }},
    {$project: {
        user_id: "$_id",
        total_events: 1,
        device_count: {$size: "$unique_devices"},
        activity_days: {
            $divide: ["$activity_span", 1000*60*60*24]
        }
    }},
    {$sort: {total_events: -1}}
]);
```

### Time-Series Analysis
```javascript
// Events per day for last 30 days
db.event_logs.aggregate([
    {$match: {
        timestamp: {$gte: new Date(Date.now() - 30*24*60*60*1000)}
    }},
    {$group: {
        _id: {
            year: {$year: "$timestamp"},
            month: {$month: "$timestamp"},
            day: {$dayOfMonth: "$timestamp"}
        },
        count: {$sum: 1}
    }},
    {$sort: {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
]);

// Hourly activity pattern
db.event_logs.aggregate([
    {$group: {
        _id: {$hour: "$timestamp"},
        count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
]);

// Weekly activity pattern
db.event_logs.aggregate([
    {$group: {
        _id: {$dayOfWeek: "$timestamp"}, // 1=Sunday, 7=Saturday
        count: {$sum: 1}
    }},
    {$sort: {_id: 1}}
]);
```

---

## 🛠️ Data Management Queries

### Insert Sample Data
```javascript
// Insert sample event
db.event_logs.insertOne({
    event_type: "test.event",
    device_id: 999,
    user_id: 999,
    timestamp: new Date(),
    details: {
        message: "Test event for verification",
        source: "manual_query"
    }
});

// Insert sample device config
db.device_configs.insertOne({
    device_id: 999,
    user_id: 999,
    config_version: "1.0.0",
    settings: {
        sampling_rate: 60,
        enabled: true
    },
    created_at: new Date(),
    updated_at: new Date()
});
```

### Update Operations
```javascript
// Update event details
db.event_logs.updateOne(
    {device_id: 999},
    {$set: {details: {updated: true, timestamp: new Date()}}}
);

// Add tag to device metadata
db.device_metadata.updateOne(
    {device_id: 1},
    {$addToSet: {tags: "production"}}
);

// Remove tag from device metadata
db.device_metadata.updateOne(
    {device_id: 1},
    {$pull: {tags: "test"}}
);
```

### Cleanup Operations
```javascript
// Delete test data
db.event_logs.deleteMany({device_id: 999});
db.device_configs.deleteMany({device_id: 999});

// Delete old events (older than 90 days)
db.event_logs.deleteMany({
    timestamp: {$lt: new Date(Date.now() - 90*24*60*60*1000)}
});

// Clean up empty documents
db.device_configs.deleteMany({settings: {}});
```

---

## 📈 Performance and Monitoring Queries

### Index Information
```javascript
// List indexes for each collection
db.event_logs.getIndexes();
db.device_configs.getIndexes();
db.alerts.getIndexes();

// Index usage statistics
db.event_logs.aggregate([{$indexStats: {}}]);
```

### Performance Analysis
```javascript
// Explain query performance
db.event_logs.find({device_id: 1}).explain("executionStats");

// Collection statistics
db.event_logs.stats();

// Database profiling (enable first)
db.setProfilingLevel(2); // Profile all operations
db.system.profile.find().limit(5).sort({ts: -1}).pretty();
db.setProfilingLevel(0); // Disable profiling
```

---

## 🔧 Maintenance Commands

### Backup and Restore
```bash
# Backup specific collections
docker exec iotflow_mongodb mongodump -u iotflow -p iotflowpass --authenticationDatabase admin -d iotflow -c event_logs

# Backup entire database
docker exec iotflow_mongodb mongodump -u iotflow -p iotflowpass --authenticationDatabase admin -d iotflow

# Restore from backup
docker exec iotflow_mongodb mongorestore -u iotflow -p iotflowpass --authenticationDatabase admin -d iotflow /path/to/backup
```

### Database Maintenance
```javascript
// Compact collections (reclaim space)
db.runCommand({compact: "event_logs"});

// Repair database
db.repairDatabase();

// Get database repair info
db.runCommand({dbStats: 1});
```

---

## 🎯 Quick Reference Commands

### Most Useful Queries
```bash
# Quick stats
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('=== IoTFlow MongoDB Stats ===');
print('Event Logs:', db.event_logs.countDocuments());
print('Device Configs:', db.device_configs.countDocuments());
print('Alerts:', db.alerts.countDocuments());
print('Analytics:', db.analytics.countDocuments());
print('User Preferences:', db.user_preferences.countDocuments());
print('Device Metadata:', db.device_metadata.countDocuments());
"

# Latest activity
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('=== Latest Events ===');
db.event_logs.find().sort({timestamp: -1}).limit(5).forEach(function(doc) {
    print(doc.timestamp + ' - ' + doc.event_type + ' (Device: ' + doc.device_id + ')');
});
"

# System health check
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('=== System Health ===');
print('Database:', db.getName());
print('Collections:', db.getCollectionNames().length);
print('Total Documents:', 
    db.event_logs.countDocuments() + 
    db.device_configs.countDocuments() + 
    db.alerts.countDocuments()
);
"
```

---

## 📚 Additional Resources

### MongoDB Documentation
- [MongoDB Query Reference](https://docs.mongodb.com/manual/reference/operator/query/)
- [Aggregation Pipeline](https://docs.mongodb.com/manual/aggregation/)
- [Index Documentation](https://docs.mongodb.com/manual/indexes/)

### IoTFlow Specific
- See `src/services/mongodb_service.py` for application-level operations
- Check `scripts/mongo-init.js` for collection schemas
- Review `docker-compose.yml` for connection configuration

---

**Last Updated**: December 12, 2025  
**MongoDB Version**: 7.0  
**Authentication**: Required (iotflow:iotflowpass)
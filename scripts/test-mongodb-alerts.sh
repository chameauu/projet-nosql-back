#!/bin/bash

echo "🧪 Testing MongoDB Alert Insertion"
echo "=================================="

# Test 1: Insert a simple alert that matches the schema
echo "1. Testing simple alert insertion..."
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
db.alerts.insertOne({
    device_id: NumberInt(999),
    user_id: NumberInt(999),
    alert_type: 'threshold_exceeded',
    severity: 'warning',
    status: 'active',
    message: 'Test alert - temperature threshold exceeded',
    details: {
        threshold: 30.0,
        current_value: 32.5,
        measurement: 'temperature'
    },
    acknowledged: false,
    created_at: new Date()
});
print('✓ Simple alert inserted');
"

# Test 2: Check if alert was inserted
echo "2. Verifying alert insertion..."
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
print('Total alerts:', db.alerts.countDocuments());
db.alerts.find({device_id: 999}).forEach(function(doc) {
    print('Found alert:', doc.alert_type, '(' + doc.severity + ')');
});
"

# Test 3: Insert multiple alerts
echo "3. Inserting multiple test alerts..."
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
var alerts = [
    {
        device_id: NumberInt(1001),
        user_id: NumberInt(1),
        alert_type: 'device_offline',
        severity: 'error',
        status: 'active',
        message: 'Device has gone offline',
        acknowledged: false,
        created_at: new Date()
    },
    {
        device_id: NumberInt(1002),
        user_id: NumberInt(1),
        alert_type: 'anomaly',
        severity: 'critical',
        status: 'active',
        message: 'Anomalous readings detected',
        acknowledged: false,
        created_at: new Date()
    },
    {
        device_id: NumberInt(1003),
        user_id: NumberInt(1),
        alert_type: 'maintenance',
        severity: 'info',
        status: 'resolved',
        message: 'Scheduled maintenance completed',
        acknowledged: true,
        created_at: new Date(),
        resolved_at: new Date()
    }
];

db.alerts.insertMany(alerts);
print('✓ Multiple alerts inserted');
"

# Test 4: Final verification
echo "4. Final verification..."
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
print('=== Alert Summary ===');
print('Total alerts:', db.alerts.countDocuments());
print('Active alerts:', db.alerts.countDocuments({status: 'active'}));
print('Resolved alerts:', db.alerts.countDocuments({status: 'resolved'}));
print('');
print('Alerts by severity:');
db.alerts.aggregate([
    {\$group: {_id: '\$severity', count: {\$sum: 1}}},
    {\$sort: {count: -1}}
]).forEach(function(doc) {
    print('  ' + doc._id + ': ' + doc.count);
});
print('');
print('Sample alerts:');
db.alerts.find({}, {alert_type: 1, severity: 1, message: 1, status: 1}).limit(5).forEach(function(doc) {
    print('- ' + doc.alert_type + ' (' + doc.severity + ', ' + doc.status + '): ' + doc.message);
});
"

echo ""
echo "🎉 MongoDB alert testing complete!"
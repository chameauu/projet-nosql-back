#!/bin/bash

echo "📊 MongoDB Quick Stats - IoTFlow"
echo "================================"

# Collection counts
echo "📁 Collection Counts:"
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
db.getCollectionNames().forEach(function(collection) {
    print('   ' + collection + ': ' + db[collection].countDocuments());
});
"

echo ""
echo "📈 Latest Activity:"
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
print('   Recent Events:');
db.event_logs.find().sort({timestamp: -1}).limit(5).forEach(function(doc) {
    print('   - ' + doc.event_type + ' (Device: ' + doc.device_id + ')');
});
"

echo ""
echo "🏷️ Event Types:"
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
var types = db.event_logs.distinct('event_type');
types.forEach(function(type) {
    var count = db.event_logs.countDocuments({event_type: type});
    print('   - ' + type + ': ' + count);
});
"

echo ""
echo "📊 Database Size:"
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin iotflow --eval "
var stats = db.stats();
print('   Storage Size: ' + Math.round(stats.storageSize / 1024) + ' KB');
print('   Data Size: ' + Math.round(stats.dataSize / 1024) + ' KB');
print('   Index Size: ' + Math.round(stats.indexSize / 1024) + ' KB');
"
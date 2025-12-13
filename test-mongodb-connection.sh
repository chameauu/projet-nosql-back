#!/bin/bash

echo "=== Testing MongoDB Connection ==="

# Check if MongoDB container is running
echo "1. Checking MongoDB container status..."
docker ps | grep mongodb

# Test basic MongoDB connection
echo "2. Testing basic MongoDB connection..."
docker exec iotflow_mongodb mongosh --eval "print('MongoDB connection successful')"

# Test database access
echo "3. Testing database access..."
docker exec iotflow_mongodb mongosh --eval "
use iotflow;
print('Using database: ' + db.getName());
"

# Test collection operations
echo "4. Testing collection operations..."
docker exec iotflow_mongodb mongosh --eval "
use iotflow;
print('Collections in database:');
db.getCollectionNames().forEach(function(name) { print('  - ' + name); });
"

# Test insert and query
echo "5. Testing insert and query operations..."
docker exec iotflow_mongodb mongosh --eval "
use iotflow;
// Insert test document
db.test_collection.insertOne({test: 'connection', timestamp: new Date()});
print('Test document inserted');

// Query test document
var result = db.test_collection.findOne({test: 'connection'});
print('Test document found: ' + (result ? 'YES' : 'NO'));

// Clean up
db.test_collection.deleteMany({test: 'connection'});
print('Test document cleaned up');
"

echo "=== MongoDB Connection Test Complete ==="
# 🎬 Simple NoSQL Demo Commands

**Quick demonstration of polyglot persistence**

---

## 🚀 Prerequisites

```bash
# Start all databases
cd service-web-back
docker compose up -d

# Wait for databases to be ready (30 seconds)
sleep 30

# Initialize PostgreSQL
poetry run python init_db.py

# Start Flask API (in another terminal)
poetry run python app.py
```

---

## 📋 Quick Demo Steps

### 1. Test Database Connections

```bash
# Test PostgreSQL
docker exec smartsense_postgres_nosql psql -U smartsense -d smartsense -c "SELECT version();"

# Test Cassandra (may take a moment)
docker exec smartsense_cassandra cqlsh -e "DESCRIBE KEYSPACES;"

# Test Redis
docker exec smartsense_redis redis-cli -a smartsensepass ping

# Test MongoDB
docker exec smartsense_mongodb mongosh --eval "db.adminCommand('ping')"
```

### 2. Register User (PostgreSQL + MongoDB Event)

```bash
# Register user
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com", 
    "password": "demo123"
  }'

# Check user in PostgreSQL
docker exec smartsense_postgres_nosql psql -U smartsense -d smartsense -c \
  "SELECT username, email FROM users WHERE username = 'demo_user';"

# Check event in MongoDB
docker exec smartsense_mongodb mongosh --eval "
  use smartsense;
  db.event_logs.find({event_type: 'user.registered'}).pretty();
"
```

### 3. Register Device (PostgreSQL + Redis Cache + MongoDB Event)

```bash
# Get user ID from previous response and set it
USER_ID="your_user_id_here"

# Register device
curl -X POST http://localhost:5000/api/v1/devices/register \
  -H "Content-Type: application/json" \
  -H "X-User-ID: $USER_ID" \
  -d '{
    "name": "Demo Sensor",
    "device_type": "sensor",
    "location": "Demo Room"
  }'

# Save the API key from response
API_KEY="your_api_key_here"
DEVICE_ID="your_device_id_here"

# Check device in PostgreSQL
docker exec smartsense_postgres_nosql psql -U smartsense -d smartsense -c \
  "SELECT name, device_type, status FROM devices WHERE name = 'Demo Sensor';"

# Check API key in Redis
docker exec smartsense_redis redis-cli -a smartsensepass KEYS "*api_key*"

# Check device registration event in MongoDB
docker exec smartsense_mongodb mongosh --eval "
  use smartsense;
  db.event_logs.find({event_type: 'device.registered'}).pretty();
"
```

### 4. Send Telemetry (Cassandra + Redis Cache + MongoDB Event)

```bash
# Send telemetry data
curl -X POST http://localhost:5000/api/v1/telemetry \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "temperature": 23.5,
      "humidity": 65.0
    }
  }'

# Check telemetry in Cassandra
docker exec iotflow_cassandra cqlsh -e "
  USE telemetry;
  SELECT * FROM device_data WHERE device_id = $DEVICE_ID LIMIT 5;
"

# Check latest data cache in Redis
docker exec iotflow_redis redis-cli -a iotflowpass KEYS "*latest*"

# Check telemetry event in MongoDB
docker exec iotflow_mongodb mongosh --eval "
  use iotflow;
  db.event_logs.find({event_type: 'telemetry.submitted'}).pretty();
"
```

### 5. Query Latest Data (Redis Cache Hit)

```bash
# This should be very fast due to Redis caching
time curl -s "http://localhost:5000/api/v1/telemetry/$DEVICE_ID/latest" \
  -H "X-API-Key: $API_KEY"
```

---

## 🔍 Verify All Databases

### PostgreSQL - Relational Data
```bash
docker exec iotflow_postgres_nosql psql -U iotflow -d iotflow -c "
  SELECT 
    u.username,
    d.name as device_name,
    d.status
  FROM users u
  JOIN devices d ON u.id = d.user_id
  WHERE u.username = 'demo_user';
"
```

### Cassandra - Time-Series Data
```bash
docker exec iotflow_cassandra cqlsh -e "
  USE telemetry;
  SELECT COUNT(*) FROM device_data WHERE device_id = $DEVICE_ID;
"
```

### Redis - Cached Data
```bash
# Show all cached keys
docker exec iotflow_redis redis-cli -a iotflowpass KEYS "*"

# Show latest data for device
docker exec iotflow_redis redis-cli -a iotflowpass HGETALL "latest:$DEVICE_ID"
```

### MongoDB - Events
```bash
# Show all events
docker exec iotflow_mongodb mongosh --eval "
  use iotflow;
  print('Total events: ' + db.event_logs.countDocuments());
  db.event_logs.find().forEach(function(doc) {
    print(doc.timestamp + ' - ' + doc.event_type);
  });
"
```

---

## 🧹 Cleanup

```bash
# Remove test data
docker exec iotflow_postgres_nosql psql -U iotflow -d iotflow -c "
  DELETE FROM devices WHERE name = 'Demo Sensor';
  DELETE FROM users WHERE username = 'demo_user';
"

# Clear Redis
docker exec iotflow_redis redis-cli -a iotflowpass FLUSHALL

# Clear MongoDB events
docker exec iotflow_mongodb mongosh --eval "
  use iotflow;
  db.event_logs.deleteMany({});
"

# Clear Cassandra (if needed)
docker exec iotflow_cassandra cqlsh -e "
  USE telemetry;
  TRUNCATE device_data;
"
```

---

## 🚨 Troubleshooting

### If MongoDB commands fail:
```bash
# Check MongoDB container
docker logs iotflow_mongodb

# Try alternative connection
docker exec -it iotflow_mongodb bash
mongosh
```

### If Cassandra commands fail:
```bash
# Wait for Cassandra to be ready
docker exec iotflow_cassandra nodetool status

# Initialize keyspace if needed
docker exec iotflow_cassandra cqlsh -f /path/to/init.cql
```

### If Redis commands fail:
```bash
# Check Redis logs
docker logs iotflow_redis

# Test without password first
docker exec iotflow_redis redis-cli ping
```

---

**Demo Complete! Each database serves its optimal purpose in the polyglot architecture.**
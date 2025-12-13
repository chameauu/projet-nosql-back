#!/bin/bash

echo "🔄 Migrating from IoTFlow to SmartSense"
echo "======================================"

# Stop current containers
echo "1. Stopping old IoTFlow containers..."
docker stop iotflow_postgres_nosql iotflow_cassandra iotflow_redis iotflow_mongodb 2>/dev/null || true
docker stop iotflow_cassandra_web iotflow_redis_commander iotflow_mongo_express 2>/dev/null || true

# Remove old containers
echo "2. Removing old containers..."
docker rm iotflow_postgres_nosql iotflow_cassandra iotflow_redis iotflow_mongodb 2>/dev/null || true
docker rm iotflow_cassandra_web iotflow_redis_commander iotflow_mongo_express 2>/dev/null || true

# Remove old network
echo "3. Removing old network..."
docker network rm iotflow-network 2>/dev/null || true

# Start new SmartSense containers
echo "4. Starting new SmartSense containers..."
docker compose up -d

# Wait for containers to be ready
echo "5. Waiting for containers to be ready..."
sleep 30

# Initialize new database
echo "6. Initializing SmartSense database..."
poetry run python init_db.py

# Verify containers are running
echo "7. Verifying new containers..."
docker compose ps

echo ""
echo "✅ Migration to SmartSense complete!"
echo ""
echo "New container names:"
echo "  - smartsense_postgres_nosql"
echo "  - smartsense_cassandra" 
echo "  - smartsense_redis"
echo "  - smartsense_mongodb"
echo ""
echo "New database names:"
echo "  - PostgreSQL: smartsense"
echo "  - MongoDB: smartsense"
echo "  - Cassandra: telemetry (unchanged)"
echo ""
echo "New credentials:"
echo "  - PostgreSQL: smartsense:smartsensepass"
echo "  - Redis: smartsensepass"
echo "  - MongoDB: no authentication"
echo ""
echo "🚀 SmartSense is ready to use!"
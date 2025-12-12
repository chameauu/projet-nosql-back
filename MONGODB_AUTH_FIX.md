# 🔧 MongoDB Authentication Fix Guide

## 📋 Problem
MongoDB is configured with authentication (security feature), but Docker commands fail because they don't provide credentials.

## ✅ Solutions

### **Option 1: Use Authenticated Commands (Recommended)**

#### Test MongoDB Connection
```bash
# Test connection with authentication
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "db.adminCommand('ping')"
```

#### Check Databases
```bash
# List databases with authentication
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "show dbs"
```

#### Count Documents in Collections
```bash
# Count event logs
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
db.event_logs.countDocuments()
"

# Count all collections
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('Event Logs:', db.event_logs.countDocuments());
print('Device Configs:', db.device_configs.countDocuments());
print('Alerts:', db.alerts.countDocuments());
print('Analytics:', db.analytics.countDocuments());
"
```

#### Initialize MongoDB with Authentication
```bash
# Run initialization script with authentication
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin < scripts/mongo-init.js
```

---

### **Option 2: Disable Authentication (Development Only)**

If you want to disable authentication for development, update `docker-compose.yml`:

```yaml
# MongoDB - Flexible document storage (configs, events, alerts)
mongodb:
  image: mongo:7.0
  container_name: iotflow_mongodb
  # Remove these lines to disable authentication:
  # environment:
  #   MONGO_INITDB_ROOT_USERNAME: iotflow
  #   MONGO_INITDB_ROOT_PASSWORD: iotflowpass
  #   MONGO_INITDB_DATABASE: iotflow
  volumes:
    - ./instance/mongodb_data:/data/db
    - ./scripts/mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
  ports:
    - "27017:27017"
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
    interval: 10s
    retries: 5
  networks:
    - iotflow-network
```

**Then update the MongoDB service URI:**
```python
# In src/services/mongodb_service.py
self.uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/iotflow')
```

---

### **Option 3: Environment Variable Configuration**

Update your `.env` file to include MongoDB credentials:

```bash
# Add to .env file
MONGODB_URI=mongodb://iotflow:iotflowpass@localhost:27017/iotflow?authSource=admin
MONGODB_DATABASE=iotflow
MONGODB_USERNAME=iotflow
MONGODB_PASSWORD=iotflowpass
```

---

## 🧪 Verification Commands

### **With Authentication (Option 1)**

```bash
# 1. Test connection
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "db.adminCommand('ping')"

# 2. List databases
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "show dbs"

# 3. Check collections
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
show collections;
"

# 4. Count documents
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('Collections in iotflow database:');
db.getCollectionNames().forEach(function(collection) {
    print(collection + ':', db[collection].countDocuments());
});
"

# 5. Sample event logs
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
db.event_logs.find().limit(3).pretty();
"
```

### **Without Authentication (Option 2)**

```bash
# After disabling auth, these commands work:
docker exec iotflow_mongodb mongosh --eval "show dbs"
docker exec iotflow_mongodb mongosh --eval "use iotflow; show collections"
docker exec iotflow_mongodb mongosh --eval "use iotflow; db.event_logs.countDocuments()"
```

---

## 🔄 Apply the Fix

### **Recommended: Keep Authentication (Production Ready)**

1. **Use authenticated commands for verification:**
   ```bash
   # Test MongoDB with authentication
   docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
   use iotflow;
   print('MongoDB Status: Connected');
   print('Database:', db.getName());
   print('Collections:', db.getCollectionNames().length);
   "
   ```

2. **Update verification script:**
   ```bash
   # Create a verification script
   cat > scripts/verify-mongodb.sh << 'EOF'
   #!/bin/bash
   echo "🔍 MongoDB Verification with Authentication"
   
   # Test connection
   echo "Testing connection..."
   docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "db.adminCommand('ping')" > /dev/null 2>&1
   if [ $? -eq 0 ]; then
       echo "✅ MongoDB connection successful"
   else
       echo "❌ MongoDB connection failed"
       exit 1
   fi
   
   # Check collections
   echo "Checking collections..."
   docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
   use iotflow;
   print('Collections in iotflow database:');
   db.getCollectionNames().forEach(function(collection) {
       print('  ' + collection + ':', db[collection].countDocuments());
   });
   "
   EOF
   
   chmod +x scripts/verify-mongodb.sh
   ./scripts/verify-mongodb.sh
   ```

---

## 🎯 Current Status

- ✅ **MongoDB is running correctly with authentication**
- ✅ **Application connects successfully** (using proper URI with credentials)
- ✅ **Security is enabled** (production-ready)
- ⚠️ **Docker commands need authentication** (this is expected and secure)

## 📝 Recommendation

**Keep authentication enabled** for security and use the authenticated commands for verification. This is the production-ready approach.

The "authentication required" errors you're seeing are actually **good security features** - they mean MongoDB is properly secured and only authenticated connections can access the data.

---

## 🔧 Quick Fix Commands

Run these commands to verify MongoDB is working with authentication:

```bash
# Quick verification
docker exec iotflow_mongodb mongosh -u iotflow -p iotflowpass --authenticationDatabase admin --eval "
use iotflow;
print('✅ MongoDB Status: Connected and Authenticated');
print('📊 Database:', db.getName());
print('📁 Collections:', db.getCollectionNames().join(', '));
print('📈 Event Logs Count:', db.event_logs.countDocuments());
"
```

This will confirm MongoDB is working correctly with proper authentication.
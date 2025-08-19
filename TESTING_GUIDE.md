# 🧪 Docker-Based Testing Quick Reference Guide

## 📋 Pre-Test Checklist
- [ ] Docker and Docker Compose installed
- [ ] Python 3 and pip3 available  
- [ ] All required ports available (3000, 3306, 6379, 8000)
- [ ] `jq` command available for JSON processing
- [ ] Project files present (docker-compose.yml, backend/, frontend/, tests/)

## 🚀 Quick Start Commands

### 1. Validate Environment
```bash
./validate_test_env.sh
```

### 2. Run Complete Test Suite
```bash
./docker_test_plan.sh
```

### 3. Manual Service Management
```bash
# Start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs mysql
docker-compose logs redis

# Stop and cleanup
docker-compose down -v
```

## 🔧 Individual Test Commands

### Health Check Tests
```bash
# Basic health
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/health/ready

# Liveness probe  
curl http://localhost:8000/health/live
```

### Authentication Tests
```bash
# Container-internal testing (recommended)
docker exec -it bailian_backend python3 -m pytest backend/tests/test_auth.py -v

# Manual auth test
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123!"}'
```

### AI Integration Tests
```bash
# Qwen standalone test
docker exec -it bailian_backend python3 backend/tests/qwen_api_standalone_test.py

# Service layer tests
docker exec -it bailian_backend python3 -m pytest backend/tests/test_qwen_service_layer.py -v

# Integration tests
docker exec -it bailian_backend python3 -m pytest backend/tests/test_qwen_api_integration.py -v
```

### Backend API Tests
```bash
# Comprehensive backend integrity
docker exec -it bailian_backend python3 -m pytest backend/tests/test_backend_integrity.py -v

# API endpoints
docker exec -it bailian_backend python3 -m pytest backend/tests/test_api_endpoints.py -v

# Enhanced models
docker exec -it bailian_backend python3 -m pytest backend/tests/test_enhanced_models.py -v
```

### System Integration Tests
```bash
# Frontend accessibility
python3 tests/frontend_test.py

# Smoke tests
python3 tests/smoke_test.py

# Integration tests
python3 tests/integration_testing.py

# Performance tests
python3 tests/performance_testing.py
```

## 📊 Monitoring & Metrics

### Metrics Endpoint
```bash
# View Prometheus metrics
curl http://localhost:8000/metrics

# Specific metrics testing
docker exec -it bailian_backend python3 -m pytest backend/tests/test_metrics.py -v
```

### Log Monitoring
```bash
# Follow backend logs
docker-compose logs -f backend

# Check specific container logs
docker logs bailian_backend
docker logs bailian_mysql  
docker logs bailian_redis
```

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Docker Build Failures
```bash
# Clear Docker cache
docker system prune -f
docker builder prune -f

# Rebuild without cache
docker-compose build --no-cache
```

#### 2. Port Conflicts
```bash
# Check port usage
lsof -i :8000
lsof -i :3000
lsof -i :3306
lsof -i :6379

# Kill processes using ports
sudo kill -9 $(lsof -ti:8000)
```

#### 3. Database Connection Issues
```bash
# Check MySQL container
docker exec -it bailian_mysql mysql -u bailian_user -pbailian_password -e "SHOW DATABASES;"

# Reset database
docker-compose down -v
docker volume prune -f
docker-compose up -d mysql
```

#### 4. Redis Connection Issues
```bash
# Test Redis connectivity
docker exec -it bailian_redis redis-cli ping

# Check Redis logs
docker logs bailian_redis
```

#### 5. API Key Issues
```bash
# Check environment variables in container
docker exec -it bailian_backend env | grep QWEN

# Test with different API key
docker-compose down
# Edit docker-compose.yml to update QWEN_API_KEY
docker-compose up -d backend
```

## 🎯 Success Criteria Reference

### Phase 1: Infrastructure (Required)
- ✅ All containers start successfully
- ✅ Health endpoints return 200
- ✅ Database and Redis connections work

### Phase 2: Authentication (Critical)  
- ✅ User registration and login work
- ✅ JWT tokens generated correctly
- ✅ Role-based access functions

### Phase 3: AI Integration (Core Feature)
- ✅ At least one Qwen model responds
- ✅ Token usage tracking works
- ✅ Error handling functions

### Phase 4: Backend APIs (Essential)
- ✅ 80% of API tests pass
- ✅ Database operations work
- ✅ Metrics collection active

### Phase 5: System Integration (Important)
- ✅ Frontend-backend communication
- ✅ End-to-end workflows function
- ✅ Error handling works

### Phase 6: Performance (Validation)
- ✅ Concurrent request handling
- ✅ Response times < 5 seconds
- ✅ Rate limiting works

## 📈 Next Steps After Testing

### If Success Rate ≥ 80%
1. ✅ Ready for cloud migration
2. 📋 Prepare production environment variables
3. 🚀 Deploy to Alibaba Cloud
4. 📊 Monitor production metrics

### If Success Rate 60-79%
1. 🔧 Review failed components
2. 🐛 Fix critical issues
3. 🔄 Re-run targeted tests
4. ⏳ Delay cloud migration until fixes complete

### If Success Rate < 60%
1. 🚨 Major issues detected
2. 🔍 Comprehensive code review needed
3. 🛠️ Implement fixes for core functionality
4. 🧪 Complete re-testing required

## 📞 Support Resources

- **Project Documentation**: `/Users/chengpeng/Documents/bailian_demo/QWEN_API_DOCUMENTATION.md`
- **Test Records**: `/Users/chengpeng/Documents/bailian_demo/test_records/`
- **Backend Tests**: `/Users/chengpeng/Documents/bailian_demo/backend/tests/`
- **Integration Tests**: `/Users/chengpeng/Documents/bailian_demo/tests/`
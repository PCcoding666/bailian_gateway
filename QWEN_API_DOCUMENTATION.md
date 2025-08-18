# Qwen API Integration Documentation

## 📋 API Summary Report

**Testing Date:** 2025-08-18  
**Project:** Bailian Demo - Alibaba Cloud AI Integration Platform  
**Status:** Code Analysis Complete - Ready for Testing

---

## 🔗 Available API Endpoints

### 1. **Chat Completions API**
- **Endpoint:** `POST /api/bailian/chat/completions`
- **Description:** Qwen model chat completions using OpenAI-compatible API
- **Authentication:** Bearer JWT token required

#### Input Format:
```json
{
  "model": "qwen-max",                    // string - AI model name
  "messages": [                           // array - Chat conversation
    {
      "role": "system",                   // string - message role
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",                     // string - message role  
      "content": "Hello, can you help me?"
    }
  ],
  "temperature": 0.7,                     // float - randomness (0.0-2.0, optional)
  "max_tokens": 1000                      // integer - max response tokens (optional)
}
```

#### Output Format:
```json
{
  "code": 200,                            // integer - response code
  "message": "Request successful",        // string - response message
  "data": {                              // object - OpenAI-compatible response
    "id": "chatcmpl-abc123",             // string - completion ID
    "object": "chat.completion",          // string - object type
    "created": 1699900000,               // integer - unix timestamp
    "model": "qwen-max",                 // string - model used
    "choices": [                         // array - generated responses
      {
        "index": 0,                      // integer - choice index
        "message": {                     // object - generated message
          "role": "assistant",           // string - response role
          "content": "Hello! I'd be happy to help..."
        },
        "finish_reason": "stop"          // string - completion reason
      }
    ],
    "usage": {                           // object - token usage
      "prompt_tokens": 25,               // integer - input tokens
      "completion_tokens": 30,           // integer - generated tokens
      "total_tokens": 55                 // integer - total tokens
    }
  }
}
```

#### Rate Limiting:
- **Default:** 100 requests per minute
- **Admin:** 1000 requests per minute
- **Premium:** 500 requests per minute

---

### 2. **Content Generation API**
- **Endpoint:** `POST /api/bailian/generation`
- **Description:** Wanx model content/image generation
- **Authentication:** Bearer JWT token required

#### Input Format:
```json
{
  "model": "wanx-v1",                     // string - generation model
  "prompt": "Create a beautiful landscape painting", // string - generation prompt
  "parameters": {                         // object - model-specific parameters (optional)
    "size": "1024*1024",                 // string - image dimensions
    "style": "realistic",                // string - generation style
    "quality": "high"                    // string - output quality
  }
}
```

#### Output Format:
```json
{
  "code": 200,                            // integer - response code
  "message": "Request successful",        // string - response message
  "data": {                              // object - generation response
    "output": {                          // object - generation output
      "task_id": "task-12345",           // string - generation task ID
      "task_status": "SUCCEEDED",        // string - task status
      "results": [                       // array - generated content
        {
          "url": "https://dashscope-result.../image.jpg" // string - result URL
        }
      ]
    }
  }
}
```

#### Rate Limiting:
- **Default:** 50 requests per minute
- **Admin:** 200 requests per minute
- **Premium:** 100 requests per minute

---

## 🔐 Authentication System

### Login API
- **Endpoint:** `POST /api/auth/login`
- **Description:** User authentication to get JWT tokens

#### Input:
```json
{
  "username": "admin",
  "password": "AdminPass123!"
}
```

#### Output:
```json
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com"
    }
  }
}
```

---

## 🏥 Health Check APIs

### 1. Basic Health Check
- **Endpoint:** `GET /health`
- **Description:** Basic service health status
- **Authentication:** None required

#### Output:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-18T08:38:18.141Z"
}
```

### 2. Kubernetes Readiness Probe
- **Endpoint:** `GET /health/ready`
- **Description:** Comprehensive dependency health check
- **Authentication:** None required

#### Output (Healthy):
```json
{
  "status": "ready",
  "timestamp": "2025-08-18T08:38:18.163Z",
  "checks": {
    "database": "connected",
    "redis": "connected", 
    "dashscope_api": "configured"
  }
}
```

#### Output (Unhealthy):
```json
{
  "status": "not_ready",
  "timestamp": "2025-08-18T08:38:18.163Z",
  "checks": {
    "database": "error: connection failed",
    "redis": "connected",
    "dashscope_api": "not_configured"
  }
}
```

### 3. Kubernetes Liveness Probe
- **Endpoint:** `GET /health/live`
- **Description:** Application liveness check
- **Authentication:** None required

#### Output:
```json
{
  "status": "alive",
  "timestamp": "2025-08-18T08:38:18.158Z",
  "service": "bailian-backend",
  "version": "0.1.0"
}
```

---

## 📊 Metrics API

### Prometheus Metrics
- **Endpoint:** `GET /metrics`
- **Description:** Prometheus-compatible metrics
- **Authentication:** None required
- **Format:** Prometheus text format

#### Key Metrics Available:
- `http_requests_total` - Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds` - Request duration histogram
- `database_queries_total` - Database query count by operation
- `ai_requests_total` - AI service requests by model and status
- `ai_token_usage_total` - Token usage by model and type
- `health_check_status` - Health check status by component

---

## ⚡ Function Compute Integration

### Serverless AI Processing
The system supports migrating AI processing tasks to Alibaba Cloud Function Compute for better scalability and cost optimization.

#### Environment Variables Required:
- `FC_QWEN_ENDPOINT` - Qwen Function Compute endpoint
- `FC_WANX_ENDPOINT` - Wanx Function Compute endpoint  
- `FC_AUTH_TOKEN` - Function Compute authentication token

#### Function Request Format:
```json
{
  "model": "qwen-max",
  "prompt": "Hello world",
  "messages": [...],
  "parameters": {...},
  "user_id": 123,
  "correlation_id": "req-123-456"
}
```

#### Function Response Format:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "X-Correlation-ID": "req-123-456"
  },
  "body": {
    "success": true,
    "data": {...},
    "token_usage": {
      "input_tokens": 20,
      "output_tokens": 15,
      "total_tokens": 35
    }
  }
}
```

---

## 💰 Cost Analysis

### Token Usage Tracking
All API calls are tracked with detailed token usage metrics:

- **Input Tokens:** Tokens in the request (prompt, messages)
- **Output Tokens:** Tokens in the response (generated content)
- **Total Tokens:** Sum of input and output tokens

### Estimated Costs (Rough Estimates):
- **Qwen Models:** ~$0.002 per token
- **Wanx Models:** ~$0.01 per image generation
- **Function Compute:** ~$0.0000002 per request + compute time

---

## 🔧 Configuration Requirements

### Environment Variables:
```bash
# API Keys
QWEN_API_KEY=sk-1391e4bfcc2847c488dfed3f49e90597

# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bailian
DB_USER=bailian_user
DB_PASSWORD=bailian_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Application
JWT_SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
METRICS_ENABLED=true

# Function Compute (Optional)
FC_QWEN_ENDPOINT=https://your-fc-endpoint
FC_WANX_ENDPOINT=https://your-fc-endpoint
FC_AUTH_TOKEN=your-fc-token
```

---

## 🚀 Cloud Migration Readiness

### Current Status: **TESTING REQUIRED**

Before proceeding with cloud migration, the following tests must pass:

1. ✅ **API Documentation** - Complete
2. ⏳ **Service Health Check** - Needs Testing
3. ⏳ **Authentication Flow** - Needs Testing  
4. ⏳ **Qwen Chat Completions** - Needs Testing
5. ⏳ **Wanx Generation** - Needs Testing
6. ⏳ **Metrics Collection** - Needs Testing
7. ⏳ **Load Testing** - Pending
8. ⏳ **Function Compute** - Pending

### Migration Prerequisites:
- [ ] All API endpoints return success rate ≥ 80%
- [ ] Valid Qwen API key with sufficient credits
- [ ] Database and Redis connectivity confirmed
- [ ] Metrics collection working properly
- [ ] Authentication system functional

### Next Steps:
1. **Start the backend service** with `docker-compose up --build -d`
2. **Run API tests** with `python test_qwen_apis.py`
3. **Review test results** and fix any issues
4. **Validate token usage** and cost estimates
5. **Proceed with cloud migration** when tests pass

---

## 📞 Support Information

- **DashScope API Documentation:** https://dashscope.aliyuncs.com/
- **Bailian Platform:** https://bailian.console.aliyun.com/
- **Function Compute:** https://fc.console.aliyun.com/

This documentation provides a complete overview of all Qwen API integrations and their data formats. Once testing is completed, we can proceed with confidence to the cloud migration phase.
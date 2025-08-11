# API Interface Specification Design

## 1. User Authentication Related Interfaces

### 1.1 User Registration

**HTTP Method**: POST  
**URL Path**: `/api/auth/register`  
**Request Parameters**:
- **Body Parameters**:
  - `username` (string, required): Username
  - `email` (string, required): Email address
  - `password` (string, required): Password
  - `nickname` (string, optional): User nickname
  - `phone` (string, optional): Phone number

**Response Format**:
```json
{
  "code": 200,
  "message": "Registration successful",
  "data": {
    "user_id": 123456,
    "username": "example_user",
    "email": "user@example.com",
    "nickname": "Example",
    "avatar_url": null,
    "phone": null,
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Registration successful
- 400: Request parameter error
- 409: Username or email already exists
- 500: Server internal error

**Authentication Requirement**: No authentication required

### 1.2 User Login

**HTTP Method**: POST  
**URL Path**: `/api/auth/login`  
**Request Parameters**:
- **Body Parameters**:
  - `username` (string, required): Username or email
  - `password` (string, required): Password

**Response Format**:
```json
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "user_id": 123456,
      "username": "example_user",
      "email": "user@example.com",
      "nickname": "Example",
      "avatar_url": null,
      "phone": null,
      "status": 1
    }
  }
}
```

**Status Code Description**:
- 200: Login successful
- 400: Request parameter error
- 401: Username or password incorrect
- 403: User account has been disabled
- 500: Server internal error

**Authentication Requirement**: No authentication required

### 1.3 User Logout

**HTTP Method**: POST  
**URL Path**: `/api/auth/logout`  
**Request Parameters**: None

**Response Format**:
```json
{
  "code": 200,
  "message": "Logout successful",
  "data": null
}
```

**Status Code Description**:
- 200: Logout successful
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 1.4 Refresh Token

**HTTP Method**: POST  
**URL Path**: `/api/auth/refresh`  
**Request Parameters**:
- **Body Parameters**:
  - `refresh_token` (string, required): Refresh token

**Response Format**:
```json
{
  "code": 200,
  "message": "Token refresh successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

**Status Code Description**:
- 200: Token refresh successful
- 400: Request parameter error
- 401: Refresh token is invalid or expired
- 500: Server internal error

**Authentication Requirement**: No authentication required (but valid refresh_token is needed)

### 1.5 Get Current User Information

**HTTP Method**: GET  
**URL Path**: `/api/auth/user`  
**Request Parameters**: None

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "user_id": 123456,
    "username": "example_user",
    "email": "user@example.com",
    "nickname": "Example",
    "avatar_url": null,
    "phone": null,
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "last_login_at": "2023-01-02T00:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

## 2. Conversation Management Interfaces

### 2.1 Create Conversation

**HTTP Method**: POST  
**URL Path**: `/api/conversations`  
**Request Parameters**:
- **Body Parameters**:
  - `title` (string, optional): Conversation title
  - `model_name` (string, required): AI model name to be used

**Response Format**:
```json
{
  "code": 200,
  "message": "Creation successful",
  "data": {
    "conversation_id": 789012,
    "title": "New Conversation",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Creation successful
- 400: Request parameter error
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 2.2 Get Conversation List

**HTTP Method**: GET  
**URL Path**: `/api/conversations`  
**Request Parameters**:
- **Query Parameters**:
  - `page` (integer, optional): Page number, default is 1
  - `limit` (integer, optional): Number of items per page, default is 10, maximum 100
  - `model_name` (string, optional): Filter by model name

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "conversations": [
      {
        "conversation_id": 789012,
        "title": "New Conversation",
        "model_name": "qwen-vl-max-latest",
        "status": 1,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 10,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 400: Request parameter error
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 2.3 Get Conversation Details

**HTTP Method**: GET  
**URL Path**: `/api/conversations/{conversation_id}`  
**Request Parameters**:
- **Path Parameters**:
  - `conversation_id` (integer, required): Conversation ID

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "conversation_id": 789012,
    "title": "New Conversation",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to access this conversation
- 404: Conversation does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 2.4 Update Conversation

**HTTP Method**: PUT  
**URL Path**: `/api/conversations/{conversation_id}`  
**Request Parameters**:
- **Path Parameters**:
  - `conversation_id` (integer, required): Conversation ID
- **Body Parameters**:
  - `title` (string, optional): Conversation title

**Response Format**:
```json
{
  "code": 200,
  "message": "Update successful",
  "data": {
    "conversation_id": 789012,
    "title": "Updated Conversation Title",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T01:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Update successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to modify this conversation
- 404: Conversation does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 2.5 Delete Conversation

**HTTP Method**: DELETE  
**URL Path**: `/api/conversations/{conversation_id}`  
**Request Parameters**:
- **Path Parameters**:
  - `conversation_id` (integer, required): Conversation ID

**Response Format**:
```json
{
  "code": 200,
  "message": "Deletion successful",
  "data": null
}
```

**Status Code Description**:
- 200: Deletion successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to delete this conversation
- 404: Conversation does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

## 3. Message Management Interfaces

### 3.1 Send Message

**HTTP Method**: POST  
**URL Path**: `/api/conversations/{conversation_id}/messages`  
**Request Parameters**:
- **Path Parameters**:
  - `conversation_id` (integer, required): Conversation ID
- **Body Parameters**:
  - `content` (array, required): Message content array
    - `type` (string, required): Content type (text, image_url, video_url)
    - `text` (string, optional): Text content (required when type is text)
    - `image_url` (object, optional): Image URL information (required when type is image_url)
      - `url` (string, required): Image URL
    - `video_url` (object, optional): Video URL information (required when type is video_url)
      - `url` (string, required): Video URL

**Response Format**:
```json
{
  "code": 200,
  "message": "Send successful",
  "data": {
    "message_id": 345678,
    "conversation_id": 789012,
    "user_id": 123456,
    "role": "user",
    "content_type": "text",
    "content": [
      {
        "type": "text",
        "text": "Hello, please introduce yourself"
      }
    ],
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

**Status Code Description**:
- 200: Send successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to send messages in this conversation
- 404: Conversation does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 3.2 Get Message History

**HTTP Method**: GET  
**URL Path**: `/api/conversations/{conversation_id}/messages`  
**Request Parameters**:
- **Path Parameters**:
  - `conversation_id` (integer, required): Conversation ID
- **Query Parameters**:
  - `page` (integer, optional): Page number, default is 1
  - `limit` (integer, optional): Number of items per page, default is 20, maximum 100

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "messages": [
      {
        "message_id": 345678,
        "conversation_id": 789012,
        "user_id": 123456,
        "role": "user",
        "content_type": "text",
        "content": [
          {
            "type": "text",
            "text": "Hello, please introduce yourself"
          }
        ],
        "status": 1,
        "created_at": "2023-01-01T00:00:00Z"
      },
      {
        "message_id": 345679,
        "conversation_id": 789012,
        "user_id": 0,
        "role": "assistant",
        "content_type": "text",
        "content": [
          {
            "type": "text",
            "text": "I am Qwen, a large-scale language model under Alibaba Group..."
          }
        ],
        "status": 1,
        "created_at": "2023-01-01T00:00:01Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total": 2,
      "total_pages": 1
    }
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to access messages in this conversation
- 404: Conversation does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 3.3 Delete Message

**HTTP Method**: DELETE  
**URL Path**: `/api/messages/{message_id}`  
**Request Parameters**:
- **Path Parameters**:
  - `message_id` (integer, required): Message ID

**Response Format**:
```json
{
  "code": 200,
  "message": "Deletion successful",
  "data": null
}
```

**Status Code Description**:
- 200: Deletion successful
- 400: Request parameter error
- 401: Not authenticated
- 403: No permission to delete this message
- 404: Message does not exist
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

## 4. Alibaba Cloud Bailian API Proxy Interface

### 4.1 Call AI Model

**HTTP Method**: POST  
**URL Path**: `/api/bailian/chat/completions`  
**Request Parameters**:
- **Body Parameters**:
  - `model` (string, required): Model name, e.g., "qwen-vl-max-latest"
  - `messages` (array, required): Message history
    - `role` (string, required): Role (user, assistant, system)
    - `content` (array, required): Content array
      - `type` (string, required): Content type (text, image_url, video_url)
      - `text` (string, optional): Text content (required when type is text)
      - `image_url` (object, optional): Image URL information (required when type is image_url)
        - `url` (string, required): Image URL
      - `video_url` (object, optional): Video URL information (required when type is video_url)
        - `url` (string, required): Video URL
  - `temperature` (number, optional): Sampling temperature, range 0-2, default 1
  - `max_tokens` (integer, optional): Maximum number of tokens to generate

**Response Format**:
```json
{
  "code": 200,
  "message": "Request successful",
  "data": {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "qwen-vl-max-latest",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": [
            {
              "type": "text",
              "text": "I am Qwen, a large-scale language model under Alibaba Group..."
            }
          ]
        },
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 9,
      "completion_tokens": 12,
      "total_tokens": 21
    }
  }
}
```

**Status Code Description**:
- 200: Request successful
- 400: Request parameter error
- 401: Not authenticated
- 429: Request rate limit exceeded
- 500: Server internal error
- 503: Bailian API service unavailable

**Authentication Requirement**: JWT Token authentication required

## 5. History Record Query Interface

### 5.1 Query API Call History

**HTTP Method**: GET  
**URL Path**: `/api/history/api-calls`  
**Request Parameters**:
- **Query Parameters**:
  - `page` (integer, optional): Page number, default is 1
  - `limit` (integer, optional): Number of items per page, default is 10, maximum 100
  - `model_name` (string, optional): Filter by model name
  - `start_date` (string, optional): Start date (YYYY-MM-DD)
  - `end_date` (string, optional): End date (YYYY-MM-DD)

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "api_calls": [
      {
        "id": 112233,
        "user_id": 123456,
        "conversation_id": 789012,
        "message_id": 345678,
        "model_name": "qwen-vl-max-latest",
        "api_endpoint": "/api/bailian/chat/completions",
        "status_code": 200,
        "request_tokens": 9,
        "response_tokens": 12,
        "total_tokens": 21,
        "call_duration": 1200,
        "client_ip": "192.168.1.100",
        "created_at": "2023-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 10,
      "total": 1,
      "total_pages": 1
    }
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 400: Request parameter error
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required

### 5.2 Query Conversation History Statistics

**HTTP Method**: GET  
**URL Path**: `/api/history/conversations/statistics`  
**Request Parameters**:
- **Query Parameters**:
  - `start_date` (string, optional): Start date (YYYY-MM-DD)
  - `end_date` (string, optional): End date (YYYY-MM-DD)
  - `model_name` (string, optional): Filter by model name

**Response Format**:
```json
{
  "code": 200,
  "message": "Retrieval successful",
  "data": {
    "total_conversations": 15,
    "total_messages": 128,
    "total_tokens": 2560,
    "model_statistics": [
      {
        "model_name": "qwen-vl-max-latest",
        "conversation_count": 10,
        "message_count": 85,
        "token_count": 1700
      },
      {
        "model_name": "qwen-plus",
        "conversation_count": 5,
        "message_count": 43,
        "token_count": 860
      }
    ],
    "daily_statistics": [
      {
        "date": "2023-01-01",
        "conversation_count": 3,
        "message_count": 24,
        "token_count": 480
      }
    ]
  }
}
```

**Status Code Description**:
- 200: Retrieval successful
- 400: Request parameter error
- 401: Not authenticated
- 500: Server internal error

**Authentication Requirement**: JWT Token authentication required
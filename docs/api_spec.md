# API接口规范设计

## 1. 用户认证相关接口

### 1.1 用户注册

**HTTP方法**: POST  
**URL路径**: `/api/auth/register`  
**请求参数**:
- **Body参数**:
  - `username` (string, required): 用户名
  - `email` (string, required): 邮箱地址
  - `password` (string, required): 密码
  - `nickname` (string, optional): 用户昵称
  - `phone` (string, optional): 手机号码

**响应格式**:
```json
{
  "code": 200,
  "message": "注册成功",
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

**状态码说明**:
- 200: 注册成功
- 400: 请求参数错误
- 409: 用户名或邮箱已存在
- 500: 服务器内部错误

**认证要求**: 无需认证

### 1.2 用户登录

**HTTP方法**: POST  
**URL路径**: `/api/auth/login`  
**请求参数**:
- **Body参数**:
  - `username` (string, required): 用户名或邮箱
  - `password` (string, required): 密码

**响应格式**:
```json
{
  "code": 200,
  "message": "登录成功",
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

**状态码说明**:
- 200: 登录成功
- 400: 请求参数错误
- 401: 用户名或密码错误
- 403: 用户账户已被禁用
- 500: 服务器内部错误

**认证要求**: 无需认证

### 1.3 用户登出

**HTTP方法**: POST  
**URL路径**: `/api/auth/logout`  
**请求参数**: 无

**响应格式**:
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

**状态码说明**:
- 200: 登出成功
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 1.4 刷新Token

**HTTP方法**: POST  
**URL路径**: `/api/auth/refresh`  
**请求参数**:
- **Body参数**:
  - `refresh_token` (string, required): 刷新令牌

**响应格式**:
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

**状态码说明**:
- 200: Token刷新成功
- 400: 请求参数错误
- 401: 刷新令牌无效或已过期
- 500: 服务器内部错误

**认证要求**: 无需认证（但需要有效的refresh_token）

### 1.5 获取当前用户信息

**HTTP方法**: GET  
**URL路径**: `/api/auth/user`  
**请求参数**: 无

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
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

**状态码说明**:
- 200: 获取成功
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

## 2. 对话管理接口

### 2.1 创建对话

**HTTP方法**: POST  
**URL路径**: `/api/conversations`  
**请求参数**:
- **Body参数**:
  - `title` (string, optional): 对话标题
  - `model_name` (string, required): 使用的AI模型名称

**响应格式**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "conversation_id": 789012,
    "title": "新对话",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

**状态码说明**:
- 200: 创建成功
- 400: 请求参数错误
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 2.2 获取对话列表

**HTTP方法**: GET  
**URL路径**: `/api/conversations`  
**请求参数**:
- **Query参数**:
  - `page` (integer, optional): 页码，默认为1
  - `limit` (integer, optional): 每页数量，默认为10，最大100
  - `model_name` (string, optional): 按模型名称筛选

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "conversations": [
      {
        "conversation_id": 789012,
        "title": "新对话",
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

**状态码说明**:
- 200: 获取成功
- 400: 请求参数错误
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 2.3 获取对话详情

**HTTP方法**: GET  
**URL路径**: `/api/conversations/{conversation_id}`  
**请求参数**:
- **Path参数**:
  - `conversation_id` (integer, required): 对话ID

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "conversation_id": 789012,
    "title": "新对话",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

**状态码说明**:
- 200: 获取成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限访问该对话
- 404: 对话不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 2.4 更新对话

**HTTP方法**: PUT  
**URL路径**: `/api/conversations/{conversation_id}`  
**请求参数**:
- **Path参数**:
  - `conversation_id` (integer, required): 对话ID
- **Body参数**:
  - `title` (string, optional): 对话标题

**响应格式**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "conversation_id": 789012,
    "title": "更新后的对话标题",
    "model_name": "qwen-vl-max-latest",
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T01:00:00Z"
  }
}
```

**状态码说明**:
- 200: 更新成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限修改该对话
- 404: 对话不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 2.5 删除对话

**HTTP方法**: DELETE  
**URL路径**: `/api/conversations/{conversation_id}`  
**请求参数**:
- **Path参数**:
  - `conversation_id` (integer, required): 对话ID

**响应格式**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**状态码说明**:
- 200: 删除成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限删除该对话
- 404: 对话不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

## 3. 消息管理接口

### 3.1 发送消息

**HTTP方法**: POST  
**URL路径**: `/api/conversations/{conversation_id}/messages`  
**请求参数**:
- **Path参数**:
  - `conversation_id` (integer, required): 对话ID
- **Body参数**:
  - `content` (array, required): 消息内容数组
    - `type` (string, required): 内容类型(text, image_url, video_url)
    - `text` (string, optional): 文本内容(type为text时必需)
    - `image_url` (object, optional): 图片URL信息(type为image_url时必需)
      - `url` (string, required): 图片URL
    - `video_url` (object, optional): 视频URL信息(type为video_url时必需)
      - `url` (string, required): 视频URL

**响应格式**:
```json
{
  "code": 200,
  "message": "发送成功",
  "data": {
    "message_id": 345678,
    "conversation_id": 789012,
    "user_id": 123456,
    "role": "user",
    "content_type": "text",
    "content": [
      {
        "type": "text",
        "text": "你好，请介绍一下你自己"
      }
    ],
    "status": 1,
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

**状态码说明**:
- 200: 发送成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限在该对话中发送消息
- 404: 对话不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 3.2 获取消息历史

**HTTP方法**: GET  
**URL路径**: `/api/conversations/{conversation_id}/messages`  
**请求参数**:
- **Path参数**:
  - `conversation_id` (integer, required): 对话ID
- **Query参数**:
  - `page` (integer, optional): 页码，默认为1
  - `limit` (integer, optional): 每页数量，默认为20，最大100

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
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
            "text": "你好，请介绍一下你自己"
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
            "text": "我是通义千问，阿里巴巴集团旗下的超大规模语言模型..."
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

**状态码说明**:
- 200: 获取成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限访问该对话的消息
- 404: 对话不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 3.3 删除消息

**HTTP方法**: DELETE  
**URL路径**: `/api/messages/{message_id}`  
**请求参数**:
- **Path参数**:
  - `message_id` (integer, required): 消息ID

**响应格式**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**状态码说明**:
- 200: 删除成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限删除该消息
- 404: 消息不存在
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

## 4. 阿里云百炼API代理接口

### 4.1 调用AI模型

**HTTP方法**: POST  
**URL路径**: `/api/bailian/chat/completions`  
**请求参数**:
- **Body参数**:
  - `model` (string, required): 模型名称，如"qwen-vl-max-latest"
  - `messages` (array, required): 消息历史
    - `role` (string, required): 角色(user, assistant, system)
    - `content` (array, required): 内容数组
      - `type` (string, required): 内容类型(text, image_url, video_url)
      - `text` (string, optional): 文本内容(type为text时必需)
      - `image_url` (object, optional): 图片URL信息(type为image_url时必需)
        - `url` (string, required): 图片URL
      - `video_url` (object, optional): 视频URL信息(type为video_url时必需)
        - `url` (string, required): 视频URL
  - `temperature` (number, optional): 采样温度，范围0-2，默认1
  - `max_tokens` (integer, optional): 最大生成token数

**响应格式**:
```json
{
  "code": 200,
  "message": "请求成功",
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
              "text": "我是通义千问，阿里巴巴集团旗下的超大规模语言模型..."
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

**状态码说明**:
- 200: 请求成功
- 400: 请求参数错误
- 401: 未认证
- 429: 请求频率超限
- 500: 服务器内部错误
- 503: 百炼API服务不可用

**认证要求**: 需要JWT Token认证

## 5. 历史记录查询接口

### 5.1 查询API调用历史

**HTTP方法**: GET  
**URL路径**: `/api/history/api-calls`  
**请求参数**:
- **Query参数**:
  - `page` (integer, optional): 页码，默认为1
  - `limit` (integer, optional): 每页数量，默认为10，最大100
  - `model_name` (string, optional): 按模型名称筛选
  - `start_date` (string, optional): 开始日期(YYYY-MM-DD)
  - `end_date` (string, optional): 结束日期(YYYY-MM-DD)

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
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

**状态码说明**:
- 200: 获取成功
- 400: 请求参数错误
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证

### 5.2 查询对话历史统计

**HTTP方法**: GET  
**URL路径**: `/api/history/conversations/statistics`  
**请求参数**:
- **Query参数**:
  - `start_date` (string, optional): 开始日期(YYYY-MM-DD)
  - `end_date` (string, optional): 结束日期(YYYY-MM-DD)
  - `model_name` (string, optional): 按模型名称筛选

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
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

**状态码说明**:
- 200: 获取成功
- 400: 请求参数错误
- 401: 未认证
- 500: 服务器内部错误

**认证要求**: 需要JWT Token认证
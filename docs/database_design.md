# 数据库模型设计

## 1. 用户表（users）

存储用户基本信息

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户唯一标识',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱地址',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    nickname VARCHAR(100) COMMENT '用户昵称',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    phone VARCHAR(20) COMMENT '手机号码',
    status TINYINT DEFAULT 1 COMMENT '用户状态：1-正常，0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at TIMESTAMP NULL COMMENT '最后登录时间'
) COMMENT '用户信息表';
```

**字段说明：**
- `id`: BIGINT, 主键，自增，用户唯一标识
- `username`: VARCHAR(50), 唯一索引，用户名，用于登录
- `email`: VARCHAR(100), 唯一索引，邮箱地址，用于登录和联系
- `password_hash`: VARCHAR(255), 密码哈希值，安全存储用户密码
- `nickname`: VARCHAR(100), 用户昵称，用于显示
- `avatar_url`: VARCHAR(500), 用户头像URL
- `phone`: VARCHAR(20), 手机号码
- `status`: TINYINT, 用户状态（1-正常，0-禁用）
- `created_at`: TIMESTAMP, 创建时间，默认当前时间
- `updated_at`: TIMESTAMP, 更新时间，默认当前时间，更新时自动刷新
- `last_login_at`: TIMESTAMP, 最后登录时间，可为空

## 2. 对话历史表（conversations）

存储用户与AI的对话历史

```sql
CREATE TABLE conversations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '对话唯一标识',
    user_id BIGINT NOT NULL COMMENT '关联的用户ID',
    title VARCHAR(255) COMMENT '对话标题',
    model_name VARCHAR(100) NOT NULL COMMENT '使用的AI模型名称',
    status TINYINT DEFAULT 1 COMMENT '对话状态：1-进行中，0-已结束',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) COMMENT '对话历史表';
```

**字段说明：**
- `id`: BIGINT, 主键，自增，对话唯一标识
- `user_id`: BIGINT, 外键，关联用户表的ID
- `title`: VARCHAR(255), 对话标题，可由用户自定义或系统生成
- `model_name`: VARCHAR(100), 使用的AI模型名称（如qwen-vl-max-latest）
- `status`: TINYINT, 对话状态（1-进行中，0-已结束）
- `created_at`: TIMESTAMP, 创建时间，默认当前时间
- `updated_at`: TIMESTAMP, 更新时间，默认当前时间，更新时自动刷新
- 外键约束：当用户被删除时，级联删除相关对话记录
- 索引：为user_id和created_at创建索引以提高查询性能

## 3. 对话消息表（messages）

存储具体的对话消息

```sql
CREATE TABLE messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '消息唯一标识',
    conversation_id BIGINT NOT NULL COMMENT '关联的对话ID',
    user_id BIGINT NOT NULL COMMENT '发送消息的用户ID',
    role ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色：user-用户，assistant-AI助手，system-系统',
    content_type ENUM('text', 'image_url', 'video_url') NOT NULL DEFAULT 'text' COMMENT '内容类型',
    content TEXT NOT NULL COMMENT '消息内容（JSON格式存储）',
    status TINYINT DEFAULT 1 COMMENT '消息状态：1-正常，0-已删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) COMMENT '对话消息表';
```

**字段说明：**
- `id`: BIGINT, 主键，自增，消息唯一标识
- `conversation_id`: BIGINT, 外键，关联对话表的ID
- `user_id`: BIGINT, 外键，关联用户表的ID
- `role`: ENUM, 消息角色（user-用户，assistant-AI助手，system-系统）
- `content_type`: ENUM, 内容类型（text-文本，image_url-图片URL，video_url-视频URL）
- `content`: TEXT, 消息内容，以JSON格式存储以支持多种内容类型
- `status`: TINYINT, 消息状态（1-正常，0-已删除）
- `created_at`: TIMESTAMP, 创建时间，默认当前时间
- 外键约束：当对话或用户被删除时，级联删除相关消息记录
- 索引：为conversation_id、user_id和created_at创建索引以提高查询性能

## 4. API调用记录表（api_calls）

记录用户API使用情况

```sql
CREATE TABLE api_calls (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '调用记录唯一标识',
    user_id BIGINT NOT NULL COMMENT '发起调用的用户ID',
    conversation_id BIGINT COMMENT '关联的对话ID',
    message_id BIGINT COMMENT '关联的消息ID',
    model_name VARCHAR(100) NOT NULL COMMENT '调用的AI模型名称',
    api_endpoint VARCHAR(255) NOT NULL COMMENT 'API端点',
    request_content LONGTEXT COMMENT '请求内容',
    response_content LONGTEXT COMMENT '响应内容',
    status_code SMALLINT COMMENT 'HTTP状态码',
    request_tokens INT DEFAULT 0 COMMENT '请求使用的token数',
    response_tokens INT DEFAULT 0 COMMENT '响应使用的token数',
    total_tokens INT DEFAULT 0 COMMENT '总token数',
    call_duration INT COMMENT '调用耗时（毫秒）',
    client_ip VARCHAR(45) COMMENT '客户端IP地址',
    user_agent TEXT COMMENT '用户代理信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_model_name (model_name),
    INDEX idx_created_at (created_at),
    INDEX idx_user_model_date (user_id, model_name, created_at)
) COMMENT 'API调用记录表';
```

**字段说明：**
- `id`: BIGINT, 主键，自增，调用记录唯一标识
- `user_id`: BIGINT, 外键，关联用户表的ID
- `conversation_id`: BIGINT, 外键，关联对话表的ID，可为空
- `message_id`: BIGINT, 外键，关联消息表的ID，可为空
- `model_name`: VARCHAR(100), 调用的AI模型名称
- `api_endpoint`: VARCHAR(255), API端点URL
- `request_content`: LONGTEXT, 请求内容，记录发送给API的完整请求
- `response_content`: LONGTEXT, 响应内容，记录API返回的完整响应
- `status_code`: SMALLINT, HTTP状态码
- `request_tokens`: INT, 请求使用的token数
- `response_tokens`: INT, 响应使用的token数
- `total_tokens`: INT, 总token数（请求+响应）
- `call_duration`: INT, 调用耗时（毫秒）
- `client_ip`: VARCHAR(45), 客户端IP地址（支持IPv6）
- `user_agent`: TEXT, 用户代理信息
- `created_at`: TIMESTAMP, 创建时间，默认当前时间
- 外键约束：当用户被删除时，级联删除相关调用记录；当对话或消息被删除时，设置为NULL
- 索引：为user_id、model_name、created_at创建索引，以及组合索引user_model_date以提高查询性能

## 表关系说明

1. **users** ↔ **conversations**: 一对多关系，一个用户可以有多个对话
2. **conversations** ↔ **messages**: 一对多关系，一个对话包含多条消息
3. **users** ↔ **api_calls**: 一对多关系，一个用户可以有多个API调用记录
4. **conversations** ↔ **api_calls**: 一对多关系，一个对话可以有多个API调用记录
5. **messages** ↔ **api_calls**: 一对多关系，一条消息可以对应多个API调用记录

## 设计考虑

1. **安全性**：
   - 密码使用哈希存储
   - 敏感信息如API密钥不在数据库中存储
   - 使用外键约束保证数据完整性

2. **性能优化**：
   - 为常用查询字段创建索引
   - 使用适当的数据类型以节省存储空间
   - 时间戳字段自动更新

3. **扩展性**：
   - 字段长度预留扩展空间
   - 支持多种内容类型（文本、图片、视频）
   - 可记录详细的API调用信息用于分析

4. **可维护性**：
   - 字段命名清晰明确
   - 添加详细注释说明
   - 合理的表结构设计

这个数据库模型设计满足了系统架构文档中提到的需求，能够有效支持用户管理、对话历史记录、消息存储和API调用监控等功能。
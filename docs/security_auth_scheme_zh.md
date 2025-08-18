# 安全认证和授权方案设计

## 1. 用户认证机制

### 1.1 JWT令牌机制

#### 实现方案：
- 使用JWT（JSON Web Tokens）进行用户身份认证
- 采用非对称加密算法（RS256）确保令牌安全
- 访问令牌有效期：1小时
- 刷新令牌有效期：7天
- 令牌包含基本用户信息（user_id、username、roles等）

#### 令牌结构：
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123456,
    "username": "example_user",
    "roles": ["user"],
    "exp": 1677652288,
    "iat": 1677648688,
    "iss": "bailian-api-platform"
  }
}
```

#### 认证流程：
1. 用户提交登录凭证
2. 后端验证用户身份
3. 生成JWT访问令牌和刷新令牌
4. 将令牌返回给客户端
5. 客户端在后续请求中携带访问令牌
6. 后端验证令牌有效性
7. 令牌过期时使用刷新令牌刷新

### 1.2 OAuth2集成（可选扩展）

#### 实现方案：
- 集成第三方登录（微信、GitHub、Google等）
- 使用OAuth2.0协议标准
- 提供标准的授权码流程
- 支持PKCE增强安全性

## 2. API接口授权机制

### 2.1 RBAC权限模型

#### 角色设计：
- **普通用户（user）**：可以创建对话、发送消息、查看历史
- **高级用户（premium_user）**：除了普通用户权限外，可以使用更高级的模型
- **管理员（admin）**：系统管理权限，可以查看所有用户数据

#### 权限控制：
- 基于角色的访问控制（RBAC）
- 细粒度的API权限验证
- 为每个API端点定义所需的权限级别

#### 权限验证流程：
1. 解析JWT令牌获取用户角色信息
2. 检查API端点所需的权限
3. 验证用户角色是否满足权限要求
4. 授权时执行业务逻辑，否则返回403错误

### 2.2 数据级权限控制

#### 实现方案：
- 用户只能访问自己的数据（与user_id关联）
- 通过user_id隔离对话和消息
- 管理员可以访问所有用户数据（由角色决定）

## 3. 数据传输安全

### 3.1 HTTPS加密传输

#### 实现方案：
- 强制使用HTTPS协议
- TLS 1.2或更高版本
- 使用安全的加密套件
- HSTS（HTTP严格传输安全）头部

### 3.2 敏感数据加密存储

#### 实现方案：
- 用户密码使用bcrypt哈希存储（已在数据库设计中体现）
- API密钥在传输过程中加密
- 敏感配置信息加密存储

### 3.3 数据库连接安全

#### 实现方案：
- 使用SSL/TLS加密数据库连接
- 配置数据库用户最小权限原则
- 定期轮换数据库凭证

## 4. 密码安全策略

### 4.1 密码复杂度要求

#### 实现方案：
- 最小长度：8个字符
- 必须包含大小写字母、数字和特殊字符
- 不允许常见弱密码
- 不允许与用户名或邮箱相同

### 4.2 密码存储安全

#### 实现方案：
- 使用bcrypt算法进行哈希
- 盐值自动生成并存储
- 哈希迭代次数：12轮

### 4.3 密码重置机制

#### 实现方案：
- 通过邮箱发送密码重置链接
- 重置链接有效期：1小时
- 重置后原密码立即失效

## 5. API调用频率限制

### 5.1 限流策略

#### 实现方案：
- 基于用户的API调用限流
- 普通用户：每分钟10次调用
- 高级用户：每分钟100次调用
- 管理员：无限制或更高限制

### 5.2 限流算法

#### 实现方案：
- 使用令牌桶算法
- Redis存储限流计数器
- 分布式环境中的统一限流

### 5.3 限流响应

#### 实现方案：
- 超出限制时返回429状态码
- 在响应头中包含限流信息：
  - X-RateLimit-Limit: 100
  - X-RateLimit-Remaining: 99
  - X-RateLimit-Reset: 1677652288

## 6. 阿里云百炼API密钥安全管理

### 6.1 密钥存储安全

#### 实现方案：
- API密钥不存储在数据库中
- 使用环境变量或密钥管理服务（如HashiCorp Vault）
- 定期轮换API密钥
- 使用多个密钥轮换来减少单点故障

### 6.2 密钥访问控制

#### 实现方案：
- 仅在需要调用阿里云API的服务中访问密钥
- 使用服务账户最小权限原则
- 记录密钥访问日志

### 6.3 密钥泄露防护

#### 实现方案：
- 监控异常密钥使用
- 自动禁用可疑密钥
- 建立密钥泄露应急响应流程

## 7. 日志和审计机制

### 7.1 日志内容

#### 实现方案：
- 用户登录/登出日志
- API调用日志（已包含在api_calls表中）
- 权限变更日志
- 安全事件日志
- 系统错误日志

### 7.2 日志安全

#### 实现方案：
- 脱敏敏感信息
- 加密日志文件存储
- 控制日志访问权限
- 定期备份和归档

### 7.3 审计跟踪

#### 实现方案：
- 记录用户操作轨迹
- 关联用户ID、操作时间、操作类型、影响数据
- 提供审计日志查询接口
- 定期生成安全审计报告

## 8. 技术实现细节

### 8.1 JWT实现代码示例

```python
import jwt
import datetime
from cryptography.hazmat.primitives import serialization

# JWT配置
JWT_ALGORITHM = "RS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 生成访问令牌
def create_access_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    private_key = open("jwt-private.pem", "rb").read()
    private_key = serialization.load_pem_private_key(private_key, password=None)
    encoded_jwt = jwt.encode(data, private_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# 生成刷新令牌
def create_refresh_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    private_key = open("jwt-private.pem", "rb").read()
    private_key = serialization.load_pem_private_key(private_key, password=None)
    encoded_jwt = jwt.encode(data, private_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt
```

### 8.2 权限验证中间件示例

```python
from functools import wraps
from flask import request, jsonify

def require_auth(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"code": 401, "message": "未提供认证令牌"}), 401
            
            try:
                # 验证令牌
                payload = verify_jwt_token(token)
                user_roles = payload.get('roles', [])
                
                # 检查角色权限
                if roles and not any(role in user_roles for role in roles):
                    return jsonify({"code": 403, "message": "权限不足"}), 403
                
                # 将用户信息添加到请求上下文
                request.current_user = payload
                
            except jwt.ExpiredSignatureError:
                return jsonify({"code": 401, "message": "令牌已过期"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"code": 401, "message": "无效令牌"}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 8.3 密码处理示例

```python
import bcrypt

# 密码加密
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 密码验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### 8.4 限流实现示例

```python
import redis
from functools import wraps
from flask import request

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def rate_limit(max_requests=100, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取用户标识
            user_id = request.current_user.get('user_id') if hasattr(request, 'current_user') else 'anonymous'
            key = f"rate_limit:{user_id}:{request.endpoint}"
            
            # 使用Redis计数器
            current = redis_client.get(key)
            if current is None:
                redis_client.setex(key, window, 1)
            elif int(current) >= max_requests:
                return jsonify({"code": 429, "message": "超出请求频率限制"}), 429
            else:
                redis_client.incr(key)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 9. 安全考虑和最佳实践

### 9.1 安全头部设置

- Content-Security-Policy
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### 9.2 输入验证和过滤

- 验证所有用户输入
- 防止SQL注入攻击
- 防止XSS攻击
- 防止CSRF攻击

### 9.3 安全监控和告警

- 实时监控异常登录行为
- 监控API调用异常模式
- 设置安全事件告警机制
- 定期进行安全扫描和渗透测试

### 9.4 事件响应计划

- 建立安全事件响应流程
- 密钥泄露应急处理
- 用户数据泄露应急处理
- 系统漏洞修复流程

## 10. 未来改进建议

1. 集成多因素认证（MFA）
2. 实现单点登录（SSO）
3. 添加用户会话管理
4. 实现更细粒度的权限控制
5. 添加安全日志分析功能
6. 实现自动化安全测试

本安全认证和授权方案提供了一个完整的安全保护机制，能够有效保护系统和用户数据安全。
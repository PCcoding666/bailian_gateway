# frontend/Dockerfile
# 使用阿里云的官方 Node.js 镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/node:16-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# 更换 npm 源为淘宝镜像并安装依赖
RUN npm config set registry https://registry.npmmirror.com && \
    npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
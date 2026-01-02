# 部署文档

## 环境要求

### 后端
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+（可选）

### 前端
- Node.js 16+
- npm 或 yarn

## 后端部署步骤

### 1. 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置：
- 数据库连接信息
- Redis连接信息（如使用）
- 通义千问API密钥
- JWT密钥

### 3. 创建数据库

```bash
mysql -u root -p < ../database/init.sql
```

### 4. 运行数据库迁移

系统会自动创建数据表（通过SQLAlchemy）。

### 5. 启动后端服务

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 前端部署步骤

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置API地址

编辑 `vite.config.js`，修改proxy配置中的target为后端地址。

### 3. 开发环境运行

```bash
npm run dev
```

### 4. 生产环境构建

```bash
npm run build
```

构建后的文件在 `dist` 目录，可以部署到Nginx等Web服务器。

## Docker部署（可选）

### 后端Dockerfile示例

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### 前端Dockerfile示例

```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

## Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 性能优化建议

1. **数据库优化**
   - 添加适当的索引
   - 使用连接池
   - 定期清理历史数据

2. **缓存策略**
   - 使用Redis缓存频繁访问的数据
   - 缓存教学设计模板

3. **并发处理**
   - 使用Gunicorn或uWSGI部署后端
   - 配置适当的worker数量

4. **静态资源**
   - 使用CDN加速
   - 启用Gzip压缩

## 监控与日志

建议配置：
- 应用日志记录
- 错误监控（如Sentry）
- 性能监控（如Prometheus）

## 安全建议

1. 生产环境必须修改默认密钥
2. 启用HTTPS
3. 配置CORS白名单
4. 定期更新依赖包
5. 数据库访问权限控制


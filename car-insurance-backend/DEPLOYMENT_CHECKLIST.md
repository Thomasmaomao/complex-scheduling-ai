# 车险询价系统 Beta v1.0 - 生产部署清单

**文档版本**: v1.0  
**创建日期**: 2026-03-30  
**目标环境**: 生产环境  
**预计部署时间**: 2-4 小时

---

## 📋 一、部署前检查清单

### 1.1 环境准备

| 检查项 | 状态 | 负责人 | 备注 |
|--------|------|--------|------|
| 服务器资源确认（CPU/内存/磁盘） | ⏳ 待确认 | 运维 | 建议：4 核 8G 以上 |
| 操作系统版本确认（CentOS 7+/Ubuntu 18.04+） | ⏳ 待确认 | 运维 | |
| 网络配置（防火墙、安全组） | ⏳ 待确认 | 运维 | 开放 80/443/3306/6379 端口 |
| 域名解析配置 | ⏳ 待确认 | 运维 | api.insurance.com |
| SSL 证书准备 | ⏳ 待确认 | 运维 | Let's Encrypt 或商业证书 |

### 1.2 软件依赖

| 软件 | 版本要求 | 状态 | 安装命令 |
|------|----------|------|----------|
| Python | 3.8+ | ⏳ 待安装 | `python3.8 --version` |
| Node.js | 18+ | ⏳ 待安装 | `node -v` |
| MySQL | 8.0+ | ⏳ 待安装 | `mysql --version` |
| Redis | 6.0+ | ⏳ 待安装 | `redis-server --version` |
| Nginx | 1.18+ | ⏳ 待安装 | `nginx -v` |
| Supervisor | 4.0+ | ⏳ 待安装 | `supervisord -v` |

### 1.3 数据库准备

| 检查项 | 状态 | SQL 脚本 | 备注 |
|--------|------|----------|------|
| 创建数据库 car_insurance | ⏳ 待执行 | `CREATE DATABASE car_insurance` | utf8mb4 字符集 |
| 创建 10 个核心表 | ⏳ 待执行 | `data/schema.sql` | 含索引 |
| 初始化业务单元数据（5 条） | ⏳ 待执行 | `data/initial_data.sql` | |
| 初始化策略配置（1 条） | ⏳ 待执行 | `data/initial_data.sql` | |
| 初始化保司评分（3 条） | ⏳ 待执行 | `data/initial_data.sql` | |
| 创建数据库用户并授权 | ⏳ 待执行 | `GRANT ALL PRIVILEGES` | 最小权限原则 |

### 1.4 Redis 配置

| 检查项 | 状态 | 配置值 | 备注 |
|--------|------|--------|------|
| Redis 服务启动 | ⏳ 待确认 | 6379 端口 | |
| 内存配置 | ⏳ 待确认 | maxmemory 2GB | |
| 持久化配置 | ⏳ 待确认 | RDB+AOF | |
| 密码配置 | ⏳ 待确认 | 强密码 | 生产环境必须 |

---

## 🔧 二、后端部署

### 2.1 代码部署

```bash
# 1. 创建部署目录
sudo mkdir -p /opt/car-insurance
sudo chown -R admin:admin /opt/car-insurance

# 2. 上传代码
cd /opt/car-insurance
git clone <repository-url> .
# 或上传 car-insurance-backend 目录

# 3. 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置生产环境参数
```

### 2.2 环境配置（.env）

```ini
# 应用配置
APP_NAME=车险询价系统
APP_VERSION=Beta v1.0
APP_ENV=production
DEBUG=False

# API 配置
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/car_insurance

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/car-insurance/app.log

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_EXPIRE_HOURS=24
```

### 2.3 日志配置

```bash
# 创建日志目录
sudo mkdir -p /var/log/car-insurance
sudo chown -R admin:admin /var/log/car-insurance

# 配置日志轮转（/etc/logrotate.d/car-insurance）
/var/log/car-insurance/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 admin admin
    postrotate
        kill -USR1 `cat /var/run/car-insurance.pid 2>/dev/null` 2>/dev/null || true
    endscript
}
```

### 2.4 Supervisor 配置

```ini
# /etc/supervisor/conf.d/car-insurance.conf
[program:car-insurance]
command=/opt/car-insurance/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/car-insurance
user=admin
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
numprocs=1
stdout_logfile=/var/log/car-insurance/supervisor.log
stderr_logfile=/var/log/car-insurance/supervisor_err.log
environment=PATH="/opt/car-insurance/venv/bin:%(ENV_PATH)s"
```

```bash
# 重启 Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start car-insurance
```

### 2.5 Nginx 配置

```nginx
# /etc/nginx/sites-available/car-insurance
server {
    listen 80;
    server_name api.insurance.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.insurance.com;
    
    ssl_certificate /etc/letsencrypt/live/api.insurance.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.insurance.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering off;
    }
    
    # 静态文件（前端）
    location / {
        root /opt/car-insurance/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存配置
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 访问日志
    access_log /var/log/nginx/car-insurance_access.log;
    error_log /var/log/nginx/car-insurance_error.log;
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/car-insurance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🖥️ 三、前端部署

### 3.1 构建生产版本

```bash
cd /opt/car-insurance/vue3-car-insurance

# 安装依赖
npm install

# 配置生产环境变量
cat > .env.production << EOF
VITE_API_BASE_URL=https://api.insurance.com/api/v1
EOF

# 构建
npm run build

# 检查构建产物
ls -lh dist/
```

### 3.2 部署到 Nginx

```bash
# 复制构建产物到 Nginx 目录
sudo cp -r dist/* /opt/car-insurance/frontend/dist/

# 设置权限
sudo chown -R www-data:www-data /opt/car-insurance/frontend/dist
sudo chmod -R 755 /opt/car-insurance/frontend/dist
```

---

## 🔒 四、安全配置

### 4.1 数据库安全

```sql
-- 创建专用数据库用户
CREATE USER 'car_insurance'@'localhost' IDENTIFIED BY 'StrongPassword123!';

-- 最小权限授权
GRANT SELECT, INSERT, UPDATE, DELETE ON car_insurance.* TO 'car_insurance'@'localhost';
FLUSH PRIVILEGES;

-- 禁止远程访问
UPDATE mysql.user SET Host='localhost' WHERE User='car_insurance';
FLUSH PRIVILEGES;
```

### 4.2 Redis 安全

```ini
# /etc/redis/redis.conf
bind 127.0.0.1
requirepass StrongRedisPassword123!
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### 4.3 应用安全

- [ ] 配置 CORS 白名单
- [ ] 启用 JWT 认证
- [ ] 配置请求限流（Nginx limit_req）
- [ ] 启用 HTTPS
- [ ] 配置 CSP 安全策略

---

## 📊 五、监控配置

### 5.1 应用监控

```python
# 添加健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "Beta v1.0",
        "timestamp": datetime.now().isoformat()
    }
```

### 5.2 日志监控

```bash
# 配置日志收集
sudo mkdir -p /var/log/car-insurance
sudo touch /var/log/car-insurance/{app,error,access}.log
sudo chown admin:admin /var/log/car-insurance/*.log
```

### 5.3 告警配置

| 指标 | 阈值 | 告警方式 | 负责人 |
|------|------|----------|--------|
| CPU 使用率 | > 80% | 邮件/短信 | 运维 |
| 内存使用率 | > 85% | 邮件/短信 | 运维 |
| 磁盘使用率 | > 90% | 邮件/短信 | 运维 |
| API 错误率 | > 5% | 邮件/短信 | 开发 |
| API 响应时间 | > 1s | 邮件/短信 | 开发 |
| 数据库连接数 | > 80% | 邮件/短信 | DBA |

---

## 💾 六、备份策略

### 6.1 数据库备份

```bash
#!/bin/bash
# /opt/scripts/backup-db.sh

BACKUP_DIR="/backup/car-insurance/db"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u car_insurance -p'password' car_insurance > $BACKUP_DIR/car_insurance_$DATE.sql

# 压缩
gzip $BACKUP_DIR/car_insurance_$DATE.sql

# 删除旧备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 上传到云存储（可选）
# aws s3 cp $BACKUP_DIR/car_insurance_$DATE.sql.gz s3://your-bucket/backups/
```

```bash
# 配置 cron（每天凌晨 2 点）
0 2 * * * /opt/scripts/backup-db.sh >> /var/log/backup-db.log 2>&1
```

### 6.2 代码备份

- [ ] Git 仓库远程备份
- [ ] 定期创建 release tag
- [ ] 文档备份到云存储

---

## 🧪 七、部署验证

### 7.1 功能验证

| 验证项 | 预期结果 | 状态 |
|--------|----------|------|
| 健康检查接口 | 返回 200 | ⏳ 待验证 |
| 询价接口 | 返回报价结果 | ⏳ 待验证 |
| 策略配置接口 | 返回配置数据 | ⏳ 待验证 |
| 前端页面加载 | 正常显示 | ⏳ 待验证 |
| HTTPS 重定向 | 80→443 | ⏳ 待验证 |

### 7.2 性能验证

| 验证项 | 目标值 | 状态 |
|--------|--------|------|
| 首页加载时间 | < 2s | ⏳ 待验证 |
| API 响应时间 | < 500ms | ⏳ 待验证 |
| 并发 50 用户 | 成功率>95% | ⏳ 待验证 |

### 7.3 安全验证

| 验证项 | 预期结果 | 状态 |
|--------|----------|------|
| SQL 注入测试 | 被阻止 | ⏳ 待验证 |
| XSS 测试 | 被阻止 | ⏳ 待验证 |
| CSRF 保护 | 启用 | ⏳ 待验证 |
| HTTPS | 强制启用 | ⏳ 待验证 |

---

## 📝 八、回滚计划

### 8.1 回滚条件

- API 错误率 > 10%
- 核心功能不可用
- 数据库异常
- 性能严重下降

### 8.2 回滚步骤

```bash
# 1. 停止服务
sudo supervisorctl stop car-insurance

# 2. 恢复代码
cd /opt/car-insurance
git checkout <previous-version>

# 3. 恢复数据库（如需要）
mysql -u car_insurance -p car_insurance < /backup/car-insurance/db/car_insurance_YYYYMMDD.sql

# 4. 重启服务
sudo supervisorctl start car-insurance

# 5. 验证
curl https://api.insurance.com/health
```

---

## ✅ 九、部署检查清单

### 部署前（-1 天）

- [ ] 完成所有环境准备
- [ ] 完成数据库初始化
- [ ] 完成代码部署
- [ ] 完成配置检查
- [ ] 完成备份策略配置

### 部署日（D-Day）

- [ ] 00:00 - 开始部署窗口
- [ ] 00:30 - 后端部署完成
- [ ] 01:00 - 前端部署完成
- [ ] 01:30 - 功能验证完成
- [ ] 02:00 - 性能验证完成
- [ ] 02:30 - 安全验证完成
- [ ] 03:00 - 部署完成，观察期开始

### 部署后（+1 天）

- [ ] 监控系统运行正常
- [ ] 无重大告警
- [ ] 用户反馈正常
- [ ] 性能指标达标
- [ ] 关闭部署窗口

---

## 📞 十、联系方式

| 角色 | 姓名 | 电话 | 邮箱 |
|------|------|------|------|
| 项目经理 | 待定 | - | - |
| 技术负责人 | 待定 | - | - |
| 运维负责人 | 待定 | - | - |
| DBA | 待定 | - | - |

---

**文档版本**: v1.0  
**创建日期**: 2026-03-30  
**状态**: ✅ 已完成  
**下一步**: 按清单逐项执行部署

# 🚀 快速开始指南

> 5 分钟快速体验智能业务决策平台

---

## 📋 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- 内存 4GB+
- 磁盘 10GB+

---

## 🔧 方式一：本地部署（推荐）

### 步骤 1：克隆仓库

```bash
git clone https://github.com/Thomasmaomao/complex-scheduling-ai.git
cd complex-scheduling-ai/docs
```

### 步骤 2：运行部署脚本

```bash
chmod +x setup.sh
./setup.sh
```

### 步骤 3：访问系统

```
🌐 本地访问地址：
   - 前端：http://localhost:8002
   - API 文档：http://localhost:8001/docs

🌐 公网访问地址（推荐）：
   - 前端：http://47.103.19.238:8002
   - API 文档：http://47.103.19.238:8001/docs

🔐 演示环境说明：
   - 当前为公开演示，无需登录即可体验
   - 数据每日重置，请勿输入敏感信息
```

---

## 🌐 方式二：在线演示

**无需部署，直接体验！**

```
🌐 演示地址：http://47.103.19.238:8002

🔐 当前为公开演示，无需登录即可体验
```

**演示说明**：
- ✅ 开放体验：无需登录，直接访问
- ⚠️ 只读模式（不可保存策略）
- ⚠️ 数据每日重置，请勿输入真实信息

---

## 📖 方式三：查看文档

### 系统架构

详见：[ARCHITECTURE.md](ARCHITECTURE.md)

### 业务模型

详见：[BUSINESS-MODEL.md](BUSINESS-MODEL.md)

### API 文档

详见：[API-REFERENCE.md](API-REFERENCE.md)

---

## 🎯 快速体验流程

### 1. 查看策略总览（2 分钟）

1. 访问 http://47.103.19.238:8002/admin
2. 查看策略列表
3. 点击"详情"查看策略信息

### 2. 体验智能服务（3 分钟）

1. 访问 http://47.103.19.238:8002
2. 点击"智能服务" → "车险询价示例"
3. 查看智能推荐结果

### 3. 测试策略功能（5 分钟）

1. 访问 http://47.103.19.238:8002/admin
2. 点击"策略工厂" → "新建策略"
3. 完成 5 步向导
4. 运行模拟测试
5. 保存测试结果

---

## ❓ 常见问题

### Q1: 端口被占用怎么办？

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8003:8001"  # 修改前端端口
  - "8004:80"    # 修改后端端口
```

### Q2: 数据库连接失败？

检查 MySQL 是否启动：

```bash
docker-compose ps
docker-compose logs mysql
```

### Q3: 前端页面空白？

清除浏览器缓存（Ctrl+Shift+R）或检查：

```bash
docker-compose logs frontend
```

---

## 📬 获取帮助

- 📧 Email: shufe_myj@outlook.com
- 🌐 GitHub: https://github.com/Thomasmaomao/complex-scheduling-ai
- 📚 文档：https://github.com/Thomasmaomao/complex-scheduling-ai/tree/main/docs

---

**祝您使用愉快！** 🎉

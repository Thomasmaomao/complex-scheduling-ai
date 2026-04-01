# 车险询价系统 - 后端 API

## 项目简介

车险询价系统后端服务，基于 FastAPI 构建，提供精算模型驱动的智能报价功能。

## 技术栈

- **框架**: FastAPI
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **ORM**: SQLAlchemy 2.0
- **测试**: Pytest

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 询价模块 `/api/v1/quote`

- `POST /calculate` - 计算车险报价
- `GET /test-cases` - 获取测试用例
- `POST /batch-calculate` - 批量计算

### 策略模块 `/api/v1/strategy`

- `GET /config` - 获取策略配置
- `POST /config` - 保存策略配置
- `GET /list` - 策略列表
- `POST /test` - 测试策略

### 保司模块 `/api/v1/insurer`

- `GET /list` - 保司列表
- `GET /{insurer_id}` - 保司详情
- `POST /{insurer_id}/priority` - 更新优先级

### 分析模块 `/api/v1/analytics`

- `GET /dashboard` - 分析看板
- `GET /strategy/comparison` - 策略对比
- `GET /premium/analysis` - 保费分析

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_actuarial_model.py -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 项目结构

```
car-insurance-backend/
├── app/
│   ├── api/           # API 路由
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   ├── schemas/       # Pydantic Schema
│   ├── services/      # 业务服务
│   │   ├── actuarial_model.py  # 精算模型
│   │   └── strategy_engine.py  # 策略引擎
│   └── main.py        # 应用入口
├── tests/             # 测试文件
├── data/              # 数据文件
├── logs/              # 日志文件
├── requirements.txt   # 依赖
└── .env               # 环境配置
```

## 核心功能

### 精算模型

- 交强险保费计算
- 商业险保费计算（三者险、车损险等）
- 平台风险评分（0-100 分，10 档）
- 考虑因素：车型、地区、燃料类型、车主年龄等

### 策略引擎

- 多因子评分系统
- 智能保司推荐
- 推荐理由生成
- 策略配置与测试

## 版本

- **当前版本**: Beta v1.0
- **发布日期**: 2026-03-30

## 许可证

MIT License

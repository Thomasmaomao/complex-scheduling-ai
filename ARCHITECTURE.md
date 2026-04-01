# 🏗️ 架构设计

> 智能业务决策平台技术架构详解

---

## 📋 目录

1. [整体架构](#整体架构)
2. [技术栈](#技术栈)
3. [数据模型](#数据模型)
4. [核心模块](#核心模块)
5. [部署架构](#部署架构)

---

## 🏛️ 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                         用户层                                │
│  C 端用户 (车险询价)  |  B 端用户 (策略管理)                   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ 智能服务   │  │ 策略中心   │  │ 数据可视化 │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                     API 网关层 (FastAPI)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ 策略管理   │  │ 测试引擎   │  │ 数据分析   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                      数据访问层                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ MySQL      │  │ Redis      │  │ 文件系统   │            │
│  │ (主数据)   │  │ (缓存)     │  │ (日志)     │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## 💻 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.x | 核心框架 |
| Element Plus | 2.x | UI 组件库 |
| Vue Router | 4.x | 路由管理 |
| Pinia / Vuex | 4.x / 3.x | 状态管理 |
| Axios | 1.x | HTTP 客户端 |
| Vite | 4.x | 构建工具 |

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 核心语言 |
| FastAPI | 0.x | Web 框架 |
| Pydantic | 1.x / 2.x | 数据验证 |
| SQLAlchemy | 2.x | ORM |
| PyMySQL | 1.x | MySQL 驱动 |
| Redis | 7.x | 缓存 |

### 数据库

| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0 | 主数据库 |
| Redis | 7.x | 缓存/会话 |

### 部署

| 技术 | 版本 | 用途 |
|------|------|------|
| Docker | 20.10+ | 容器化 |
| Docker Compose | 2.x | 编排工具 |
| Nginx | 1.x | 反向代理 |

---

## 🗄️ 数据模型

### 核心表结构

```sql
-- 策略主表
strategies (
    id, name, description, status, version,
    fixed_cost_ratio, target_loss_ratio, market_expense_ratio,
    autonomous_discount_min, autonomous_discount_max, is_calculate,
    created_at, updated_at, created_by
)

-- 策略机构关联表
strategy_institutions (
    id, strategy_id, institution_code, institution_name
)

-- 策略业务单元表
strategy_business_units (
    id, strategy_id, unit_id, unit_name,
    fixed_cost_ratio, target_loss_ratio, market_expense_ratio,
    autonomous_discount_min, autonomous_discount_max, is_calculate
)

-- 业务单元主表
business_unit (
    id, unit_id, unit_name, description,
    policy_count, avg_premium, pure_risk_cost,
    expected_loss_ratio, expected_profit_margin
)

-- 测试结果表
strategy_test_results (
    id, strategy_id, test_type, passed, result_summary,
    conversion_rate_lift, profit_lift, p_value,
    completed_at, created_at
)

-- 策略版本表
strategy_versions (
    id, strategy_id, version_number, snapshot_data,
    change_summary, created_at, created_by
)
```

### 数据关系

```
strategies (1) ──→ (N) strategy_institutions
strategies (1) ──→ (N) strategy_business_units
strategies (1) ──→ (N) strategy_test_results
strategies (1) ──→ (N) strategy_versions

business_unit (1) ──→ (N) strategy_business_units
```

---

## 🔧 核心模块

### 1. 策略引擎 (Strategy Engine)

**位置**：`backend/app/services/strategy_engine.py`

**功能**：
- 保司推荐算法
- 多因子评分模型
- 策略匹配逻辑

**核心方法**：
```python
class StrategyEngine:
    def calculate_insurer_score(...)  # 计算保司评分
    def select_recommended_insurer(...)  # 选择推荐保司
    def get_all_insurer_quotes(...)  # 获取所有保司报价
```

### 2. 精算模型 (Actuarial Model)

**位置**：`backend/app/services/actuarial_model.py`

**功能**：
- 保费计算
- 风险评分
- 费率表管理

**核心方法**：
```python
class ActuarialModel:
    def calculate_full_premium(...)  # 计算完整保费
    def calculate_platform_risk_score(...)  # 计算平台风险评分
    def get_rate_table(...)  # 获取费率表
```

### 3. 测试引擎 (Test Engine)

**位置**：`backend/app/api/strategy.py`

**功能**：
- 模拟测试
- A/B 测试
- 情景测试

**API 端点**：
```python
POST /strategies/{strategy_id}/tests/simulation    # 模拟测试
POST /strategies/{strategy_id}/tests/ab            # A/B 测试
POST /strategies/{strategy_id}/tests/scenario      # 情景测试
```

### 4. 权限控制 (Permission Control)

**位置**：`backend/app/core/permission.py`

**功能**：
- 策略权限检查
- 用户角色管理
- 操作审计

**权限级别**：
- `owner` - 所有者（可删除）
- `editor` - 编辑者（可修改）
- `viewer` - 查看者（只读）
- `none` - 无权限

---

## 🚀 部署架构

### 开发环境

```
┌─────────────────┐
│   开发机器      │
│                 │
│  ┌───────────┐  │
│  │ 前端开发  │  │
│  │ :8002     │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ 后端开发  │  │
│  │ :8001     │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │  MySQL    │  │
│  │  :3306    │  │
│  └───────────┘  │
└─────────────────┘
```

### 生产环境

```
┌─────────────────────────────────────────┐
│              Nginx (反向代理)            │
│              :80 / :443                 │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Docker Compose 编排            │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │ Frontend │  │ Backend  │            │
│  │  :80     │  │  :8001   │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │  MySQL   │  │  Redis   │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

---

## 🔒 安全设计

### 1. 认证机制

- 基于用户 ID 的简单认证
- 会话管理（Redis）
- CORS 配置

### 2. 数据验证

- Pydantic 模型验证
- SQL 注入防护（参数化查询）
- XSS 防护（前端转义）

### 3. 权限控制

- 策略级别权限
- 操作级别权限
- 审计日志

---

## 📊 性能优化

### 1. 数据库优化

- 索引优化
- 查询优化
- 连接池管理

### 2. 缓存策略

- Redis 缓存热点数据
- 前端静态资源缓存
- API 响应缓存

### 3. 前端优化

- 组件懒加载
- 路由懒加载
- 静态资源压缩

---

## 📝 开发规范

### 代码风格

- Python: PEP 8
- JavaScript: ESLint + Prettier
- Vue: Vue Style Guide

### Git 工作流

```
main (生产)
  ↑
develop (开发)
  ↑
feature/* (功能分支)
```

### 提交规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

---

## 📬 技术支持

- 📧 Email: shufe_myj@outlook.com
- 🌐 GitHub: https://github.com/Thomasmaomao/complex-scheduling-ai

---

**文档创建者**：AI Assistant  
**最后更新**：2026-04-01  
**版本**：Beta 1.0

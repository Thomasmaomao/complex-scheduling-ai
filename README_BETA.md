# 🧠 智能业务决策平台

> **Intelligent Business Decision Platform**
>
> 由 AI Agent 全栈开发的业务决策系统 — 从需求分析到 UI 设计，从数据库建模到 API 开发

[![Beta](https://img.shields.io/badge/release-beta%201.0-blue)]()
[![AI-Powered](https://img.shields.io/badge/AI-Agent%20Developed-purple)]()
[![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-red)]()

---

## 🤖 本项目由 AI Agent 全栈开发

本项目完整展示了 AI Agent 在复杂业务系统开发中的全栈能力：

| 开发环节 | AI 贡献 | 人工参与 |
|---------|--------|---------|
| 📋 需求分析 | ✅ 业务场景抽象、用例设计 | 需求确认 |
| 🎨 UI/UX 设计 | ✅ 布局设计、配色方案、交互设计 | 风格确认 |
| 🗄️ 数据库设计 | ✅ 表结构设计、字段定义、数据预设 | 业务规则确认 |
| ⚙️ 后端开发 | ✅ API 设计、业务逻辑、数据验证 | 代码审查 |
| 🎭 前端开发 | ✅ 组件开发、状态管理、样式实现 | 交互确认 |
| 📊 数据建模 | ✅ 精算模型、情景参数、业务规则 | 模型验证 |
| 📚 文档编写 | ✅ 技术文档、API 文档、用户指南 | - |

**开发效率**：
- ⏱️ **8 天完成 MVP**（传统方式需 3-5 个月）
- 💰 **成本降低 80 万+**（从 80-120 万降到几乎 0）
- 👤 **1 人完成**（传统需 6-8 人月）
- 📝 **~3500 行代码**（精简高效）
- 🔄 **15+ 次快速迭代**
- 📖 **95%+ 文档完整度**

---

## 💡 核心价值

### 对业务负责人
- ✅ **可解释的决策引擎** — 每一步决策都有清晰的业务逻辑
- ✅ **情景模拟能力** — 政策调整前提前预估影响
- ✅ **多场景适配** — 金融、SaaS、保险，一套方法论

### 对技术负责人
- ✅ **清晰的分层架构** — 前端/后端/数据分离
- ✅ **可扩展的设计** — 策略引擎支持动态配置
- ✅ **完整的测试覆盖** — 单元测试 + 集成测试

### 对开发者
- ✅ **开箱即用** — 一键部署，5 分钟启动
- ✅ **完整文档** — 从业务模型到 API 详解
- ✅ **示例数据** — 内置演示数据，快速验证

---

## 🎯 核心功能

### 1. 智能服务（C 端场景演示）
- 🚗 **车险询价示例** — 演示 C 端用户实时决策场景
- 🎯 **智能决策结果** — 基于策略引擎的实时推荐
- 📊 **多维度对比** — 多家方案智能比价

### 2. 策略中心（B 端能力展示）
- 🏭 **策略工厂** — 策略总览、新建策略
- 🧪 **策略实验室** — 模拟测试、A/B 测试
- 📈 **效果看板** — 全量发布、效果追踪
- ⚙️ **渠道管理** — 渠道配置、动态调控

### 3. 业务建模
- 📊 **业务分群** — 多维度业务拆分，独立核算
- 🧮 **成本建模** — 量化收入、成本、风险
- 📈 **收益预测** — 多情景收益测算

---

## 🚀 快速开始

### 方式一：在线演示（推荐）

```
🌐 演示地址：http://47.103.19.238:8002

🔐 当前为公开演示，无需登录即可体验
```

**演示环境说明**：
- ✅ 开放体验：无需登录，直接访问
- ✅ 测试案例：内置演示数据，快速体验
- ⚠️ 数据每日重置，请勿输入真实信息
- ⚠️ 只读模式（不可保存策略）

**快速体验流程**：
1. 访问 http://47.103.19.238:8002
2. 点击"智能服务" → "车险询价示例"
3. 使用预设测试数据快速体验
4. 查看智能决策结果

### 方式二：本地部署

```bash
# 克隆仓库
git clone https://github.com/Thomasmaomao/complex-scheduling-ai.git
cd complex-scheduling-ai

# 运行部署脚本
./scripts/setup.sh

# 启动服务
docker-compose up -d

# 访问 http://localhost:8080
```

**系统要求**：
- Docker 20.10+
- 内存 4GB+
- 磁盘 10GB+

---

## 📊 适用场景

| 行业 | 应用场景 | 核心价值 |
|------|---------|---------|
| 💰 **金融科技** | 信贷定价、风控策略、资产组合优化 | 风险 - 收益平衡 |
| 💻 **SaaS 服务** | 订阅定价、套餐设计、续费策略 | LTV/CAC 优化 |
| 🛡️ **保险科技** | 精算定价、承保策略、再保优化 | 赔付率控制 |

---

## 📚 文档导航

- [📖 系统概述](docs/OVERVIEW.md) — 完整介绍
- [🏗️ 架构设计](docs/ARCHITECTURE.md) — 技术架构详解
- [📊 业务模型](docs/BUSINESS-MODEL.md) — 核心方法论
- [🎯 适用场景](docs/SCENARIOS.md) — 多行业应用
- [🚀 部署指南](docs/DEPLOYMENT.md) — 本地部署步骤
- [📝 API 文档](docs/API-REFERENCE.md) — 完整 API 说明
- [❓ 常见问题](docs/FAQ.md) — FAQ

---

## 📸 系统截图

### 首页 - 智能业务决策平台
![首页](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/EJq6bkJCHowLKUxCDhzcPdDSnBb)

### 车险询价示例
![车险询价](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/CQwubrD93oOTNuxX2OacPJ3unVe)

### 智能决策结果
![决策结果](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/SvOAb97pJoW6w8xUFABc9DLKnic)

### 策略中心侧边栏
![策略中心](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/XN5ebvab7okH8gx1tfhctNr9nxQ)

### 策略总览
![策略总览](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/ZyvgbG9FkokaLJx2qKPcTLPfnnN)

### 情景分析
![情景分析](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/all/BbdSbInZBoCuMuxEKyfcwSAtn0c)

> 更多截图详见飞书文档：[📸 截图拍摄清单](https://my.feishu.cn/docx/GMnDdAZOpoDeURx59bscENvYnPt)

---

## 🛡️ 数据安全说明

- ✅ 演示数据完全脱敏
- ✅ 使用代号（保司 A/B/C）
- ✅ 敏感配置环境变量
- ✅ 示例数据均为虚构

详见：[SECURITY.md](SECURITY.md)

---

## 📄 版权说明

**CC BY-NC-SA 4.0** — 禁止商用，详见 [LICENSE](LICENSE)

- ✅ 允许学习、研究、修改、分享
- ❌ **禁止商业用途**
- ✅ 修改后必须使用相同协议

---

## 📬 联系合作

- 📧 Email: shufe_myj@outlook.com
- 🌐 GitHub: https://github.com/Thomasmaomao/complex-scheduling-ai

---

## 🙏 致谢

本项目由 [OpenClaw](https://github.com/openclaw/openclaw) AI Agent 全栈开发。

---

**🌟 如果这个项目对你有帮助，请给一个 Star！**

-- 车险询价系统 - 策略管理数据库表结构
-- 创建时间：2026-03-31
-- 版本：v1.1

-- 使用数据库
USE car_insurance;

-- ============================================
-- 1. 策略主表
-- ============================================
DROP TABLE IF EXISTS `strategies`;
CREATE TABLE `strategies` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '策略 ID（strategy_时间戳_随机数）',
  `name` VARCHAR(200) NOT NULL COMMENT '策略名称',
  `description` TEXT COMMENT '策略描述',
  
  -- 策略参数（修改精度为 DECIMAL(6,4) 允许超过 1 的值）
  `fixed_cost_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.1000 COMMENT '固定成本率',
  `target_loss_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.7500 COMMENT '目标赔付率',
  `market_expense_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.1200 COMMENT '市场费用率',
  `autonomous_discount_min` DECIMAL(6,4) NOT NULL DEFAULT 0.5000 COMMENT '自主系数下限',
  `autonomous_discount_max` DECIMAL(6,4) NOT NULL DEFAULT 0.6500 COMMENT '自主系数上限',
  
  -- 适用范围
  `scope_type` ENUM('all', 'specified', 'channel') DEFAULT 'specified' COMMENT '发布范围类型',
  
  -- 状态管理
  `status` ENUM(
    'draft',              -- 草稿：策略配置中心已保存
    'simulation_passed',  -- 模拟测试通过
    'simulation_failed',  -- 模拟测试失败
    'ab_test_passed',     -- A/B 测试通过
    'ab_test_failed',     -- A/B 测试失败
    'published',          -- 已发布（生产环境生效）
    'archived'            -- 已归档（历史版本）
  ) DEFAULT 'draft' COMMENT '策略状态',
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(64) COMMENT '创建人',
  
  -- 索引
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表';

-- ============================================
-- 2. 策略 - 机构关联表
-- ============================================
DROP TABLE IF EXISTS `strategy_institutions`;
CREATE TABLE `strategy_institutions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID',
  `institution_code` VARCHAR(50) NOT NULL COMMENT '机构代码（shanghai, beijing, ...）',
  `institution_name` VARCHAR(100) NOT NULL COMMENT '机构名称（上海，北京，...）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `uk_strategy_institution` (`strategy_id`, `institution_code`),
  INDEX `idx_institution` (`institution_code`),
  INDEX `idx_strategy_id` (`strategy_id`),
  CONSTRAINT `fk_strategy_institutions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略 - 机构关联表';

-- ============================================
-- 3. 策略 - 业务单元关联表
-- ============================================
DROP TABLE IF EXISTS `strategy_business_units`;
CREATE TABLE `strategy_business_units` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID',
  `unit_id` VARCHAR(50) NOT NULL COMMENT '业务单元 ID（BU001, BU002, ...）',
  `unit_name` VARCHAR(100) NOT NULL COMMENT '业务单元名称（燃油车 - 续保，...）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `uk_strategy_unit` (`strategy_id`, `unit_id`),
  INDEX `idx_strategy_id` (`strategy_id`),
  INDEX `idx_unit_id` (`unit_id`),
  CONSTRAINT `fk_strategy_business_units_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略 - 业务单元关联表';

-- ============================================
-- 4. 策略测试记录表
-- ============================================
DROP TABLE IF EXISTS `strategy_test_results`;
CREATE TABLE `strategy_test_results` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '测试记录 ID',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID',
  
  -- 测试类型
  `test_type` ENUM('simulation', 'ab_test') NOT NULL COMMENT '测试类型',
  
  -- 测试结果
  `passed` TINYINT(1) NOT NULL COMMENT '是否通过（1=通过，0=失败）',
  `result_summary` TEXT COMMENT '测试结果摘要（成交率 +X%，利润 +X%）',
  
  -- 详细指标
  `conversion_rate_lift` DECIMAL(6,4) COMMENT '成交率提升（百分比）',
  `profit_lift` DECIMAL(6,4) COMMENT '利润提升（百分点）',
  `p_value` DECIMAL(8,5) COMMENT 'P 值（统计显著性）',
  
  -- 测试配置
  `sample_size` INT COMMENT '样本量',
  `test_duration_days` INT COMMENT '测试周期（天）',
  `control_group` VARCHAR(100) COMMENT '对照组',
  `treatment_group` VARCHAR(100) COMMENT '实验组',
  
  -- 时间戳
  `started_at` DATETIME COMMENT '测试开始时间',
  `completed_at` DATETIME COMMENT '测试完成时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  INDEX `idx_strategy` (`strategy_id`),
  INDEX `idx_test_type` (`test_type`),
  INDEX `idx_passed` (`passed`),
  CONSTRAINT `fk_strategy_test_results_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略测试记录表';

-- ============================================
-- 5. 策略发布记录表
-- ============================================
DROP TABLE IF EXISTS `strategy_publish_records`;
CREATE TABLE `strategy_publish_records` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '发布记录 ID（PUB_时间戳_随机数）',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID',
  
  -- 发布配置
  `publish_scope` ENUM('all', 'specified', 'channel') NOT NULL COMMENT '发布范围',
  `publish_description` TEXT COMMENT '发布描述',
  `rollback_plan` TEXT COMMENT '回滚预案',
  
  -- 发布时间
  `timing_type` ENUM('immediate', 'scheduled') NOT NULL DEFAULT 'immediate' COMMENT '发布时间类型',
  `scheduled_time` DATETIME COMMENT '定时发布时间',
  `published_at` DATETIME COMMENT '实际发布时间',
  
  -- 发布状态
  `publish_status` ENUM('pending', 'published', 'rolled_back', 'failed') DEFAULT 'pending' COMMENT '发布状态',
  
  -- 发布后指标（用于追踪效果）
  `post_publish_profit` DECIMAL(10,2) COMMENT '发布后利润',
  `post_publish_conversion` DECIMAL(6,4) COMMENT '发布后成交率',
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX `idx_strategy` (`strategy_id`),
  INDEX `idx_status` (`publish_status`),
  INDEX `idx_published_at` (`published_at`),
  CONSTRAINT `fk_strategy_publish_records_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略发布记录表';

-- ============================================
-- 6. 策略发布 - 机构关联表
-- ============================================
DROP TABLE IF EXISTS `strategy_publish_institutions`;
CREATE TABLE `strategy_publish_institutions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `publish_id` VARCHAR(64) NOT NULL COMMENT '发布记录 ID',
  `institution_code` VARCHAR(50) NOT NULL COMMENT '机构代码',
  `institution_name` VARCHAR(100) NOT NULL COMMENT '机构名称',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `uk_publish_institution` (`publish_id`, `institution_code`),
  INDEX `idx_publish_id` (`publish_id`),
  INDEX `idx_institution_code` (`institution_code`),
  CONSTRAINT `fk_strategy_publish_institutions_publish` 
    FOREIGN KEY (`publish_id`) REFERENCES `strategy_publish_records`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略发布 - 机构关联表';

-- ============================================
-- 初始化数据 - 示例策略
-- ============================================
INSERT IGNORE INTO `strategies` (`id`, `name`, `description`, `fixed_cost_ratio`, `target_loss_ratio`, `market_expense_ratio`, `autonomous_discount_min`, `autonomous_discount_max`, `status`, `created_by`) VALUES
('strategy_init_001', '基准策略（自主系数 0.68）', '当前线上策略', 0.1000, 0.7500, 0.1200, 0.6800, 0.6800, 'published', 'system'),
('strategy_init_002', '激进策略（自主系数 0.53）', '降低自主系数，提升成交率', 0.1000, 0.7500, 0.1200, 0.5300, 0.5300, 'draft', 'system'),
('strategy_init_003', '保守策略（自主系数 0.75）', '提高自主系数，保证利润率', 0.1000, 0.7500, 0.1200, 0.7500, 0.7500, 'draft', 'system');

-- 初始化机构关联
INSERT IGNORE INTO `strategy_institutions` (`strategy_id`, `institution_code`, `institution_name`) VALUES
('strategy_init_001', 'shanghai', '上海'),
('strategy_init_001', 'beijing', '北京'),
('strategy_init_001', 'guangdong', '广东'),
('strategy_init_001', 'zhejiang', '浙江');

-- 初始化业务单元关联
INSERT IGNORE INTO `strategy_business_units` (`strategy_id`, `unit_id`, `unit_name`) VALUES
('strategy_init_001', 'BU001', '燃油车 - 续保'),
('strategy_init_001', 'BU002', '燃油车 - 新保'),
('strategy_init_001', 'BU003', '新能源 - 高价值'),
('strategy_init_001', 'BU004', '新能源 - 普通'),
('strategy_init_001', 'BU005', '豪车 - 续保');

-- ============================================
-- 视图：策略完整信息（含关联数据）
-- ============================================
DROP VIEW IF EXISTS `v_strategy_full`;
CREATE VIEW `v_strategy_full` AS
SELECT 
  s.*,
  GROUP_CONCAT(DISTINCT si.institution_name ORDER BY si.institution_name SEPARATOR ',') AS institutions,
  GROUP_CONCAT(DISTINCT sbu.unit_name ORDER BY sbu.unit_name SEPARATOR ',') AS business_units
FROM `strategies` s
LEFT JOIN `strategy_institutions` si ON s.id = si.strategy_id
LEFT JOIN `strategy_business_units` sbu ON s.id = sbu.strategy_id
GROUP BY s.id;

-- ============================================
-- 说明
-- ============================================
-- 1. 所有策略 ID 统一格式：strategy_时间戳_随机数
-- 2. 发布记录 ID 统一格式：PUB_时间戳_随机数
-- 3. 测试记录 ID 统一格式：TEST_时间戳_随机数
-- 4. 状态流转：draft → simulation_passed/failed → ab_test_passed/failed → published → archived
-- 5. 外键级联删除：删除策略时，自动删除关联的机构、业务单元、测试记录、发布记录
-- 6. v1.1 变更：
--    - 修改 DECIMAL 精度从 (5,4) 改为 (6,4)，允许超过 1 的值
--    - 为所有外键添加索引（idx_strategy_id, idx_publish_id 等）
--    - 为外键约束添加命名（fk_xxx）

-- ============================================
-- 车险询价系统 - 策略管理模块 Phase 1 数据库迁移
-- ============================================
-- 创建时间：2026-03-31 18:38
-- 版本：v3.0（根据 STRATEGY_DESIGN_V3.md）
-- 说明：创建完整的 7 个策略管理表
-- ============================================

SET FOREIGN_KEY_CHECKS = 0;

USE car_insurance;

-- ============================================
-- 1. strategies（策略主表）
-- ============================================
DROP TABLE IF EXISTS `strategies`;
CREATE TABLE `strategies` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '策略 ID（strategy_时间戳_随机数）',
  `name` VARCHAR(200) NOT NULL COMMENT '策略名称',
  `description` TEXT COMMENT '策略描述',
  
  -- 策略参数（全局兜底参数）
  `fixed_cost_ratio` DECIMAL(6,4) COMMENT '固定成本率（全局兜底）',
  `target_loss_ratio` DECIMAL(6,4) COMMENT '目标赔付率（全局兜底）',
  `market_expense_ratio` DECIMAL(6,4) COMMENT '市场费用率（全局兜底）',
  `autonomous_discount_min` DECIMAL(6,4) COMMENT '自主系数下限（全局兜底）',
  `autonomous_discount_max` DECIMAL(6,4) COMMENT '自主系数上限（全局兜底）',
  `is_calculate` TINYINT(1) DEFAULT 0 COMMENT '是否反算折扣（全局兜底）',
  
  -- 发布范围
  `scope_type` ENUM('all', 'specified', 'channel') DEFAULT 'specified' COMMENT '发布范围类型',
  
  -- 状态管理
  `status` ENUM(
    'draft',
    'simulation_passed',
    'simulation_failed',
    'ab_test_passed',
    'ab_test_failed',
    'published',
    'disabled',
    'archived'
  ) DEFAULT 'draft' COMMENT '策略状态',
  
  -- 乐观锁
  `version` INT DEFAULT 1 COMMENT '版本号（乐观锁）',
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(64) COMMENT '创建人',
  
  -- 索引
  INDEX `idx_status` (`status`),
  INDEX `idx_created_at` (`created_at`),
  INDEX `idx_version` (`version`),
  INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表';

-- ============================================
-- 2. strategy_institutions（策略 - 机构关联表）
-- ============================================
DROP TABLE IF EXISTS `strategy_institutions`;
CREATE TABLE `strategy_institutions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `institution_code` VARCHAR(50) NOT NULL COMMENT '机构代码',
  `institution_name` VARCHAR(100) NOT NULL COMMENT '机构名称',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 约束
  UNIQUE KEY `uk_strategy_institution` (`strategy_id`, `institution_code`),
  INDEX `idx_strategy_id` (`strategy_id`),
  INDEX `idx_institution_code` (`institution_code`),
  CONSTRAINT `fk_strategy_institutions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略 - 机构关联表';

-- ============================================
-- 3. strategy_business_units（策略 - 业务单元关联表）
-- ============================================
DROP TABLE IF EXISTS `strategy_business_units`;
CREATE TABLE `strategy_business_units` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `unit_id` VARCHAR(50) NOT NULL COMMENT '业务单元 ID',
  `unit_name` VARCHAR(100) NOT NULL COMMENT '业务单元名称',
  
  -- 独立参数（可选，NULL 表示使用全局参数）
  `fixed_cost_ratio` DECIMAL(6,4) NULL COMMENT '固定成本率（独立参数）',
  `target_loss_ratio` DECIMAL(6,4) NULL COMMENT '目标赔付率（独立参数）',
  `market_expense_ratio` DECIMAL(6,4) NULL COMMENT '市场费用率（独立参数）',
  `autonomous_discount_min` DECIMAL(6,4) NULL COMMENT '自主系数下限（独立参数）',
  `autonomous_discount_max` DECIMAL(6,4) NULL COMMENT '自主系数上限（独立参数）',
  `is_calculate` TINYINT(1) NULL COMMENT '是否反算折扣（独立参数）',
  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 约束
  UNIQUE KEY `uk_strategy_unit` (`strategy_id`, `unit_id`),
  INDEX `idx_strategy_id` (`strategy_id`),
  INDEX `idx_unit_id` (`unit_id`),
  CONSTRAINT `fk_strategy_business_units_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略 - 业务单元关联表';

-- ============================================
-- 4. strategy_permissions（策略权限表）
-- ============================================
DROP TABLE IF EXISTS `strategy_permissions`;
CREATE TABLE `strategy_permissions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户 ID',
  `role` ENUM('owner', 'editor', 'viewer') NOT NULL COMMENT '角色',
  `granted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  
  -- 约束
  UNIQUE KEY `uk_strategy_user` (`strategy_id`, `user_id`),
  INDEX `idx_strategy_id` (`strategy_id`),
  INDEX `idx_user_id` (`user_id`),
  CONSTRAINT `fk_strategy_permissions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略权限表';

-- ============================================
-- 5. strategy_versions（策略版本表）
-- ============================================
DROP TABLE IF EXISTS `strategy_versions`;
CREATE TABLE `strategy_versions` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '版本 ID（version_时间戳_随机数）',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `version_number` INT NOT NULL COMMENT '版本号',
  `snapshot_data` JSON NOT NULL COMMENT '完整策略快照',
  `change_summary` TEXT COMMENT '变更摘要',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(64) COMMENT '创建人',
  
  -- 约束
  INDEX `idx_strategy_version` (`strategy_id`, `version_number`),
  INDEX `idx_strategy_id` (`strategy_id`),
  CONSTRAINT `fk_strategy_versions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略版本表';

-- ============================================
-- 6. strategy_test_results（策略测试记录表）
-- ============================================
DROP TABLE IF EXISTS `strategy_test_results`;
CREATE TABLE `strategy_test_results` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '测试记录 ID',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  
  -- 测试类型
  `test_type` ENUM('simulation', 'ab_test') NOT NULL COMMENT '测试类型',
  
  -- 测试结果
  `passed` TINYINT(1) NOT NULL COMMENT '是否通过',
  `result_summary` TEXT COMMENT '测试结果摘要',
  
  -- 详细指标
  `conversion_rate_lift` DECIMAL(6,4) COMMENT '成交率提升',
  `profit_lift` DECIMAL(6,4) COMMENT '利润提升',
  `p_value` DECIMAL(8,5) COMMENT 'P 值',
  
  -- 测试配置
  `sample_size` INT COMMENT '样本量',
  
  -- 时间戳
  `completed_at` DATETIME COMMENT '完成时间',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 约束
  INDEX `idx_strategy` (`strategy_id`),
  INDEX `idx_test_type` (`test_type`),
  INDEX `idx_passed` (`passed`),
  CONSTRAINT `fk_strategy_test_results_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略测试记录表';

-- ============================================
-- 7. strategy_publish_records（策略发布记录表）
-- ============================================
DROP TABLE IF EXISTS `strategy_publish_records`;
CREATE TABLE `strategy_publish_records` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '发布记录 ID',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  
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
  
  -- 时间戳
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  
  -- 约束
  INDEX `idx_strategy` (`strategy_id`),
  INDEX `idx_publish_status` (`publish_status`),
  INDEX `idx_published_at` (`published_at`),
  CONSTRAINT `fk_strategy_publish_records_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略发布记录表';

-- ============================================
-- 初始化数据
-- ============================================

-- 插入示例策略
INSERT INTO `strategies` (`id`, `name`, `description`, `fixed_cost_ratio`, `target_loss_ratio`, `market_expense_ratio`, `autonomous_discount_min`, `autonomous_discount_max`, `is_calculate`, `scope_type`, `status`, `version`, `created_by`) VALUES
('strategy_20260331_0001', '燃油车续保策略', '针对燃油车续保客户的差异化定价策略', 0.1000, 0.7500, 0.1200, 0.5000, 0.6500, 1, 'specified', 'draft', 1, 'admin'),
('strategy_20260331_0002', '新能源策略', '新能源车辆专属定价策略', 0.0800, 0.7000, 0.1500, 0.5500, 0.7000, 1, 'specified', 'draft', 1, 'admin'),
('strategy_20260331_0003', '豪车策略', '高端车辆专属定价策略', 0.1200, 0.6500, 0.1000, 0.6000, 0.8000, 0, 'all', 'draft', 1, 'admin');

-- 插入示例机构关联
INSERT INTO `strategy_institutions` (`strategy_id`, `institution_code`, `institution_name`) VALUES
('strategy_20260331_0001', 'shanghai', '上海'),
('strategy_20260331_0001', 'beijing', '北京'),
('strategy_20260331_0002', 'shanghai', '上海'),
('strategy_20260331_0002', 'guangdong', '广东'),
('strategy_20260331_0003', 'shanghai', '上海'),
('strategy_20260331_0003', 'beijing', '北京'),
('strategy_20260331_0003', 'guangdong', '广东'),
('strategy_20260331_0003', 'zhejiang', '浙江');

-- 插入示例业务单元关联
INSERT INTO `strategy_business_units` (`strategy_id`, `unit_id`, `unit_name`) VALUES
('strategy_20260331_0001', 'BU001', '燃油车 - 续保'),
('strategy_20260331_0001', 'BU002', '燃油车 - 新保'),
('strategy_20260331_0002', 'BU003', '新能源 - 高价值'),
('strategy_20260331_0002', 'BU004', '新能源 - 普通'),
('strategy_20260331_0003', 'BU005', '豪车 - 续保'),
('strategy_20260331_0003', 'BU006', '豪车 - 新保');

-- 插入示例权限（admin 为所有策略的 owner）
INSERT INTO `strategy_permissions` (`strategy_id`, `user_id`, `role`) VALUES
('strategy_20260331_0001', 'admin', 'owner'),
('strategy_20260331_0002', 'admin', 'owner'),
('strategy_20260331_0003', 'admin', 'owner');

-- ============================================
-- 创建视图：策略完整信息
-- ============================================
DROP VIEW IF EXISTS `v_strategy_full`;
CREATE VIEW `v_strategy_full` AS
SELECT 
  s.id,
  s.name,
  s.description,
  s.status,
  s.version,
  s.scope_type,
  s.created_at,
  s.created_by,
  GROUP_CONCAT(DISTINCT si.institution_name ORDER BY si.institution_name SEPARATOR ',') AS institutions,
  COUNT(DISTINCT sbu.unit_id) AS business_unit_count
FROM `strategies` s
LEFT JOIN `strategy_institutions` si ON s.id = si.strategy_id
LEFT JOIN `strategy_business_units` sbu ON s.id = sbu.strategy_id
GROUP BY s.id;

-- ============================================
-- 验证迁移结果
-- ============================================
SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Migration Phase 1 completed successfully!' AS status;
SELECT COUNT(*) AS strategy_count FROM strategies;
SELECT COUNT(*) AS institution_count FROM strategy_institutions;
SELECT COUNT(*) AS business_unit_count FROM strategy_business_units;
SELECT COUNT(*) AS permission_count FROM strategy_permissions;
SELECT COUNT(*) AS version_count FROM strategy_versions;
SELECT COUNT(*) AS test_count FROM strategy_test_results;
SELECT COUNT(*) AS publish_count FROM strategy_publish_records;

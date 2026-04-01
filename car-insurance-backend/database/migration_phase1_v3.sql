-- 车险询价系统 - 策略管理模块 Phase 1 数据库迁移脚本
-- 设计文档版本：v3.0
-- 创建时间：2026-03-31
-- 阶段：Phase 1 - 数据库迁移
-- 说明：在现有表结构上添加新字段和新表，支持权限控制、版本管理和乐观锁

USE car_insurance;

-- ============================================
-- 开始迁移
-- ============================================
SELECT '🚀 开始 Phase 1 数据库迁移...' AS status;

-- ============================================
-- 1. 备份现有数据
-- ============================================
SELECT '📦 备份现有数据...' AS step;

-- 创建临时备份表（如果 strategies 表存在）
DROP TABLE IF EXISTS `strategies_backup_phase1`;
CREATE TABLE `strategies_backup_phase1` AS SELECT * FROM `strategies` WHERE 1=0;

INSERT INTO `strategies_backup_phase1` SELECT * FROM `strategies`;

SELECT CONCAT('✅ 已备份 strategies 表，共 ', ROW_COUNT(), ' 条记录') AS status;

-- ============================================
-- 2. 修改 strategies 表 - 添加 version 字段（乐观锁）
-- ============================================
SELECT '🔧 修改 strategies 表 - 添加 version 字段...' AS step;

-- 检查 version 字段是否已存在
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategies' 
    AND COLUMN_NAME = 'version'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategies` ADD COLUMN `version` INT NOT NULL DEFAULT 1 COMMENT ''版本号（乐观锁）'' AFTER `status`',
    'SELECT ''✅ version 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 为 version 字段添加索引
SET @index_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategies' 
    AND INDEX_NAME = 'idx_version'
);

SET @sql = IF(@index_exists = 0,
    'ALTER TABLE `strategies` ADD INDEX `idx_version` (`version`)',
    'SELECT ''✅ idx_version 索引已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '✅ strategies 表 version 字段添加完成' AS status;

-- ============================================
-- 3. 修改 strategies 表 - 添加 is_calculate 字段
-- ============================================
SELECT '🔧 修改 strategies 表 - 添加 is_calculate 字段...' AS step;

-- 检查 is_calculate 字段是否已存在
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategies' 
    AND COLUMN_NAME = 'is_calculate'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategies` ADD COLUMN `is_calculate` TINYINT(1) NOT NULL DEFAULT 0 COMMENT ''是否反算折扣（全局兜底）'' AFTER `autonomous_discount_max`',
    'SELECT ''✅ is_calculate 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '✅ strategies 表 is_calculate 字段添加完成' AS status;

-- ============================================
-- 4. 修改 strategy_business_units 表 - 添加独立参数字段
-- ============================================
SELECT '🔧 修改 strategy_business_units 表 - 添加独立参数字段...' AS step;

-- 添加 fixed_cost_ratio
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'fixed_cost_ratio'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `fixed_cost_ratio` DECIMAL(6,4) DEFAULT NULL COMMENT ''固定成本率（独立参数）'' AFTER `unit_name`',
    'SELECT ''✅ fixed_cost_ratio 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 target_loss_ratio
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'target_loss_ratio'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `target_loss_ratio` DECIMAL(6,4) DEFAULT NULL COMMENT ''目标赔付率（独立参数）'' AFTER `fixed_cost_ratio`',
    'SELECT ''✅ target_loss_ratio 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 market_expense_ratio
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'market_expense_ratio'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `market_expense_ratio` DECIMAL(6,4) DEFAULT NULL COMMENT ''市场费用率（独立参数）'' AFTER `target_loss_ratio`',
    'SELECT ''✅ market_expense_ratio 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 autonomous_discount_min
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'autonomous_discount_min'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `autonomous_discount_min` DECIMAL(6,4) DEFAULT NULL COMMENT ''自主系数下限（独立参数）'' AFTER `market_expense_ratio`',
    'SELECT ''✅ autonomous_discount_min 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 autonomous_discount_max
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'autonomous_discount_max'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `autonomous_discount_max` DECIMAL(6,4) DEFAULT NULL COMMENT ''自主系数上限（独立参数）'' AFTER `autonomous_discount_min`',
    'SELECT ''✅ autonomous_discount_max 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 is_calculate
SET @column_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'car_insurance' 
    AND TABLE_NAME = 'strategy_business_units' 
    AND COLUMN_NAME = 'is_calculate'
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE `strategy_business_units` ADD COLUMN `is_calculate` TINYINT(1) DEFAULT NULL COMMENT ''是否反算折扣（独立参数）'' AFTER `autonomous_discount_max`',
    'SELECT ''✅ is_calculate 字段已存在'' AS skip'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT '✅ strategy_business_units 表独立参数字段添加完成' AS status;

-- ============================================
-- 5. 创建 strategy_permissions 表（新增）
-- ============================================
SELECT '🔧 创建 strategy_permissions 表...' AS step;

DROP TABLE IF EXISTS `strategy_permissions`;
CREATE TABLE `strategy_permissions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '自增主键',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `user_id` VARCHAR(64) NOT NULL COMMENT '用户 ID',
  `role` VARCHAR(50) NOT NULL COMMENT '角色（owner/editor/viewer）',
  `granted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
  
  UNIQUE KEY `uk_strategy_user` (`strategy_id`, `user_id`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_strategy_id` (`strategy_id`),
  CONSTRAINT `fk_strategy_permissions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略权限表';

SELECT '✅ strategy_permissions 表创建完成' AS status;

-- ============================================
-- 6. 创建 strategy_versions 表（新增）
-- ============================================
SELECT '🔧 创建 strategy_versions 表...' AS step;

DROP TABLE IF EXISTS `strategy_versions`;
CREATE TABLE `strategy_versions` (
  `id` VARCHAR(64) PRIMARY KEY COMMENT '版本 ID（version_时间戳_随机数）',
  `strategy_id` VARCHAR(64) NOT NULL COMMENT '策略 ID（外键）',
  `version_number` INT NOT NULL COMMENT '版本号（从 1 开始递增）',
  `snapshot_data` JSON NOT NULL COMMENT '完整策略快照（含所有参数）',
  `change_summary` TEXT COMMENT '变更摘要',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(64) COMMENT '创建人',
  
  INDEX `idx_strategy_version` (`strategy_id`, `version_number`),
  INDEX `idx_strategy_id` (`strategy_id`),
  CONSTRAINT `fk_strategy_versions_strategy` 
    FOREIGN KEY (`strategy_id`) REFERENCES `strategies`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略版本表';

SELECT '✅ strategy_versions 表创建完成' AS status;

-- ============================================
-- 7. 更新 strategies 表的 status 枚举（添加 disabled 状态）
-- ============================================
SELECT '🔧 更新 strategies 表 status 枚举...' AS step;

-- 修改 status 字段，添加 disabled 状态
ALTER TABLE `strategies` 
MODIFY COLUMN `status` ENUM(
    'draft',              -- 草稿：策略配置中心已保存
    'simulation_passed',  -- 模拟测试通过
    'simulation_failed',  -- 模拟测试失败
    'ab_test_passed',     -- A/B 测试通过
    'ab_test_failed',     -- A/B 测试失败
    'published',          -- 已发布（生产环境生效）
    'archived',           -- 已归档（历史版本）
    'disabled'            -- 已禁用（软删除）
  ) DEFAULT 'draft' COMMENT '策略状态';

SELECT '✅ strategies 表 status 枚举更新完成' AS status;

-- ============================================
-- 8. 初始化权限数据（为现有策略创建 owner 权限）
-- ============================================
SELECT '🔧 初始化权限数据...' AS step;

-- 为现有策略的创建人分配 owner 权限
INSERT INTO `strategy_permissions` (`strategy_id`, `user_id`, `role`, `granted_at`)
SELECT 
    s.id AS strategy_id,
    COALESCE(s.created_by, 'system') AS user_id,
    'owner' AS role,
    s.created_at AS granted_at
FROM `strategies` s
WHERE NOT EXISTS (
    SELECT 1 FROM `strategy_permissions` sp 
    WHERE sp.strategy_id = s.id AND sp.user_id = COALESCE(s.created_by, 'system')
);

SELECT CONCAT('✅ 已初始化 ', ROW_COUNT(), ' 条权限记录') AS status;

-- ============================================
-- 9. 为现有策略初始化 version 字段
-- ============================================
SELECT '🔧 初始化 version 字段...' AS step;

UPDATE `strategies` 
SET `version` = 1 
WHERE `version` IS NULL OR `version` = 0;

SELECT CONCAT('✅ 已初始化 ', ROW_COUNT(), ' 条记录的 version 字段') AS status;

-- ============================================
-- 10. 验证表结构
-- ============================================
SELECT '🔍 验证表结构...' AS step;

-- 验证 strategies 表结构
SELECT 'strategies 表结构:' AS table_name;
DESC `strategies`;

-- 验证 strategy_business_units 表结构
SELECT 'strategy_business_units 表结构:' AS table_name;
DESC `strategy_business_units`;

-- 验证 strategy_permissions 表结构
SELECT 'strategy_permissions 表结构:' AS table_name;
DESC `strategy_permissions`;

-- 验证 strategy_versions 表结构
SELECT 'strategy_versions 表结构:' AS table_name;
DESC `strategy_versions`;

-- ============================================
-- 11. 验证索引
-- ============================================
SELECT '🔍 验证索引...' AS step;

-- 检查 strategies 表索引
SELECT 'strategies 表索引:' AS index_check;
SHOW INDEX FROM `strategies`;

-- 检查 strategy_permissions 表索引
SELECT 'strategy_permissions 表索引:' AS index_check;
SHOW INDEX FROM `strategy_permissions`;

-- 检查 strategy_versions 表索引
SELECT 'strategy_versions 表索引:' AS index_check;
SHOW INDEX FROM `strategy_versions`;

-- ============================================
-- 12. 数据完整性检查
-- ============================================
SELECT '🔍 数据完整性检查...' AS step;

-- 统计各表记录数
SELECT 'strategies' AS table_name, COUNT(*) AS record_count FROM `strategies`
UNION ALL
SELECT 'strategy_institutions' AS table_name, COUNT(*) AS record_count FROM `strategy_institutions`
UNION ALL
SELECT 'strategy_business_units' AS table_name, COUNT(*) AS record_count FROM `strategy_business_units`
UNION ALL
SELECT 'strategy_permissions' AS table_name, COUNT(*) AS record_count FROM `strategy_permissions`
UNION ALL
SELECT 'strategy_versions' AS table_name, COUNT(*) AS record_count FROM `strategy_versions`
UNION ALL
SELECT 'strategy_test_results' AS table_name, COUNT(*) AS record_count FROM `strategy_test_results`
UNION ALL
SELECT 'strategy_publish_records' AS table_name, COUNT(*) AS record_count FROM `strategy_publish_records`;

-- ============================================
-- 迁移完成
-- ============================================
SELECT '✅=========================================' AS status;
SELECT '✅ Phase 1 数据库迁移完成！' AS status;
SELECT '✅=========================================' AS status;
SELECT '变更摘要:' AS summary;
SELECT '  1. strategies 表新增 version 字段（乐观锁）' AS change1;
SELECT '  2. strategies 表新增 is_calculate 字段' AS change2;
SELECT '  3. strategy_business_units 表新增 6 个独立参数字段' AS change3;
SELECT '  4. 创建 strategy_permissions 表（权限控制）' AS change4;
SELECT '  5. 创建 strategy_versions 表（版本管理）' AS change5;
SELECT '  6. strategies 表 status 枚举添加 disabled 状态' AS change6;
SELECT '  7. 初始化现有数据的权限和版本号' AS change7;
SELECT '===========================================' AS status;

-- ============================================
-- 回滚脚本（如果需要）
-- ============================================
/*
-- 回滚步骤（谨慎使用）：
-- 1. 删除新表
DROP TABLE IF EXISTS `strategy_versions`;
DROP TABLE IF EXISTS `strategy_permissions`;

-- 2. 恢复 strategies 表备份
DELETE FROM `strategies`;
INSERT INTO `strategies` SELECT * FROM `strategies_backup_phase1`;

-- 3. 删除备份表
DROP TABLE IF EXISTS `strategies_backup_phase1`;
*/

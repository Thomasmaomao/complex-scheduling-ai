-- 车险询价系统 - Phase 2 计算逻辑数据库迁移
-- 创建时间：2026-03-31 19:50
-- 版本：v2.0
-- 说明：添加情景测试数据存储和计算逻辑存储字段

-- 使用数据库
USE car_insurance;

-- ============================================
-- 1. 策略版本表 - 添加计算字段
-- ============================================

-- 添加 RP 纯风险保费字段
ALTER TABLE `strategies` 
ADD COLUMN `rp_premium` DECIMAL(10,2) COMMENT 'RP 纯风险保费（平均保费 × 目标赔付率）' AFTER `autonomous_discount_max`;

-- 添加计算后的总保费字段
ALTER TABLE `strategies` 
ADD COLUMN `total_premium_calculated` DECIMAL(12,2) COMMENT '计算后的总保费' AFTER `rp_premium`;

-- 添加计算后的总利润字段
ALTER TABLE `strategies` 
ADD COLUMN `total_profit_calculated` DECIMAL(12,2) COMMENT '计算后的总利润' AFTER `total_premium_calculated`;

-- 添加计算后的利润率字段
ALTER TABLE `strategies` 
ADD COLUMN `profit_margin_calculated` DECIMAL(6,4) COMMENT '计算后的利润率' AFTER `total_profit_calculated`;

-- 添加情景测试数据字段（JSON 格式）
ALTER TABLE `strategies` 
ADD COLUMN `scenario_test_data` TEXT COMMENT '情景测试数据（JSON 格式）' AFTER `profit_margin_calculated`;

-- ============================================
-- 2. 策略版本表 - 添加计算字段
-- ============================================

-- 检查 strategy_versions 表是否存在 calculation_data 字段
-- 如果不存在则添加
SET @dbname = DATABASE();
SET @tablename = 'strategy_versions';
SET @columnname = 'calculation_data';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " TEXT COMMENT '计算数据（JSON 格式）'")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- 添加 scenario_data 字段
SET @columnname = 'scenario_data';
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 1",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " TEXT COMMENT '情景测试数据（JSON 格式）'")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- ============================================
-- 3. 更新现有数据的计算结果
-- ============================================

-- 更新策略主表的计算字段
UPDATE `strategies` 
SET 
  `rp_premium` = 4500 * `target_loss_ratio`,  -- 假设平均保费 4500
  `profit_margin_calculated` = 1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`,
  `total_premium_calculated` = 5000 * 4500,  -- 假设 5000 保单 × 4500 平均保费
  `total_profit_calculated` = 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`),
  `scenario_test_data` = JSON_ARRAY(
    JSON_OBJECT('scenario_id', 1, 'change_rate', -0.02, 'scenario_profit', 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`) * 0.98),
    JSON_OBJECT('scenario_id', 2, 'change_rate', -0.01, 'scenario_profit', 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`) * 0.99),
    JSON_OBJECT('scenario_id', 3, 'change_rate', 0, 'scenario_profit', 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`)),
    JSON_OBJECT('scenario_id', 4, 'change_rate', 0.01, 'scenario_profit', 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`) * 1.01),
    JSON_OBJECT('scenario_id', 5, 'change_rate', 0.02, 'scenario_profit', 5000 * 4500 * (1 - `fixed_cost_ratio` - `target_loss_ratio` - `market_expense_ratio`) * 1.02)
  )
WHERE `status` != 'disabled';

-- ============================================
-- 4. 更新策略版本表的快照数据
-- ============================================

-- 更新现有版本的快照数据，添加计算字段
UPDATE `strategy_versions` sv
SET sv.`snapshot_data` = JSON_INSERT(
  sv.`snapshot_data`,
  '$.calculations.rp_premium', 4500 * (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.target_loss_ratio') + 0),
  '$.calculations.profit_margin', 1 - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.fixed_cost_ratio') + 0) 
    - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.target_loss_ratio') + 0) 
    - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.market_expense_ratio') + 0),
  '$.calculations.expected_profit', 5000 * 4500 * (1 - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.fixed_cost_ratio') + 0) 
    - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.target_loss_ratio') + 0) 
    - (JSON_EXTRACT(sv.`snapshot_data`, '$.global_params.market_expense_ratio') + 0)),
  '$.calculations.total_premium', 5000 * 4500
)
WHERE JSON_EXTRACT(sv.`snapshot_data`, '$.calculations') IS NULL;

-- ============================================
-- 5. 添加索引
-- ============================================

-- 为新增字段添加索引（如果需要频繁查询）
CREATE INDEX `idx_rp_premium` ON `strategies`(`rp_premium`);
CREATE INDEX `idx_profit_margin` ON `strategies`(`profit_margin_calculated`);

-- ============================================
-- 6. 验证更新
-- ============================================

-- 验证数据更新
SELECT 
  id, 
  name, 
  target_loss_ratio,
  rp_premium,
  profit_margin_calculated,
  total_premium_calculated,
  total_profit_calculated
FROM strategies
WHERE status != 'disabled'
LIMIT 5;

-- ============================================
-- 7. 回滚脚本（可选）
-- ============================================

-- 如果需要回滚，执行以下 SQL：
/*
ALTER TABLE `strategies` DROP COLUMN `rp_premium`;
ALTER TABLE `strategies` DROP COLUMN `total_premium_calculated`;
ALTER TABLE `strategies` DROP COLUMN `total_profit_calculated`;
ALTER TABLE `strategies` DROP COLUMN `profit_margin_calculated`;
ALTER TABLE `strategies` DROP COLUMN `scenario_test_data`;

ALTER TABLE `strategy_versions` DROP COLUMN IF EXISTS `calculation_data`;
ALTER TABLE `strategy_versions` DROP COLUMN IF EXISTS `scenario_data`;
*/

-- ============================================
-- 迁移完成
-- ============================================

SELECT 'Phase 2 数据库迁移完成' AS status;

-- 车险询价系统 - 策略管理数据库迁移脚本
-- 版本：v1.0 -> v1.1
-- 说明：添加外键索引，修改 DECIMAL 精度

USE car_insurance;

-- ============================================
-- 1. 修改 strategies 表的 DECIMAL 精度
-- ============================================
ALTER TABLE `strategies` 
  MODIFY COLUMN `fixed_cost_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.1000 COMMENT '固定成本率',
  MODIFY COLUMN `target_loss_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.7500 COMMENT '目标赔付率',
  MODIFY COLUMN `market_expense_ratio` DECIMAL(6,4) NOT NULL DEFAULT 0.1200 COMMENT '市场费用率',
  MODIFY COLUMN `autonomous_discount_min` DECIMAL(6,4) NOT NULL DEFAULT 0.5000 COMMENT '自主系数下限',
  MODIFY COLUMN `autonomous_discount_max` DECIMAL(6,4) NOT NULL DEFAULT 0.6500 COMMENT '自主系数上限';

-- ============================================
-- 2. 为 strategy_institutions 表添加索引
-- ============================================
-- 添加 strategy_id 索引
ALTER TABLE `strategy_institutions` ADD INDEX `idx_strategy_id` (`strategy_id`);

-- ============================================
-- 3. 为 strategy_business_units 表添加索引
-- ============================================
-- 添加 strategy_id 索引
ALTER TABLE `strategy_business_units` ADD INDEX `idx_strategy_id` (`strategy_id`);

-- 添加 unit_id 索引
ALTER TABLE `strategy_business_units` ADD INDEX `idx_unit_id` (`unit_id`);

-- ============================================
-- 4. 为 strategy_publish_institutions 表添加索引
-- ============================================
-- 添加 publish_id 索引
ALTER TABLE `strategy_publish_institutions` ADD INDEX `idx_publish_id` (`publish_id`);

-- 添加 institution_code 索引
ALTER TABLE `strategy_publish_institutions` ADD INDEX `idx_institution_code` (`institution_code`);

-- ============================================
-- 迁移完成
-- ============================================
SELECT '数据库迁移完成！' AS migration_status;

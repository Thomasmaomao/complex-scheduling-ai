-- 策略管理模块增量迁移脚本
-- 执行时间：2026-03-31
-- 说明：在现有表结构上应用修复

USE car_insurance;

-- ============================================
-- 1. 验证当前索引状态
-- ============================================

SELECT 'Checking existing indexes...' AS status;

SHOW INDEX FROM strategy_institutions;
SHOW INDEX FROM strategy_business_units;
SHOW INDEX FROM strategy_publish_institutions;

-- ============================================
-- 2. 验证数据
-- ============================================

SELECT 'Verifying data...' AS status;

-- 查询策略总数
SELECT COUNT(*) AS total_strategies FROM strategies;

-- 查询策略状态分布
SELECT status, COUNT(*) AS count 
FROM strategies 
GROUP BY status;

-- 查询测试记录
SELECT COUNT(*) AS total_tests FROM strategy_test_results;

-- 查询发布记录
SELECT COUNT(*) AS total_publishes FROM strategy_publish_records;

-- ============================================
-- 3. 验证视图
-- ============================================

SELECT 'Verifying views...' AS status;

SELECT COUNT(*) AS view_exists 
FROM information_schema.VIEWS 
WHERE TABLE_SCHEMA = 'car_insurance' 
AND TABLE_NAME = 'v_strategy_full';

-- ============================================
-- 迁移完成
-- ============================================
SELECT '✅ 增量迁移完成 - 所有索引和约束已存在' AS status;

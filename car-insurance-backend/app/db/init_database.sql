-- ============================================
-- 智能业务决策平台 - 数据库初始化脚本
-- ============================================
-- 执行：mysql -u root -p car_insurance < init_database.sql

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS car_insurance 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE car_insurance;

-- ============================================
-- 策略表
-- ============================================
CREATE TABLE IF NOT EXISTS strategies (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status ENUM('draft', 'simulation_passed', 'simulation_failed', 'ab_test_passed', 'ab_test_failed', 'published', 'disabled', 'archived') DEFAULT 'draft',
    version INT DEFAULT 1,
    fixed_cost_ratio DECIMAL(6,4),
    target_loss_ratio DECIMAL(6,4),
    market_expense_ratio DECIMAL(6,4),
    autonomous_discount_min DECIMAL(6,4),
    autonomous_discount_max DECIMAL(6,4),
    is_calculate TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(64),
    INDEX idx_status (status),
    INDEX idx_version (version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 策略机构关联表
-- ============================================
CREATE TABLE IF NOT EXISTS strategy_institutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id VARCHAR(64) NOT NULL,
    institution_code VARCHAR(50) NOT NULL,
    institution_name VARCHAR(100) NOT NULL,
    UNIQUE KEY uk_strategy_institution (strategy_id, institution_code),
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 策略业务单元表
-- ============================================
CREATE TABLE IF NOT EXISTS strategy_business_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id VARCHAR(64) NOT NULL,
    unit_id VARCHAR(50) NOT NULL,
    unit_name VARCHAR(100) NOT NULL,
    fixed_cost_ratio DECIMAL(6,4),
    target_loss_ratio DECIMAL(6,4),
    market_expense_ratio DECIMAL(6,4),
    autonomous_discount_min DECIMAL(6,4),
    autonomous_discount_max DECIMAL(6,4),
    is_calculate TINYINT(1) DEFAULT 0,
    UNIQUE KEY uk_strategy_unit (strategy_id, unit_id),
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 业务单元主表
-- ============================================
CREATE TABLE IF NOT EXISTS business_unit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id VARCHAR(50) UNIQUE NOT NULL,
    unit_name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    policy_count INT DEFAULT 0,
    avg_premium DECIMAL(10,2) DEFAULT 0,
    pure_risk_cost DECIMAL(10,2) DEFAULT 0,
    expected_loss_ratio DECIMAL(5,4),
    expected_profit_margin DECIMAL(5,4),
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 测试结果表
-- ============================================
CREATE TABLE IF NOT EXISTS strategy_test_results (
    id VARCHAR(64) PRIMARY KEY,
    strategy_id VARCHAR(64) NOT NULL,
    test_type ENUM('simulation', 'ab_test') NOT NULL,
    passed TINYINT(1) NOT NULL,
    result_summary TEXT,
    conversion_rate_lift DECIMAL(6,4),
    profit_lift DECIMAL(6,4),
    p_value DECIMAL(8,5),
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_strategy (strategy_id),
    INDEX idx_test_type (test_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- 插入演示数据 - 业务单元
-- ============================================
INSERT INTO business_unit (unit_id, unit_name, description, policy_count, avg_premium, pure_risk_cost, expected_loss_ratio, expected_profit_margin) VALUES
('BU001', '燃油车 - 续保', '燃油车续保客户群体', 5000, 3500.00, 2520.00, 0.72, 0.06),
('BU002', '燃油车 - 新保', '燃油车新保客户群体', 2000, 4800.00, 3840.00, 0.80, -0.02),
('BU003', '新能源 - 高价值', '新能源高价值客户群体', 1500, 5800.00, 4234.00, 0.73, 0.05),
('BU004', '新能源 - 普通', '新能源普通客户群体', 3000, 4500.00, 3555.00, 0.79, -0.01),
('BU005', '豪车 - 续保', '豪车续保客户群体', 500, 15000.00, 10500.00, 0.70, 0.08)
ON DUPLICATE KEY UPDATE 
    unit_name = VALUES(unit_name),
    policy_count = VALUES(policy_count),
    avg_premium = VALUES(avg_premium),
    pure_risk_cost = VALUES(pure_risk_cost);

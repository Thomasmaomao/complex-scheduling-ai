-- 车险询价系统 Beta v1.0 - 核心数据表结构
-- 创建日期：2026-03-30
-- 数据库：car_insurance
-- 字符集：utf8mb4

-- ========================================
-- 1. 创建数据库
-- ========================================
CREATE DATABASE IF NOT EXISTS car_insurance 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE car_insurance;

-- ========================================
-- 2. 业务单元表 (business_unit)
-- ========================================
CREATE TABLE IF NOT EXISTS business_unit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id VARCHAR(50) NOT NULL UNIQUE COMMENT '业务单元 ID',
    unit_name VARCHAR(100) NOT NULL COMMENT '业务单元名称',
    description VARCHAR(500) COMMENT '业务单元描述',
    
    -- 业务单元属性
    vehicle_type VARCHAR(50) COMMENT '车辆类型 (燃油车/新能源)',
    customer_type VARCHAR(50) COMMENT '客户类型 (新保/续保)',
    channel_type VARCHAR(50) COMMENT '渠道类型 (直销/代理/经纪)',
    
    -- 利润特征
    expected_loss_ratio DECIMAL(5,4) COMMENT '预期赔付率',
    expected_profit_margin DECIMAL(5,4) COMMENT '预期利润率',
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_unit_id (unit_id),
    INDEX idx_vehicle_type (vehicle_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='业务单元表';

-- 插入 5 个默认业务单元
INSERT INTO business_unit (unit_id, unit_name, description, vehicle_type, customer_type, channel_type, expected_loss_ratio, expected_profit_margin) VALUES
('BU001', '燃油车 - 续保 - 直销', '燃油车续保业务，直销渠道', '燃油车', '续保', '直销', 0.60, 0.08),
('BU002', '燃油车 - 新保 - 直销', '燃油车新保业务，直销渠道', '燃油车', '新保', '直销', 0.65, 0.05),
('BU003', '燃油车 - 续保 - 代理', '燃油车续保业务，代理渠道', '燃油车', '续保', '代理', 0.62, 0.06),
('BU004', '新能源 - 续保 - 直销', '新能源车续保业务，直销渠道', '新能源', '续保', '直销', 0.70, 0.03),
('BU005', '新能源 - 新保 - 直销', '新能源车新保业务，直销渠道', '新能源', '新保', '直销', 0.75, 0.02);

-- ========================================
-- 3. 策略配置表 (strategy_config)
-- ========================================
CREATE TABLE IF NOT EXISTS strategy_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL UNIQUE COMMENT '策略 ID',
    strategy_name VARCHAR(100) NOT NULL COMMENT '策略名称',
    description VARCHAR(500) COMMENT '策略描述',
    
    -- 业务单元配置
    business_units JSON COMMENT '业务单元配置',
    
    -- 优先级权重
    price_weight DECIMAL(5,4) DEFAULT 0.40 COMMENT '价格权重',
    service_weight DECIMAL(5,4) DEFAULT 0.35 COMMENT '服务权重',
    claim_weight DECIMAL(5,4) DEFAULT 0.25 COMMENT '赔付权重',
    
    -- 阈值规则
    min_price_score INT DEFAULT 60 COMMENT '最低价格得分',
    min_service_score INT DEFAULT 70 COMMENT '最低服务得分',
    min_claim_score INT DEFAULT 60 COMMENT '最低赔付得分',
    
    -- 成本模拟配置
    cost_simulation_config JSON COMMENT '成本模拟配置',
    
    -- 收益模拟配置
    revenue_simulation_config JSON COMMENT '收益模拟配置',
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50) COMMENT '创建人',
    updated_by VARCHAR(50) COMMENT '更新人',
    
    INDEX idx_strategy_id (strategy_id),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略配置表';

-- 插入默认策略配置
INSERT INTO strategy_config (strategy_id, strategy_name, description, business_units, price_weight, service_weight, claim_weight) VALUES
('default_v1', '默认推荐策略', '综合考虑价格、服务和赔付的平衡策略', 
 '["BU001", "BU002", "BU003", "BU004", "BU005"]', 
 0.40, 0.35, 0.25);

-- ========================================
-- 4. 保司评分表 (insurer_score)
-- ========================================
CREATE TABLE IF NOT EXISTS insurer_score (
    id INT AUTO_INCREMENT PRIMARY KEY,
    insurer_id VARCHAR(50) NOT NULL COMMENT '保司 ID',
    insurer_name VARCHAR(100) NOT NULL COMMENT '保司名称',
    score_date DATE NOT NULL COMMENT '评分日期',
    
    -- 三维度评分
    price_score INT DEFAULT 0 COMMENT '价格得分 (0-100)',
    service_score INT DEFAULT 0 COMMENT '服务得分 (0-100)',
    claim_score INT DEFAULT 0 COMMENT '赔付得分 (0-100)',
    overall_score INT DEFAULT 0 COMMENT '综合得分 (0-100)',
    
    -- 评分权重
    price_weight DECIMAL(5,4) DEFAULT 0.40 COMMENT '价格权重',
    service_weight DECIMAL(5,4) DEFAULT 0.35 COMMENT '服务权重',
    claim_weight DECIMAL(5,4) DEFAULT 0.25 COMMENT '赔付权重',
    
    -- 动态因素
    quota_usage DECIMAL(5,4) DEFAULT 0 COMMENT '额度使用率',
    loss_ratio DECIMAL(5,4) DEFAULT 0 COMMENT '赔付率',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_insurer_date (insurer_id, score_date),
    INDEX idx_overall_score (overall_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='保司评分表';

-- 插入 3 家保司初始评分
INSERT INTO insurer_score (insurer_id, insurer_name, score_date, price_score, service_score, claim_score, overall_score) VALUES
('picc', '人保财险', CURDATE(), 85, 90, 88, 88),
('pingan', '平安产险', CURDATE(), 80, 92, 85, 86),
('cpic', '太平洋产险', CURDATE(), 82, 88, 86, 85);

-- ========================================
-- 5. 保司优先级动态调整表 (insurer_priority_adjustment)
-- ========================================
CREATE TABLE IF NOT EXISTS insurer_priority_adjustment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    insurer_id VARCHAR(50) NOT NULL COMMENT '保司 ID',
    adjustment_date DATE NOT NULL COMMENT '调整日期',
    
    -- 调整前优先级
    original_priority INT DEFAULT 0 COMMENT '原始优先级',
    
    -- 调整因素
    quota_factor DECIMAL(5,4) DEFAULT 1.0 COMMENT '额度系数',
    loss_ratio_factor DECIMAL(5,4) DEFAULT 1.0 COMMENT '赔付率系数',
    
    -- 调整后优先级
    adjusted_priority INT DEFAULT 0 COMMENT '调整后优先级',
    priority_change INT DEFAULT 0 COMMENT '优先级变化值',
    
    -- 调整原因
    reason_code VARCHAR(50) COMMENT '调整原因代码',
    reason_desc VARCHAR(500) COMMENT '调整原因描述',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) COMMENT '创建人',
    
    INDEX idx_insurer_date (insurer_id, adjustment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='保司优先级动态调整表';

-- ========================================
-- 6. 决策日志表 (decision_log)
-- ========================================
CREATE TABLE IF NOT EXISTS decision_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL COMMENT '请求 ID',
    quote_time DATETIME NOT NULL COMMENT '询价时间',
    
    -- 客户信息（脱敏）
    region VARCHAR(50) COMMENT '地区',
    vehicle_value DECIMAL(12,2) COMMENT '车辆价值',
    fuel_type VARCHAR(20) COMMENT '燃料类型',
    driver_age INT COMMENT '驾驶员年龄',
    
    -- 决策过程
    step1_premium_calc JSON COMMENT '步骤 1: 保费计算结果',
    step2_risk_score INT COMMENT '步骤 2: 风险评分',
    step3_strategy_match JSON COMMENT '步骤 3: 策略匹配结果',
    step4_scoring JSON COMMENT '步骤 4: 评分结果',
    step5_recommendation JSON COMMENT '步骤 5: 推荐结果',
    
    -- 推荐结果
    recommended_insurer_id VARCHAR(50) COMMENT '推荐保司 ID',
    recommended_insurer_name VARCHAR(100) COMMENT '推荐保司名称',
    total_premium DECIMAL(12,2) COMMENT '总保费',
    
    -- 性能指标
    calculation_time_ms INT COMMENT '计算耗时 (毫秒)',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_request_id (request_id),
    INDEX idx_quote_time (quote_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='决策日志表';

-- ========================================
-- 7. A/B 测试实验表 (ab_test_experiment)
-- ========================================
CREATE TABLE IF NOT EXISTS ab_test_experiment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_id VARCHAR(50) NOT NULL UNIQUE COMMENT '实验 ID',
    experiment_name VARCHAR(100) NOT NULL COMMENT '实验名称',
    description VARCHAR(500) COMMENT '实验描述',
    
    -- 实验配置
    strategy_a_id VARCHAR(50) NOT NULL COMMENT '策略 A ID',
    strategy_b_id VARCHAR(50) NOT NULL COMMENT '策略 B ID',
    
    -- 流量分配
    traffic_split DECIMAL(5,4) DEFAULT 0.50 COMMENT '流量分配比例 (0-1)',
    
    -- 实验周期
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    
    -- 实验状态
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态 (draft/running/completed)',
    
    -- 样本量
    sample_size_a INT DEFAULT 0 COMMENT 'A 组样本量',
    sample_size_b INT DEFAULT 0 COMMENT 'B 组样本量',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(50) COMMENT '创建人',
    
    INDEX idx_experiment_id (experiment_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A/B 测试实验表';

-- ========================================
-- 8. A/B 测试结果表 (ab_test_result)
-- ========================================
CREATE TABLE IF NOT EXISTS ab_test_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    experiment_id VARCHAR(50) NOT NULL COMMENT '实验 ID',
    result_date DATE NOT NULL COMMENT '结果日期',
    
    -- A 组结果
    strategy_a_id VARCHAR(50) NOT NULL COMMENT '策略 A ID',
    conversion_rate_a DECIMAL(5,4) COMMENT 'A 组成率',
    profit_a DECIMAL(15,2) COMMENT 'A 组利润',
    sample_size_a INT COMMENT 'A 组样本量',
    
    -- B 组结果
    strategy_b_id VARCHAR(50) NOT NULL COMMENT '策略 B ID',
    conversion_rate_b DECIMAL(5,4) COMMENT 'B 组成率',
    profit_b DECIMAL(15,2) COMMENT 'B 组利润',
    sample_size_b INT COMMENT 'B 组样本量',
    
    -- 统计检验
    p_value DECIMAL(10,8) COMMENT 'P 值',
    is_significant BOOLEAN DEFAULT FALSE COMMENT '是否显著',
    confidence_level DECIMAL(5,4) COMMENT '置信水平',
    
    -- 结论
    conclusion VARCHAR(500) COMMENT '实验结论',
    recommendation VARCHAR(500) COMMENT '推荐建议',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_experiment_date (experiment_id, result_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A/B 测试结果表';

-- ========================================
-- 完成提示
-- ========================================
SELECT '✅ 数据库表创建完成！' AS status;
SELECT '共创建 7 个核心数据表：' AS message;
SELECT '1. business_unit (业务单元表)' AS table1;
SELECT '2. strategy_config (策略配置表)' AS table2;
SELECT '3. insurer_score (保司评分表)' AS table3;
SELECT '4. insurer_priority_adjustment (保司优先级动态调整表)' AS table4;
SELECT '5. decision_log (决策日志表)' AS table5;
SELECT '6. ab_test_experiment (A/B 测试实验表)' AS table6;
SELECT '7. ab_test_result (A/B 测试结果表)' AS table7;

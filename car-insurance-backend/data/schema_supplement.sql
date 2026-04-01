-- 补充表创建 SQL（3 个表）
USE car_insurance;

-- 表 1: rate_table_cache（费率表缓存表）
CREATE TABLE IF NOT EXISTS rate_table_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rate_type VARCHAR(50) NOT NULL COMMENT '费率类型（compulsory/commercial/ncd）',
    vehicle_type VARCHAR(50) COMMENT '车辆类型',
    fuel_type VARCHAR(20) COMMENT '燃料类型',
    region VARCHAR(50) COMMENT '地区',
    vehicle_age INT COMMENT '车龄',
    base_premium DECIMAL(12,2) COMMENT '基准保费',
    rate_factor DECIMAL(5,4) COMMENT '费率系数',
    ncd_factor DECIMAL(5,4) COMMENT 'NCD 系数',
    valid_from DATE COMMENT '生效日期',
    valid_to DATE COMMENT '失效日期',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rate_type (rate_type),
    INDEX idx_vehicle_region (vehicle_type, region),
    INDEX idx_valid_date (valid_from, valid_to)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='费率表缓存表';

-- 表 2: simulation_result（模拟测试结果表）
CREATE TABLE IF NOT EXISTS simulation_result (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    simulation_id VARCHAR(50) NOT NULL UNIQUE COMMENT '模拟 ID（唯一）',
    strategy_id VARCHAR(50) NOT NULL COMMENT '策略 ID',
    test_type VARCHAR(20) NOT NULL COMMENT '测试类型（simulation/ab_test）',
    test_date DATE NOT NULL COMMENT '测试日期',
    sample_size INT COMMENT '样本量',
    time_range VARCHAR(20) COMMENT '时间范围（7d/14d/30d）',
    baseline_avg_premium DECIMAL(12,2) COMMENT '基准平均保费',
    baseline_conversion_rate DECIMAL(5,4) COMMENT '基准成交率',
    baseline_profit DECIMAL(15,2) COMMENT '基准利润',
    test_avg_premium DECIMAL(12,2) COMMENT '测试平均保费',
    test_conversion_rate DECIMAL(5,4) COMMENT '测试成交率',
    test_profit DECIMAL(15,2) COMMENT '测试利润',
    change_premium DECIMAL(5,4) COMMENT '保费变化率',
    change_conversion_rate DECIMAL(5,4) COMMENT '成交率变化率',
    change_profit DECIMAL(5,4) COMMENT '利润变化率',
    conclusion VARCHAR(500) COMMENT '测试结论',
    recommendation VARCHAR(500) COMMENT '推荐建议',
    risks JSON COMMENT '风险列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_simulation_id (simulation_id),
    INDEX idx_strategy_id (strategy_id),
    INDEX idx_test_date (test_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模拟测试结果表';

-- 表 3: business_unit_performance（业务单元绩效表）
CREATE TABLE IF NOT EXISTS business_unit_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    unit_id VARCHAR(50) NOT NULL COMMENT '业务单元 ID',
    stat_date DATE NOT NULL COMMENT '统计日期',
    policy_count INT COMMENT '保单数',
    premium_income DECIMAL(15,2) COMMENT '保费收入',
    avg_autonomous_discount DECIMAL(5,4) COMMENT '平均自主系数',
    conversion_rate DECIMAL(5,4) COMMENT '成交率',
    profit_contribution DECIMAL(15,2) COMMENT '利润贡献',
    profit_margin DECIMAL(5,4) COMMENT '利润率',
    loss_ratio DECIMAL(5,4) COMMENT '赔付率',
    percentage DECIMAL(5,4) COMMENT '占比（该单元/总计）',
    risk_level VARCHAR(20) COMMENT '风险等级（low/medium/high）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_unit_date (unit_id, stat_date),
    INDEX idx_stat_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='业务单元绩效表';

SELECT '✅ 补充表创建完成！' AS status;
SELECT '共创建 3 个补充数据表：' AS message;
SELECT '1. rate_table_cache (费率表缓存表)' AS table1;
SELECT '2. simulation_result (模拟测试结果表)' AS table2;
SELECT '3. business_unit_performance (业务单元绩效表)' AS table3;

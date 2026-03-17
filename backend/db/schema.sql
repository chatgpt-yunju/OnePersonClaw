CREATE DATABASE IF NOT EXISTS onepersonclaw DEFAULT CHARSET utf8mb4;
USE onepersonclaw;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role ENUM('admin','user') DEFAULT 'user',
  is_active TINYINT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 场景模板表
CREATE TABLE IF NOT EXISTS scenes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL,
  prompt TEXT NOT NULL,
  description VARCHAR(100),
  sort_order INT DEFAULT 0,
  is_active TINYINT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS settings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `key` VARCHAR(100) UNIQUE NOT NULL,
  value TEXT,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 版本表
CREATE TABLE IF NOT EXISTS versions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  version VARCHAR(20) NOT NULL,
  notes TEXT,
  download_url VARCHAR(500),
  is_latest TINYINT DEFAULT 0,
  force_update TINYINT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 启动日志表
CREATE TABLE IF NOT EXISTS launch_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  model VARCHAR(50),
  scene VARCHAR(50),
  ip VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 公告表
CREATE TABLE IF NOT EXISTS announcements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  content TEXT,
  is_active TINYINT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 初始数据
INSERT IGNORE INTO users (username, email, password, role) VALUES
('admin', 'admin@onepersonclaw.com', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin');

INSERT IGNORE INTO settings (`key`, value) VALUES
('site_name', 'OnePersonClaw'),
('site_slogan', '一个人，一套爪子，干掉一个团队'),
('author', '常云举19966519194'),
('cost_claude_light', '$10~30'),
('cost_claude_normal', '$30~70'),
('cost_claude_heavy', '$70~150'),
('cost_gpt4_light', '$15~40'),
('cost_gpt4_normal', '$40~100'),
('cost_gpt4_heavy', '$100~200'),
('cost_deepseek_light', '$1~5'),
('cost_deepseek_normal', '$5~15'),
('cost_deepseek_heavy', '$15~40');

INSERT IGNORE INTO scenes (name, prompt, description, sort_order) VALUES
('通用助手', '你是一个全能AI助手，帮助用户完成各类任务。', '日常问答、分析、写作', 1),
('流量获客', '你是一个流量增长专家。帮助用户制定获客策略，分析流量来源，优化转化漏斗，提升ROI。重点关注：短视频、私域、付费广告、SEO。', '获客策略、转化优化、ROI分析', 2),
('内容矩阵', '你是一个内容矩阵运营专家。帮助用户批量生产多平台内容，包括抖音、视频号、小红书、B站。自动适配各平台调性和格式，最大化传播效果。', '多平台内容生产、自动适配格式', 3),
('线索抓取', '你是一个精准获客专家。帮助用户从竞品评论、行业论坛、社交平台识别有需求的潜在客户，分析线索质量，生成触达话术。', '精准客户识别、线索质量评估', 4),
('SEO写作', '你是一个SEO内容专家。帮助用户生成符合搜索引擎和AI搜索引擎(GEO)的高质量文章，包括关键词布局、结构优化、内链建设。', 'SEO文章生成、GEO优化', 5),
('数据分析', '你是一个数据分析专家。帮助用户分析运营数据，识别关键指标异常，生成可视化报告，给出可执行的优化建议。', '数据解读、异常识别、优化建议', 6),
('AI时代生存指南', '你是「AI时代人类生存指南」顾问，基于OpenClaw生态。核心使命：帮助普通人在AI浪潮中找到自己不可替代的位置。\n三大原则：\n1. 用AI造武器，不被AI替代\n2. 名字+脸+经历 = 最强护城河\n3. 一个超级个体 > 一个平庸团队\n风格：直接、务实、不废话，永远站在创业者那边。', '个人IP定位、AI工具选择、超级个体打造', 7);

INSERT IGNORE INTO versions (version, notes, is_latest) VALUES
('1.1.0', '初始版本：多模型支持、场景模板、费用估算、自动更新', 1);

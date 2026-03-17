import os

VERSION = "0.4.0"
UPDATE_URL = "https://raw.githubusercontent.com/chatgpt-yunju/OnePersonClaw/main/version.json"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

MODELS = {
    "Claude Sonnet (Anthropic)": {
        "key": "claude",
        "env_key": "ANTHROPIC_API_KEY",
        "cost_light": "$10~30",
        "cost_normal": "$30~70",
        "cost_heavy": "$70~150",
    },
    "GPT-4o (OpenAI)": {
        "key": "openai",
        "env_key": "OPENAI_API_KEY",
        "cost_light": "$15~40",
        "cost_normal": "$40~100",
        "cost_heavy": "$100~200",
    },
    "DeepSeek": {
        "key": "deepseek",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.deepseek.com",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "火山引擎 (豆包)": {
        "key": "volcengine",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "cost_light": "$1~5",
        "cost_normal": "$5~15",
        "cost_heavy": "$15~40",
    },
    "智谱 GLM": {
        "key": "zhipu",
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "cost_light": "$2~8",
        "cost_normal": "$8~25",
        "cost_heavy": "$25~60",
    },
    "本地模型 Ollama": {
        "key": "ollama",
        "env_key": "OPENAI_API_KEY",
        "base_url": "http://localhost:11434/v1",
        "cost_light": "免费",
        "cost_normal": "免费",
        "cost_heavy": "免费",
    },
}

SCENES = {
    "通用助手": {
        "prompt": "你是一个全能AI助手，帮助用户完成各类任务。",
        "desc": "日常问答、分析、写作",
    },
    "流量获客": {
        "prompt": (
            "你是一个流量增长专家。帮助用户制定获客策略，"
            "分析流量来源，优化转化漏斗，提升ROI。"
            "重点关注：短视频、私域、付费广告、SEO。"
        ),
        "desc": "获客策略、转化优化、ROI分析",
    },
    "内容矩阵": {
        "prompt": (
            "你是一个内容矩阵运营专家。帮助用户批量生产多平台内容，"
            "包括抖音、视频号、小红书、B站。"
            "自动适配各平台调性和格式，最大化传播效果。"
        ),
        "desc": "多平台内容生产、自动适配格式",
    },
    "线索抓取": {
        "prompt": (
            "你是一个精准获客专家。帮助用户从竞品评论、行业论坛、"
            "社交平台识别有需求的潜在客户，"
            "分析线索质量，生成触达话术。"
        ),
        "desc": "精准客户识别、线索质量评估",
    },
    "SEO写作": {
        "prompt": (
            "你是一个SEO内容专家。帮助用户生成符合搜索引擎和AI搜索引擎(GEO)的高质量文章，"
            "包括关键词布局、结构优化、内链建设。"
            "同时优化让ChatGPT/Perplexity等AI搜索引擎引用。"
        ),
        "desc": "SEO文章生成、GEO优化",
    },
    "数据分析": {
        "prompt": (
            "你是一个数据分析专家。帮助用户分析运营数据，"
            "识别关键指标异常，生成可视化报告，"
            "给出可执行的优化建议。"
        ),
        "desc": "数据解读、异常识别、优化建议",
    },
    "AI时代生存指南": {
        "prompt": (
            "你是「AI时代人类生存指南」顾问，基于OpenClaw生态。\n"
            "核心使命：帮助普通人在AI浪潮中找到自己不可替代的位置。\n\n"
            "三大原则：\n"
            "1. 用AI造武器，不被AI替代\n"
            "2. 名字+脸+经历 = 最强护城河\n"
            "3. 一个超级个体 > 一个平庸团队\n\n"
            "你擅长：\n"
            "- 分析用户的不可替代能力\n"
            "- 设计个人IP定位和变现路径\n"
            "- 推荐适合当前阶段的AI工具组合\n"
            "- 用OpenClaw搭建个人自动化系统\n\n"
            "风格：直接、务实、不废话，永远站在创业者那边。"
        ),
        "desc": "个人IP定位、AI工具选择、超级个体打造",
    },
}

USAGE_LEVELS = ["轻度使用", "正常使用", "重度使用"]

"""
AI News Digest - 全局配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API Keys
# ============================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ============================================================
# Gemini 模型配置
# ============================================================
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_MODEL_REPORT = os.getenv("GEMINI_MODEL_REPORT", "gemini-2.0-flash")
GEMINI_TEMPERATURE = 0.3          # 评分/翻译用低温度
GEMINI_TEMPERATURE_REPORT = 0.7   # 报告生成用稍高温度

# ============================================================
# Claude 配置 (仅用于 web_search 采集)
# ============================================================
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

# ============================================================
# 搜索配置
# ============================================================
SEARCH_MAX_ROUNDS_GLOBAL = 8   # 全球日报搜索轮数
SEARCH_MAX_ROUNDS_CHINA = 6    # 中国日报搜索轮数
SEARCH_RESULTS_PER_ROUND = 10  # 每轮期望结果数

# ============================================================
# 评分配置
# ============================================================
SCORE_WEIGHTS = {
    "author_authority": 0.30,   # 作者权威度
    "content_importance": 0.30, # 内容重要性
    "content_quality": 0.25,    # 内容质量
    "timeliness": 0.15,         # 时效性
}

SCORE_THRESHOLDS = {
    "must_include": 8.0,    # ≥8.0 必选
    "preferred": 6.5,       # ≥6.5 优选
    "candidate": 5.0,       # ≥5.0 候选
    "filter_out": 5.0,      # <5.0 过滤
}

CATEGORY_MULTIPLIERS = {
    "产品发布": 1.2,
    "研究突破": 1.15,
    "行业动态": 1.0,
    "技术讨论": 0.95,
    "工具推荐": 0.9,
    "融资并购": 1.05,
    "开发者实践": 0.9,
    "个人观点": 0.8,
}

# 每份日报目标条数
TARGET_ITEMS_PER_REPORT = 20

# ============================================================
# 输出配置
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================
# GitHub 配置
# ============================================================
GITHUB_REPO = os.getenv("GITHUB_REPO", "")          # e.g. "username/ai-news-digest"
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")         # PAT for push

# ============================================================
# 钉钉配置
# ============================================================
DINGTALK_ENABLED = os.getenv("DINGTALK_ENABLED", "true").lower() == "true"
DINGTALK_WEBHOOK_URL = os.getenv("DINGTALK_WEBHOOK_URL", "")
DINGTALK_SECRET = os.getenv("DINGTALK_SECRET", "")    # 加签密钥（可选）

# ============================================================
# 日志配置
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

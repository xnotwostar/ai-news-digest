"""
AI News Digest - Twitter 账号配置与搜索关键词
"""

# ============================================================
# 全球AI日报 - 账号清单
# ============================================================

GLOBAL_ACCOUNTS = {
    # --- 核心层 (权重 8-10) ---
    # OpenAI 生态
    "@sama": {"name": "Sam Altman", "org": "OpenAI", "weight": 10},
    "@OpenAI": {"name": "OpenAI Official", "org": "OpenAI", "weight": 10},
    "@gdb": {"name": "Greg Brockman", "org": "OpenAI", "weight": 9},
    "@ilyasut": {"name": "Ilya Sutskever", "org": "SSI", "weight": 9},

    # Anthropic
    "@AnthropicAI": {"name": "Anthropic Official", "org": "Anthropic", "weight": 10},

    # Google / DeepMind
    "@GoogleDeepMind": {"name": "DeepMind Official", "org": "Google", "weight": 10},
    "@GoogleAI": {"name": "Google AI Official", "org": "Google", "weight": 10},
    "@demikiessabis": {"name": "Demis Hassabis", "org": "Google", "weight": 10},
    "@jeffdean": {"name": "Jeff Dean", "org": "Google", "weight": 9},

    # 顶级研究者
    "@karpathy": {"name": "Andrej Karpathy", "org": "Independent", "weight": 10},
    "@ylecun": {"name": "Yann LeCun", "org": "Meta", "weight": 10},
    "@_akhaliq": {"name": "AK", "org": "Papers", "weight": 9},
    "@fchollet": {"name": "François Chollet", "org": "Google", "weight": 8},
    "@hardmaru": {"name": "David Ha", "org": "Sakana AI", "weight": 8},
    "@goodside": {"name": "Riley Goodside", "org": "Prompt Eng", "weight": 8},

    # AI 工程
    "@hwchase17": {"name": "Harrison Chase", "org": "LangChain", "weight": 9},
    "@jerryjliu0": {"name": "Jerry Liu", "org": "LlamaIndex", "weight": 9},
    "@swyx": {"name": "Swyx", "org": "AI Eng", "weight": 8},

    # 应用与洞察
    "@emollick": {"name": "Ethan Mollick", "org": "Wharton", "weight": 8},
    "@simonw": {"name": "Simon Willison", "org": "AI Tools", "weight": 8},

    # --- 重要层 (权重 6-8) ---
    "@geoffreyhinton": {"name": "Geoffrey Hinton", "org": "Academia", "weight": 9},
    "@yoshuabengio": {"name": "Yoshua Bengio", "org": "Mila", "weight": 9},
    "@benedictevans": {"name": "Benedict Evans", "org": "a16z", "weight": 8},
    "@balajis": {"name": "Balaji Srinivasan", "org": "Investor", "weight": 8},
    "@pmarca": {"name": "Marc Andreessen", "org": "a16z", "weight": 8},
    "@naval": {"name": "Naval Ravikant", "org": "Investor", "weight": 8},
    "@paulg": {"name": "Paul Graham", "org": "YC", "weight": 8},
    "@levelsio": {"name": "Pieter Levels", "org": "Indie", "weight": 7},
    "@rauchg": {"name": "Guillermo Rauch", "org": "Vercel", "weight": 7},
    "@soumithchintala": {"name": "Soumith", "org": "PyTorch", "weight": 7},
    "@jeremyphoward": {"name": "Jeremy Howard", "org": "fast.ai", "weight": 7},
    "@jackclarkSF": {"name": "Jack Clark", "org": "Anthropic", "weight": 7},

    # --- 公司官方 (权重 9) ---
    "@MistralAI": {"name": "Mistral AI", "org": "Mistral", "weight": 9},
    "@MetaAI": {"name": "Meta AI", "org": "Meta", "weight": 9},
    "@HuggingFace": {"name": "Hugging Face", "org": "HF", "weight": 9},
    "@StabilityAI": {"name": "Stability AI", "org": "Stability", "weight": 8},
    "@runwayml": {"name": "Runway", "org": "Runway", "weight": 8},
    "@midjourney": {"name": "Midjourney", "org": "Midjourney", "weight": 8},
    "@perplexity_ai": {"name": "Perplexity", "org": "Perplexity", "weight": 8},
    "@xaboratory": {"name": "xAI", "org": "xAI", "weight": 9},
}


# ============================================================
# 中国AI日报 - 账号清单
# ============================================================

CHINA_ACCOUNTS = {
    # --- 核心层 ---
    "@dotey": {"name": "宝玉", "org": "AI翻译分享", "weight": 10},
    "@op7418": {"name": "OP7", "org": "AI工具推荐", "weight": 10},
    "@01AI": {"name": "零一万物", "org": "01.AI", "weight": 10},
    "@Moonshot_AI": {"name": "月之暗面/Kimi", "org": "Moonshot", "weight": 10},
    "@minimaxai": {"name": "MiniMax", "org": "MiniMax", "weight": 9},
    "@zhipu_ai": {"name": "智谱AI", "org": "Zhipu", "weight": 9},
    "@Alibaba_Qwen": {"name": "阿里通义千问", "org": "Alibaba", "weight": 9},
    "@BaiduAI": {"name": "百度文心", "org": "Baidu", "weight": 9},
    "@stepfun_ai": {"name": "阶跃星辰", "org": "StepFun", "weight": 8},
    "@jiqizhixin": {"name": "机器之心", "org": "Media", "weight": 9},
    "@QbitAI": {"name": "量子位", "org": "Media", "weight": 9},

    # --- 重要层 ---
    "@Keso": {"name": "keso", "org": "科技评论", "weight": 8},
    "@Fenng": {"name": "冯大辉", "org": "科技评论", "weight": 8},
    "@ruanyf": {"name": "阮一峰", "org": "技术博客", "weight": 8},
    "@SenseTime_cn": {"name": "商汤科技", "org": "SenseTime", "weight": 8},
    "@iFLYTEK_AI": {"name": "科大讯飞", "org": "iFlytek", "weight": 8},
    "@geekpark": {"name": "极客公园", "org": "Media", "weight": 7},
    "@GitHubDaily": {"name": "GitHub Daily", "org": "Community", "weight": 7},
    "@yihong0618": {"name": "yihong", "org": "Developer", "weight": 7},
    "@vikingmute": {"name": "Viking", "org": "Developer", "weight": 7},
    "@weijunext": {"name": "JunExt", "org": "Developer", "weight": 7},
}


# ============================================================
# 搜索关键词配置
# ============================================================

GLOBAL_SEARCH_QUERIES = [
    # 按主题组织搜索查询，每个查询会触发一次 web_search
    "OpenAI GPT announcement today site:x.com",
    "Anthropic Claude new release site:x.com",
    "Google Gemini AI update site:x.com",
    "AI breakthrough research today site:x.com",
    "LLM new model release 2026 site:x.com",
    "AI tool launch product site:x.com",
    "AI industry news funding acquisition site:x.com",
    "transformer architecture paper arxiv site:x.com",
]

CHINA_SEARCH_QUERIES = [
    "大模型 发布 最新 site:x.com",
    "Kimi 月之暗面 OR 智谱 OR 通义千问 site:x.com",
    "国产大模型 AI应用 site:x.com",
    "AI创业 融资 中国 site:x.com",
    "AI开源 中国开发者 site:x.com",
    "百度文心 OR 零一万物 OR 阶跃星辰 site:x.com",
]


# ============================================================
# 搜索查询生成辅助
# ============================================================

def build_account_search_queries(accounts: dict, batch_size: int = 5) -> list[str]:
    """
    将账号列表按批次组合为搜索查询
    e.g. "@sama OR @OpenAI OR @karpathy AI news today"
    """
    handles = list(accounts.keys())
    queries = []
    for i in range(0, len(handles), batch_size):
        batch = handles[i:i + batch_size]
        query = " OR ".join(batch) + " AI news today"
        queries.append(query)
    return queries

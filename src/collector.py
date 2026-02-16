"""
数据采集模块 - 通过 Claude API web_search 采集 AI 新闻
"""
import json
import logging
import re
from datetime import datetime, timezone
from anthropic import Anthropic

from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from config.accounts import (
    GLOBAL_ACCOUNTS, CHINA_ACCOUNTS,
    GLOBAL_SEARCH_QUERIES, CHINA_SEARCH_QUERIES,
    build_account_search_queries,
)

logger = logging.getLogger(__name__)


class NewsCollector:
    """通过 Claude web_search 采集 AI 新闻"""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    # ----------------------------------------------------------
    # 公开接口
    # ----------------------------------------------------------
    def collect_global(self) -> list[dict]:
        """采集全球 AI 新闻"""
        logger.info("开始采集全球 AI 新闻...")
        queries = GLOBAL_SEARCH_QUERIES + build_account_search_queries(GLOBAL_ACCOUNTS)
        raw_items = self._search_multiple(queries, context="全球AI新闻")
        items = self._parse_and_deduplicate(raw_items, GLOBAL_ACCOUNTS)
        logger.info(f"全球新闻采集完成，共 {len(items)} 条")
        return items

    def collect_china(self) -> list[dict]:
        """采集中国 AI 新闻"""
        logger.info("开始采集中国 AI 新闻...")
        queries = CHINA_SEARCH_QUERIES + build_account_search_queries(CHINA_ACCOUNTS)
        raw_items = self._search_multiple(queries, context="中国AI新闻")
        items = self._parse_and_deduplicate(raw_items, CHINA_ACCOUNTS)
        logger.info(f"中国新闻采集完成，共 {len(items)} 条")
        return items

    # ----------------------------------------------------------
    # 内部方法
    # ----------------------------------------------------------
    def _search_multiple(self, queries: list[str], context: str) -> list[dict]:
        """执行多轮搜索，合并结果"""
        all_items = []
        for i, query in enumerate(queries):
            logger.info(f"  搜索 [{i+1}/{len(queries)}]: {query[:60]}...")
            try:
                items = self._search_once(query, context)
                all_items.extend(items)
                logger.info(f"    获取到 {len(items)} 条结果")
            except Exception as e:
                logger.warning(f"    搜索失败: {e}")
        return all_items

    def _search_once(self, query: str, context: str) -> list[dict]:
        """
        单次 Claude web_search 调用
        让 Claude 搜索并结构化返回结果
        """
        today = datetime.now().strftime("%Y年%m月%d日")

        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3,
            }],
            messages=[{
                "role": "user",
                "content": f"""你是一个AI新闻采集助手。请搜索以下查询，找到今天（{today}）或最近24小时内的相关AI新闻推文。

搜索查询: {query}
新闻类型: {context}

请搜索后，将找到的每条新闻/推文整理为以下JSON格式，返回一个JSON数组：

```json
[
  {{
    "title": "简短标题（中文）",
    "content": "推文/新闻的完整内容",
    "author": "作者名或Twitter handle（如 @sama）",
    "source_url": "原文链接",
    "published_time": "发布时间（尽量精确，如 2小时前、今天上午）",
    "category": "分类：产品发布/研究突破/行业动态/技术讨论/工具推荐/融资并购/开发者实践/个人观点",
    "language": "en 或 zh"
  }}
]
```

要求：
1. 只返回与AI/大模型/机器学习相关的内容
2. 优先返回最新、最重要的信息
3. 如果没有找到相关结果，返回空数组 []
4. 只返回JSON，不要其他文字"""
            }]
        )

        return self._extract_items_from_response(response)

    def _extract_items_from_response(self, response) -> list[dict]:
        """从 Claude 响应中提取结构化数据"""
        items = []

        # 遍历 response content blocks
        for block in response.content:
            if block.type == "text":
                text = block.text
                # 尝试提取 JSON 数组
                json_items = self._extract_json_array(text)
                if json_items:
                    items.extend(json_items)

        return items

    def _extract_json_array(self, text: str) -> list[dict]:
        """从文本中提取 JSON 数组"""
        # 尝试直接解析
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, TypeError):
            pass

        # 尝试从 markdown 代码块中提取
        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
            r'\[[\s\S]*?\{[\s\S]*?\}[\s\S]*?\]',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        return data
                except (json.JSONDecodeError, TypeError):
                    continue

        return []

    def _parse_and_deduplicate(self, raw_items: list[dict], accounts: dict) -> list[dict]:
        """清洗、标准化、去重"""
        seen = set()
        cleaned = []

        for item in raw_items:
            if not isinstance(item, dict):
                continue

            # 标准化字段
            title = item.get("title", "").strip()
            content = item.get("content", "").strip()
            author = item.get("author", "").strip()
            url = item.get("source_url", "").strip()

            if not content and not title:
                continue

            # 去重 key：基于内容前100字符 + 作者
            dedup_key = f"{author}:{content[:100]}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # 查找作者权重
            author_weight = 5  # 默认权重
            for handle, info in accounts.items():
                if handle.lower() in author.lower() or info["name"].lower() in author.lower():
                    author_weight = info["weight"]
                    author = handle  # 标准化为 handle
                    break

            cleaned.append({
                "title": title,
                "content": content,
                "author": author,
                "author_weight": author_weight,
                "source_url": url,
                "published_time": item.get("published_time", ""),
                "category": item.get("category", "行业动态"),
                "language": item.get("language", "en"),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info(f"  清洗去重: {len(raw_items)} → {len(cleaned)} 条")
        return cleaned

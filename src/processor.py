"""
Gemini 处理模块 - 评分、翻译、报告生成
"""
import json
import logging
import re
from datetime import datetime

import google.generativeai as genai

from config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODEL_REPORT,
    GEMINI_TEMPERATURE, GEMINI_TEMPERATURE_REPORT,
    SCORE_WEIGHTS, SCORE_THRESHOLDS, CATEGORY_MULTIPLIERS,
    TARGET_ITEMS_PER_REPORT,
)

logger = logging.getLogger(__name__)


class GeminiProcessor:
    """使用 Gemini API 进行评分、翻译和报告生成"""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.model_report = genai.GenerativeModel(GEMINI_MODEL_REPORT)

    # ==========================================================
    # 1. 评分
    # ==========================================================
    def score_items(self, items: list[dict]) -> list[dict]:
        """对所有 item 评分并排序"""
        logger.info(f"开始评分，共 {len(items)} 条...")

        # 分批调用 Gemini 评分
        batch_size = 10
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            self._score_batch(batch)

        # 计算最终分数
        for item in items:
            item["final_score"] = self._calculate_final_score(item)

        # 按分数排序
        items.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        logger.info(f"评分完成，最高分 {items[0]['final_score']:.1f}" if items else "无数据")
        return items

    def _score_batch(self, batch: list[dict]):
        """批量调用 Gemini 评分"""
        items_text = []
        for idx, item in enumerate(batch):
            items_text.append(
                f"[{idx}] 作者: {item['author']} | 标题: {item['title']}\n"
                f"内容: {item['content'][:300]}"
            )

        prompt = f"""你是AI新闻评分专家。请对以下{len(batch)}条AI资讯打分。

对每条内容评估两个维度（1-10分）：

**内容重要性**（权重30%）:
- 10分: 重大突破（新模型发布、行业格局改变）
- 8-9分: 重要进展（功能更新、有影响力的论文）
- 6-7分: 有价值（实用工具、技术经验）
- 4-5分: 一般（常规更新、个人观点）
- 1-3分: 低价值（闲聊、广告）

**内容质量**（权重25%）:
- 高分: 有具体数据/对比、技术细节、可验证链接、结构清晰
- 低分: 空泛、无数据、纯转发、过多emoji

资讯列表:
{chr(10).join(items_text)}

请只返回JSON数组，格式:
```json
[
  {{"index": 0, "importance": 8, "quality": 7, "category": "产品发布"}},
  {{"index": 1, "importance": 6, "quality": 5, "category": "技术讨论"}}
]
```
category 可选值: 产品发布/研究突破/行业动态/技术讨论/工具推荐/融资并购/开发者实践/个人观点"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                ),
            )
            scores = self._parse_json_array(response.text)

            for score_item in scores:
                idx = score_item.get("index", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["importance_score"] = score_item.get("importance", 5)
                    batch[idx]["quality_score"] = score_item.get("quality", 5)
                    if score_item.get("category"):
                        batch[idx]["category"] = score_item["category"]

        except Exception as e:
            logger.warning(f"批量评分失败: {e}，使用默认分数")
            for item in batch:
                item.setdefault("importance_score", 5)
                item.setdefault("quality_score", 5)

    def _calculate_final_score(self, item: dict) -> float:
        """计算最终加权分数"""
        author_score = min(item.get("author_weight", 5) / 10 * 10, 10)
        importance = item.get("importance_score", 5)
        quality = item.get("quality_score", 5)

        # 时效性：基于 published_time 文本估算
        timeliness = self._estimate_timeliness(item.get("published_time", ""))

        base_score = (
            author_score * SCORE_WEIGHTS["author_authority"] +
            importance * SCORE_WEIGHTS["content_importance"] +
            quality * SCORE_WEIGHTS["content_quality"] +
            timeliness * SCORE_WEIGHTS["timeliness"]
        )

        # 类别系数
        category = item.get("category", "行业动态")
        multiplier = CATEGORY_MULTIPLIERS.get(category, 1.0)

        return round(min(base_score * multiplier, 10.0), 2)

    def _estimate_timeliness(self, time_text: str) -> float:
        """从文本估算时效性分数"""
        if not time_text:
            return 5.0

        time_lower = time_text.lower()
        # 关键词匹配
        if any(w in time_lower for w in ["刚刚", "just now", "minutes ago", "分钟前"]):
            return 10.0
        if any(w in time_lower for w in ["1小时", "1 hour", "1h"]):
            return 9.0
        if any(w in time_lower for w in ["小时前", "hours ago", "今天上午", "今天下午", "today"]):
            return 8.0
        if any(w in time_lower for w in ["昨天", "yesterday", "1天前", "1 day"]):
            return 6.0
        if any(w in time_lower for w in ["2天", "2 day", "前天"]):
            return 4.0
        return 5.0

    # ==========================================================
    # 2. 筛选
    # ==========================================================
    def select_items(self, items: list[dict]) -> list[dict]:
        """按分数和类别均衡筛选"""
        must = [i for i in items if i.get("final_score", 0) >= SCORE_THRESHOLDS["must_include"]]
        preferred = [i for i in items if SCORE_THRESHOLDS["preferred"] <= i.get("final_score", 0) < SCORE_THRESHOLDS["must_include"]]
        candidates = [i for i in items if SCORE_THRESHOLDS["candidate"] <= i.get("final_score", 0) < SCORE_THRESHOLDS["preferred"]]

        selected = list(must)
        remaining = TARGET_ITEMS_PER_REPORT - len(selected)

        if remaining > 0:
            selected.extend(preferred[:remaining])
            remaining = TARGET_ITEMS_PER_REPORT - len(selected)

        if remaining > 0:
            selected.extend(candidates[:remaining])

        logger.info(f"筛选结果: 必选{len(must)} + 优选{min(len(preferred), TARGET_ITEMS_PER_REPORT - len(must))} = {len(selected)} 条")
        return selected

    # ==========================================================
    # 3. 翻译
    # ==========================================================
    def translate_items(self, items: list[dict]) -> list[dict]:
        """翻译英文内容为中文"""
        to_translate = [i for i in items if i.get("language") == "en"]
        if not to_translate:
            logger.info("无需翻译的英文内容")
            return items

        logger.info(f"翻译 {len(to_translate)} 条英文内容...")

        batch_size = 8
        for i in range(0, len(to_translate), batch_size):
            batch = to_translate[i:i + batch_size]
            self._translate_batch(batch)

        return items

    def _translate_batch(self, batch: list[dict]):
        """批量翻译"""
        texts = []
        for idx, item in enumerate(batch):
            texts.append(f"[{idx}] {item['content'][:500]}")

        prompt = f"""将以下{len(batch)}条英文AI新闻翻译为中文。

要求:
1. 技术术语保留英文原文（transformer, API, token, GPU, LLM, RAG, benchmark 等不翻译）
2. 产品名保留原文（GPT-5, Claude, Gemini, LangChain 等）
3. 数字、百分比、货币符号保持原样
4. 链接保持原样
5. 译文自然流畅，符合中文表达

待翻译:
{chr(10).join(texts)}

只返回JSON数组:
```json
[
  {{"index": 0, "translation": "翻译后的中文内容"}},
  {{"index": 1, "translation": "翻译后的中文内容"}}
]
```"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                ),
            )
            translations = self._parse_json_array(response.text)

            for t in translations:
                idx = t.get("index", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["content_zh"] = t.get("translation", batch[idx]["content"])
                    if batch[idx].get("title"):
                        # 标题也需要翻译，但通常已经是中文
                        pass

        except Exception as e:
            logger.warning(f"批量翻译失败: {e}")
            for item in batch:
                item.setdefault("content_zh", item["content"])

        # 确保每个 item 都有 content_zh
        for item in batch:
            item.setdefault("content_zh", item["content"])

    # ==========================================================
    # 4. 报告生成
    # ==========================================================
    def generate_report(self, items: list[dict], report_type: str = "global") -> str:
        """使用 Gemini 生成最终中文 Markdown 日报"""
        today = datetime.now().strftime("%Y年%m月%d日")

        # 准备数据
        items_data = []
        for item in items:
            content = item.get("content_zh") or item.get("content", "")
            items_data.append({
                "title": item.get("title", ""),
                "content": content[:300],
                "author": item.get("author", ""),
                "source_url": item.get("source_url", ""),
                "published_time": item.get("published_time", ""),
                "category": item.get("category", "行业动态"),
                "score": item.get("final_score", 0),
            })

        report_name = "全球AI日报" if report_type == "global" else "中国AI日报"
        emoji = "🤖" if report_type == "global" else "🇨🇳"

        if report_type == "global":
            categories_section = """按以下类别组织：
- 🔥 产品发布
- 🔬 研究突破
- 📊 行业动态
- 💡 技术讨论
- 🛠️ 工具推荐"""
        else:
            categories_section = """按以下类别组织：
- 🎯 国内产品
- 🔬 技术进展
- 💼 融资并购
- 💡 开发者实践
- 🛠️ 工具推荐
- 📊 行业观察"""

        prompt = f"""基于以下AI资讯数据，生成一份专业的中文日报。

报告名称: {emoji} {report_name} - {today}

资讯数据:
{json.dumps(items_data, ensure_ascii=False, indent=2)}

{categories_section}

格式要求:
1. 开头 "## 📌 今日要点" 列出3-5条最重要信息
2. 分类别展示，每条包含：加粗标题、一句话描述、来源和时间
3. 每条格式如下：
   • **标题**
     描述内容（1-2句话）
     来源: @作者 | 时间 | [查看原文](url)
4. 空类别（无内容）跳过不显示
5. 全部使用中文，技术术语保留英文
6. 末尾加: _本报告由AI自动生成 | 数据来源: Twitter | {today}_
7. 总字数控制在600-1000字

只返回 Markdown 内容，不要其他说明。"""

        try:
            response = self.model_report.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE_REPORT,
                    max_output_tokens=3000,
                ),
            )
            report = response.text.strip()

            # 确保有一级标题
            if not report.startswith("#"):
                report = f"# {emoji} {report_name} - {today}\n\n{report}"

            return report

        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return self._fallback_report(items, report_type, today)

    def _fallback_report(self, items: list[dict], report_type: str, today: str) -> str:
        """降级生成：简单模板拼接"""
        emoji = "🤖" if report_type == "global" else "🇨🇳"
        name = "全球AI日报" if report_type == "global" else "中国AI日报"

        lines = [f"# {emoji} {name} - {today}\n"]
        lines.append("## 📌 今日要点\n")
        for item in items[:5]:
            lines.append(f"- {item.get('title', item.get('content', '')[:50])}")
        lines.append("\n---\n")

        for item in items:
            content = item.get("content_zh") or item.get("content", "")
            lines.append(f"• **{item.get('title', '无标题')}**")
            lines.append(f"  {content[:150]}")
            lines.append(f"  来源: {item.get('author', '')} | {item.get('published_time', '')}")
            if item.get("source_url"):
                lines.append(f"  [查看原文]({item['source_url']})")
            lines.append("")

        lines.append(f"\n_本报告由AI自动生成 | {today}_")
        return "\n".join(lines)

    # ==========================================================
    # 工具方法
    # ==========================================================
    def _parse_json_array(self, text: str) -> list[dict]:
        """从文本中解析 JSON 数组"""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass

        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n(.*?)\n```',
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

        # 最后尝试找最外层的 [ ... ]
        bracket_match = re.search(r'\[[\s\S]*\]', text)
        if bracket_match:
            try:
                return json.loads(bracket_match.group())
            except (json.JSONDecodeError, TypeError):
                pass

        return []

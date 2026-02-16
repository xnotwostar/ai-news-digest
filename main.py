#!/usr/bin/env python3
"""
AI News Digest - 每日AI新闻日报生成器
主入口程序

用法:
    python main.py                 # 生成全球+中国双日报
    python main.py --type global   # 仅全球日报
    python main.py --type china    # 仅中国日报
    python main.py --no-push       # 生成但不推送
    python main.py --no-dingtalk   # 不发钉钉
"""
import argparse
import logging
import sys
from datetime import datetime

from src.collector import NewsCollector
from src.processor import GeminiProcessor
from src.publisher import GitHubPublisher, DingTalkPublisher
from config.settings import LOG_LEVEL, REPORTS_DIR

# 日志配置
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ai-digest")


def run_digest(report_type: str, collector: NewsCollector, processor: GeminiProcessor) -> str | None:
    """
    执行单份日报的完整流程

    Args:
        report_type: "global" 或 "china"

    Returns:
        生成的 Markdown 报告内容，失败返回 None
    """
    type_name = "全球" if report_type == "global" else "中国"
    logger.info(f"{'='*50}")
    logger.info(f"开始生成 {type_name}AI日报")
    logger.info(f"{'='*50}")

    # Step 1: 采集
    logger.info("📡 Step 1/4: 数据采集...")
    if report_type == "global":
        items = collector.collect_global()
    else:
        items = collector.collect_china()

    if not items:
        logger.warning(f"未采集到{type_name}新闻数据")
        return None

    # Step 2: 评分 + 筛选
    logger.info("📊 Step 2/4: 评分筛选...")
    scored_items = processor.score_items(items)
    selected_items = processor.select_items(scored_items)

    if not selected_items:
        logger.warning("筛选后无内容")
        return None

    # Step 3: 翻译
    logger.info("🌐 Step 3/4: 翻译处理...")
    translated_items = processor.translate_items(selected_items)

    # Step 4: 生成报告
    logger.info("📝 Step 4/4: 生成报告...")
    report = processor.generate_report(translated_items, report_type)

    # 保存本地副本
    today = datetime.now().strftime("%Y-%m-%d")
    local_path = REPORTS_DIR / f"{report_type}-ai-digest-{today}.md"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(report, encoding="utf-8")
    logger.info(f"💾 本地保存: {local_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="AI News Digest - 每日AI新闻日报生成器")
    parser.add_argument(
        "--type", choices=["global", "china", "both"], default="both",
        help="日报类型: global(全球), china(中国), both(两者) 默认: both",
    )
    parser.add_argument("--no-push", action="store_true", help="不推送到 GitHub")
    parser.add_argument("--no-dingtalk", action="store_true", help="不发送钉钉通知")
    parser.add_argument("--dry-run", action="store_true", help="试运行：只采集和评分，不生成报告")
    args = parser.parse_args()

    start_time = datetime.now()
    logger.info(f"🚀 AI News Digest 启动 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 初始化模块
    collector = NewsCollector()
    processor = GeminiProcessor()

    # 生成日报
    reports = {}
    types_to_run = ["global", "china"] if args.type == "both" else [args.type]

    for report_type in types_to_run:
        report = run_digest(report_type, collector, processor)
        if report:
            reports[report_type] = report

    if not reports:
        logger.error("❌ 未能生成任何日报")
        sys.exit(1)

    if args.dry_run:
        logger.info("🔍 试运行完成，跳过发布")
        for rt, content in reports.items():
            print(f"\n{'='*60}")
            print(f"  {rt.upper()} 日报预览")
            print(f"{'='*60}")
            print(content[:500])
            print("...")
        sys.exit(0)

    # 发布
    if not args.no_push:
        logger.info("📤 推送到 GitHub...")
        github = GitHubPublisher()
        github.publish(reports)

    if not args.no_dingtalk:
        logger.info("🔔 发送钉钉通知...")
        dingtalk = DingTalkPublisher()
        dingtalk.publish(reports)

    # 完成
    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"✅ 全部完成！耗时 {elapsed:.1f} 秒")
    logger.info(f"   生成日报: {', '.join(reports.keys())}")


if __name__ == "__main__":
    main()

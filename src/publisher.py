"""
发布模块 - GitHub 推送 & 钉钉 Webhook 通知
"""
import hashlib
import hmac
import json
import logging
import subprocess
import time
import urllib.parse
import base64
from datetime import datetime
from pathlib import Path

import requests

from config.settings import (
    GITHUB_REPO, GITHUB_BRANCH, GITHUB_TOKEN,
    DINGTALK_ENABLED, DINGTALK_WEBHOOK_URL, DINGTALK_SECRET,
    REPORTS_DIR,
)

logger = logging.getLogger(__name__)


class GitHubPublisher:
    """将日报推送到 GitHub 公开仓库"""

    def __init__(self):
        self.repo = GITHUB_REPO
        self.branch = GITHUB_BRANCH
        self.token = GITHUB_TOKEN

    def publish(self, reports: dict[str, str]) -> bool:
        """
        将报告文件 commit & push 到 GitHub

        Args:
            reports: {"global": "markdown内容", "china": "markdown内容"}
        """
        if not self.repo or not self.token:
            logger.warning("GitHub 配置不完整，跳过推送")
            return False

        today = datetime.now().strftime("%Y-%m-%d")
        year_month = datetime.now().strftime("%Y/%m")

        try:
            # 保存文件到本地 reports 目录
            report_dir = REPORTS_DIR / year_month
            report_dir.mkdir(parents=True, exist_ok=True)

            files_to_commit = []
            for report_type, content in reports.items():
                filename = f"{report_type}-ai-digest-{today}.md"
                filepath = report_dir / filename
                filepath.write_text(content, encoding="utf-8")
                # Git 中的相对路径
                git_path = f"reports/{year_month}/{filename}"
                files_to_commit.append((str(filepath), git_path))
                logger.info(f"  保存报告: {filepath}")

            # 同时更新 latest 软链（方便访问最新日报）
            for report_type, content in reports.items():
                latest_path = REPORTS_DIR / f"latest-{report_type}.md"
                latest_path.write_text(content, encoding="utf-8")
                files_to_commit.append((str(latest_path), f"reports/latest-{report_type}.md"))

            # Git 操作
            return self._git_commit_and_push(files_to_commit, today)

        except Exception as e:
            logger.error(f"GitHub 推送失败: {e}")
            return False

    def _git_commit_and_push(self, files: list[tuple], today: str) -> bool:
        """执行 git add, commit, push"""
        repo_dir = REPORTS_DIR.parent

        try:
            # 配置 git（如果在 CI 环境中）
            self._run_git(repo_dir, ["git", "config", "user.email", "ai-digest-bot@users.noreply.github.com"])
            self._run_git(repo_dir, ["git", "config", "user.name", "AI Digest Bot"])

            # 设置远程仓库地址（带 token）
            remote_url = f"https://x-access-token:{self.token}@github.com/{self.repo}.git"
            self._run_git(repo_dir, ["git", "remote", "set-url", "origin", remote_url])

            # Pull 最新
            self._run_git(repo_dir, ["git", "pull", "origin", self.branch, "--rebase"])

            # Add 所有报告文件
            for local_path, _ in files:
                self._run_git(repo_dir, ["git", "add", local_path])

            # Commit
            commit_msg = f"📰 AI News Digest - {today}"
            result = self._run_git(repo_dir, ["git", "commit", "-m", commit_msg])

            if "nothing to commit" in result:
                logger.info("无新内容需要提交")
                return True

            # Push
            self._run_git(repo_dir, ["git", "push", "origin", self.branch])
            logger.info(f"✅ 成功推送到 GitHub: {self.repo}")
            return True

        except Exception as e:
            logger.error(f"Git 操作失败: {e}")
            return False

    def _run_git(self, cwd: Path, cmd: list[str]) -> str:
        """执行 git 命令"""
        result = subprocess.run(
            cmd, cwd=str(cwd),
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logger.debug(f"Git stderr: {result.stderr}")
        return result.stdout + result.stderr


class DingTalkPublisher:
    """钉钉 Webhook 推送日报"""

    def __init__(self):
        self.webhook_url = DINGTALK_WEBHOOK_URL
        self.secret = DINGTALK_SECRET
        self.enabled = DINGTALK_ENABLED

    def publish(self, reports: dict[str, str]) -> bool:
        """
        推送日报到钉钉群

        Args:
            reports: {"global": "markdown内容", "china": "markdown内容"}
        """
        if not self.enabled:
            logger.info("钉钉推送已禁用")
            return True

        if not self.webhook_url:
            logger.warning("钉钉 Webhook URL 未配置，跳过推送")
            return False

        success = True
        for report_type, content in reports.items():
            title = "🤖 全球AI日报" if report_type == "global" else "🇨🇳 中国AI日报"
            try:
                self._send_markdown(title, content)
                logger.info(f"✅ 钉钉推送成功: {title}")
            except Exception as e:
                logger.error(f"钉钉推送失败 ({title}): {e}")
                success = False

        return success

    def _send_markdown(self, title: str, content: str):
        """发送 Markdown 消息"""
        url = self._get_signed_url()

        # 钉钉 Markdown 消息体
        # 注意：钉钉 Markdown 有长度限制（约20000字符）
        # 如果超长则截断
        if len(content) > 18000:
            content = content[:18000] + "\n\n...(内容已截断)"

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content,
            }
        }

        headers = {"Content-Type": "application/json; charset=utf-8"}

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()

        if result.get("errcode") != 0:
            raise RuntimeError(f"钉钉API错误: {result}")

    def _get_signed_url(self) -> str:
        """生成带签名的 Webhook URL"""
        if not self.secret:
            return self.webhook_url

        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        return f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"

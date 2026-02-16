# 🤖 AI News Digest - 每日AI新闻日报

自动采集、评分、翻译并生成AI领域中文日报，分为 **全球AI日报** 和 **中国AI日报** 两份。

## 架构

```
Claude web_search 采集 → Gemini 评分/翻译/生成 → GitHub 存档 + 钉钉推送
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

需要的 Key:
- `ANTHROPIC_API_KEY` - Claude API（用于 web_search 数据采集）
- `GEMINI_API_KEY` - Google Gemini API（用于评分、翻译、报告生成）
- `GITHUB_TOKEN` - GitHub PAT（用于自动推送报告）
- `DINGTALK_WEBHOOK_URL` - 钉钉机器人 Webhook（可选）

### 3. 运行

```bash
# 生成全球+中国双日报
python main.py

# 仅全球日报
python main.py --type global

# 仅中国日报
python main.py --type china

# 试运行（不推送）
python main.py --dry-run

# 不发钉钉
python main.py --no-dingtalk
```

## 自动化部署

### GitHub Actions（推荐）

项目已包含 `.github/workflows/daily-digest.yml`，在 GitHub 仓库的 Settings → Secrets 中添加:

- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `DINGTALK_WEBHOOK_URL`（可选）
- `DINGTALK_SECRET`（可选）

默认每天北京时间 8:00 自动运行，也可在 Actions 页面手动触发。

### Docker

```bash
docker build -t ai-news-digest .
docker run --env-file .env ai-news-digest
```

## 项目结构

```
ai-news-digest/
├── main.py                    # 主入口
├── config/
│   ├── settings.py            # 全局配置
│   └── accounts.py            # 账号清单 & 搜索关键词
├── src/
│   ├── collector.py           # Claude web_search 数据采集
│   ├── processor.py           # Gemini 评分/翻译/报告生成
│   └── publisher.py           # GitHub 推送 & 钉钉通知
├── reports/                   # 生成的日报存放目录
├── .github/workflows/
│   └── daily-digest.yml       # GitHub Actions 定时任务
├── .env.example               # 环境变量模板
├── requirements.txt
├── Dockerfile
└── README.md
```

## 评分系统

4维度加权评分，满分10分:

| 维度 | 权重 | 说明 |
|------|------|------|
| 作者权威度 | 30% | 基于预设权重表（1-10） |
| 内容重要性 | 30% | Gemini 评估（产品发布>研究>一般） |
| 内容质量 | 25% | Gemini 评估（数据密度、技术深度） |
| 时效性 | 15% | 基于发布时间（越新越高） |

## 自定义

- **添加/删除监控账号**: 编辑 `config/accounts.py`
- **调整搜索关键词**: 编辑 `config/accounts.py` 中的 `*_SEARCH_QUERIES`
- **修改评分权重**: 编辑 `config/settings.py` 中的 `SCORE_WEIGHTS`
- **切换 Gemini 模型**: 通过环境变量 `GEMINI_MODEL` 设置

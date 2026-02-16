# AI News Digest - 完整部署指南

## 前置条件

| 需要准备 | 获取方式 |
|----------|---------|
| Anthropic API Key | https://console.anthropic.com → API Keys |
| Google Gemini API Key | https://aistudio.google.com/apikey |
| GitHub 账号 | https://github.com |
| 钉钉群机器人 Webhook（可选） | 钉钉群设置 → 智能群助手 → 添加机器人 |

---

## 第一步：创建 GitHub 仓库

### 1.1 新建仓库

到 https://github.com/new 创建仓库：

- Repository name: `ai-news-digest`
- 选择 **Public**
- 勾选 "Add a README file"
- 点击 Create repository

### 1.2 克隆到本地

```bash
git clone https://github.com/你的用户名/ai-news-digest.git
cd ai-news-digest
```

### 1.3 把项目文件复制进去

将生成的所有项目文件复制到仓库目录中，结构如下：

```
ai-news-digest/
├── main.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── accounts.py
├── src/
│   ├── __init__.py
│   ├── collector.py
│   ├── processor.py
│   └── publisher.py
├── reports/          ← 自动生成，先创建空目录
└── .github/
    └── workflows/
        └── daily-digest.yml
```

```bash
# 创建 reports 目录占位
mkdir -p reports
touch reports/.gitkeep
```

### 1.4 首次提交

```bash
git add .
git commit -m "init: AI News Digest project"
git push origin main
```

---

## 第二步：配置 GitHub Secrets

到仓库页面 → **Settings** → 左侧 **Secrets and variables** → **Actions** → **New repository secret**

依次添加以下 secrets：

| Secret 名称 | 值 | 必填 |
|-------------|---|------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` 你的 Claude API Key | ✅ |
| `GEMINI_API_KEY` | `AIzaSy...` 你的 Gemini API Key | ✅ |
| `DINGTALK_WEBHOOK_URL` | `https://oapi.dingtalk.com/robot/send?access_token=xxx` | 可选 |
| `DINGTALK_SECRET` | `SECxxx` 钉钉机器人加签密钥 | 可选 |

> **注意**：GitHub Actions 自带 `GITHUB_TOKEN`，不需要额外配置 GitHub 推送权限。

---

## 第三步：配置钉钉机器人（可选）

### 3.1 创建机器人

1. 打开钉钉群 → 右上角设置 → **智能群助手** → **添加机器人**
2. 选择 **自定义（通过Webhook接入自定义服务）**
3. 机器人名称填：`AI日报助手`
4. 安全设置选择 **加签**，复制生成的密钥（以 `SEC` 开头）
5. 点击完成，复制 Webhook URL

### 3.2 记录两个值

- **Webhook URL**: `https://oapi.dingtalk.com/robot/send?access_token=xxxxxx`
- **加签密钥**: `SECxxxxxxxxxxxxxxxxxxxxxxxx`

这两个值分别填入 GitHub Secrets 的 `DINGTALK_WEBHOOK_URL` 和 `DINGTALK_SECRET`。

---

## 第四步：验证 GitHub Actions

### 4.1 手动触发一次

1. 到仓库页面 → **Actions** 标签页
2. 左侧选择 **Daily AI News Digest**
3. 点击 **Run workflow** → 选择 `both` → **Run workflow**

### 4.2 查看运行日志

点击运行中的 workflow → 查看 `generate-digest` job 的日志。

正常流程大约 3-8 分钟完成，日志中会显示：

```
📡 Step 1/4: 数据采集...
  搜索 [1/14]: OpenAI GPT announcement today...
    获取到 5 条结果
  ...
📊 Step 2/4: 评分筛选...
🌐 Step 3/4: 翻译处理...
📝 Step 4/4: 生成报告...
✅ 全部完成！耗时 180.5 秒
```

### 4.3 检查输出

运行成功后：
- 仓库的 `reports/` 目录会出现当天的日报文件
- `reports/latest-global.md` 和 `reports/latest-china.md` 始终指向最新日报
- 如果配置了钉钉，群里会收到两条 Markdown 消息

---

## 第五步：自动定时运行

GitHub Actions 已配置 cron `0 0 * * *`（UTC 0:00 = 北京时间 8:00），每天自动运行。

### 调整运行时间

编辑 `.github/workflows/daily-digest.yml`：

```yaml
schedule:
  # UTC 时间，北京时间 = UTC + 8
  - cron: '0 0 * * *'    # 北京时间 08:00
  # - cron: '0 22 * * *'  # 北京时间 06:00（次日）
  # - cron: '30 1 * * *'  # 北京时间 09:30
```

> **注意**：GitHub Actions 的 cron 调度有 5-15 分钟的随机延迟，这是正常现象。

---

## 第六步：本地开发与调试（可选）

如果你想在本地运行或调试：

### 6.1 环境搭建

```bash
cd ai-news-digest

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 6.2 本地运行

```bash
# 试运行（只采集评分，不推送）
python main.py --dry-run

# 生成全球日报，不推送
python main.py --type global --no-push --no-dingtalk

# 完整运行（会推送 GitHub + 钉钉）
python main.py
```

### 6.3 Docker 运行

```bash
docker build -t ai-news-digest .
docker run --env-file .env ai-news-digest

# 指定只生成中国日报
docker run --env-file .env ai-news-digest python main.py --type china
```

---

## 常见问题

### Q: GitHub Actions 运行失败，提示 API Key 错误？
检查 Settings → Secrets 中的 key 是否正确粘贴，注意前后不要有空格或换行。

### Q: 钉钉没收到消息？
1. 确认 `DINGTALK_WEBHOOK_URL` 和 `DINGTALK_SECRET` 都已配置
2. 确认机器人安全设置是"加签"模式
3. 查看 Actions 日志中钉钉推送的错误信息

### Q: 采集到的新闻太少？
编辑 `config/accounts.py`，增加搜索关键词或调整查询语句。也可以在 `config/settings.py` 中降低 `SCORE_THRESHOLDS` 的阈值。

### Q: 想换 Gemini 模型？
在 GitHub Secrets 中添加 `GEMINI_MODEL` 和 `GEMINI_MODEL_REPORT`，或直接修改 `config/settings.py`。

### Q: 每月大概花多少钱？
- Anthropic API（web_search）：约 $20-40/月
- Gemini API（Flash 模型）：免费额度通常够用，超出约 $1-5/月
- GitHub Actions：公开仓库免费

---

## 运行架构图

```
┌──────────────────────────────────────────────────────┐
│  GitHub Actions  (每天 UTC 0:00 / 北京时间 8:00)      │
│                                                      │
│  1. checkout repo                                    │
│  2. pip install                                      │
│  3. python main.py --type both                       │
│     ├─ collector.py → Claude web_search 采集          │
│     ├─ processor.py → Gemini 评分/翻译/生成           │
│     └─ publisher.py → 钉钉推送                       │
│  4. git add + commit + push reports/                 │
└──────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐         ┌──────────────────┐
│  GitHub 仓库      │         │  钉钉群           │
│  reports/         │         │  Markdown 日报    │
│  ├─ 2026/02/      │         │  全球 + 中国      │
│  │  ├─ global-... │         └──────────────────┘
│  │  └─ china-...  │
│  ├─ latest-*.md   │
│  └─ ...           │
└──────────────────┘
```

# BossJob AI 智能匹配工作台 Demo

基于简历和求职偏好，自动匹配东南亚岗位的 AI Agent Demo。

## 功能流程

```
上传简历 (PDF)
    ↓ OCR / 文本提取 + Llama 结构化解析
收集求职偏好（对话 + 表单）
    ↓ 自由文本 → Llama 抽取槽位
匹配引擎（两阶段）
    ↓ SQL 硬过滤 → 向量重排 → Llama 生成匹配理由
展示 Top 3 岗位，收集点赞 / 点踩偏好信号
    ↓ 写回 DB，影响下次召回
进入全量岗位列表
```

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Next.js 14 + Tailwind CSS + Zustand |
| 前端原型 | 单页 HTML（已对接 API，可独立演示） |
| 后端 | FastAPI + Python 3.11 |
| 数据库 | PostgreSQL 16 + pgvector |
| 解析 | pypdf（原生 PDF）/ PaddleOCR（扫描件） |
| 生成 / 推理 | 本地部署 Llama 3.1（OpenAI-compatible API） |
| 向量嵌入 | sentence-transformers `all-MiniLM-L6-v2`（384 维，本地运行） |

## 目录结构

```
.
├── bossjob-onboarding.html   # 前端原型（HTML，可独立演示）
├── docker-compose.yml        # PostgreSQL + pgvector + 后端容器
├── frontend/                 # Next.js 前端
│   ├── src/
│   │   ├── app/              # App Router 入口
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   └── StepNav.tsx       # 步骤导航栏
│   │   │   └── steps/
│   │   │       ├── ResumeUpload.tsx  # Step 1：上传简历
│   │   │       ├── Preferences.tsx   # Step 2：偏好收集（对话 + 浮动卡片）
│   │   │       ├── PreferenceCard.tsx
│   │   │       ├── Matches.tsx       # Step 3：匹配结果 + 反馈
│   │   │       └── Explore.tsx       # Step 4：完成页
│   │   ├── store/
│   │   │   └── onboarding.ts         # Zustand 全局状态
│   │   ├── lib/
│   │   │   ├── api.ts                # 后端 API 调用封装
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── index.ts              # TypeScript 类型定义
│   └── package.json
└── backend/
    ├── main.py               # FastAPI 入口
    ├── prompts.py            # Llama prompt 模板（解析 / 偏好提取 / 匹配理由）
    ├── schema.sql            # 数据库建表，容器启动时自动执行
    ├── requirements.txt
    ├── Dockerfile
    ├── routers/
    │   ├── resume.py         # POST /api/resume/parse
    │   ├── preferences.py    # POST /api/preferences/extract|save
    │   └── matches.py        # POST /api/matches/search|feedback
    ├── services/
    │   ├── llama.py          # Llama HTTP 客户端 + 本地 embedding
    │   └── matcher.py        # 两阶段匹配 pipeline
    └── scripts/
        └── import_jds.py     # JD 批量导入脚本
```

## 快速启动

### 1. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，填入已部署的 Llama 地址：

```env
LLAMA_BASE_URL=http://your-llama-host:port
LLAMA_MODEL=llama3.1
```

### 2. 启动数据库 + 后端

```bash
docker compose up
```

首次启动会自动执行 `schema.sql` 建表。后端运行在 `http://localhost:8000`。

### 3. 导入岗位数据

编辑 `backend/scripts/import_jds.py`，在 `JDS` 列表中填入真实 JD 数据，然后：

```bash
cd backend
python scripts/import_jds.py
```

脚本会自动生成向量嵌入并写入数据库。

### 4. 启动 Next.js 前端

```bash
cd frontend
cp .env.local.example .env.local   # 默认指向 http://localhost:8000，无需修改
npm install
npm run dev
```

打开 `http://localhost:3000` 即可使用完整的四步 onboarding 流程。

### 4b. 仅使用 HTML 原型（无需 Node.js）

直接用浏览器打开 `bossjob-onboarding.html`。API 地址在文件顶部 `<script>` 中的 `var API` 变量修改。

> **Demo 模式**：未上传 PDF 时，两种前端均使用 hardcoded 示例数据，不依赖后端，可独立演示。

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/resume/parse` | 上传 PDF，返回 `resume_id` + 结构化简历 JSON |
| POST | `/api/preferences/extract` | 自由文本 → 求职偏好槽位 JSON |
| POST | `/api/preferences/save` | 保存 / 更新偏好记录 |
| POST | `/api/matches/search` | 两阶段匹配，返回 Top N 岗位 + 匹配理由 |
| POST | `/api/matches/feedback` | 写入点赞 / 点踩信号 |
| GET  | `/health` | 健康检查 |

完整请求 / 响应结构见 `frontend/src/types/index.ts`。

## 数据约束

- 简历：仅支持 PDF，限 5 页以内
- OCR：识别置信度 < 85% 时标记警告
- JD 库：建议控制在 100 条以内，保证向量检索 < 100ms
- 匹配理由：Llama 严格基于简历事实生成，禁止捏造未提及技能

## JD 数据格式

`import_jds.py` 中每条 JD 的必填字段：

```python
{
    "title":            "职位名称",
    "company":          "公司名称",
    "location":         "城市, 国家",           # 如 "Singapore" / "Jakarta, Indonesia"
    "work_arrangement": "onsite|hybrid|remote",
    "job_type":         "full-time|part-time|contract|internship",
    "salary_min":       5000,                   # 月薪，整数
    "salary_max":       8000,
    "currency":         "SGD|MYR|IDR|PHP|USD",
    "description":      "完整职位描述（用于向量嵌入和 Llama 推理）",
    "highlights":       ["亮点1", "亮点2", "亮点3"],   # 展示在匹配卡片上
    "tags":             ["tag1", "tag2"],               # 技能 / 领域标签，提升嵌入质量
}
```

## 已知限制

- 无用户认证，无投递功能，无 ATS 集成（Demo 范围）
- "在线填写简历"入口（Page 1）暂未实现
- Llama 推理延迟取决于部署环境，Page 3 首次加载可能需要 5–15 秒

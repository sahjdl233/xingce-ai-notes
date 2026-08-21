# xingce-ai-notes · 行测错题智能整理

基于 Cloudflare Pages 的纯前端行测错题整理工具：把一次做错的题目合集整段粘贴进去，AI 自动分类，并按各题型模板逐道整理成可背诵的错题卡片，可直接粘贴进 Obsidian 错题本。

## 功能特性

- **自动分类**：言语理解 / 逻辑填空 / 数量关系 / 判断推理 / 资料分析 / 常识判断·政治理论，无法归类的走通用模板
- **两步生成**：先分类、再按类型分批调用，每类只携带对应模板，模板遵循度高
- **常识/政治特殊规则**：只输出「题目解析 + 逐条知识点积累」，不做错因分析；涉及可能变化的官方提法时自动附加 ⚠️ 核实提示
- **其余类型**：解析 + 错因 + 正确思路 + 秒题技巧 / 公式 / 易混词，字段与仓库内 Obsidian 模板一一对应
- **格式零出错**：AI 只输出结构化 JSON 字段，最终 markdown 由程序按固定模板渲染，字段顺序与版式 100% 稳定
- **大题量支持**：自动分块、并行调用，一次处理几十上百道也没问题
- **多级导出**：逐卡复制 / 复制本类 / 复制全部 / 下载本类 .md / 下载全部 .md

## 技术方案

| 模块 | 说明 |
| --- | --- |
| 前端 | 单文件 `index.html`，无框架、无构建 |
| 代理 | `functions/api/chat.js`（Cloudflare Pages Functions），透传 OpenAI 兼容接口，解决浏览器跨域 |
| API | 任意 OpenAI 兼容服务（Base URL + 模型名 + Key），Key 仅用于拼接请求头、不落盘 |

### 生成流程

1. 整段粘贴错题合集（支持粉笔复制格式）
2. 客户端按空行分块，AI 逐块识别题目并分类（6 类 + 通用兜底）
3. 按类型批量调用生成接口，每类携带对应的字段 schema
4. 程序按固定模板渲染 markdown，按原始输入顺序展示为卡片

## 项目结构

```
.
├── index.html                 # 单文件前端
├── functions/
│   └── api/
│       └── chat.js            # Cloudflare Pages Functions 代理
├── preview_server.py          # 本地完整预览（静态 + /api/chat 代理）
├── README.md
└── <各类>错题本.md             # Obsidian 参考模板，输出格式与其对齐
```

## 部署到 Cloudflare Pages

三种方式任选。部署完成后打开 `*.pages.dev` 链接即可使用。

### 方式一：Wrangler CLI

在项目根目录执行：

```bash
npx wrangler pages deploy . --project-name=xingce-ai-notes
```

### 方式二：Git 集成（推荐）

1. 把仓库推送到 GitHub
2. Cloudflare 控制台 → Workers & Pages → Create → Pages → Connect to Git
3. 选择仓库，构建命令留空，构建输出目录填 `/`
4. `functions/` 会被自动识别为 Pages Functions

### 方式三：控制台 Direct Upload

Create project → Direct upload → 上传**整个项目文件夹**（必须包含 `functions/` 子目录，否则 `/api/chat` 会 404）。

## 使用

1. 打开部署后的页面
2. 接口设置：Base URL（如 `https://api.deepseek.com/v1`）、模型名、API Key
3. 把粉笔复制的错题合集整段粘贴到文本框
4. 点击「开始整理」，等待逐题卡片生成

提示：Base URL 与模型名会记住；只有勾选「记住 Key」才会把 Key 存到本机浏览器。

## 本地预览

仓库自带带代理的预览服务器，可完整跑通生成流程：

```bash
python3 preview_server.py . 8000
```

打开 http://localhost:8000 即可使用；若只想看界面，用 `python3 -m http.server 8000` 即可（但 `/api/chat` 不可用）。

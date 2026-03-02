# OpenClaw Workspace Viewer 实施方案

本文档给出一个可迭代、可验证的 Workspace Viewer 方案，用于在 OpenClaw 工作目录中高效浏览与搜索 Markdown 文档。目标是在不引入安全隐患的前提下，提供清晰的文件树、快速搜索、优秀的 Markdown 渲染与便捷的导航体验。

## 1. 目标与范围
- 支持浏览 OpenClaw 工作区（默认根目录：/Users/mocklab/.openclaw/workspace，可配置）内的所有 Markdown 文件（.md/.mdx）。
- 提供文件树导航、全文搜索、面包屑/历史/收藏、TOC（标题目录）、代码高亮、Mermaid 图、任务列表、表格、脚注、图片等常见 Markdown 能力。
- 保持安全：禁止任意路径访问和 XSS；仅允许访问工作区内文件。
- 可扩展：后续可接入反向链接/知识图谱、批量导出、批注、高级搜索等能力。

## 2. 用户故事（简述）
- 作为用户，我可以在左侧树中查看目录与 Markdown 文件，并在右侧阅读内容。
- 我可以在搜索框输入关键词，快速定位包含关键词的文档与段落。
- 我可以查看文档 TOC，快速跳转到各标题。
- 我可以复制当前文档的深链（带锚点）或生成可分享的本地链接。
- 我可以查看最近打开与收藏的文档。

## 3. 技术选型（建议）
- 后端：Node.js (Express/Koa) 提供目录索引与文件读取 API；使用 chokidar 做文件变更监听；TypeScript 保持类型安全。
- 前端：Vite + React + TypeScript。组件：文件树（可虚拟滚动）、Markdown 渲染（remark/rehype/unified 生态）、代码高亮（Shiki 或 highlight.js）、Mermaid（mermaid-js）。
- 搜索：初期使用简单索引（路径名/标题/正文内存索引 + 关键词匹配）；后续可替换为 lunr.js/flexsearch。
- 样式：Tailwind CSS 或 CSS Modules（根据项目既有风格决定，若无则选 Tailwind）。
- 打包与运行：单 repo（web 与 server 在同目录下），一键启动开发服务并提供预览。

## 4. 架构概览
- Server（后端）
  - 索引器：扫描工作区，构建目录树与文档元数据缓存；watch 变更并增量更新。
  - API：只读接口，返回树、文档内容、搜索结果；对 path 做严格校验与归一化，限制在根目录内。
- Client（前端）
  - 左侧：文件树（折叠/展开、搜索结果标记、最近/收藏）。
  - 右侧：Markdown 渲染区（TOC、锚点、代码高亮、Mermaid、图片/附件处理）。
  - 顶部：全局搜索框、面包屑、操作按钮（复制链接、在系统/IDE 打开）。

## 5. 后端设计
### 5.1 目录与路径
- 工作区根：config.root 默认为 /Users/mocklab/.openclaw/workspace，可在 config 文件中覆盖。
- 忽略：node_modules、.git、.DS_Store、隐藏目录、体积超大文件（> 5MB，可配置）、非文本资源默认不索引正文。
- 路径安全：使用 path.resolve + path.relative 校验，禁止 “..” 越权；只允许以 root 为前缀的真实路径。

### 5.2 数据结构
- TreeNode
  - type: "dir" | "file"
  - name: string
  - path: string（相对 root 的统一分隔符路径）
  - children?: TreeNode[]
  - meta?: { size, mtime, headings?: Heading[], hasMermaid?: boolean }
- Index
  - map: path -> { title, headings, plainText, updatedAt }
  - 支持按关键词检索（大小写不敏感，中文分词先用简单空白/标点切分，后续可接第三方分词）。

### 5.3 API 草案
- GET /api/tree
  - 返回目录树（延迟加载可选：先返回顶层，再按需加载子树）。
- GET /api/file?path=<relativePath>
  - 返回文件内容（UTF-8 文本），并携带 meta（例如 mtime、size）。
- GET /api/toc?path=<relativePath>
  - 返回该文件的标题结构（在服务端以 remark 提前抽取，或前端解析后缓存）。
- GET /api/search?q=keyword
  - 返回命中文档列表与片段摘要（匹配行的上下文片段；为性能可限定前 N 条）。
- GET /api/meta
  - 返回基本信息（root、忽略规则、版本、构建信息）。

### 5.4 索引与监听
- 启动时全量扫描构建树与索引（可逐步异步完成：优先目录树，其次文档标题与正文）。
- chokidar 监听新增/删除/修改事件，实时更新树和索引，向前端推送变更（SSE 或 WebSocket；v1 可前端定时轮询 /api/meta?etag）。

## 6. 前端设计
### 6.1 页面布局
- 头部：搜索框、面包屑、动作按钮
- 左侧：文件树/收藏/最近切换
- 主区：Markdown 预览 + TOC（右侧抽屉或内嵌）

### 6.2 基础交互
- 文件树点击打开文档；保持展开状态；选中高亮。
- 搜索：实时展示命中文档；点击跳转并高亮关键词。
- 面包屑：反映当前文档路径，支持向上跳转。
- 最近/收藏：本地存储保存，支持清空。
- 链接处理：相对链接在应用内跳转；外链新窗口；锚点定位并平滑滚动。

### 6.3 性能与可用性
- 大树/长列表采用虚拟列表（如 react-virtual）。
- 大文档延迟渲染（TOC 与代码高亮异步分步进行）。
- 图片按需加载。
- 初次加载 skeleton 占位。

## 7. Markdown 渲染策略
- 基础：remark-parse、remark-gfm、remark-footnotes、remark-frontmatter、rehype-highlight 或 Shiki、rehype-slug、rehype-autolink-headings。
- Mermaid：检测 ```mermaid 代码块，使用 mermaid.initialize 后渲染；渲染前进行 HTML sanitize。
- 数学：可选引入 KaTeX（remark-math/rehype-katex）。
- 安全：DOMPurify（或 rehype-sanitize）防止 XSS；严格只允许受控标签与属性。
- 链接重写：本地相对链接转换为应用内路由（带 path 与 hash）；file:// 链接按需保留。

## 8. 搜索实现（v1）
- 索引字段：path、文件名、标题（# Heading）、正文纯文本（去除代码块可选）。
- 匹配：不区分大小写，中文按基本切词；支持前缀/包含匹配。
- 排序：文件名/标题命中优先；最近修改优先；短路径优先。
- 结果摘要：返回命中的若干片段，前端高亮关键词。
- 性能：限制单次返回数量（如 100）；长文本索引长度上限（如 200KB，可配置）。

## 9. 配置与可扩展性
- 配置文件：openclaw-viewer.config.json
  - root、ignorePatterns、maxFileSize、features（mermaid/katex/toc/search 等开关）
  - port、host、basePath、etag/缓存策略
- 可扩展点：自定义渲染器、短代码/指令、外部数据源接入、Markdown 宏。

## 10. 安全与合规
- 服务端对 path 进行 resolve/relative 校验，拒绝越权访问。
- 对渲染 HTML 做 sanitize，禁止内联脚本与危险属性。
- 不记录敏感内容到日志；不暴露绝对路径给前端（只传相对 path）。
- 仅提供只读接口；不支持写入/删除。

## 11. 目录结构（建议）
```
workspace-viewer/
  server/
    src/
      index.ts
      api/
        tree.ts
        file.ts
        search.ts
      core/
        indexer.ts
        fs-utils.ts
        sanitizer.ts
      types/
        index.ts
    package.json
  web/
    src/
      main.tsx
      app.tsx
      components/
        Tree.tsx
        Viewer.tsx
        SearchBox.tsx
        Toc.tsx
      styles/
    index.html
    vite.config.ts
    package.json
  openclaw-viewer.config.json
  README.md
```

## 12. 接口定义示例
- GET /api/tree
```json
{
  "type": "dir",
  "name": "workspace",
  "path": "",
  "children": [
    { "type": "file", "name": "README.md", "path": "README.md" },
    { "type": "dir", "name": "docs", "path": "docs", "children": [...] }
  ]
}
```
- GET /api/file?path=docs/guide.md
```json
{
  "path": "docs/guide.md",
  "mtime": 1730456789000,
  "size": 12345,
  "content": "# Guide\\n..."
}
```
- GET /api/search?q=workspace
```json
{
  "query": "workspace",
  "results": [
    {
      "path": "README.md",
      "title": "OpenClaw Workspace",
      "snippets": ["...workspace 概述...", "...如何使用 workspace..."],
      "score": 12.3
    }
  ]
}
```

## 13. 迭代里程碑与实施步骤
1) 初始化工程与配置
   - 新建 mono 目录结构（server + web）；初始化 package.json、TS 配置、eslint/prettier；编写 README。
   - 定义 openclaw-viewer.config.json（默认 root 指向 /Users/mocklab/.openclaw/workspace）。
2) 最小可用版本（MVP）
   - 后端实现 /api/tree 与 /api/file（仅限 .md/.mdx），完成路径校验与忽略规则。
   - 前端实现基本布局、文件树、文档加载与渲染（remark + rehype-highlight），支持 TOC 与锚点。
   - 基本样式与暗色模式。
3) 搜索能力
   - 构建轻量索引，提供 /api/search；前端搜索框联动高亮与跳转。
4) 增强渲染
   - Mermaid、任务列表、表格优化、图片相对路径处理、外链处理。
5) 增强可用性
   - 最近/收藏、复制链接（带锚点）、面包屑优化、错误与空态页面。
6) 监听与热更新
   - chokidar 增量更新索引；前端使用 ETag 或事件推送刷新树/文档。
7) 打包与一键启动
   - npm scripts：dev（并发启动 server 与 web）、build、preview；提供使用文档。
8) 验收与文档
   - 覆盖用户故事与验收清单；截图/动图；常见问题与故障排查。

## 14. 验收标准（Checklist）
- 能浏览根目录下所有 Markdown 文件，路径越权被拒绝。
- 文件树能展开/折叠，高亮当前项，保留状态。
- Markdown 渲染正确：标题、代码高亮、链接、图片、表格、任务列表、脚注。
- TOC 正确滚动定位，锚点唯一且稳定。
- 搜索可返回命中文档与片段，点击后跳转并高亮。
- Mermaid 渲染正确且安全；禁用脚本注入。
- 最近/收藏可用且持久化；复制深链正确。
- 大目录/大文档仍流畅（虚拟列表/懒加载生效）。
- 无敏感信息泄漏；日志不包含文档正文。

## 15. 风险与缓解
- 大型仓库扫描耗时：采用延迟/分批索引、按需子树加载；对大文件跳过正文索引。
- XSS 风险：统一 sanitize；只读接口；不信任 Markdown 内嵌 HTML。
- Mermaid 渲染资源开销：仅按需加载；超大图限制渲染。
- 跨平台路径处理：统一使用 POSIX 风格相对路径；服务端转换。

## 16. 后续可选功能
- 反向链接与知识图谱（解析链接关系，图可视化）。
- 多根目录聚合视图（多个 workspace）。
- 导出静态站点（只读）供分享。
- 文档间比较、差异高亮。
- 批注与任务分配（与 Issue/任务系统集成）。

## 17. 开发与验证方式
- 单元测试：路径校验、索引构建、Markdown 解析（标题抽取/链接重写）、搜索匹配。
- 端到端：启动 dev，使用浏览器验证树/搜索/渲染/TOC/收藏；截屏留存。
- 在 Trae IDE 中通过本地预览验证渲染效果与路由跳转。

—— 完 —


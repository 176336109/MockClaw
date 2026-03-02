# OpenClaw Workspace Viewer 升级方案 (v2)

基于用户反馈，本方案专注于大幅提升视觉体验与渲染能力，在保持项目轻量级（无需复杂构建）的前提下进行深度改造。

## 1. 核心改进目标
1.  **渲染美化**：引入工业级 Markdown 样式（GitHub Styling），解决“丑”的问题。
2.  **图表增强**：
    - **UML**：深度集成 Mermaid（支持流程图、时序图、类图、甘特图等）。
    - **思维导图**：集成 Markmap，支持将任意 Markdown 文档一键切换为思维导图模式。
3.  **交互优化**：
    - 实现左侧目录树的**折叠/展开**功能，支持保持展开状态。
    - 增加“文档/导图”视图切换开关。
4.  **整体 UI 重设计**：采用现代化的深色主题（Dark Mode），优化排版、间距与图标。

## 2. 技术实现策略（轻量化路线）
为了不引入繁重的 Node.js 构建流程（如 Webpack/Vite），我们继续利用现代浏览器的 ES Module 能力与 CDN 资源，直接增强 `web/` 目录下的静态文件。

### 2.1 依赖库更新 (CDN)
- **样式**：`github-markdown-css` (提供标准的 Markdown 排版)。
- **图标**：`FontAwesome` 或 SVG 图标（用于目录树）。
- **思维导图**：`markmap-lib` + `markmap-view` (用于解析与渲染思维导图)。
- **核心渲染**：保持 `markdown-it`，增加插件 `markdown-it-task-lists`, `markdown-it-emoji` 等。

### 2.2 目录树改造 (`client.js`)
- 数据结构保持不变。
- 渲染逻辑：将 `buildTreeNode` 改为生成带状态的 DOM。
- 交互：点击目录名切换 `expanded` 类，通过 CSS 控制子节点 `display`。
- 状态记忆：(可选) 使用 `localStorage` 记住展开的路径。

### 2.3 思维导图集成
- 在顶部栏增加“思维导图”按钮。
- 点击后：
  1. 隐藏 Markdown 内容区，显示 Markmap 容器。
  2. 调用 `markmap-lib` 解析当前 Markdown 内容。
  3. 使用 `markmap-view` 在 SVG 中渲染。
- 支持缩放、拖拽与节点折叠。

### 2.4 样式重构 (`styles.css`)
- **布局**：使用 CSS Grid，左侧固定宽（可拖拽调整可选），右侧自适应。
- **配色**：参考 GitHub Dark Dimmed 主题。
  - 背景：`#22272e`
  - 侧边栏：`#1c2128`
  - 文字：`#adbac7`
  - 链接：`#539bf5`
- **排版**：限制最大阅读宽度（`max-width: 900px`），居中对齐，提升阅读体验。

## 3. 实施步骤
1.  **样式升级**：引入 `github-markdown-css`，重写 `styles.css` 适配深色主题与新布局。
2.  **目录树交互**：修改 `client.js`，实现折叠逻辑与图标切换。
3.  **Markmap 集成**：引入 Markmap 库，实现文档/导图视图切换逻辑。
4.  **Markdown 配置优化**：配置 markdown-it 插件，优化 Mermaid 渲染时机。
5.  **验证**：检查各类 UML 图显示是否正常，目录折叠是否顺滑。

## 4. 验收标准
- [ ] 界面美观，符合现代审美（深色模式）。
- [ ] 目录树默认折叠，点击可展开/收起。
- [ ] Markdown 正文渲染接近 GitHub 效果。
- [ ] Mermaid 图表（流程/时序/饼图）正常渲染。
- [ ] 点击“思维导图”按钮，能正确展示当前文档的脑图结构。

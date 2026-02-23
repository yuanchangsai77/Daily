# 新功能接入流程

本文档总结了在 Daily 系统中添加新功能时的常规步骤，参考了“每日瞬间”模块的落地流程。按照此脚手架执行，可确保前后端、文档与版本控制保持一致。

## 1. 规划与需求记录

1. 明确用户场景：写下功能目的、核心数据对象、主要交互（例如：上传照片、提交表单、查看列表）。
2. 记录约束：文件大小限制、字段必填项、是否需要认证等。
3. 若功能涉及多页面或跨模块交互，在 `docs/` 下新增草案或线框文件，便于协作讨论。

## 2. 后端改动（`datalite/app.py`）

1. **数据库表**：在 `init_db()` 中创建/更新所需表。必要时添加迁移脚本或初始化脚本。
2. **静态资源**：若需要存储文件，配置 `UPLOAD_DIR` 与 `send_from_directory` 路由，并在 `.gitignore` 中排除真实文件，只保留 `.gitkeep`。
3. **API 路由**：新增 Blueprint 或直接在 Flask 应用中实现 REST 端点（GET/POST/PUT/DELETE）。保持：
   - 统一 JSON 结构与错误返回（`{'error': 'message'}`）。
   - 输入校验：检查必填字段、文件类型、大小、数据库连接关闭。
   - 返回值包含前端需要的全部字段（例如已保存文件的访问 URL）。
4. **页面路由**：为新 HTML/前端模块添加路由（`@app.route('/new-feature')`），通过 `send_from_directory(STATIC_DIR, 'xxx.html')` 返回。

## 3. 前端改动（`func/`）

1. 在 `func/` 内新增对应页面（或扩展现有页面）。保持统一的 HTML/CSS 风格与提示语。
2. 通过 `fetch` 调用后端 API；表单提交推荐使用 `FormData` 或 JSON，对成功/失败情况给出友好反馈。
3. 在 `func/index.html` 中新增入口按钮/卡片，确保用户可以从首页发现新功能。
4. 若有共享组件（toast、loading 等），尽量复用已有代码片段或封装函数。

## 4. 文档与配置

1. **README**：更新功能列表、使用说明、API 表、目录结构等，让仓库访客了解新模块。
2. **`.gitignore`**：添加新的日志、数据库、上传目录等条目，并保留 `.gitkeep` 以提交目录结构。
3. **其他文档**：如需交付使用手册或 API 参考，可在 `docs/` 目录拓展相应文件。

## 5. 测试与验证

1. 运行 `PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile datalite/app.py` 确认语法无误。
2. 启动 `python3 datalite/app.py`，在浏览器逐步操作：
   - 功能入口能打开；
   - 表单校验、上传/提交成功；
   - 列表或画廊能显示新增数据；
   - 错误时提示信息合理。
3. 如有条件，补充 Flask test client 或前端自动化脚本。

## 6. 提交与发布

1. `git status` 确认变更范围；确保未提交真实数据文件。
2. `git add . && git commit -m "Add <feature>`，并在 commit message 中说明核心改动。
3. `git push -u origin <branch>`；创建 PR/合并请求并描述测试步骤。
4. 更新发行说明或项目更新记录（若有）。

按照上述步骤执行，可以在不破坏现有功能的情况下快速扩展功能，并为后续接入本地大模型或自动化流程打好基础。***

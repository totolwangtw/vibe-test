# 项目管理工具（本地版）

> 一个可以放在 Windows 文件夹中、双击即用的项目管理工具。后端 Python + SQLite，前端 Vue 3（Vben Admin 风格）。

## ✨ 功能特性

### 工作台 Dashboard
- 项目数、任务总数、进行中、待办数等关键指标卡
- 任务状态分布饼图、优先级分布柱状图、工时概览图
- 项目状态列表（含进度、任务完成数、逾期数）
- 未完成待办快览、近期会议时间线

### 项目管理
- 多项目支持，每个项目独立配置成员、颜色、优先级、起止日期
- 项目详情页：指标卡 + 快速入口（任务/甘特图/会议/待办）+ 成员管理

### 任务管理（多层级）
- 树形结构任务，支持任意层级展开/缩放（父子任务）
- 行内编辑：状态、优先级、责任人、起止日期、进度、工时
- 任务详情抽屉：富文本（HTML）业务需求描述、附件上传/下载、标签、颜色、星标
- 工时记录：按日期/成员/工时记录，自动汇总到任务
- 支持搜索、状态筛选、责任人筛选、全部展开/折叠

### 甘特图（日 / 周 / 月）
- 基于 dhtmlxGantt，支持日、周、月三种时间尺度切换
- 任务条拖拽改期、改时长、改进度，自动同步后端
- 优先级颜色区分、关键路径高亮、任务间依赖链接

### 会议记录（日会 / 周会）
- 按时间线展示，区分日会/周会
- 富文本会议纪要、主持人、参会人
- 直接在会议中产出待办，指派责任人 + @提及
- 待办数实时统计

### 待办追踪
- 待办列表，可勾选完成、改状态/优先级/截止日期
- 责任人指派、@提及多人（用于关注通知）
- 截止日期高亮、逾期标红
- 按状态（待办/进行中/已完成）筛选

### 假期管理
- 按成员记录假期（事假/病假/年假/法定节假日）
- 起止区间、天数自动计算
- 项目维度查询成员假期

### 主题与体验
- Vben Admin 风格布局：侧边栏 + 顶栏 + 标签页 + 面包屑
- 深色/浅色主题一键切换
- 侧边栏可折叠、标签页可关闭
- 全中文界面

## 📁 项目结构

```
pm-tool/
├── start.bat                 # ★ Windows 一键启动脚本（双击即可）
├── start.sh                  # Linux/macOS 启动脚本（开发用）
├── README.md
├── backend/                  # 后端（FastAPI + SQLite）
│   ├── app/
│   │   ├── main.py           # FastAPI 入口，同时托管前端静态资源
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py         # 数据库模型（含种子数据）
│   │   ├── schemas.py        # Pydantic 输入输出
│   │   ├── crud.py
│   │   └── routers/          # 各业务路由
│   │       ├── projects.py
│   │       ├── tasks.py      # 含多层级树、甘特图数据
│   │       ├── attachments.py
│   │       ├── meetings.py
│   │       ├── todos.py
│   │       ├── holidays.py
│   │       ├── members.py
│   │       └── dashboard.py
│   ├── requirements.txt
│   ├── .venv/                # 自动创建的虚拟环境
│   └── data/
│       ├── pm.db             # ★ SQLite 数据库文件（核心数据）
│       └── uploads/          # 上传的附件
└── frontend/                 # 前端（Vue 3 + Vite + Element Plus）
    ├── src/
    │   ├── api/              # axios 客户端 + 类型
    │   ├── layouts/BasicLayout.vue  # Vben 风格主布局
    │   ├── components/       # 共享组件（富文本、标签）
    │   ├── views/
    │   │   ├── dashboard/    # 工作台
    │   │   ├── projects/     # 项目列表 + 详情
    │   │   ├── tasks/        # 任务管理
    │   │   ├── gantt/        # 甘特图
    │   │   ├── meetings/     # 会议记录
    │   │   ├── todos/        # 待办追踪
    │   │   ├── holidays/     # 假期管理
    │   │   ├── members/      # 成员管理
    │   │   └── settings/
    │   ├── stores/           # Pinia
    │   ├── router/
    │   └── styles/main.scss
    ├── dist/                 # ★ 前端构建产物（生产用）
    └── package.json
```

## 🚀 Windows 部署（核心使用方式）

### 前置要求
1. **Python 3.10+**（推荐 3.12）
   - 下载：https://www.python.org/downloads/windows/
   - 安装时务必勾选 **"Add Python to PATH"**
2. **前端已构建**：`frontend/dist/index.html` 必须存在
   - 本仓库已附带构建好的 `dist`，无需再构建
   - 如需修改前端，参考下方"开发模式"

### 启动步骤
1. 把整个 `pm-tool` 文件夹复制到 Windows 任意位置（如 `D:\tools\pm-tool`）
2. **双击 `start.bat`**
3. 首次启动会自动：
   - 创建虚拟环境 `backend\.venv`
   - 安装 Python 依赖（约 1-2 分钟）
   - 初始化 SQLite 数据库 `backend\data\pm.db`
   - 写入示例数据（1 个项目 + 5 个成员 + 7 个任务 + 1 个会议 + 2 个待办）
4. 浏览器会自动打开 `http://127.0.0.1:8000`

### 日常使用
- 直接双击 `start.bat` 即可
- 关闭命令行窗口或按 `Ctrl+C` 停止服务
- 任何机器只要装了 Python 都可以运行（不需要管理员权限）

### 数据备份与迁移
- **数据库**：`backend\data\pm.db` —— 复制这个文件即可备份/迁移
- **附件**：`backend\data\uploads\` —— 整个文件夹复制
- **多机器使用**：把整个 `pm-tool` 目录拷贝到其他 Windows 机器即可，无需重新配置

## 🛠️ 开发模式（修改前端代码）

如需修改前端 UI：

```bash
# 1. 安装 Node.js 18+ 和 pnpm
npm install -g pnpm

# 2. 进入前端目录
cd frontend
pnpm install

# 3. 启动开发服务器（热更新，API 自动代理到 8000 端口）
pnpm dev
# → 浏览器打开 http://127.0.0.1:5173

# 4. 同时另起一个后端（开发态）
cd ../backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000

# 5. 修改完成后构建生产产物
cd frontend
pnpm build:force
# → 产物输出到 frontend\dist\
```

构建完成后，`start.bat` 启动时会自动加载新的前端。

## 🔌 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 后端 | FastAPI 0.115 | 现代、高性能、自动生成 API 文档 |
| ORM | SQLAlchemy 2.0 | Python 主流 ORM |
| 数据库 | SQLite | 单文件零部署，Windows 友好 |
| 富文本 | wangEditor 5 | HTML 输出，轻量易用 |
| 甘特图 | dhtmlxGantt 9 (GPL) | 社区版，可商用免费用于内部 |
| 前端框架 | Vue 3 + Vite 6 + TypeScript | 主流前端栈 |
| UI 库 | Element Plus 2.8 | 企业级 UI，Vben Admin 同款 |
| 图表 | ECharts 5 | 国内主流可视化 |
| 状态管理 | Pinia | Vue 官方推荐 |
| HTTP | Axios | API 调用 |

## 📖 API 文档

服务启动后访问：
- **Swagger UI**：http://127.0.0.1:8000/docs
- **ReDoc**：http://127.0.0.1:8000/redoc

## 🎯 设计建议（额外功能）

在原需求基础上额外提供的：

1. **活动日志模型** `activities`（已建表，可用于扩展操作审计）
2. **任务标签 Tag**：彩色标签便于任务分类
3. **任务颜色自定义**：在甘特图中按颜色区分任务类型
4. **关键路径高亮**：甘特图勾选即可查看项目关键路径
5. **项目仪表盘**：单项目维度查看任务状态/优先级/责任人分布
6. **任务搜索与多维筛选**：按标题、状态、责任人快速过滤
7. **@提及的实时关联**：待办里的 @ 会在 Dashboard 卡片显示

如果需要进一步增强，建议后续可加：
- 邮件/钉钉/飞书通知（结合 @提及触发）
- 任务拖拽排序（前端 reorder + 后端 batch 接口已就绪）
- 数据导入导出（CSV/Excel）
- 多人共享访问（局域网内 `--host 0.0.0.0`）
- 自动备份（定时复制 pm.db）

## ⚠️ 常见问题

**Q：双击 start.bat 没反应 / 闪退？**
A：右键 → 用记事本打开，删除 `> nul` 重定向查看错误；或检查 Python 是否正确加入 PATH。

**Q：依赖安装失败 / 网络慢？**
A：可配置国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

**Q：前端打不开 / 显示"前端尚未构建"？**
A：检查 `frontend\dist\index.html` 是否存在。如果不存在，参考"开发模式"重新构建。

**Q：如何重置数据？**
A：删除 `backend\data\pm.db` 文件后重启服务，会自动重建并写入示例数据。

**Q：可以让局域网其他同事访问吗？**
A：编辑 `start.bat`，把 `--host 127.0.0.1` 改为 `--host 0.0.0.0`，然后他人通过 `http://你的IP:8000` 访问。

**Q：附件大小有限制吗？**
A：默认无限制（受磁盘空间限制）。如需限制，可在 `app/main.py` 增加中间件。

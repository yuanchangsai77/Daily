# Daily

一个轻量的生活管理工具，包含 **每日打卡** 与 **记账管理** 两大功能。后端使用 Flask + SQLite 提供统一 API，并把前端页面（`func/` 目录）作为静态文件直接服务，让你在浏览器里完成所有操作。

## 功能亮点

- **每日打卡**
  - 添加、删除每日目标，支持一键打卡/取消。
  - GitHub 风格的 6 周热力图，深绿色代表当天完成的目标更多。
  - 自动计算「最高连续打卡天数」与「当前连卡」。
- **记账管理**
  - 快速录入收入/支出，金额支持小数。
  - 实时汇总净收入，支持删除任意记录。
- **单一后端**
  - 所有数据保存于 `datalite/data.db` SQLite 文件。
  - RESTful API：`/goals` 与 `/transactions` 提供 GET/POST/DELETE 等操作。

## 快速开始

> 需要 Python 3.9+。如果你使用虚拟环境，请先创建并激活。

```bash
git clone git@github.com:yuanchangsai77/Daily.git
cd Daily
pip install Flask
python3 datalite/app.py
```

启动后访问：

- `http://127.0.0.1:5000/`：功能选择面板。
- `http://127.0.0.1:5000/daily-tracker`：每日打卡。
- `http://127.0.0.1:5000/accounting`：记账管理。

## API 概览

| Method | Endpoint                 | 说明                     |
| ------ | ------------------------ | ------------------------ |
| GET    | `/goals`                 | 获取所有目标             |
| POST   | `/goals`                 | 新增目标（JSON：name 等）|
| DELETE | `/goals`                 | 删除目标（JSON：id）     |
| PUT    | `/goals/<goal_id>`       | 更新目标完成状态/名称    |
| GET    | `/transactions`          | 获取所有账务记录         |
| POST   | `/transactions`          | 新增账务记录             |
| DELETE | `/transactions`          | 删除账务记录（JSON：id） |

## 代码结构

```
datalite/
├── app.py            # Flask 入口、API、静态文件服务
├── data.db           # 运行时 SQLite 数据库（已在 .gitignore 中排除）
func/
├── index.html        # 功能选择页
├── daily_tracker.html
└── accounting_manager.html
agent.md              # 高层功能说明
```

## 开源许可

本项目采用 [MIT License](LICENSE)。

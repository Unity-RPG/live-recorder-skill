# 🎬 LiveStream-Recorder-Skill (全自动直播监控录制与状态运维技能)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-green.svg)](https://ffmpeg.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Antigravity Skill](https://img.shields.io/badge/Antigravity-Skill%20Compatible-purple.svg)]()

> **LiveStream-Recorder-Skill** 是一套专为长周期、无人值守、高稳定性直播录制设计的自动化运维技能。适用于抖音、快手、TikTok、B站等数十个主流平台的实时开播检测、智能TS分段切片、自动封装MP4、按主播与日期动态归档，并提供桌面浮动红绿状态灯与全流程安全优雅启停机制。

---

## 🌟 核心特性 (Key Features)

- 🔄 **7×24小时全自动无人值守**：多线程心跳轮询主播开播状态，开播即录，关播即停，支持热加载新增主播。
- 🚥 **桌面悬浮状态监控灯 (`traffic_light.py`)**：轻量级 Tkinter 悬浮组件，绿灯（录制中）、红灯（等待开播）、灰灯（未运行），内置本地 TCP 端口锁单例防护与窗口置顶拖拽。
- 🛡️ **优雅停机与数据防损 (`stop_record.bat`)**：采用 `stop_signal.txt` 信号通信机制，通知 FFmpeg 完整写入数据缓冲头与索引，杜绝断流或强杀导致的视频文件损坏。
- 📂 **结构化归档与动态命名**：支持 `{date} {author}`、`{date} {title}` 占位符，自动按日期和主播分类归档至指定硬盘目录。
- ⚡ **分段切片与无损转码**：支持按设定时长（默认 1800 秒 / 30 分钟）自动切片，录制完毕自动调用 FFmpeg 转为 MP4 并清理临时文件。
- 🩹 **高可用自愈与容错机制**：
  - **磁盘检测自愈**：内置 `check_disk_capacity` 根盘兜底补丁，彻底避免父级目录移动引起的 `FileNotFoundError` 闪退崩溃。
  - **编码保护**：严格保证 `.ini` 文件的 `UTF-8 with BOM` 规范，避免中文键名解析错位。
  - **CMD 控制台保护**：批处理脚本适配 Windows GBK 本地代码页，彻底杜绝中文乱码。

---

## 🏗️ 目录结构 (Directory Structure)

```text
live-recorder-skill/
├── SKILL.md                 # Antigravity 核心技能定义与操作手册
├── README.md                # 项目文档与 GitHub 首页
├── LICENSE                  # MIT 开源许可证
├── .gitignore               # Git 忽略文件（忽略媒体流、日志与私密配置）
├── scripts/                 # 核心控制与辅助运维工具
│   ├── traffic_light.py     # 桌面浮动三色状态灯组件
│   ├── start_record.bat     # 一键启动脚本（环境变量注入 + 状态灯联动）
│   ├── stop_record.bat      # 优雅安全停止脚本（信号机制 + 60s 退出等待）
│   ├── patch_disk_usage.py  # 磁盘检测崩溃自动热补丁工具
│   └── health_check.py      # 环境、依赖与配置健康巡检脚本
├── templates/               # 标准配置文件模板
│   ├── config.ini.template  # 生产级录制参数配置模板（带完整注释）
│   └── URL_config.ini.template # 多平台主播关注列表模板
└── references/              # 参考资料与深度技术文档
    ├── troubleshooting.md   # 进阶踩坑与疑难排查手册
    └── platforms.md         # 支持的主播平台矩阵与 URL 提取规范
```

---

## 🚀 快速上手 (Quick Start)

### 1. 准备依赖
- **Python**：3.10 或更高版本
- **FFmpeg**：建议下载较新的 static build，并确保 `ffmpeg.exe` 在系统环境变量 `PATH` 中，或置于项目根目录的 `ffmpeg/bin/` 文件夹内。

### 2. 运行健康检查
在项目根目录下运行健康检查工具，快速验证当前环境：
```bash
python scripts/health_check.py .
```

### 3. 初始化配置文件
从模板复制生成您的配置文件：
```bash
# 复制主配置模板
copy templates\config.ini.template config\config.ini

# 复制主播监控列表模板
copy templates\URL_config.ini.template config\URL_config.ini
```

- 在 `config/config.ini` 中修改您的视频保存路径：
  ```ini
  直播保存路径(不填则默认) = F:\直播归档\直播未剪
  保存文件夹自定义命名 = {date} {author}
  ```
- 在 `config/URL_config.ini` 中填入您要监控的主播链接：
  ```ini
  https://live.douyin.com/971223901932,主播: 示例主播
  ```

### 4. 启动与停止
- **一键启动**：双击运行 `scripts\start_record.bat`。桌面右上角将自动出现状态监控指示灯。
- **安全停止**：双击运行 `scripts\stop_record.bat`，等待程序安全刷新文件缓冲区后退出。

---

## 🤖 在 AI 智能体 / Antigravity 中使用 (Agent Integration)

将本文件夹置入您的 Antigravity / Claude Code Skills 目录（如 `~/.gemini/config/skills/live-recorder`）。

您可以直接对 AI 说：
- *"帮我添加一个抖音新主播监控：https://live.douyin.com/xxxxxx，备注叫小张"*
- *"检查一下当前直播录制状态，为什么录制灯不亮了？"*
- *"我想把以后的录制视频都存到 E 盘的直播未剪文件夹中，帮我修改配置"*

AI 智能体将按照 `SKILL.md` 中的规范自动执行参数检查、BOM 编码维护、热补丁校验及优雅启停。

---

## 🛠️ 故障排查 (Troubleshooting)

| 故障现象 | 根因 | 解决方案 |
| :--- | :--- | :--- |
| **程序突然闪退** | 移动了目录导致 `shutil.disk_usage` 抛出 `WinError 3` | 运行 `python scripts/patch_disk_usage.py` 打入容错补丁 |
| **状态灯启动后闪退** | 上次残留的僵尸进程占用了 TCP 47653 端口锁 | 在任务管理器或 PowerShell 中杀死残留的 `traffic_light.py` |
| **生成的文件夹中文乱码** | `config.ini` 未以 `UTF-8 with BOM` 格式保存 | 用 VS Code 选择 `Save with Encoding` -> `UTF-8 with BOM` 保存 |
| **控制台终端文字乱码** | Windows CMD 终端代码页与 UTF-8 批处理冲突 | 使用本仓库中以 ANSI/GBK 编码保存的 `.bat` 脚本 |

详细深度排查指引请参考 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 📄 开源许可证 (License)

本项目遵循 [MIT 许可证](LICENSE)。

---
name: live-recorder
description: 全自动多平台网络直播监控与录制工作流（Live Stream Recording & Monitoring Automation）。支持抖音、快手、TikTok、B站等数十个主流平台的无人值守直播监测、智能切片分段录制、无损转码MP4、主播级与日期级自动化归档（{date} {author}）、桌面悬浮状态监控灯（绿/红/灰三色交通灯）、安全优雅启停与多进程守护、以及路径与磁盘容量自愈等企业级运维能力。
---

# 全自动多平台直播录制与状态运维技能 (Live Stream Recording & Ops Skill)

本 Skill 沉淀了一套高可靠、无人值守的跨平台网络直播实时监测、自动化录制分段转码、动态归档以及桌面状态监控的完整运维工作流。

---

## 一、 系统架构与运转流程

```mermaid
flowchart TD
    subgraph 控制与交互层
        A[桌面快捷方式 / 启动脚本] -->|启动| B(start_record.bat)
        C[停止指令 / 快捷方式] -->|写入 signal| D(stop_record.bat)
        E[桌面状态灯 traffic_light.py] -->|读取状态| F[(recorder_status.txt)]
    end

    subgraph 核心引擎层
        B -->|拉起| G[DouyinLiveRecorder 主程序]
        G -->|状态上报| F
        G -->|监听信号| H{检测到 stop_signal?}
        H -->|是| I[等待切片完成并优雅安全退出]
        G -->|读取配置| J[config.ini / URL_config.ini]
        G -->|心跳轮询| K{主播是否开播?}
    end

    subgraph 采集与转码层
        K -->|已开播| L[FFmpeg / 原画拉流]
        L -->|按时间切片 1800s| M[临时 TS 切片文件]
        M -->|录制结束/切片完成| N[自动无损封装 MP4]
    end

    subgraph 存储与归档层
        N -->|动态结构化命名| O[F:/.../直播未剪/{date} {author}/]
        O -->|容错防护| P[磁盘空间与目录自愈检测]
    end
```

---

## 二、 核心组件与目录结构

推荐的标准化工作流目录如下：

```
live-recorder-skill/
├── SKILL.md                 # 核心技能说明书与 Agent 执行指导
├── README.md                # GitHub 仓库首页说明文档
├── LICENSE                  # MIT 开源许可证
├── .gitignore               # Git 忽略文件（忽略录制视频、日志与虚拟环境）
├── scripts/                 # 核心控制与辅助运维脚本
│   ├── traffic_light.py     # 桌面浮动三色状态灯（绿=录制，红=等待，灰=未运行）
│   ├── start_record.bat     # 一键启动脚本（集成 FFmpeg/Node/Python 环境注入）
│   ├── stop_record.bat      # 优雅安全停止脚本（信号通知 + 60s 安全落盘等待）
│   ├── patch_disk_usage.py  # 磁盘检测崩溃自动热补丁脚本（解决路径变动闪退）
│   └── health_check.py      # 环境、依赖与配置健康巡检脚本
├── templates/               # 标准配置文件模板
│   ├── config.ini.template  # 生产级录制参数配置模板（带完整注释）
│   └── URL_config.ini.template # 多平台主播关注列表模板
└── references/              # 参考资料与深度排查文档
    ├── troubleshooting.md   # 进阶踩坑与疑难排查手册
    └── platforms.md         # 支持的主播平台矩阵与 URL 提取规范
```

---

## 三、 关键配置文件规范

### 1. 录制主配置文件 (`config/config.ini`)
- **文件编码必须为**：`UTF-8 with BOM`（即 Python 中的 `utf-8-sig`）。若丢失 BOM 头，部分 Windows 环境下可能导致中文键名或路径乱码。
- **推荐生产级配置项**：
  ```ini
  [录制设置]
  language(zh_cn/en) = zh_cn
  是否跳过代理检测(是/否) = 否
  直播保存路径(不填则默认) = F:\视频归档\直播未剪
  保存文件夹是否以作者区分 = 否
  保存文件夹是否以时间区分 = 否
  保存文件夹是否以标题区分 = 否
  保存文件夹自定义命名 = {date} {author}
  保存文件名是否包含标题 = 否
  是否去除名称中的表情符号 = 是
  视频保存格式ts|mkv|flv|mp4|mp3音频|m4a音频 = ts
  原画|超清|高清|标清|流畅 = 原画
  同一时间访问网络的线程数 = 3
  循环时间(秒) = 300
  排队读取网址时间(秒) = 0
  分段录制是否开启 = 是
  视频分段时间(秒) = 1800
  录制完成后自动转为mp4格式 = 是
  追加格式后删除原文件 = 是
  ```

### 2. 主播关注列表 (`config/URL_config.ini`)
- **文件编码**：`UTF-8 with BOM`。
- **书写规范**：每行一条记录，支持主流格式：
  1. `[直播间或主页链接],主播: [主播别名]` （推荐，最直观）
  2. `[画质要求],[直播间链接],主播: [主播别名]` （例如：`超清,https://...,主播: 张三`）
  3. 开头加 `#` 表示**临时暂停监测**，程序不会拉取该主播，但保留记录。

---

## 四、 核心运维机制与标准作业程序 (SOP)

### SOP 1：添加新主播监控
1. 打开 `config/URL_config.ini`。
2. 在最后一行追加新主播地址与别名，例如：
   ```ini
   https://live.douyin.com/971223901932,主播: 小胖肖正江
   ```
3. 保存文件。若录制程序正在运行，它将在下一轮循环（默认 300 秒）自动热加载新增主播，无需强行重启。

### SOP 2：变更直播保存路径
1. 打开 `config/config.ini`。
2. 修改 `直播保存路径(不填则默认)` 为新目标路径，例如：
   ```ini
   直播保存路径(不填则默认) = F:\肖正江\小胖\小胖\直播\直播未剪
   ```
3. 确保以 `UTF-8 with BOM` 格式保存。
4. 同步更新 `start_record.bat` 中终端显示的“保存位置”提示信息（注意该批处理文件应使用 ANSI/GBK 编码，防止 Windows CMD 终端中文乱码）。

### SOP 3：安全停止录制（防止损坏视频）
- **严禁直接强杀进程或直接点控制台红叉**（这会导致当前正在写入的 TS/MP4 分段文件头部损坏无法播放）。
- **正确方式**：
  1. 运行 `stop_record.bat`。
  2. 该脚本会写入 `stop_signal.txt`，主程序捕获后会等待当前网络缓存全部写入磁盘并安全关闭 FFmpeg。
  3. 脚本在 60 秒内检测进程退出后自动退出。

---

## 五、 容错设计与高可用自愈策略

### 1. 目标路径被移动导致 `shutil.disk_usage` 闪退自愈
- **故障现象**：若用户移动了外层目录，配置路径暂时不存在，原生代码调用 `shutil.disk_usage(directory)` 会直接抛出 `FileNotFoundError: [WinError 3]` 导致整个守护进程崩溃。
- **防御修复**：对 `src/utils.py` 中的 `check_disk_capacity` 做兜底回退：
  ```python
  def check_disk_capacity(file_path: str | Path, show: bool = False) -> float:
      absolute_path = os.path.abspath(file_path)
      directory = os.path.dirname(absolute_path)
      disk_root = Path(directory).anchor or "C:\\"
      try:
          disk_usage = shutil.disk_usage(directory)
      except (FileNotFoundError, OSError):
          disk_usage = shutil.disk_usage(disk_root)
      free_space_gb = disk_usage.free / (1024 ** 3)
      return free_space_gb
  ```

### 2. 状态灯单例绑定防重复启动
- `traffic_light.py` 内置固定本地 TCP 端口（`47653`）监听互斥锁。若用户多次双击启动，后续实例检测到端口占用将静默退出，保证屏幕上始终仅有一个悬浮灯。

### 3. 多源代理与海外平台隔离
- 国内平台（抖音、快手、B站）走本地直连。
- 海外平台（TikTok、Twitch 等）通过配置中的 `使用代理录制的平台` 触发全局/局部代理路由，互不干扰。

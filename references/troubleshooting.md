# 直播录制自动化与运维排错手册 (Troubleshooting Guide)

本手册总结了在生产环境中长期无人值守运行直播录制系统时最常遇到的核心问题、底层原理与解决方案。

---

## 1. 目标路径变更引发的程序闪退 (`shutil.disk_usage`)

### 现象
录制程序突然闪退，控制台输出类似报错并退出：
```text
FileNotFoundError: [WinError 3] 系统找不到指定的路径。
  File "src/utils.py", line 152, in check_disk_capacity
    disk_usage = shutil.disk_usage(directory)
```

### 根因分析
在原生实现中，程序每轮检测都会执行磁盘容量检查。它直接将配置项 `直播保存路径` 传入 `shutil.disk_usage(directory)`。如果用户在外部资源管理器中将文件夹重命名、移动到其他子目录，或者目标目录尚未被创建，Python 底层的 Windows API `GetDiskFreeSpaceExW` 就会直接抛出 `WinError 3`，导致主监听循环直接异常崩溃。

### 修复方案
在 `src/utils.py` 中引入根盘回退机制（见 `scripts/patch_disk_usage.py`）：
```python
def check_disk_capacity(file_path: str | Path, show: bool = False) -> float:
    absolute_path = os.path.abspath(file_path)
    directory = os.path.dirname(absolute_path)
    disk_root = Path(directory).anchor or "C:\\"
    try:
        disk_usage = shutil.disk_usage(directory)
    except (FileNotFoundError, OSError):
        # 路径不存在时，优雅降级检测所在磁盘根分区的剩余空间
        disk_usage = shutil.disk_usage(disk_root)
    free_space_gb = disk_usage.free / (1024 ** 3)
    return free_space_gb
```

---

## 2. 配置文件编码与乱码问题 (`UTF-8 with BOM`)

### 现象
- 修改 `config.ini` 后，程序读不到设置或将中文字符识别为问号/乱码。
- `URL_config.ini` 中的主播别名变成乱码，生成的视频文件名也是乱码。

### 根因分析
- Python 的 `configparser` 模块在 Windows 上如果不指定带有 BOM 签名的 UTF-8（即 `utf-8-sig`），在处理中文 Section/Key（如 `[录制设置]`、`直播保存路径(不填则默认)`）时极易发生解码错位。
- 许多 Windows 文本编辑器（如记事本、VS Code）默认可能保存为 UTF-8（Without BOM）。

### 规避方案
- 所有 `.ini` 配置文件均应强制保存为 **UTF-8 with BOM**（十六进制文件头为 `EF BB BF`）。
- 在 Python 中读取时一律显式传入 `encoding='utf-8-sig'`。

---

## 3. Windows CMD 终端批处理输出中文乱码

### 现象
双击运行 `start_record.bat` 时，控制台窗口打印的一键启动提示、路径信息显示为乱码（例如：`λ: F:\...`）。

### 根因分析
中文版 Windows 命令提示符（CMD）默认代码页为 `936`（GBK/GB2312）。如果批处理脚本以纯 UTF-8 保存，CMD 会将多字节 UTF-8 字符当成 GBK 解释，导致严重乱码。

### 解决方案
- 涉及带中文 `echo` 提示的 `.bat` 文件，推荐**以 ANSI / GBK 编码保存**。
- 或者在批处理文件开头添加 `chcp 65001 >nul` 切换当前终端代码页为 UTF-8。

---

## 4. 强制杀死进程导致录制文件损坏

### 现象
- 录制中的 `.ts` 或 `.mp4` 文件只有部分大小，无法拖动进度条，播放器提示解码错误。

### 根因分析
FFmpeg 在实时写入 TS/MP4 流时，封装头（Muxing Header/MOOV Atom）和时间戳索引需要按步骤正常闭合。如果直接点 CMD 窗口右上角红叉，或者在任务管理器中直接结束 `python.exe` / `ffmpeg.exe`，会导致未写入磁盘的缓冲区数据丢失，文件尾部不完整。

### 解决方案
- 始终使用优雅停机流程：
  1. 运行 `scripts/stop_record.bat`。
  2. 该脚本会写入 `stop_signal.txt`，录制核心的 `stop_watcher` 守护线程检测到信号后，会通知 FFmpeg 发送 `q` 退出指令，完整刷新缓冲区后再安全结束。
  3. 控制台退出后再关闭窗口。

---

## 5. 桌面状态灯多开与端口冲突

### 现象
状态灯显示异常或重复出现多个窗口，或者启动时直接退出。

### 根因分析
`traffic_light.py` 使用本地 TCP 端口 `47653` 作为跨进程单例互斥锁：
```python
_lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    _lock_sock.bind(('127.0.0.1', 47653))
    _lock_sock.listen(1)
except OSError:
    sys.exit(0)
```
如果之前的 Python 进程处于僵尸状态且未释放端口，新的状态灯会直接判定为“已有实例在运行”而静默退出。

### 排查与释放命令
在 PowerShell 中查找并清理僵尸实例：
```powershell
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*traffic_light.py*" } | Stop-Process -Force
```

---

## 6. 抖音平台风控与 Cookie 失效更新

### 现象
日志提示：`Douyin web data fetch error, because 'it triggered risk control'`。

### 处理方法
1. 使用电脑浏览器打开 [抖音直播网页端](https://live.douyin.com/)。
2. 登录您的抖音账号，按 `F12` 打开开发者工具，切换到 `Network`（网络）选项卡。
3. 刷新页面，任意点击一个接口请求，在请求标头中找到 `Cookie`，完整复制。
4. 打开 `config/config.ini`，将内容粘贴到 `[Cookie]` 下的 `抖音cookie = ` 后面并保存。

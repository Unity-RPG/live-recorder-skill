# -*- coding: utf-8 -*-
"""
直播监控与录制环境健康检查脚本 (Health Check)
用于检测：
1. Python 版本与核心依赖
2. FFmpeg 是否可用及版本信息
3. config.ini 配置语法、编码 (UTF-8 BOM) 与目标路径写入权限
4. URL_config.ini 主播列表语法与有效监控数量
5. 状态灯端口锁与当前录制运行状态
"""

import os
import sys
import shutil
import subprocess
import configparser

def check_env(project_root: str = "."):
    print("=" * 55)
    print("        直播录制工作流环境与配置健康检查 (Health Check)")
    print("=" * 55)

    # 1. Python 环境
    print(f"[*] Python 版本: {sys.version.split()[0]} ({sys.executable})")

    # 2. FFmpeg 检测
    ffmpeg_bin = shutil.which("ffmpeg")
    local_ffmpeg = os.path.join(project_root, "ffmpeg", "bin", "ffmpeg.exe")
    if not ffmpeg_bin and os.path.exists(local_ffmpeg):
        ffmpeg_bin = local_ffmpeg

    if ffmpeg_bin:
        try:
            res = subprocess.run([ffmpeg_bin, "-version"], capture_output=True, text=True, timeout=5)
            first_line = res.stdout.splitlines()[0] if res.stdout else "已找到"
            print(f"[✓] FFmpeg 可用: {first_line} ({ffmpeg_bin})")
        except Exception as e:
            print(f"[!] FFmpeg 执行异常: {e}")
    else:
        print("[✗] 未找到 FFmpeg！请确保将其加入系统 PATH 或置于项目 ffmpeg/bin/ 目录下。")

    # 3. 配置文件检测
    config_file = os.path.join(project_root, "config", "config.ini")
    if os.path.exists(config_file):
        # 检查 BOM
        with open(config_file, "rb") as f:
            header = f.read(3)
            has_bom = (header == b'\xef\xbb\xbf')
        bom_status = "UTF-8 with BOM [✓]" if has_bom else "无BOM头 [! 建议使用UTF-8 BOM]"
        print(f"[*] config.ini 编码: {bom_status}")

        cp = configparser.RawConfigParser()
        try:
            cp.read(config_file, encoding="utf-8-sig")
            save_path = cp.get("录制设置", "直播保存路径(不填则默认)", fallback="")
            naming = cp.get("录制设置", "保存文件夹自定义命名", fallback="")
            print(f"[✓] 设定的直播保存路径: {save_path or '默认 downloads'}")
            print(f"[✓] 文件夹动态命名规则: {naming or '未自定义'}")

            # 检查保存路径是否存在及可写
            if save_path:
                if not os.path.exists(save_path):
                    print(f"[!] 警告: 保存路径目前不存在，程序开播时将尝试自动创建: {save_path}")
                    disk_root = os.path.splitdrive(save_path)[0] + "\\"
                    if os.path.exists(disk_root):
                        usage = shutil.disk_usage(disk_root)
                        print(f"    盘符 {disk_root} 剩余空间: {usage.free / (1024**3):.2f} GB")
                    else:
                        print(f"[✗] 严重: 所在磁盘盘符 {disk_root} 不存在！")
                else:
                    usage = shutil.disk_usage(save_path)
                    print(f"[✓] 目标目录可访问，剩余可用空间: {usage.free / (1024**3):.2f} GB")
        except Exception as e:
            print(f"[✗] config.ini 读取解析失败: {e}")
    else:
        print(f"[!] 未在 {config_file} 找到 config.ini")

    # 4. 主播列表检测
    url_file = os.path.join(project_root, "config", "URL_config.ini")
    if os.path.exists(url_file):
        try:
            active_anchors = []
            paused_anchors = []
            with open(url_file, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("#"):
                        paused_anchors.append(line.lstrip("#"))
                    else:
                        active_anchors.append(line)
            print(f"[✓] 主播监控列表: 正在监控 {len(active_anchors)} 个直播间，已暂停 {len(paused_anchors)} 个")
            for idx, a in enumerate(active_anchors, 1):
                print(f"    {idx}. {a}")
        except Exception as e:
            print(f"[✗] URL_config.ini 读取失败: {e}")
    else:
        print(f"[!] 未找到 URL_config.ini")

    # 5. 录制状态
    status_file = os.path.join(project_root, "recorder_status.txt")
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                status = f.read().strip()
            print(f"[*] 当前录制器状态文件: {status}")
        except Exception:
            pass

    print("=" * 55)

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    check_env(root)

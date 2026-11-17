# -*- coding: utf-8 -*-
"""
桌面录制状态灯组件 (Traffic Light Status Indicator)
特性：
1. 绿灯=录制中，红灯=暂停(未在录制/等待开播)，灰色=程序未运行
2. 内置 TCP 端口锁单例模式，防止多实例重复启动
3. 无边框无干扰设计、置顶显示、支持全局自由拖拽
4. 自动检测状态文件更新时间，超时自动判为未运行 (Stale check)
"""

import os
import socket
import sys
import time
import tkinter as tk

_LOCK_PORT = 47653
_lock_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    _lock_sock.bind(('127.0.0.1', _LOCK_PORT))
    _lock_sock.listen(1)
except OSError:
    # 端口已被占用，说明已有运行中的状态灯实例，静默安全退出
    sys.exit(0)

BASE = os.path.dirname(os.path.abspath(__file__))
# 优先查找当前目录或上一级目录中的 recorder_status.txt
STATUS_FILE = os.path.join(BASE, "recorder_status.txt")
if not os.path.exists(STATUS_FILE) and os.path.exists(os.path.join(os.path.dirname(BASE), "recorder_status.txt")):
    STATUS_FILE = os.path.join(os.path.dirname(BASE), "recorder_status.txt")

STALE_SECONDS = 600

STATES = {
    "RECORDING": ("#27ae60", "录制中", "正在录制直播"),
    "WAITING": ("#e74c3c", "暂停", "等待开播 / 未在录制"),
    "STOPPED": ("#95a5a6", "未运行", "录制程序未启动"),
}
BG = "#f5f6fa"


class TrafficLight(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("录制状态灯")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=BG)
        self._drag = {"x": 0, "y": 0}

        # 状态圆点
        self.canvas = tk.Canvas(self, width=46, height=46, bg=BG, highlightthickness=0)
        self.canvas.pack(side="left", padx=(12, 4), pady=10)
        self.light = self.canvas.create_oval(5, 5, 41, 41, fill="#95a5a6", outline="")

        # 主标题
        self.txt = tk.Label(
            self, text="未运行", font=("Microsoft YaHei UI", 12, "bold"),
            bg=BG, fg="#2c3e50"
        )
        self.txt.pack(side="left", padx=(0, 4))

        # 副标题
        self.sub = tk.Label(
            self, text="", font=("Microsoft YaHei UI", 8),
            bg=BG, fg="#7f8c8d"
        )
        self.sub.pack(side="left", padx=(0, 8))

        # 关闭按钮
        close_btn = tk.Label(
            self, text="×", font=("Segoe UI", 13), bg=BG,
            fg="#7f8c8d", cursor="hand2"
        )
        close_btn.pack(side="right", padx=(0, 8))
        close_btn.bind("<Button-1>", lambda e: self.destroy())

        # 拖拽绑定
        for w in (self, self.canvas, self.txt, self.sub, close_btn):
            w.bind("<Button-1>", self._start_drag)
            w.bind("<B1-Motion>", self._do_drag)

        self._place_top_right()
        self.update_status()
        self.after(1000, self._tick)

    def _place_top_right(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() - self.winfo_width() - 24
        self.geometry(f"+{x}+24")

    def _start_drag(self, e):
        self._drag["x"] = e.x_root - self.winfo_x()
        self._drag["y"] = e.y_root - self.winfo_y()

    def _do_drag(self, e):
        self.geometry(f"+{e.x_root - self._drag['x']}+{e.y_root - self._drag['y']}")

    def _read_status(self):
        try:
            if not os.path.exists(STATUS_FILE):
                return "STOPPED"
            if time.time() - os.path.getmtime(STATUS_FILE) > STALE_SECONDS:
                return "STOPPED"
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                s = f.read().strip().upper()
            return s if s in STATES else "STOPPED"
        except Exception:
            return "STOPPED"

    def update_status(self):
        status = self._read_status()
        color, title, sub = STATES[status]
        self.canvas.itemconfig(self.light, fill=color)
        self.txt.config(text=title)
        self.sub.config(text=sub)
        self.title(f"录制状态灯 - {title}")

    def _tick(self):
        self.update_status()
        self.after(1000, self._tick)


if __name__ == "__main__":
    app = TrafficLight()
    app.mainloop()

# -*- coding: utf-8 -*-
"""
磁盘路径检测容错补丁脚本 (Patch for DouyinLiveRecorder utils.py)
作用：自动为 src/utils.py 中的 check_disk_capacity 注入路径不存在时的根盘回退机制，
彻底防止因用户重命名或移动父级目录而导致的程序抛出 FileNotFoundError 并闪退。
"""

import os
import sys

def apply_patch(project_dir: str = ".") -> bool:
    utils_path = os.path.join(project_dir, "src", "utils.py")
    if not os.path.exists(utils_path):
        print(f"[!] 未找到目标文件: {utils_path}")
        return False

    with open(utils_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已打过补丁
    if "disk_root = Path(directory).anchor or \"C:\\\\\"" in content:
        print("[✓] src/utils.py 已具备路径自愈容错能力，无需重复打补丁。")
        return True

    target_code = """def check_disk_capacity(file_path: str | Path, show: bool = False) -> float:
    absolute_path = os.path.abspath(file_path)
    directory = os.path.dirname(absolute_path)
    disk_usage = shutil.disk_usage(directory)
    disk_root = Path(directory).anchor
    free_space_gb = disk_usage.free / (1024 ** 3)"""

    replacement_code = """def check_disk_capacity(file_path: str | Path, show: bool = False) -> float:
    absolute_path = os.path.abspath(file_path)
    directory = os.path.dirname(absolute_path)
    disk_root = Path(directory).anchor or "C:\\\\"
    try:
        disk_usage = shutil.disk_usage(directory)
    except (FileNotFoundError, OSError):
        disk_usage = shutil.disk_usage(disk_root)
    free_space_gb = disk_usage.free / (1024 ** 3)"""

    if target_code in content:
        new_content = content.replace(target_code, replacement_code)
        with open(utils_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("[✓] 成功打入磁盘容错补丁！")
        return True
    else:
        print("[!] 未能准确定位原函数代码块，请手动比对修改。")
        return False

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    apply_patch(target_dir)

# build.py打包程序
import os
import sys


def build_executable():
    """打包为可执行文件"""
    # PyInstaller打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包为单个文件
        "--noconsole",  # 不显示控制台窗口（Windows）
        "--name=bl_monitor",  # 可执行文件名称
        "--add-data=bl_notification.py;.",  # 包含依赖文件
        "--hidden-import=selenium",
        "--hidden-import=requests",
        "--hidden-import=schedule",
        "start_bl_monitor.py"
    ]

    # 执行打包命令
    os.system(" ".join(cmd))
    print("打包完成！可执行文件位于 dist/bl_monitor.exe")


if __name__ == "__main__":
    build_executable()

#启动脚本
# start_bl_monitor.py


import sys
import os
from BL import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

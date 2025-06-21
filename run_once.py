#单次运行脚本
# run_once.py
"""
单次运行BL检查脚本
用于测试或手动执行一次检查
"""

from BL import run_bl_check

if __name__ == "__main__":
    print("开始执行单次BL状态检查...")
    run_bl_check()
    print("单次检查完成")
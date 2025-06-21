# bl_notification.py
import requests
from datetime import datetime

# 监控系统API地址
MONITOR_API_URL = "http://0.0.0.0:6020/api/report"

# 需要@的人员手机号列表
AT_MOBILES = ["", ""]  # 需要@的手机号


def send_notification(results):
    """
    发送通知到监控系统

    参数:
        results: BL号码处理结果列表
    """
    # 准备通知数据
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if results:
        # 有符合条件的BL号码时，发送详细通知
        details = {}
        for i, result in enumerate(results, 1):
            details[f"BL号码{i}"] = f"{result['bl_number']} - {result['status']}"

        data = {
            "program_name": "韩国海关BL状态查询",
            "status": "success",
            "message": f"发现{len(results)}个符合条件的BL号码",
            "details": details,
            "at_mobiles": AT_MOBILES,  # 有结果时@人员
            "at_all": False
        }
    else:
        # 无符合条件的BL号码时，发送简化通知
        data = {
            "program_name": "韩国海关BL状态查询",
            "status": "success",
            "message": "BL监测运行成功",
            "details": {},
            "at_mobiles": [],  # 无结果时不@人员
            "at_all": False
        }

    try:
        # 发送POST请求到监控API
        response = requests.post(MONITOR_API_URL, json=data)
        response.raise_for_status()
        print(f"通知发送成功: {response.text}")
        return True
    except Exception as e:
        print(f"通知发送失败: {e}")
        return False

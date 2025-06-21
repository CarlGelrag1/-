韩国海关BL状态监控系统

这是一个用于监控韩国海关BL（Bill of Lading）状态的自动化监控系统。该系统会定期从钉钉获取待监控的BL号码列表，自动访问韩国海关网站查询每个BL号码的状态，并在发现特定状态时发送通知。

系统架构

本系统由多个模块组成，实现数据获取、状态查询、通知推送等功能：

1. 数据获取模块 (excel_get.py)
从钉钉下载包含BL号码的Excel文件
解析Excel文件并提取BL号码
提供REST API接口供其他模块访问BL号码数据
定时任务每8小时更新一次BL号码列表
2. 状态查询模块 (BL.py)
使用Selenium自动化浏览器访问韩国海关网站
查询每个BL号码的最新状态
支持定时任务配置（每天08:00和16:00执行）
记录详细日志信息
支持单次运行模式
3. 通知模块 (bl_notification.py)
发送通知到指定API地址
支持消息提醒功能（可配置需要@的手机号）
4. 打包模块 (build.py)
使用PyInstaller将程序打包为可执行文件
主要功能
自动化监控韩国海关BL状态
检测特定状态变化："반출신고" 和 "수입(사용소비) 결재통보"
钉钉Excel文件自动同步
日志记录和监控
REST API接口支持

文件结构
bl_monitor/
├── BL.py                # 主程序 - BL状态查询逻辑

├── bl_notification.py   # 通知模块 - 发送状态变更通知

├── excel_get.py         # 数据获取 - 从钉钉下载并解析Excel文件

├── build.py             # 打包脚本 - 将程序打包为可执行文件

├── run_once.py          # 单次运行脚本 - 用于测试或手动执行

├── start_bl_monitor.py  # 启动脚本 - 包含异常处理的启动入口

└── README.md            # 项目说明文档

技术栈
Python 3.x
Selenium (浏览器自动化)
Pandas (Excel数据处理)
Flask (REST API服务)
Requests (HTTP请求)
Schedule (定时任务)
Logging (日志记录)

配置说明
钉钉API配置 (excel_get.py):
APP_KEY: 钉钉应用的App Key
APP_SECRET: 钉钉应用的App Secret
SPACE_ID: 钉盘空间ID
DENTRY_ID: 文件ID
UNION_ID: 用户unionId
海关API配置 (BL.py):
API_URL: 获取BL号码列表的API地址
通知配置 (bl_notification.py):
MONITOR_API_URL: 监控系统的API地址
AT_MOBILES: 需要@的手机号列表
使用说明
确保已安装所有依赖库
配置钉钉API参数和海关API参数
将钉钉中的Excel文件设置为共享访问

版权信息
本工具仅供学习和研究使用，请勿用于非法用途。使用本工具请遵守相关法律法规。
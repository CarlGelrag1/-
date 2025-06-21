from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import json
import schedule
from datetime import datetime
import logging

from bl_notification import send_notification

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bl_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")

# API接口URL
API_URL = "http://0.0.0.0:6000/api/bl_numbers"


def get_bl_numbers():
    """从API获取BL号码列表"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        # 返回data字段中的列表
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data
    except Exception as e:
        logging.error(f"获取BL号码失败: {e}")
        return []


def process_bl_number(driver, bl_number):
    """处理单个BL号码"""
    try:
        # 访问网站
        driver.get("https://unipass.customs.go.kr/csp/index.do")

        # 使用WebDriverWait确保页面完全加载
        wait = WebDriverWait(driver, 20)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        time.sleep(5)

        # 点击 "M B/L - H B/L" 单选框
        radio_button = wait.until(
            EC.element_to_be_clickable((By.ID, "INDEX_cargoS02"))
        )
        radio_button.click()

        time.sleep(5)

        # 输入BL号码
        bl_input = wait.until(
            EC.presence_of_element_located((By.ID, "INDEX_hblNo"))
        )
        bl_input.clear()
        bl_input.send_keys(bl_number)

        time.sleep(5)

        # 点击查询按钮
        search_button = wait.until(
            EC.element_to_be_clickable((By.ID, "INDEX_btnRetrieveCargPrgsInfo"))
        )
        search_button.click()

        # 等待页面更新并确保完全加载
        time.sleep(5)  # 给页面一些初始加载时间
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        # 检查是否有结果表格
        try:
            # 先检查表格是否存在
            table_exists = driver.execute_script("return document.getElementById('MYC0405102Q_resultListL') !== null")

            if not table_exists:
                logging.info(f"BL号码 {bl_number} 没有查询到数据表格")
                return None

            # 使用JavaScript直接获取所有处理状态
            statuses = driver.execute_script("""
                var results = [];
                var table = document.getElementById('MYC0405102Q_resultListL');
                if(!table) return results;

                var rows = table.querySelectorAll('tbody > tr');
                var currentGroup = null;

                for(var i=0; i<rows.length; i++) {
                    var row = rows[i];
                    if(!row.getAttribute('name') || row.getAttribute('name') !== 'mycMergeTr') {
                        var cells = row.cells;
                        if(cells && cells.length > 1) {
                            var status = cells[1].textContent.trim();
                            var number = cells[0].textContent.trim();
                            results.push({
                                rowNum: number,
                                status: status
                            });
                        }
                    }
                }
                return results;
            """)

            if not statuses:
                logging.info(f"BL号码 {bl_number} 没有获取到状态数据")
                return None

            # 检查是否有特定状态
            has_release_notice = False
            has_payment_notice = False
            status = ""

            for item in statuses:
                if "반출신고" in item['status']:  # 优先返回此状态
                    has_release_notice = True
                    status = "반출신고"
                    break
                elif "수입(사용소비) 결재통보" in item['status']:
                    has_payment_notice = True
                    status = "수입(사용소비) 결재통보"

            # 返回结果
            if has_release_notice or has_payment_notice:
                return {"bl_number": bl_number, "status": status}

            logging.info(f"BL号码 {bl_number} 没有匹配的状态")
            return None

        except Exception as e:
            logging.error(f"BL号码 {bl_number} 解析表格时出错: {e}")
            return None

    except Exception as e:
        logging.error(f"处理BL号码 {bl_number} 时出错: {e}")
        return None


def run_bl_check():
    """执行BL检查任务"""
    logging.info("=== 开始执行BL状态检查任务 ===")

    # 初始化WebDriver
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # 获取BL号码列表
        bl_data = get_bl_numbers()
        results = []

        # 处理每个BL号码
        if isinstance(bl_data, list):
            for item in bl_data:
                if isinstance(item, dict) and 'bl_number' in item:
                    bl_number = item['bl_number']
                    logging.info(f"正在处理BL号码: {bl_number}")

                    result = process_bl_number(driver, bl_number)
                    if result:
                        results.append(result)
                        logging.info(f"找到结果: {result}")
                else:
                    logging.warning(f"跳过无效数据项: {item}")
        else:
            logging.error(f"无法处理的数据格式: {bl_data}")

        # 输出最终结果
        logging.info("=== 最终结果 ===")
        if results:
            for result in results:
                logging.info(f"BL号码: {result['bl_number']}, 状态: {result['status']}")
        else:
            logging.info("未发现符合条件的BL号码")

        # 发送通知
        send_notification(results)

        logging.info("=== BL状态检查任务完成 ===")

    except Exception as e:
        logging.error(f"执行BL检查任务时出现错误: {e}")
    finally:
        driver.quit()


def main():
    """主函数 - 设置定时任务"""
    logging.info("BL状态监控系统启动")

    # 设置定时任务
    schedule.every().day.at("08:00").do(run_bl_check)
    schedule.every().day.at("16:00").do(run_bl_check)
    logging.info("定时任务已设置: 每天08:00和16:00执行")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次是否有任务需要执行
    except KeyboardInterrupt:
        logging.info("系统停止运行")


if __name__ == "__main__":
    main()

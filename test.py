from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import json

from bl_notification import send_notification

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
        print(f"获取BL号码失败: {e}")
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
                print(f"BL号码 {bl_number} 没有查询到数据表格")
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
                print(f"BL号码 {bl_number} 没有获取到状态数据")
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

            print(f"BL号码 {bl_number} 没有匹配的状态")
            return None

        except Exception as e:
            print(f"BL号码 {bl_number} 解析表格时出错: {e}")
            return None

    except Exception as e:
        print(f"处理BL号码 {bl_number} 时出错: {e}")
        return None


def main():
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
                    print(f"正在处理BL号码: {bl_number}")

                    result = process_bl_number(driver, bl_number)
                    if result:
                        results.append(result)
                        print(f"找到结果: {result}")
                else:
                    print(f"跳过无效数据项: {item}")
        else:
            print(f"无法处理的数据格式: {bl_data}")

        # 输出最终结果
        print("\n最终结果:")
        for result in results:
            print(f"BL号码: {result['bl_number']}, 状态: {result['status']}")

        # 发送通知
        send_notification(results)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()

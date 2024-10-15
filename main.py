from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import yaml
from mlog import SeleniumLogger

log_file_path = 'process.log'

def monitor_website():
    # 读取 YAML 配置文件
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # 使用配置文件中的常量
    session_url = config['session_url']
    index = int(config['index'])
    len = int(config['len'])

    # 设置Chrome选项，使其连接到一个已经打开的浏览器窗口
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", session_url.replace("http://localhost", "127.0.0.1"))
    # 创建WebDriver实例，不启动新的浏览器窗口
    driver = webdriver.Chrome(options=chrome_options)
    # 创建SeleniumLogger实例
    l = SeleniumLogger(log_file_path)

    l.log(f"session_url:{session_url}, index:{index}, len:{len}")

    # 现在你可以像平常一样使用driver来控制浏览器
    # 例如，获取当前页面的URL
    current_url = driver.current_url
    error_list = set()

    try:
        for i in range(index, len):
            process(driver, l, current_url, i, error_list)

        # 对报错的进行重新处理
        for j in error_list:
            l.log(f"重新处理第{j}个视频")
            process(driver, l, current_url, j)
    except Exception as e:
        l.log(f"出现错误: {e}")
    finally:
        l.log("程序结束")


def process(driver, l, current_url, i, error_list=set()):
    if i < 10:
        paper = "0"+str(i)
    else:
        paper = str(i)

    # 防止异常页面，页面重新载入
    driver.get(current_url)
    l.log(f"Current URL:{current_url}")

    a_element = driver.find_element(
        By.XPATH, "(//li[@id='li"+paper+"'])/a")
    a_element.click()

    # 等待页面加载
    time.sleep(2)

    try:
        intervalPause = driver.execute_script("return intervalPause;")
        l.log(f"intervalPause:{intervalPause}")
        driver.execute_script("clearInterval(intervalPause);")
        l.log("清除定时器")

        # 移除console.clear()的调用
        # driver.execute_script("console.clear = function() {}")
    except Exception as e:
        l.log(f"清除定时器完成,{str(e)}")

    l.log(f"开始播放第{str(i)}个视频")
    driver.execute_script("window.cc_js_Player.play();")

    while True:
        try:
            position = driver.execute_script(
                "return window.cc_js_Player.getPosition();")
            duration = driver.execute_script(
                "return window.cc_js_Player.getDuration();")

            position = int(position)
            duration = int(duration)

            driver.execute_script("window.cc_js_Player.play();")
            print("play 剩余时间:", convert_seconds_to_minutes(
                duration - position), " 秒")

            if (duration - position) < 5:
                l.log("视频播放结束")
                time.sleep(5)
                break
            time.sleep(random.randint(30, 40))
        except Exception as e:
            time.sleep(1)
            l.log(f"内部出现错误: {e}")
            error_list.add(i)
            break


def convert_seconds_to_minutes(seconds):
    # 整数除法得到分钟数
    minutes = seconds // 60
    # 取余得到秒数
    remaining_seconds = seconds % 60
    # 格式化输出
    return f"{minutes}:{remaining_seconds:02d}"


if __name__ == "__main__":
    monitor_website()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
import yaml
from PIL import Image

from mlog import SeleniumLogger
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

log_file_path = "login.log"


def monitor_website(url, username, password):

    # 创建一个新的Chrome浏览器实例
    driver = webdriver.Chrome()

    # 创建SeleniumLogger实例
    l = SeleniumLogger(log_file_path)

    # 获取 DevTools 端口
    session_url = driver.capabilities['goog:chromeOptions']['debuggerAddress']

    l.log(f"session url:{session_url},url:{
          url},username:{username},password:{password}")
    append_session_url_to_config(session_url)

    try:
        driver.get(url)

        # 自动填写用户名和密码
        # 等待页面加载
        time.sleep(2)
        username_input = driver.find_element(
            By.NAME, "login_name")  # 替换为实际的用户名输入框的name属性
        password_input = driver.find_element(
            By.NAME, "login_pass")  # 替换为实际的密码输入框的name属性

        # 输入用户名 密码
        username_input.send_keys(username)
        password_input.send_keys(password)

        l.log(f"登录用户名：{username}")
        l.log(f"登录密码：{password}")

        # 等待验证码图片加载完成
        wait = WebDriverWait(driver, 3)
        img_element = wait.until(
            EC.presence_of_element_located((By.ID, 'imgVerify')))

        # 截取整个页面的屏幕截图
        driver.save_screenshot('screenshot.png')
        # 获取验证码图片的位置和大小
        location = img_element.location
        size = img_element.size

        # 计算截图中验证码图片的裁剪区域
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        # 打开截图
        img = Image.open('screenshot.png')
        # 裁剪出验证码图片
        crop_img = img.crop((left, top, right, bottom))
        # 保存裁剪后的验证码图片
        crop_img.save('captcha.png')

        # 使用 Tesseract 识别验证码
        captcha_text = pytesseract.image_to_string(crop_img)
        l.log(f"验证码为：{captcha_text}")

        # 填写验证码
        captcha_input = captcha_text.strip()
        captcha_field = driver.find_element(
            By.NAME, "verify_input")  # 替换为实际的验证码输入框的name属性
        captcha_field.send_keys(captcha_input)

        captcha_input = input("请输入ok开始运行:")

        # 提交表单
        try:
            login_but = driver.find_element(
                By.ID, "login_but")
            login_but.click()
        except:
            pass

        l.log("登录成功，服务已开启。。。")

        while True:
            time.sleep(60)

            try:
                # 检查是否有弹出的确认框
                alert = driver.switch_to.alert
                all_handles = driver.window_handles
                l.log(f"text:{alert.text},windows:{all_handles}")
                alert.accept()  # 点击“确定”

                if len(all_handles) > 1:
                    l.log("新窗口已打开")
                    # 切换到新的窗口
                    driver.switch_to.window(all_handles[1])
                    alert = driver.switch_to.alert
                    alert.accept()  # 点击确定
                l.log("确认框已被处理。")
            except Exception as e:
                pass

    except Exception as e:
        l.log(f"出现错误: {e}")
    finally:
        driver.quit()  # 关闭浏览器


# 将 session_url 追加到 YAML 配置文件
def append_session_url_to_config(session_url):
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file) or {}
    config['session_url'] = session_url
    with open('config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(config, file, default_flow_style=False)


if __name__ == "__main__":
    # 读取 YAML 配置文件
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    # 使用配置文件中的常量
    url_to_monitor = config['url_to_monitor']
    username = config['username']
    password = config['password']
    monitor_website(url_to_monitor, username, password)

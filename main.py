import time
import os
import sys
import threading

from proxy_auth import proxies
from selenium_recaptcha_solver import RecaptchaSolver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from msilib.schema import CheckBox

# from auth_data import bank_password, bank_emale

print("Режимы работы:")
print("0 - Открыть браузер Chrome")
print("1 - Открыть ss.lv")
print("2 - Ввести ссылку")
print("3 - Осуществить покупку")
print("4 - Оcуществить продажу")

mode = int(input("Введите номер режима: "))

if mode == 0:
    os.startfile (r"C:\WebDriver\chromedriver\Chrome.lnk")
    sys.exit()
    os._exit(0)
    
options = webdriver.ChromeOptions()
test_ua = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
def set_driver_options(options:webdriver.ChromeOptions):
    # user-agent
    options.add_argument(f'--user-agent={test_ua}')
    
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    # options.add_argument("--proxy-server=ip:port")
    
    
    options.debugger_address = 'localhost:8989'

set_driver_options(options)

caps = DesiredCapabilities().CHROME
# caps['pageLoadStrategy'] = 'eager'
caps['pageLoadStrategy'] = 'normal'

service = Service(desired_capabilities=caps, executable_path=r"C:\WebDriver\chromedriver\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

solver = RecaptchaSolver(driver=driver)

# class всплывающего диалогового окна
class_name = "alert_head"
dialog_semaphore = threading.Semaphore(value=0)

# stop_threads = False

try:
                    
    # Функция для проверки наличия класса 'new_class'
    def check_dialog_class(driver:webdriver.Chrome):
        try:
            element = driver.find_element(By.CLASS_NAME, class_name)
            # # Действия после появления класса class_name
            # click_dont_prompt_again(driver)
            # # нажать кннопку подтверить
            # click_trade_confirm_button(driver, "Confirm")
            # # нажать кннопку отмена
            # # click_trade_confirm_button(driver, "Cancel")
            # close_dialog_window(driver, element)
            click_i_see(driver, element)
        except:
            pass
        finally:
            # Release the semaphore to allow waiting threads to continue
            dialog_semaphore.release()      
              
    # Функция для выполнения проверки в отдельном потоке
    def check_dialog_thread(stop, driver:webdriver.Chrome):
        while True:
            check_dialog_class(driver)
            if stop():
                break

    # Passing authentication...
    def authentication(driver:webdriver.Chrome):
        try:
            email_input = driver.find_element(By.XPATH, "//input[@placeholder='Please enter your email']")
            email_input.clear()
            email_input.send_keys(bank_emale)

            password_input = driver.find_element(By.XPATH, "//input[@placeholder='Please enter password']")
            password_input.clear()
            password_input.send_keys(bank_password)
            
            password_input.send_keys(Keys.ENTER)
        except Exception:
            print("Поля аутентификации не найдены или уже авторизованы")
            pass

    # нажать Market
    def click_order(driver:webdriver.Chrome, arg:str):
        try:
            order = driver.find_element(By.XPATH, f"//div[contains(text(), '{arg}')]")
            driver.execute_script("arguments[0].click();", order)
        except NoSuchElementException:
            print(f"Кнопка {arg} не найдена")
            pass

    # установить значение amount
    def set_amount(driver:webdriver.Chrome, arg:str, val:str):
        try:
            input = driver.find_element(By.XPATH, f"//input[@placeholder='{arg}']")
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(Keys.BACKSPACE)
            input.send_keys(val)
        except NoSuchElementException:
            print(f"Поле для ввода {arg} не найдено")
            pass

    # установка слайдера в максимальное значение
    def turn_trade_slider(driver:webdriver.Chrome, arg:str):
        try:
            slider = driver.find_element(By.XPATH, f"//div[contains(@class, '{arg}')]//span[@style='left: 100%;']")
            slider.click()
        except NoSuchElementException:
            print(f"Не могу сдвинуть слайдер {arg}")
            pass

    # нажать кнопку buy/sell
    def click_trade_button(driver:webdriver.Chrome, arg:str):
        try:
            button = driver.find_element(By.XPATH, f"//button[contains(@class, '{arg}')]")
            driver.execute_script("arguments[0].click();", button)
        except NoSuchElementException:
            print(f"Кнопка {arg} не найдена")
            pass

    # нажать кнопку cancel/confirm Order
    # передаются два аргумента args {Cancel} / {Confirm}
    def click_trade_confirm_button(driver:webdriver.Chrome, arg:str):
        try:
            span = driver.find_element(By.XPATH, f"//span[contains(text(), '{arg}')]")
            button = span.find_element(By.XPATH, "./parent::button")
            driver.execute_script("arguments[0].click();", button)
        except NoSuchElementException:
            print(f"Кнопка {arg} не найдена")
            pass

    # активировать чек-бокс "Don't prompt again"
    def click_dont_prompt_again(driver:webdriver.Chrome):
        try:
            span = driver.find_element(By.XPATH, "//span[contains(text(), 'prompt again')]")
            check = span.find_element(By.XPATH, "./parent::div")
            driver.execute_script("arguments[0].click();", check)
        except NoSuchElementException:
            print("Чек-бокс не найден")
            pass

    # закрыть всплывающее диалоговое окно
    def close_dialog_window(driver:webdriver.Chrome, dialog):
        try:
            closeButton = dialog.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
            driver.execute_script("arguments[0].click();", closeButton)
        except NoSuchElementException:
            print("Кнопка Close не найдена")    
            pass       

    # Нажать кнопку I see
    def click_i_see(driver:webdriver.Chrome, dialog):
        try:
            # checkBox = dialog.find_element(By.XPATH, "//label[contains(@id, 'recaptcha-anchor-label')]")
            # checkBox.click()
            
            # Wait for the iframe containing the reCAPTCHA to be present.
            recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            recaptcha_iframe.find_element(By.XPATH, '//textarea[@id="g-recaptcha-response"]')
            recaptcha_iframe.click()
            # solver.click_recaptcha_v2(iframe=recaptcha_iframe)
            # span = dialog.find_element(By.XPATH, "//span[contains(text(), 'I see')]")
            # button = span.find_element(By.XPATH, "./parent::button")
            # driver.execute_script("arguments[0].click();", button)
        except NoSuchElementException:
            print("Кнопка I see не найдена")     
            pass      
        
    driver.maximize_window
    
    stop_threads = False
    # Создание и запуск потока для выполнения проверки на всплывающее диалоговое окно
    thread = threading.Thread(target=check_dialog_thread, args=(lambda : stop_threads, driver, ))
    thread.start()

    if mode == 1:
        driver.get("https://www.ss.lv/msg/ru/electronics/phones/mobile-phones/samsung/galaxy-s21-fe-5g/cbhlxb.html")
        # time.sleep(2)
        showPhone = driver.find_element(By.XPATH, "//a[contains(@onclick, '_show_phone')]")
        showPhone.click()
        time.sleep(2)
        # checkBox = driver.find_element(By.XPATH, "//label[contains(@id, 'recaptcha-anchor-label')]")
        # checkBox.click()
        
        # driver.execute_script("arguments[0].click();", showPhone)

        # authentication(driver)

    if mode == 2:
        url = str(input("Введите ссылку: "))
        # driver.get("https://www.lbank.com/en-US/trade/btc_usdt/")
        driver.get(url)
        
    if mode == 3:
        def thread_by(driver:webdriver.Chrome):
            dialog_semaphore.acquire()
            click_order(driver, "Market")
            dialog_semaphore.acquire()
            turn_trade_slider(driver, "tradeSliderGreen")
            # dialog_semaphore.acquire()
            # set_amount(driver, "Enter buying amount", "0.10")        
            dialog_semaphore.acquire()
            click_trade_button(driver, "index_buy")
        threadBy = threading.Thread(target=thread_by, args=(driver, ))
        threadBy.start()
        threadBy.join()

    if mode == 4:
        def thread_sell(driver:webdriver.Chrome):
            dialog_semaphore.acquire()
            click_order(driver, "Market")
            dialog_semaphore.acquire()
            turn_trade_slider(driver, "tradeSliderRed")
            # dialog_semaphore.acquire()
            # set_amount(driver, "Enter selling amount", "0.01")
            dialog_semaphore.acquire()
            click_trade_button(driver, "index_sel")
        threadSell = threading.Thread(target=thread_sell, args=(driver, ))
        threadSell.start()
        threadSell.join()
        
except Exception as ex:
    print(ex)
finally:
    stop_threads = True
    thread.join()
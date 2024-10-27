#!/usr/bin/env python3
import os
from time import sleep, localtime
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# exceptions
from selenium.common.exceptions import TimeoutException, \
    UnexpectedAlertPresentException, NoSuchElementException, \
    WebDriverException, InvalidSessionIdException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
# secure imports
import configparser
from config.data import USER_DATA_PATH, SESSION_PATH

DRIVER_ALIVE = False

def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver

def close_father_webdriver(driver):
    driver.close() # better just press ENTER at the main bash
    DRIVER_ALIVE = False

def get_to_apointments(driver):
    global DRIVER_ALIVE
    vars = {}
    print("Step 2\t->\tClick on link") # ----------------------------
    vars["window_handles"] = driver.window_handles
    # first link
    try:
        # vars["init_link"] = WebDriverWait(driver, 2).until(
        #     EC.presence_of_element_located((By.XPATH, "/html/body/form/div[2]/main/div[3]/div[1]/div/div/div/div/div[1]/div/section/div/div/p[24]/a"))
        # )
        vars["init_link"] = driver.find_element_by_xpath("/html/body/form/div[2]/main/div[3]/div[1]/div/div/div/div/div[1]/div/section/div/div/p[24]/a")
    except:
        # vars["init_link"] = WebDriverWait(driver, 2).until(
        #     EC.presence_of_element_located((By.XPATH, "/html/body/form/div[2]/main/div[3]/div[1]/div/div/div/div/div[1]/div/section/div/div/p[24]/a"))
        # )
        try:
            vars["init_link"] = driver.find_element_by_xpath("/html/body/form/div[2]/main/div[3]/div[1]/div/div/div/div/div[1]/div/section/div/div/ul[1]/li[2]/a[2]")
        except:
            driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
            driver.get('https://www.citaconsular.es/es/hosteds/widgetdefault/28db94e270580be60f6e00285a7d8141f/bkt873048')

    # print(vars["init_link"].text)
    vars["init_link"].click()
    sleep(10)
    print("Step 3\t->\tFind new window") # ----------------------------
    wh_now = driver.window_handles
    wh_then = vars["window_handles"]
    if len(wh_now) > len(wh_then):
      vars["alert"] = set(wh_now).difference(set(wh_then)).pop()
    driver.switch_to.window(vars["alert"])

    try:
        print("Step 4\t->\tClick on Continue button") # ----------------------------
        driver.find_element(By.ID, "idCaptchaButton").click()
    except UnexpectedAlertPresentException:
        print("Step 4\t->\tError, button not ready") # ----------------------------
        sleep(2)
        vars["alert_button"] = driver.find_element(By.ID, "idCaptchaButton")
        vars["alert_button"].click()
    except NoSuchElementException:
        print("Step 4\t->\tError, web not accessible") # ----------------------------
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return -1
        
    try:
        print("Step 5\t->\tLook for header") # ----------------------------
        vars["service_header"] = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "idBktWidgetDefaultHeader"))
        )
    except TimeoutException:
        print("Step 5\t->\tError, timeout, header not found") # ----------------------------
        print("Web not accessible")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return -2

    try:
        print("Step 6\t->\tLook for page container") # ----------------------------
        vars["service_container"] = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "idBktDefaultServicesContainer"))
        )
    except TimeoutException:
        # !!!!!!!!!!!
        print("Step 6\t->\tError, something strange... Send message!!") # ----------------------------
        with open("Output_Exception-3.html","a",encoding="utf-8") as f:
            f.write(f"{driver.page_source}\n\n\n")
        with open("config/session/shared_file.memory","w",encoding="utf-8") as f:
            f.write(f"{datetime.today()} ¡¡Hay algo raro, mirar la web!!")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return -3

    sleep(30)
    if vars["service_container"].text.find("No hay horas disponibles") >= 0:
        print("Step 7\t->\tDo nothing") # ----------------------------
        with open("config/session/shared_file.memory","w",encoding="utf-8") as f:
            f.write(f"{datetime.today()} Nada todavia :(")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return 0
    elif vars["service_container"].text.find("SE HA PRODUCIDO UN ERROR AL CARGAR LOS DATOS") >= 0:
        print("Step 7\t->\tDo nothing") # ----------------------------
        with open("config/session/shared_file.memory","w",encoding="utf-8") as f:
            f.write(f"{datetime.today()} Error de la página. Error carga de datos")
        with open("Output_LoadErrorExit.html","a",encoding="utf-8") as f:
            f.write(f"{driver.page_source}\n\n\n")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return 0
    else:
        print("Step 7\t->\tSend message!!") # ----------------------------
        with open("Output_GoodExit.html","a",encoding="utf-8") as f:
            f.write(f"{driver.page_source}\n\n\n")
        with open("config/session/shared_file.memory","w") as f:
            f.write(f"{datetime.today()} ¿¿¿Cita disponible??? dice:"+vars["service_container"].text)
            # f.write(f"{datetime.today()} ¿¿¿Cita disponible???")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        DRIVER_ALIVE = False
        return 1




def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver

def initialize_driver():
    base_url = 'https://www.exteriores.gob.es/Consulados/lahabana/es/ServiciosConsulares/Paginas/index.aspx?scco=Cuba&scd=166&scca=Visados&scs=Visado+de+estancia+(visado+Schengen)'

    options = webdriver.FirefoxOptions()
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument("--disable-plugins-discovery")
    # options.add_argument("--user-data-dir=%s"%SESSION_PATH)   # setear ruta local path

    browser = webdriver.Firefox(firefox_options=options)
    browser.get(base_url)

    session_id = browser.session_id
    executor_url = browser.command_executor._url

    config = configparser.ConfigParser()
    config.read("config/session/session.ini")
    config['SESSION']['session_id'] = session_id
    config['SESSION']['executor_url'] = executor_url

    with open('config/session/session.ini', 'w') as configfile:
        config.write(configfile)

    return browser

def main(driver):
    global DRIVER_ALIVE
    # config = configparser.ConfigParser()
    # config.read("config/session/session.ini")
    # session_id =  config['SESSION']['session_id']
    # executor_url = config['SESSION']['executor_url']
    # driver = create_driver_session(session_id, executor_url)

    # driver.switch_to.window(driver.window_handles[0])
    driver = driver
    DRIVER_ALIVE = True
	
    try:
        base_url = 'https://www.exteriores.gob.es/Consulados/lahabana/es/ServiciosConsulares/Paginas/index.aspx?scco=Cuba&scd=166&scca=Visados&scs=Visado+de+estancia+(visado+Schengen)'
        driver.get(base_url)
        sleep(5)
        print("Step 1\t->\tGet base URL")

        get_to_apointments(driver)

        sleep(2)
        # driver = create_driver_session(session_id, executor_url)
        driver.switch_to.window(driver.window_handles[0])
    except TimeoutException:
        if DRIVER_ALIVE:
            driver.close()
        print("\t\t\tnavigation failed...")
    except WebDriverException as e:
        if DRIVER_ALIVE:
            driver.close()
        print("\t\t\tsomething else failed...")
        print(e)
    finally:
        driver.quit()
        print("\t\t\tdriver closed...")

if __name__ == "__main__":
    try:
        # while 1:
        #     if (datetime.now().hour == 5 and 55<= datetime.now().minute <=59)\
        #     or (datetime.now().hour == 6 and 0<= datetime.now().minute <=35):
        #         main()
        #         print("\t\t\tsleeping 5 minutes")
        #         sleep(5*60)
        #     else:
        #         # print("\t\t\tsleeping 20 minutes")
        #         # sleep(20*60)
        #         sleep(20)
        while 1:
            with open("../vpn/LOCK.txt","w", encoding="utf-8") as f:
                f.write("LOCKED")
            
            try:
                browser = initialize_driver()

                main(browser)

                try:
                    browser.quit()
                except InvalidSessionIdException:
                    # browser.switch_to.window(browser.window_handles[0])
                    # browser.close()
                    print("\t\t\tdriver closed...")
            except Exception as e:
                print("""
                //////////////////////////////////////////////////
                //////////////////////////////////////////////////
                //////////////////////////////////////////////////
                                UNHANDLED EXCEPTION
                //////////////////////////////////////////////////
                //////////////////////////////////////////////////
                //////////////////////////////////////////////////
                ""","\n",str(e))

                try:
                    browser.quit()
                    print("\t\t\tdriver closed after exception...")
                except InvalidSessionIdException:
                    # browser.switch_to.window(browser.window_handles[0])
                    # browser.close()
                    print("\t\t\tdriver was not closed after exception")
            finally:
                with open("../vpn/LOCK.txt","w") as f:
                    f.write("FREE")
                print("\t\t\tsleeping...")
                # sleep(7*10)
                sleep(5)

                try:
                    print("\t\t\tkilling all firefox instances just in case...")
                    os.system("killall firefox")
                    print("\t\t\tall firefox instances has been killed...")
                except:
                    print("\t\t\tnot able to kill them...")
    except KeyboardInterrupt:
        print('Interrupted')

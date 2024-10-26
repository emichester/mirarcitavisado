#!/usr/bin/env python3
from time import sleep, localtime
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# exceptions
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
# secure imports
import configparser

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

def get_to_apointments(driver):
    vars = {}
    print("Step 2\t->\tClick on link") # ----------------------------
    vars["window_handles"] = driver.window_handles
    # first link
    vars["init_link"] = driver.find_element_by_xpath("/html/body/form/div[2]/main/div[3]/div[1]/div/div/div/div/div[1]/div/section/div/div/p[24]/a")
    # print(vars["init_link"].text)
    vars["init_link"].click()
    sleep(5)
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
        return -2
    try:
        print("Step 6\t->\tLook for page container") # ----------------------------
        vars["service_container"] = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "idBktDefaultServicesContainer"))
        )
    except TimeoutException:
        # !!!!!!!!!!!
        print("Step 6\t->\tError, something strange... Send message!!") # ----------------------------
        with open("Output_Exception-3.html","a") as f:
            f.write(f"{driver.page_source}\n\n\n")
        with open("config/session/shared_file.memory","w") as f:
            f.write(f"{datetime.today()} ¡¡Hay algo raro, mirar la web!!")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        return -3
    sleep(30)
    if vars["service_container"].text.find("No hay horas disponibles") >= 0:
        print("Step 7\t->\tDo nothing") # ----------------------------
        with open("config/session/shared_file.memory","w") as f:
            f.write(f"{datetime.today()} Nada todavía :(")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        return 0
    else:
        print("Step 7\t->\tSend message!!") # ----------------------------
        with open("Output_GoodExit.html","a") as f:
            f.write(f"{driver.page_source}\n\n\n")
        with open("config/session/shared_file.memory","w") as f:
            f.write(f"{datetime.today()} ¡¡Cita disponible!!")
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        return 1


def main():
    config = configparser.ConfigParser()
    config.read("config/session/session.ini")
    session_id =  config['SESSION']['session_id']
    executor_url = config['SESSION']['executor_url']
    driver = create_driver_session(session_id, executor_url)

    driver.switch_to.window(driver.window_handles[0])
		
    base_url = 'https://www.exteriores.gob.es/Consulados/lahabana/es/ServiciosConsulares/Paginas/index.aspx?scco=Cuba&scd=166&scca=Visados&scs=Visado+de+estancia+(visado+Schengen)'
    driver.get(base_url)
    sleep(5)
    print("Step 1\t->\tGet base URL")

    get_to_apointments(driver)

    sleep(2)
    driver = create_driver_session(session_id, executor_url)
    driver.switch_to.window(driver.window_handles[0])
    driver.get('https://www.duckduckgo.com')

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
            with open("/home/emilio/PaginasWeb/vpn/LOCK.txt","w") as f:
                f.write("LOCKED")
            try:
                main()
            except TimeoutException:
                print("\t\t\tnavigation failed...")
            with open("/home/emilio/PaginasWeb/vpn/LOCK.txt","w") as f:
                f.write("FREE")
            print("\t\t\tsleeping...")
            sleep(4*20)
    except KeyboardInterrupt:
        print('Interrupted')

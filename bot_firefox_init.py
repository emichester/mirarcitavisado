#!/usr/bin/env python3
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# secure imports
import configparser
from config.data import USER_DATA_PATH, SESSION_PATH

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

base_url = 'https://www.exteriores.gob.es/Consulados/lahabana/es/ServiciosConsulares/Paginas/index.aspx?scco=Cuba&scd=166&scca=Visados&scs=Visado+de+estancia+(visado+Schengen)'

timeout = 5#30

options = webdriver.FirefoxOptions()
options.add_argument('--disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--profile-directory=Default')
options.add_argument("--disable-plugins-discovery")
options.add_argument("--user-data-dir=%s"%SESSION_PATH)   # setear ruta local path

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

input() # scan the qr

browser.close()
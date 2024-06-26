# Generated by Selenium IDE

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import os

class TestUnl():
  

  def __init__(self):
    #self.options.add_experimental_option("detach", True)
    #self.google_chrome_bin = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
    #self.chrome_driver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

    self.options = webdriver.ChromeOptions()

    #self.options.binary_location = self.google_chrome_bin
    #self.options.add_extension(self.chrome_driver_path)
    #self.options.add_argument("--no-sandbox")
    #self.options.add_argument("--headless")

    #self.options.enable_downloads = True
    self.driver = webdriver.Chrome(options=self.options)

    #self.driver = webdriver.Chrome(options=self.options)
    self.wait = WebDriverWait(self.driver, 10)
    self.vars = {}

  
  def teardown_method(self):
    self.driver.quit()

  def wait_for_window(self, timeout = 1):
    time.sleep(round(timeout / 1000))
    wh_now = self.driver.window_handles
    wh_then = self.vars["window_handles"]
    if len(wh_now) > len(wh_then):
      return set(wh_now).difference(set(wh_then)).pop()
    
  def test_unl(self, url, year, mes):
    
    # Test name: unl
    # Step # | name | target | value

    # 1 | open | https://www.unl.edu.ec/ | 
    self.driver.get(url)
    print(f'Url que subo {self.driver.current_url}')

    try:
       self.driver.find_element(By.PARTIAL_LINK_TEXT, 'X').click()
    except:
        try:
          self.driver.find_element(By.XPATH, f"//a[contains(text(), 'X')]").click()
        except:
           pass

    self.original_window = self.driver.current_window_handle
    # 3 | click | linkText=Transparencia | 
    try:
       self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Transparencia').click()
    except:
       self.driver.find_element(By.XPATH, f"//a[contains(text(), 'Transparencia')]").click()

    print("Luego de dar click en transparecnia",self.original_window)
    for self.window_handle in self.driver.window_handles:
        if self.window_handle != self.original_window:
            self.driver.switch_to.window(self.window_handle)
            break

    # 4 | click | linkText=2020 | 
    #self.original_window = self.driver.current_window_handle
    try:
        self.driver.find_element(By.PARTIAL_LINK_TEXT, year).click()
    except:
        self.driver.find_element(By.XPATH, f"//a[contains(text(), '{year}')]").click()
        
    self.original_window = self.driver.current_window_handle
    print("Luego de dar click en año",self.original_window)
    for self.window_handle in self.driver.window_handles:
        if self.window_handle != self.original_window:
            self.driver.switch_to.window(self.window_handle)
            break
    
    
    # 5 | click | css=#ui-id-3 > .field-content | 
    #self.original_window = self.driver.current_window_handle
    try:
       self.driver.find_element(By.PARTIAL_LINK_TEXT, mes).click()
    except:
       self.driver.find_element(By.XPATH, f"//span[contains(text(), '{mes}')]").click()
    

    # 6 | click | linkText=Literal g.- Presupuesto de la Institución | 
    self.original_window = self.driver.current_window_handle
    print("Luego de dar click en mes", self.original_window)
    for self.window_handle in self.driver.window_handles:
        if self.window_handle != self.original_window:
            self.driver.switch_to.window(self.window_handle)
            break
    
    self.original_window = self.driver.current_window_handle
    try:
        self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Presupuesto').click()
    except:
        self.driver.find_element(By.XPATH, f"//a[contains(text(),'Presupuesto')]").click()

    # Wait for the new window or tab
    print(self.original_window)
    for self.window_handle in self.driver.window_handles:
        if self.window_handle != self.original_window:
            self.driver.switch_to.window(self.window_handle)
            break
    

    #self.original_window = self.driver.current_window_handle
    print(self.original_window)
    print(self.driver.current_url)
    link = self.driver.current_url
    return link
    #self.vars["win624"] = self.wait_for_window(2000)
  

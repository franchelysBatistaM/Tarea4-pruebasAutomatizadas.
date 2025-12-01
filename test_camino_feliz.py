import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER_PATH = "./drivers/chromedriver"  
CAPTURES_DIR = "./capturas_camino_feliz"
os.makedirs(CAPTURES_DIR, exist_ok=True)

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

def take_screenshot(driver, name):
    driver.save_screenshot(f"{CAPTURES_DIR}/{name}.png")

def test_login_correcto(driver):
    driver.get("http://127.0.0.1:5000")
    driver.find_element(By.NAME, "usuario").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(1)
    take_screenshot(driver, "01_login_correcto")
    assert "Beauty gestion de servicios" in driver.page_source

def test_crear_servicio(driver):
    driver.find_element(By.NAME, "servicio").send_keys("Planchado de pelo")
    driver.find_element(By.NAME, "precio").send_keys("20.00")
    driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    time.sleep(1)
    take_screenshot(driver, "02_crear_servicio")
    assert "Planchado de pelo" in driver.page_source

def test_editar_servicio(driver):
    driver.find_element(By.LINK_TEXT, "Editar").click()
    time.sleep(1)
    servicio_input = driver.find_element(By.NAME, "servicio")
    precio_input = driver.find_element(By.NAME, "precio")
    servicio_input.clear()
    servicio_input.send_keys("Planchado y blower")
    precio_input.clear()
    precio_input.send_keys("35.50")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(1)
    take_screenshot(driver, "03_editar_servicio")
    assert "Planchado y blower" in driver.page_source

def test_eliminar_servicio(driver):
    driver.find_element(By.LINK_TEXT, "Eliminar").click()
    alert = driver.switch_to.alert
    alert.accept()
    time.sleep(1)
    take_screenshot(driver, "04_eliminar_servicio")
    assert "Planchado y blower" not in driver.page_source

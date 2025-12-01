import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = "./drivers/chromedriver"
CAPTURES_DIR = "./capturas_pruebas_limite"
os.makedirs(CAPTURES_DIR, exist_ok=True)

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--start-maximized")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("http://127.0.0.1:5000")
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def wait(driver):
    return WebDriverWait(driver, 10)

def take_screenshot(driver, name):
    driver.save_screenshot(f"{CAPTURES_DIR}/{name}.png")

def login(driver, wait):
    driver.find_element(By.NAME, "usuario").send_keys("admin")
    driver.find_element(By.NAME, "password").send_keys("1234")
    driver.find_element(By.TAG_NAME, "button").click()
    wait.until(EC.presence_of_element_located((By.NAME, "servicio")))

def eliminar_servicio(driver, nombre_servicio):
    driver.get("http://127.0.0.1:5000/dashboard")
    time.sleep(1)
    filas = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for fila in filas:
        nombre = fila.find_element(By.CSS_SELECTOR, "td:first-child").text
        if nombre == nombre_servicio:
            eliminar_btn = fila.find_element(By.LINK_TEXT, "Eliminar")
            eliminar_btn.click()
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(1)
            break

def test_login(driver, wait):
    take_screenshot(driver, "01_pagina_login")
    login(driver, wait)
    take_screenshot(driver, "02_login_correcto")
    assert "Beauty gestion de servicios" in driver.page_source

def test_nombre_largo_no_valido(driver, wait):
    servicio_largo = "A" * 101  
    assert len(servicio_largo) == 101
    driver.find_element(By.NAME, "servicio").clear()
    driver.find_element(By.NAME, "precio").clear()
    driver.find_element(By.NAME, "servicio").send_keys(servicio_largo)
    driver.find_element(By.NAME, "precio").send_keys("50")
    driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    
    wait.until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, "div.alert-danger"),
        "El nombre del servicio no puede superar los 100 caracteres."
    ))
    take_screenshot(driver, "03_prueba_limite_servicio_101")


def test_nombre_valido_100(driver, wait):
    servicio_valido = "A" * 100 
    assert len(servicio_valido) == 100
    driver.find_element(By.NAME, "servicio").clear()
    driver.find_element(By.NAME, "precio").clear()
    driver.find_element(By.NAME, "servicio").send_keys(servicio_valido)
    driver.find_element(By.NAME, "precio").send_keys("50")
    driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    wait.until(EC.presence_of_element_located((By.XPATH, f"//table//td[text()='{servicio_valido}']")))
    take_screenshot(driver, "04_prueba_limite_servicio_100")
    eliminar_servicio(driver, servicio_valido)

def test_precio_cero_no_valido(driver, wait):
    driver.find_element(By.NAME, "servicio").clear()
    driver.find_element(By.NAME, "precio").clear()
    driver.find_element(By.NAME, "servicio").send_keys("Corte Básico")
    driver.find_element(By.NAME, "precio").send_keys("0")
    driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "El precio debe ser mayor a 0"))
    take_screenshot(driver, "05_prueba_limite_precio_0")

def test_precio_minimo_valido(driver, wait):
    servicio = "Servicio Cortes Precio Minimo"
    driver.find_element(By.NAME, "servicio").clear()
    driver.find_element(By.NAME, "precio").clear()
    driver.find_element(By.NAME, "servicio").send_keys(servicio)
    driver.find_element(By.NAME, "precio").send_keys("0.01")
    driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
    wait.until(EC.presence_of_element_located((By.XPATH, f"//table//td[text()='{servicio}']")))
    take_screenshot(driver, "06_prueba_limite_precio_minimo")
    eliminar_servicio(driver, servicio)


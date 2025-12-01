import os
import time
import pytest
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROMEDRIVER_PATH = "./drivers/chromedriver"
CAPTURES_DIR = "./capturas_negativas"
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
    path = f"{CAPTURES_DIR}/{name}.png"
    driver.save_screenshot(path)
    print(f" Captura guardada: {path}")

def login(driver, wait, usuario, password):
    driver.find_element(By.NAME, "usuario").clear()
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "usuario").send_keys(usuario)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.TAG_NAME, "button").click()

def eliminar_servicio(driver, wait, nombre_servicio):
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

@pytest.mark.order(1)
def test_login_incorrecto(driver, wait):
    try:
        login(driver, wait, "admin", "wrongpass")
        time.sleep(1)
        take_screenshot(driver, "01_login_incorrecto")
        assert "Credenciales incorrectas" in driver.page_source
        print("Prueba negativa 1: Login incorrecto PASÓ")
    except Exception:
        take_screenshot(driver, "error_login_incorrecto")
        raise

@pytest.mark.order(2)
def test_crear_servicio_sin_nombre(driver, wait):
    try:
        login(driver, wait, "admin", "1234")
        wait.until(EC.presence_of_element_located((By.NAME, "servicio"))).clear()
        wait.until(EC.presence_of_element_located((By.NAME, "precio"))).clear()
        driver.find_element(By.NAME, "precio").send_keys("10")
        driver.execute_script("document.getElementsByName('servicio')[0].removeAttribute('required')")
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        time.sleep(1)
        take_screenshot(driver, "02_servicio_sin_nombre")
        assert "Todos los campos son obligatorios." in driver.page_source
        print("Prueba negativa 2: Servicio sin nombre PASÓ")
    except Exception:
        take_screenshot(driver, "error_servicio_sin_nombre")
        raise

@pytest.mark.order(3)
def test_crear_servicio_precio_negativo(driver, wait):
    try:
        driver.find_element(By.NAME, "servicio").clear()
        driver.find_element(By.NAME, "precio").clear()
        driver.find_element(By.NAME, "servicio").send_keys("Planchado tenaza")
        driver.find_element(By.NAME, "precio").send_keys("-5")
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        time.sleep(1)
        take_screenshot(driver, "03_servicio_precio_negativo")
        assert "El precio debe ser mayor a 0." in driver.page_source
        print("Prueba negativa 3: Precio negativo PASÓ")
    except Exception:
        take_screenshot(driver, "error_precio_negativo")
        raise

@pytest.mark.order(4)
def test_crear_servicio_nombre_largo(driver, wait):
    try:
        driver.find_element(By.NAME, "servicio").clear()
        driver.find_element(By.NAME, "precio").clear()
        nombre_largo = "Servicio De Planchado, Lavado, Corte De Cabello Con Estilo Profesional Para Clientes Muy Exigentes Extra123"
        nombre_largo = nombre_largo[:101]
        driver.find_element(By.NAME, "servicio").send_keys(nombre_largo)
        driver.find_element(By.NAME, "precio").send_keys("10")
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        time.sleep(1)
        take_screenshot(driver, "04_servicio_nombre_largo")
        assert "El nombre del servicio no puede superar los 100 caracteres." in driver.page_source
        print("Prueba negativa 4: Nombre largo PASÓ")
    except Exception:
        take_screenshot(driver, "error_nombre_largo")
        raise

@pytest.mark.order(5)
def test_crear_servicios_validos(driver, wait):
    try:
        driver.find_element(By.NAME, "servicio").clear()
        driver.find_element(By.NAME, "precio").clear()
        driver.find_element(By.NAME, "servicio").send_keys("Planchado keratin")
        driver.find_element(By.NAME, "precio").send_keys("25")
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        time.sleep(1)

        driver.find_element(By.NAME, "servicio").clear()
        driver.find_element(By.NAME, "precio").clear()
        driver.find_element(By.NAME, "servicio").send_keys("Peinado gelatina")
        driver.find_element(By.NAME, "precio").send_keys("15")
        driver.find_element(By.CSS_SELECTOR, "button.btn-success").click()
        time.sleep(1)

        print("Servicios validos creados para pruebas de edicion y eliminacion.")
    except Exception:
        take_screenshot(driver, "error_crear_servicios_validos")
        raise

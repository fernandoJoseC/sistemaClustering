
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class TestDinamico():
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.options)
        self.vars ={}
    

    def teardown_method(self, method):
        self.driver.quit()

    def abrir_url(self, url):
        self.driver.get(url)

    def buscar_y_clicar(self, texto, tags):
        """Busca un texto en una lista de tags y hace clic en el primero que encuentra."""
        for tag in tags:
            try:
                element = self.driver.find_element(By.XPATH, f"//{tag}[contains(text(), '{texto}')]")
                element.click()
                return
            except NoSuchElementException:
                continue
        print(f"No se encontró el texto '{texto}' en los tags proporcionados.")

    def test_busqueda_dinamica(self, url):
        #url = "https://www.unl.edu.ec/"  # Define la URL aquí o pasa como parámetro de clase
        busquedas = {
            "Transparencia": ["h5", "h4", "span", "a"],
            "2020": ["h5", "h4", "span", "a"],
            "Enero": ["h5", "h4", "span", "a"],
            #"Rendición de cuentas": ["h5", "h4", "span", "a"],
            "Presupuesto": ["h5", "h4", "span", "a"]
        }  # Define las búsquedas aquí o como un parámetro de clase
        self.abrir_url(url)
        for texto, tags in busquedas.items():
            self.buscar_y_clicar(texto, tags)


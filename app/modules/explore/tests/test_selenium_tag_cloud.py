import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestSeleniumTagCloud:

    def setup_method(self, method):
        """Configuración inicial para cada test."""
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1854, 1048)

    def teardown_method(self, method):
        """Limpieza al finalizar cada test."""
        self.driver.quit()

    def test_selenium_tag_cloud(self):
        """Test para verificar la funcionalidad del tag cloud en la aplicación."""
        try:
            # Navegar a la página principal
            self.driver.get("http://127.0.0.1:5000/")

            # Esperar y hacer clic en la opción de la barra lateral
            sidebar_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".sidebar-item:nth-child(3) .align-middle:nth-child(2)"))
            )
            sidebar_option.click()

            # Esperar y hacer clic en un tag específico
            tag = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "tag1"))
            )
            tag.click()

            # Esperar la lista de modelos relacionados
            feature_model_item = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".list-group-item"))
            )

            # Interacción con el botón de opciones del primer modelo
            options_button = feature_model_item.find_element(By.CSS_SELECTOR, ".options-btn")
            options_button.click()

            # Esperar a que las opciones sean visibles
            options_container = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#options-99"))
            )

            # Clic en el botón "View Description"
            view_description_button = options_container.find_element(By.CSS_SELECTOR, ".btn-outline-info")
            view_description_button.click()

            # Verificar la visibilidad del modal y cerrar
            close_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-close"))
            )
            close_button.click()

            # Descargar un archivo UVL
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Download UVL"))
            )
            download_link.click()

            # Verificar que el enlace de descarga sea accesible
            assert download_link, "El enlace 'Download UVL' no se completó correctamente."

        except Exception as e:
            # Captura de pantalla en caso de error
            self.driver.save_screenshot("error_screenshot.png")
            print(f"Se produjo un error durante el test: {e}")
            raise

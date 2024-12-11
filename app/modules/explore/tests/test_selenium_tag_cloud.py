import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os


class TestSeleniumTagCloud:

    def setup_method(self, method):
        """Configuración inicial para cada test."""
        # Configuración de opciones del navegador
        chrome_options = Options()
        download_dir = os.path.abspath("descargas_temp")  # Carpeta temporal para descargas
        os.makedirs(download_dir, exist_ok=True)
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        self.download_dir = download_dir
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1854, 1048)

    def teardown_method(self, method):
        """Limpieza al finalizar cada test."""
        self.driver.quit()
        # Eliminar los archivos descargados
        for root, _, files in os.walk(self.download_dir):
            for file in files:
                os.remove(os.path.join(root, file))

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

            # Clic en el menú desplegable de Export
            dropdown_toggle = options_container.find_element(By.CSS_SELECTOR, ".btn-outline-success.dropdown-toggle")
            dropdown_toggle.click()

            # Clic en el enlace "Download UVL"
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Download UVL"))
            )
            download_link.click()

            # Verificar que el archivo se descargó correctamente
            time.sleep(5)  # Espera breve para la descarga
            downloaded_files = os.listdir(self.download_dir)
            assert len(downloaded_files) > 0, "No se descargó ningún archivo."
            print("Archivo descargado correctamente:", downloaded_files[0])

        except Exception as e:
            # Captura de pantalla en caso de error
            self.driver.save_screenshot("error_screenshot.png")
            print(f"Se produjo un error durante el test: {e}")
            raise

from core.selenium.common import initialize_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class TestTagCloud:
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.driver.set_window_size(1920, 1048)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_search_feature(self):
        self.driver.get("http://127.0.0.1:5000/")

        # Esperar la presencia del botón "Explore more datasets"
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Explore more datasets"))
        )

        # Si el clic normal falla, usar clic forzado con JavaScript
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

        # Interactuar con otros elementos después de hacer clic
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "tag2"))
        ).click()

        search_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "searchInput"))
        )
        search_input.click()
        search_input.send_keys("11")
        search_input.send_keys(Keys.ENTER)

    def test_visualize_tag(self):
        self.driver.get("http://127.0.0.1:5000/")

        # Haz clic en "Explore more datasets"
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Explore more datasets"))
        )
        self.driver.execute_script("arguments[0].click();", element)

        # Haz clic en el enlace "tag1"
        tag1_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "tag1"))
        )
        self.driver.execute_script("arguments[0].click();", tag1_link)

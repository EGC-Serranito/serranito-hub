from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initialize_driver():
    driver = webdriver.Chrome()
    return driver


class TestSelenium:
    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_selenium(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1920, 1048)

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".sidebar-item:nth-child(6) .align-middle:nth-child(2)"))
        ).click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".custom-buttons > .btn:nth-child(1)"))
        ).click()

        dropdown = self.driver.find_element(By.ID, "data-type")
        dropdown.find_element(By.XPATH, "//option[. = 'Visualizaciones por autor']").click()
        self.driver.find_element(By.CSS_SELECTOR, "#data-type > option:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)").click()
        dropdown = self.driver.find_element(By.ID, "views-filter")
        dropdown.find_element(By.XPATH, "//option[. = 'Mes']").click()
        self.driver.find_element(By.CSS_SELECTOR, "#views-filter > option:nth-child(2)").click()
        self.driver.find_element(By.ID, "views-filter").click()
        dropdown = self.driver.find_element(By.ID, "views-filter")
        dropdown.find_element(By.XPATH, "//option[. = 'Año']").click()
        self.driver.find_element(By.CSS_SELECTOR, "option:nth-child(3)").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(4)").click()

# Generated by Selenium IDE
from core.selenium.common import initialize_driver
from selenium.webdriver.common.by import By


class TestTestselenium:
    def setup_method(self):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_uvl_selenium(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1920, 1043)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".sidebar-item:nth-child(8) .align-middle:nth-child(2)"
        ).click()
        self.driver.find_element(By.ID, "myDropzone").click()
        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "desc").click()
        self.driver.find_element(By.ID, "title").click()
        self.driver.find_element(By.ID, "title").send_keys("Título de archivo UVL I")
        self.driver.find_element(By.ID, "desc").click()
        self.driver.find_element(By.ID, "desc").send_keys(
            "Esta es una descripción para este archivo UVL"
        )

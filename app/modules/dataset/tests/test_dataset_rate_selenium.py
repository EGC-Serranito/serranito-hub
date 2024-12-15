from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.selenium.common import initialize_driver


class TestTestdatasetrateselenium:
    def setup_method(self):
        self.driver = initialize_driver()
        self.driver.implicitly_wait(10)

    def teardown_method(self):
        self.driver.quit()

    def test_testdatasetrateselenium(self):
        self.driver.get("http://localhost:5000/")
        self.driver.set_window_size(945, 1016)

        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()

        dropdown = self.driver.find_element(By.ID, "rating-select")
        dropdown.find_element(By.XPATH, "//option[. = '2']").click()

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary:nth-child(3)").click()

        WebDriverWait(self.driver, 10).until(EC.alert_is_present())

        alert = self.driver.switch_to.alert
        assert alert.text == "Rating sent successfully"

        alert.accept()

from selenium.webdriver.common.by import By
from core.selenium.common import initialize_driver


class TestSeleniumprofileuser:
    def setup_method(self): 
        self.driver = initialize_driver()
        self.driver.implicitly_wait(10)

    def teardown_method(self):
        self.driver.quit()

    def test_selenium_profile_user(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1048)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(
            By.CSS_SELECTOR, ".row:nth-child(3) > .col-md-6"
        ).click()
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
        self.driver.find_element(By.LINK_TEXT, "Doe, Jane").click()
        self.driver.find_element(By.LINK_TEXT, "tag1").click()
        self.driver.find_element(By.LINK_TEXT, "tag2").click()
        self.driver.find_element(By.LINK_TEXT, "tag2").click()
        self.driver.find_element(By.ID, "reset-button").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Sample dataset 3").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(4) a").click()

    def test_selenium_view_user_profile_log_out(self):
      self.driver.get("http://127.0.0.1:5000/")
      self.driver.set_window_size(1702, 1073)
      self.driver.find_element(By.LINK_TEXT, "Sample dataset 4").click()
      self.driver.find_element(By.LINK_TEXT, "Doe, Jane").click()
      self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(2) > .col-md-6 > .mb-3").click()
      self.driver.find_element(By.ID, "email").click()
      self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
      self.driver.find_element(By.ID, "password").click()
      self.driver.find_element(By.ID, "password").send_keys("1234")
      self.driver.find_element(By.ID, "submit").click()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestEditprofile():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_editprofile(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1011)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(2) > .col-md-6").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row:nth-child(3) > .col-md-6").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-check-label").click()
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, ".nav-link > span").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Edit profile"))
        ).click()
        self.driver.find_element(By.ID, "surname").click()
        self.driver.find_element(By.ID, "surname").send_keys("DoeModed")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(1)").click()
        WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable((By.LINK_TEXT, "My profile"))
        ).click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(1)").click()
        WebDriverWait(self.driver, 10).until(
          EC.element_to_be_clickable((By.LINK_TEXT, "Edit profile"))
        ).click()
        self.driver.find_element(By.ID, "surname").click()
        self.driver.find_element(By.ID, "surname").clear()
        self.driver.find_element(By.ID, "surname").send_keys("Doe")
        self.driver.find_element(By.ID, "submit").click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Doe, John"))
        ).click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Log out"))
        ).click()

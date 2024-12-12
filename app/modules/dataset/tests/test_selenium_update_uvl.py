# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class TestSeleniumupdateuvl:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_seleniumupdateuvl(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1300, 699)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()
        self.driver.find_element(By.ID, "dataset-133").click()
        self.driver.find_element(By.ID, "open-edit-file").click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "file-edit-modal"))
        )
        self.driver.find_element(By.ID, "file-edit-modal").click()
        element = self.driver.find_element(By.ID, "fileEditContent")
        self.driver.execute_script(
            "if(arguments[0].contentEditable === 'true') {arguments[0].innerText = 'features\\n    Chat\\n\\n'}",
            element,
        )
        self.driver.find_element(By.ID, "file-edit-buttom").click()
        self.driver.find_element(By.CSS_SELECTOR, ".col-12 > .row:nth-child(2)").click()
        self.driver.find_element(By.ID, "publication_doi").clear()

        checkbox = self.driver.find_element(By.ID, "agree-checkbox")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)

        # Optionally: Perform a click using ActionChains to avoid interference
        actions = ActionChains(self.driver)
        actions.move_to_element(checkbox).click().perform()

        # Or ensure it is clickable using WebDriverWait
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.ID, "agree-checkbox"))
        )
        checkbox.click()

        upload_button = self.driver.find_element(By.ID, "upload_button")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", upload_button)

        # Optionally: Perform a click using ActionChains to avoid interference
        actions = ActionChains(self.driver)
        actions.move_to_element(upload_button).click().perform()

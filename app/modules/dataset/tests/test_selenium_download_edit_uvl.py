# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestSeleniumdownloadedituvl:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_seleniumupdateuvl(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1300, 699)
        self.driver.find_element(By.ID, "dataset-133").click()
        self.driver.find_element(By.ID, "open-edit-file").click()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "file-edit-content-modal"))
        )
        self.driver.find_element(By.ID, "file-edit-content-modal").click()
        element = self.driver.find_element(By.ID, "fileEditContent")
        self.driver.execute_script(
            "if(arguments[0].contentEditable === 'true') {arguments[0].innerText = 'features\\n    Chat\\n'}",
            element,
        )
        self.driver.find_element(By.ID, "downloadEditButton").click()

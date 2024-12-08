from core.selenium.common import initialize_driver
from selenium.webdriver.common.by import By


class TestDownloaddall:
    def setup_method(self):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_download_all_datasets_from_navbar(self):
        self.driver.get("http://localhost:5000/")
        self.driver.find_element(By.LINK_TEXT, "Download all datasets!").click()

    def test_download_all_datasets_from_download_page(self):
        self.driver.get("http://localhost:5000/download")
        self.driver.set_window_size(809, 961)
        self.driver.find_element(By.LINK_TEXT, "Download all datasets").click()

    def test_download_datasets_with_date_range(self):
        self.driver.get("http://localhost:5000/download")
        self.driver.set_window_size(809, 961)
        self.driver.find_element(By.ID, "start_date").click()
        self.driver.find_element(By.ID, "start_date").send_keys("0001-01-01")
        self.driver.find_element(By.ID, "start_date").send_keys("0019-01-01")
        self.driver.find_element(By.ID, "start_date").send_keys("0190-01-01")
        self.driver.find_element(By.ID, "start_date").send_keys("1900-01-01")
        self.driver.find_element(By.ID, "end_date").click()
        self.driver.find_element(By.ID, "end_date").send_keys("0002-01-01")
        self.driver.find_element(By.ID, "end_date").send_keys("0020-01-01")
        self.driver.find_element(By.ID, "end_date").send_keys("0206-01-01")
        self.driver.find_element(By.ID, "end_date").send_keys("2060-01-01")
        self.driver.find_element(By.CSS_SELECTOR, ".mb-1").click()

    def test_download_datasets_by_email(self):
        self.driver.get("http://localhost:5000/download")
        self.driver.set_window_size(809, 961)
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.CSS_SELECTOR, ".mt-4").click()

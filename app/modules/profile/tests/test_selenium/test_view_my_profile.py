from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.selenium.common import initialize_driver


class TestViewMyProfile:

    def setup_method(self, method):
        self.driver = initialize_driver()
        self.vars = {}

    def teardown_method(self):
        self.driver.quit()

    def test_viewMyProfile(self):
        self.driver.get("http://127.0.0.1:5000/")
        self.driver.set_window_size(1854, 1011)

        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.ID, "email").send_keys("user1@example.com")
        self.driver.find_element(By.ID, "password").send_keys("1234")
        self.driver.find_element(By.ID, "submit").click()

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.LINK_TEXT, "Doe, John"))
        )
        self.driver.find_element(By.LINK_TEXT, "Doe, John").click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "My profile"))
        )
        self.driver.find_element(By.LINK_TEXT, "My profile").click()

        name = self.driver.find_element(By.XPATH, "//div[@class='card-body']//p[contains(., 'Name:')]").text
        name = name.replace("Name:", "").strip()  # Eliminar "Name:" y espacios extra
        assert name == "John", f"Expected 'John' but got {name}"

        surname = self.driver.find_element(By.XPATH, "//div[@class='card-body']//p[contains(., 'Surname:')]").text
        surname = surname.replace("Surname:", "").strip()  # Eliminar "Surname:" y espacios extra
        assert surname == "Doe", f"Expected 'Doe' but got {surname}"

        affiliation = self.driver.find_element(By.XPATH, "//div[@class='card-body']//p[contains(., 'Affiliation:')]").text
        affiliation = affiliation.replace("Affiliation:", "").strip()  # Eliminar "Affiliation:" y espacios extra
        assert affiliation == "Some University", f"Expected 'Some University' but got {affiliation}"

        email = self.driver.find_element(By.XPATH, "//div[@class='card-body']//p[contains(., 'Email:')]").text
        email = email.replace("Email:", "").strip()  # Eliminar "Email:" y espacios extra
        assert email == "user1@example.com", f"Expected 'user1@example.com' but got {email}"

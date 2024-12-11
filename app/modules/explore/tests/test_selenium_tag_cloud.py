import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os


class TestSeleniumTagCloud:

    def setup_method(self, method):
        """Initial setup for each test."""
        # Browser options configuration
        chrome_options = Options()
        download_dir = os.path.abspath(
            "temp_downloads"
        )  # Temporary folder for downloads
        os.makedirs(download_dir, exist_ok=True)
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
            },
        )
        self.download_dir = download_dir
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(1854, 1048)

    def teardown_method(self, method):
        """Cleanup after each test."""
        self.driver.quit()
        # Remove downloaded files
        for root, _, files in os.walk(self.download_dir):
            for file in files:
                os.remove(os.path.join(root, file))

    def test_selenium_tag_cloud(self):
        """Test to verify the functionality of the tag cloud in the application."""
        try:
            # Navigate to the main page
            self.driver.get("http://127.0.0.1:5000/")

            # Wait and click on the sidebar option
            sidebar_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        ".sidebar-item:nth-child(3) .align-middle:nth-child(2)",
                    )
                )
            )
            sidebar_option.click()

            # Wait and click on a specific tag
            tag = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "tag1"))
            )
            tag.click()

            # Wait for the list of related models
            feature_model_item = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".list-group-item"))
            )

            # Interact with the options button of the first model
            options_button = feature_model_item.find_element(
                By.CSS_SELECTOR, ".options-btn"
            )
            options_button.click()

            # Wait for the options to be visible
            options_container = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#options-99"))
            )

            # Click on the Export dropdown menu
            dropdown_toggle = options_container.find_element(
                By.CSS_SELECTOR, ".btn-outline-success.dropdown-toggle"
            )
            dropdown_toggle.click()

            # Click on the "Download UVL" link
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Download UVL"))
            )
            download_link.click()

            # Click on the Export dropdown menu
            dropdown_toggle = options_container.find_element(
                By.CSS_SELECTOR, ".btn-outline-success.dropdown-toggle"
            )
            dropdown_toggle.click()

            # Click on the "Glencoe Format" link
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Glencoe Format"))
            )
            download_link.click()

            # Click on the Export dropdown menu
            dropdown_toggle = options_container.find_element(
                By.CSS_SELECTOR, ".btn-outline-success.dropdown-toggle"
            )
            dropdown_toggle.click()

            # Click on the "DIMACS Format" link
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "DIMACS Format"))
            )
            download_link.click()

            # Click on the Export dropdown menu
            dropdown_toggle = options_container.find_element(
                By.CSS_SELECTOR, ".btn-outline-success.dropdown-toggle"
            )
            dropdown_toggle.click()

            # Click on the "SPLOT Format" link
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "SPLOT Format"))
            )
            download_link.click()

            # Verify that the file was downloaded correctly
            time.sleep(5)  # Brief wait for the download
            downloaded_files = os.listdir(self.download_dir)
            assert len(downloaded_files) > 0, "No file was downloaded."
            print("File downloaded successfully:", downloaded_files[0])

        except Exception as e:
            print(f"An error occurred during the test: {e}")
            raise

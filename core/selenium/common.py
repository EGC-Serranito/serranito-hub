from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def initialize_driver():
    # Initializes the browser options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Initialise the browser using WebDriver Manager
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def close_driver(driver):
    driver.quit()

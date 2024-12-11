from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import initialize_driver, close_driver


def execute_bot_test(driver):
    """
    Ejecución de la prueba del bot con WebDriverWait.
    """
    try:
        wait = WebDriverWait(driver, 10)

        driver.get(get_host_for_selenium_testing())
        driver.set_window_size(1854, 1048)

        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()

        wait.until(EC.presence_of_element_located((By.ID, "email"))).click()
        driver.find_element(By.ID, "password").send_keys("1234")
        driver.find_element(By.ID, "email").send_keys("user1@example.com")
        driver.find_element(By.ID, "submit").click()

        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Bot Configuration"))).click()

        wait.until(EC.presence_of_element_located((By.ID, "features-selection"))).click()
        dropdown = wait.until(EC.presence_of_element_located((By.ID, "features-selection")))
        dropdown.find_element(By.XPATH, "//option[. = '@uvlhub_telegram1']").click()

        driver.find_element(By.CSS_SELECTOR, "option:nth-child(2)").click()
        driver.find_element(By.ID, "submit").click()

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#tree > .node > label"))).click()
        driver.find_element(By.CSS_SELECTOR, ".children label").click()
        driver.find_element(By.ID, "name").click()
        driver.find_element(By.ID, "name").send_keys("1959498857")
        driver.find_element(By.CSS_SELECTOR, ".form-container:nth-child(2) #submit").click()

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#tree > .node > .children > .node > .children > .node > label")
        )).click()

        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#tree > .node > .children > .node > .children > .node > .children > .node > label")
        )).click()

        driver.find_element(By.CSS_SELECTOR, ".run-btn").click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".stop-btn"))).click()

    except TimeoutException as te:
        print(f"Error de tiempo de espera: {te}")
        raise
    except Exception as e:
        print(f"Error en la ejecución del bot: {e}")
        raise


def test_bot_configuration():
    """
    Prueba principal: Configuración del bot.
    """
    driver = None
    try:
        driver = initialize_driver()
        execute_bot_test(driver)
    except Exception as e:
        print(f"Error durante la prueba: {e}")
    finally:
        close_driver(driver)


test_bot_configuration()

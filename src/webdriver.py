from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def setup_driver():
    """
    Sets up the Selenium WebDriver with Chrome options.

    Returns:
        driver: Configured Selenium WebDriver instance.
    """
    # Set up the Chrome WebDriver service
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(), options=options)
    return driver
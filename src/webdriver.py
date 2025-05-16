from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from swiftshadow.classes import ProxyInterface

# Fetch HTTPS proxies from the US
def fetch_https_proxies():
    """
    Fetches HTTPS proxies from the US using SwiftShadow.

    Returns:
        list: A list of HTTPS proxy URLs.
    """
    # Initialize the ProxyInterface with US country and HTTPS protocol
    swift = ProxyInterface(countries=["US"], protocol="https")
    return swift.get().as_list()


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

if __name__ == "__main__":
    # Example usage
    proxies = fetch_https_proxies()
    print("Fetched HTTPS Proxies:", proxies)

    driver = setup_driver()
    print("WebDriver set up successfully.")
    driver.quit()
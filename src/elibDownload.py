import time
import os
import urllib.parse
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Function to extract contractor details from a given link
def get_contractor_details(driver, link):
    """
    Extracts contractor details from the given link using Selenium.

    Args:
        driver: Selenium WebDriver instance.
        link: URL of the contractor details page.

    Returns:
        A dictionary containing contractor details or None if extraction fails.
    """
    try:
        driver.get(link)
        details = {}

        # Extract data from the first table (Contractor Details)
        details['Contract Number'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Contract #:')]]/following-sibling::td/font").text.strip()
        details['Contractor'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Contractor:')]]/following-sibling::td/font").text.strip()
        details['Address'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Address:')]]/following-sibling::td/font").get_attribute("innerHTML").replace("<br>", ", ").strip()
        details['Phone'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Call:')]]/following-sibling::td/font").text.strip()
        details['Email'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Email:')]]/following-sibling::td/font/a").text.strip()
        details['Web Address'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Web Address:')]]/following-sibling::td/font/a").get_attribute("href").strip()
        details['SAM UEI'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'SAM UEI:')]]/following-sibling::td/font").text.strip()
        details['NAICS'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'NAICS:')]]/following-sibling::td/font").text.strip()
        details['Socio-Economic'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Socio-Economic :')]]/following-sibling::td/font").get_attribute("innerHTML").replace("<br>", ", ").strip()
        details['Current Option Period End Date'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Current Option Period End Date :')]]/following-sibling::td/font").text.strip()
        details['Ultimate Contract End Date'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Ultimate Contract End Date :')]]/following-sibling::td/font").text.strip()

        # Extract data from the second table (Govt. POC and Links)
        details['Govt. POC Name'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Govt. POC:')]]/font[2]").text.strip()
        details['Govt. POC Phone'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Govt. POC:')]]/font[3]").text.strip()
        details['Govt. POC Email'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Govt. POC:')]]/font[4]/a").text.strip()
        details['Terms & Conditions Link'] = driver.find_element(By.XPATH, "//button[contains(@title, 'view Contractors Terms & Conditions')]/@onclick").get_attribute("onclick").split("'")[1]
        details['Contract Clauses Link'] = driver.find_element(By.XPATH, "//font[contains(text(), 'Contract Clauses/Exceptions:')]/following-sibling::a").get_attribute("href").strip()
        details['EPLS Status'] = driver.find_element(By.XPATH, "//td[font[contains(text(), 'EPLS :')]]/following-sibling::td/font").text.strip()

        print(f"Details extracted for {details['Contractor']}:")
        return details
    except Exception as e:
        print(f"Error extracting details for link: {link}\n{e}")
        return None

# Main function to scrape contractor details
def scrape_contractors(test_mode=False):
    """
    Scrapes contractor details for all letters A-Z.

    Args:
        test_mode: If True, adds a delay between requests for testing purposes.
    """
    missing_terms = []
    error_links = []

    # Set up the Selenium WebDriver
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    # Iterate through all letters A-Z
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        try:
            url = f"https://www.gsaelibrary.gsa.gov/ElibMain/contractorList.do?contractorListFor={letter}"
            try:
                driver.get(url)
            except WebDriverException as e:
                if "dnsNotFound" in str(e):
                    print(f"DNS resolution issue for URL: {url}. Skipping...")
                    continue
                else:
                    raise e  # Re-raise the exception if it's not a DNS issue

            # Find all contractor links on the page
            elems = driver.find_elements(By.XPATH, "//a[@href]")
            links = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href")[:58] == 'https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do']

            # Process each contractor link
            for link in links:
                try:
                    driver.get(link)
                    contractor = urllib.parse.unquote(link.split('contractorName=')[-1].split('&')[0])
                    info = get_contractor_details(driver, link)
                    if not info:
                        print(f"Failed to extract details for {contractor}. Skipping...")
                        missing_terms.append(contractor.replace('+', ' '))
                    if test_mode:
                        time.sleep(3)  # Add delay for testing
                except TimeoutException:
                    print(f"Timeout while navigating to {link}. Skipping...")
                    error_links.append(contractor.replace('+', ' '))
                    continue
                except WebDriverException as e:
                    if "dnsNotFound" in str(e):
                        print(f"DNS resolution or Invalid URL issue for link: {link}. Skipping...")
                        error_links.append(contractor.replace('+', ' '))
                        continue
                    else:
                        raise e  # Re-raise the exception if it's not a DNS issue
        except Exception as e:
            print("Error:", e)
            traceback.print_exc()

    # Save missing terms and error links to Excel files
    pd.DataFrame(missing_terms).to_excel("No_Terms.xlsx", index=False)
    pd.DataFrame(error_links).to_excel("Error_Links.xlsx", index=False)

    driver.quit()

# Run the scraper
if __name__ == "__main__":
    # Set test_mode=True for testing with delays, False for production
    scrape_contractors(test_mode=True)
    
    """GitHub Copilot
The most precise way to identify an element in Selenium is to use a unique selector that directly targets the element you want to grab. Here are some strategies to make your element identification as precise as possible:

1. Use Unique id or name Attributes
If the element has a unique id or name attribute, these are the most reliable selectors.

Example:
2. Use Specific XPath
If the element does not have a unique id or name, use an XPath that uniquely identifies the element. Avoid overly generic XPath expressions and instead target specific attributes or structure.

Tips for Precise XPath:
Target Specific Attributes: Use attributes like @class, @title, @data-*, or any other unique attribute.

Use Text Content: If the element has unique text, you can use text() or contains(text(), ...).

Navigate Relative to Other Elements: Use following-sibling, parent, or ancestor to locate elements relative to others.

Avoid Overly Broad Selectors: Avoid  or  without narrowing it down with attributes or structure.

3. Use CSS Selectors
CSS selectors are often faster than XPath and can be very precise if the element has unique classes or attributes.

Example:
Tips for Precise CSS Selectors:
Use #id for unique IDs:

Use .class for classes:

Combine attributes:

Use nth-child or nth-of-type for specific elements in a list:

4. Use WebDriverWait with Conditions
Sometimes elements take time to load. Use WebDriverWait to wait for the element to be present or visible before interacting with it.

Example:
5. Inspect the DOM for Unique Identifiers
Use your browser's developer tools (right-click > Inspect) to analyze the DOM structure. Look for:

Unique id or name attributes.
Specific class names or data-* attributes.
Text content that uniquely identifies the element.
6. Test Your Selector
Before using the selector in your script, test it in the browser's developer tools:

Open the browser's console.
Use document.querySelector for CSS selectors or $x for XPath to verify your selector works.
Example:
7. Fallback for Dynamic Elements
If the element's attributes or structure change dynamically:

Use contains() in XPath to match partial text or attributes.
Use starts-with() or ends-with() for dynamic attribute values.
Example:
8. Use try-except for Missing Elements
If the element might not always be present, wrap the lookup in a try-except block to handle errors gracefully.

Example:
Summary
The most precise way to identify an element depends on the structure of the page:

Prefer id or name attributes if available.
Use specific XPath or CSS Selectors targeting unique attributes or structure.
Test your selector in the browser's developer tools.
Use WebDriverWait to handle dynamic loading.
By following these strategies, you can reliably and precisely locate the elements you need.
    """
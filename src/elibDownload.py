import csv
import os
import time
import traceback
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

import settings
import webdriver

driver = webdriver.setup_driver()

def get_element_text(driver, xpath, attr=None, all_text=False, join_str=" | "):
    """
    Extracts text or attribute value(s) from element(s) located by the given XPath.

    Args:
        driver: Selenium WebDriver instance.
        xpath: XPath string to locate the element(s).
        attr: Optional attribute name to extract (e.g., "href"). If None, extracts text.
        all_text: If True, returns all matching elements' text/attr as a list (or joined string).
        join_str: String to join all texts if all_text is True and you want a single string.

    Returns:
        The extracted text/attribute value, a list of them, or None if not found.
    """
    try:
        if all_text:
            elements = driver.find_elements(By.XPATH, xpath)
            results = []
            for elem in elements:
                if attr:
                    val = elem.get_attribute(attr)
                else:
                    val = elem.text
                if val:
                    results.append(val.strip())
            return join_str.join(results) if results else None
        else:
            element = driver.find_element(By.XPATH, xpath)
            if attr:
                return element.get_attribute(attr).strip()
            return element.text.strip()
    except Exception:
        return None


def append_to_csv(details, output_file="contractor_data.csv"):
    """
    Saves contractor details to a CSV file. Appends to the file if it already exists.

    Args:
        details: Dictionary containing contractor details.
        output_file: Name of the CSV file to save the data.
    """
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=details.keys())
        if not file_exists:
            writer.writeheader()  # Write header only if the file is new
        writer.writerow(details)  # Append the contractor details


def get_contractor_details(driver, link):
    """
    Extracts detailed information about a contractor from the given link.

    Args:
        driver: Selenium WebDriver instance.
        link: URL of the contractor details page.

    Returns:
        A dictionary containing contractor details, or None if an error occurs.
    """
    try:
        driver.get(link)  # Navigate to the contractor details page

        # Extract contractor details using helper function
        details = {
            "URL": link,
            "Contract Number": get_element_text(
                driver,
                settings.CONTRACT_NUMBER_XPATH,
            ),
            "Contractor": get_element_text(
                driver,
                settings.CONTRACTOR_XPATH,
            ),
            "Address": get_element_text(
                driver,
                settings.ADDRESS_XPATH,
                attr="innerHTML",
            ),
            "Phone": get_element_text(
                driver,
                settings.PHONE_XPATH,
            ),
            "Email": get_element_text(
                driver,
                settings.EMAIL_XPATH,
            ),
            "Web Address": get_element_text(
                driver,
                settings.WEB_ADDRESS_XPATH,
                attr="href",
            ),
            "SAM UEI": get_element_text(
                driver,
                settings.SAM_UEI_XPATH,
            ),
            "NAICS": get_element_text(
                driver,
                settings.NAICS_XPATH,
            ),
            "Current Option Period End Date": get_element_text(
                driver,
                settings.OPTION_XPATH,
            ),
            "Ultimate Contract End Date": get_element_text(
                driver,
                settings.ULTIMATE_XPATH,
            ),
            "Contract Officer": get_element_text(
                driver,
                settings.CONTRACT_OFFICER_XPATH,
            ),
            "SINS": get_element_text(
                driver,
                settings.SIN_XPATH,
                all_text=True,
            ),
            "Source": get_element_text(
                driver,
                settings.SOURCE_XPATH,
            ),
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Extract additional details (e.g., Terms & Conditions link)
        try:
            onclick_attr = driver.find_element(
                By.XPATH,
                "//button[contains(@title, 'view Contractors Terms & Conditions')]",
            ).get_attribute("onclick")
            details["Terms & Conditions Link"] = (
                onclick_attr.split("'")[1] if onclick_attr else None
            )
        except Exception:
            details["Terms & Conditions Link"] = None

        return details
    except Exception as e:
        print(f"Error extracting details for link: {link}\n{e}")
        traceback.print_exc()
        return None


def process_contractor_link(driver, link):
    """
    Worker function to process a single contractor link.

    Args:
        driver: Selenium WebDriver instance.
        link: URL of the contractor details page.

    Returns:
        None
    """
    try:
        contractor = urllib.parse.unquote(
            link.split("contractorName=")[-1].split("&")[0]
        )
        info = get_contractor_details(driver, link)
        if info:
            append_to_csv(info)  # Save the extracted details
            print(f"Saved details for {info["Contractor"]} to CSV.")
        else:
            empty_url = {
                "URL": link,
                "Contractor": contractor,
            }
            append_to_csv(empty_url)  # Save the link with contractor name only

    except TimeoutException:
        print(f"Timeout while navigating to {link}. Skipping...")
        return link
    except WebDriverException as e:
        if "dnsNotFound" in str(e):
            print(f"DNS or invalid URL issue for link: {link}. Skipping...")
            return link
        else:
            raise e  # Re-raise the exception if it's not a DNS issue
    return


def scrape_contractors(test_mode=True):
    """
    Scrapes contractor details for all letters A-Z and saves them to a CSV file.

    Args:
        test_mode: If True, adds a delay between requests for testing purposes.
    """
    # Iterate through all letters A-Z
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        try:
            url = f"{settings.BASE_URL}{letter}"
            try:
                driver.get(url)  # Navigate to the contractor list page
            except WebDriverException as e:
                if "dnsNotFound" in str(e):
                    print(f"DNS resolution issue for URL: {url}. Skipping...")
                    continue
                else:
                    raise e  # Re-raise the exception if it's not a DNS issue

            # Extract all contractor links from the page
            elems = driver.find_elements(By.XPATH, "//a[@href]")
            links = [
                elem.get_attribute("href")
                for elem in elems
                if elem.get_attribute("href") is not None
                and elem.get_attribute("href").startswith(
                    "https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do"
                )
            ]

            if test_mode:
                links = links[:5]  # Limit to first 5 links for testing
                # Process links sequentially in test mode
                for link in links:
                    process_contractor_link(driver, link)
                    time.sleep(3)  # Add delay for testing
            else:
                # Use multithreading in production mode
                with ThreadPoolExecutor(
                    max_workers=5
                ) as executor:  # Adjust max_workers as needed
                    futures = {
                        executor.submit(process_contractor_link, driver, link): link
                        for link in links
                    }
                    for future in as_completed(futures):
                        future.result()
            if test_mode:
                print(f"Processed {len(links)} links for letter {letter}.")

        except Exception as e:
            print("Error:", e)
            traceback.print_exc()

    driver.quit()  # Close the WebDriver


if __name__ == "__main__":
    # Set test_mode=True for testing with delays, False for production
    scrape_contractors(test_mode=True)

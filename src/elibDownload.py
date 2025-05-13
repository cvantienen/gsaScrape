import time
import csv
import os
import urllib.parse
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


def get_element_text(driver, xpath, attr=None):
    try:
        element = driver.find_element(By.XPATH, xpath)
        if attr:
            return element.get_attribute(attr).strip()
        return element.text.strip()
    except Exception:
        return None


def save_contractor_details(details, output_file="contractor_data.csv"):
    file_exists = os.path.isfile(output_file)
    with open(output_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=details.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(details)


def get_contractor_details(driver, link):
    try:
        driver.get(link)
        details = {
            'Contract Number': get_element_text(driver, "//td[font[contains(text(), 'Contract #:')]]/following-sibling::td/font"),
            'Contractor': get_element_text(driver, "//td[font[contains(text(), 'Contractor:')]]/following-sibling::td/font"),
            'Address': get_element_text(driver, "//td[font[contains(text(), 'Address:')]]/following-sibling::td/font", attr="innerHTML").replace("<br>", ", ") if get_element_text(driver, "//td[font[contains(text(), 'Address:')]]/following-sibling::td/font", attr="innerHTML") else None,
            'Phone': get_element_text(driver, "//td[font[contains(text(), 'Call:')]]/following-sibling::td/font"),
            'Email': get_element_text(driver, "//td[font[contains(text(), 'Email:')]]/following-sibling::td/font/a"),
            'Web Address': get_element_text(driver, "//td[font[contains(text(), 'Web Address:')]]/following-sibling::td/font/a", attr="href"),
            'SAM UEI': get_element_text(driver, "//td[font[contains(text(), 'SAM UEI:')]]/following-sibling::td/font"),
            'NAICS': get_element_text(driver, "//td[font[contains(text(), 'NAICS:')]]/following-sibling::td/font"),
            'Socio-Economic': get_element_text(driver, "//td[font[contains(text(), 'Socio-Economic :')]]/following-sibling::td/font", attr="innerHTML").replace("<br>", ", ") if get_element_text(driver, "//td[font[contains(text(), 'Socio-Economic :')]]/following-sibling::td/font", attr="innerHTML") else None,
            'Current Option Period End Date': get_element_text(driver, "//td[font[contains(text(), 'Current Option Period End Date :')]]/following-sibling::td/font"),
            'Ultimate Contract End Date': get_element_text(driver, "//td[font[contains(text(), 'Ultimate Contract End Date :')]]/following-sibling::td/font"),
            'Govt. POC Name': get_element_text(driver, "//td[font[contains(text(), 'Govt. POC:')]]/font[2]"),
            'Govt. POC Phone': get_element_text(driver, "//td[font[contains(text(), 'Govt. POC:')]]/font[3]"),
            'Govt. POC Email': get_element_text(driver, "//td[font[contains(text(), 'Govt. POC:')]]/font[4]/a"),
            'Contract Clauses Link': get_element_text(driver, "//font[contains(text(), 'Contract Clauses/Exceptions:')]/following-sibling::a", attr="href"),
            'EPLS Status': get_element_text(driver, "//td[font[contains(text(), 'EPLS :')]]/following-sibling::td/font")
        }

        try:
            onclick_attr = driver.find_element(By.XPATH, "//button[contains(@title, 'view Contractors Terms & Conditions')]").get_attribute("onclick")
            details['Terms & Conditions Link'] = onclick_attr.split("'")[1] if onclick_attr else None
        except Exception:
            details['Terms & Conditions Link'] = None

        print(f"Details extracted for {details['Contractor'] or 'Unknown Contractor'}")
        return details
    except Exception as e:
        print(f"Error extracting details for link: {link}\n{e}")
        traceback.print_exc()
        return None


def scrape_contractors(test_mode=False):
    missing_terms = []
    error_links = []
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

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
                    raise e

            elems = driver.find_elements(By.XPATH, "//a[@href]")
            links = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href").startswith("https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do")]

            for link in links:
                try:
                    driver.get(link)
                    contractor = urllib.parse.unquote(link.split('contractorName=')[-1].split('&')[0])
                    info = get_contractor_details(driver, link)
                    if info:
                        save_contractor_details(info)
                    else:
                        print(f"Failed to extract details for {contractor}. Skipping...")
                        missing_terms.append(contractor.replace('+', ' '))
                    if test_mode:
                        time.sleep(3)
                except TimeoutException:
                    print(f"Timeout while navigating to {link}. Skipping...")
                    error_links.append(link)
                    continue
                except WebDriverException as e:
                    if "dnsNotFound" in str(e):
                        print(f"DNS or invalid URL issue for link: {link}. Skipping...")
                        error_links.append(link)
                        continue
                    else:
                        raise e
        except Exception as e:
            print("Error:", e)
            traceback.print_exc()

    pd.DataFrame(missing_terms, columns=["Missing Contractor"]).to_excel("No_Terms.xlsx", index=False)
    pd.DataFrame(error_links, columns=["Error Links"]).to_excel("Error_Links.xlsx", index=False)
    driver.quit()


if __name__ == "__main__":
    scrape_contractors(test_mode=True)
  
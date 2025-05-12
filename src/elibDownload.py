import time
import os
import urllib.parse
import re
import pandas as pd
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


def get_contractor_details(driver, link):
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

        # Extract data from the third table (Additional Details) and flatten it
        additional_details_table = driver.find_elements(By.XPATH, "//table[@cellspacing='0' and @cellpadding='2' and @border='1']/tbody/tr")

        for i, row in enumerate(additional_details_table[1:], start=1):  # Skip the header row
            cells = row.find_elements(By.XPATH, ".//td")
            details["Source"] = cells[0].text.strip()
            details["Title"] = cells[1].text.strip()
            details["Contract Number"] = cells[2].text.strip()
            details["Terms & Conditions Link"] = (
                cells[3].find_element(By.XPATH, ".//button").get_attribute("onclick").split("'")[1]
                if cells[3].find_elements(By.XPATH, ".//button") else None
            )
            details["Current Option Period End Date"] = cells[4].text.strip()
            details["Ultimate Contract End Date"] = cells[5].text.strip()
            details["Category"] = cells[6].text.strip()
            details["View Catalog Link"] = (
                cells[8].find_element(By.XPATH, ".//a").get_attribute("href")
                if cells[8].find_elements(By.XPATH, ".//a") else None
            )
        print(f"Details extracted for {details['Contractor']}:")
        return details
    except Exception as e:
        print(f"Error extracting details for link: {link}\n{e}")
        return None

missingTerms = []
errorlink = []
driver = webdriver.Firefox()

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
        time.sleep(5)
        elems = driver.find_elements(By.XPATH, "//a[@href]")
        links = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href")[:58] == 'https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do']
        for link in links:
            try:
                driver.get(link)
                contractor = urllib.parse.unquote(link.split('contractorName=')[-1].split('&')[0])
                info = get_contractor_details(driver, link)
                if not info:
                    print(f"Failed to extract details for {contractor}. Skipping...")
                    missingTerms.append(contractor.replace('+', ' '))
                time.sleep(5)
            except TimeoutException:
                print(f"Timeout while navigating to {link}. Skipping...")
                errorlink.append(contractor.replace('+', ' '))
                continue
            except WebDriverException as e:
                if "dnsNotFound" in str(e):
                    print(f"DNS resolution or Invalid Url issue for link: {link}. Skipping...")
                    errorlink.append(contractor.replace('+', ' '))
                    continue
                else:
                    raise e  # Re-raise the exception if it's not a DNS issue
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()

driver.quit()
pd.DataFrame(missingTerms).to_excel("No_Terms.xlsx", index=False)
pd.DataFrame(errorlink).to_excel("Error_Links.xlsx", index=False)
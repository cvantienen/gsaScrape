from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import urllib.parse
import time
import traceback

def get_contractor_data(driver, starting_letter):
    data = []
    try:
        letter = starting_letter.upper()
        driver.get(f"https://www.gsaelibrary.gsa.gov/ElibMain/contractorList.do?contractorListFor={letter}")
        time.sleep(5)

        elems = driver.find_elements(By.XPATH, "//a[@href]")
        links = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href")[:58] == 'https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do']

        for link in links:
            driver.get(link)
            time.sleep(3)  # Allow the page to load

            # Extract contractor details
            contractor_name = driver.find_element(By.XPATH, "//h1").text
            address = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Address:')]]/following-sibling::td/font").text
            phone = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Call:')]]/following-sibling::td/font").text
            email = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Email:')]]/following-sibling::td/font/a").text
            naics = driver.find_element(By.XPATH, "//td[font[contains(text(), 'NAICS:')]]/following-sibling::td/font").text
            socio_economic = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Socio-Economic :')]]/following-sibling::td/font").text
            option_period_end = driver.find_element(By.XPATH, "//td[font[contains(text(), 'Current Option Period End Date :')]]/following-sibling::td/font").text

            data.append({
                'Contractor Name': contractor_name,
                'Address': address,
                'Phone': phone,
                'Email': email,
                'NAICS': naics,
                'Socio-Economic Status': socio_economic,
                'Option Period End Date': option_period_end,
                'Link': link
            })
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())

    return data

def main():
    driver = webdriver.Firefox()

    all_data = []

    for by_letter in range(ord('a'), ord('z') + 1):
        current_data = get_contractor_data(driver, chr(by_letter))
        all_data.extend(current_data)

    driver.close()

    # Save to Excel
    df = pd.DataFrame(all_data)
    df.to_excel('contractor_data_expanded.xlsx', index=False)
    print("Expanded data saved to Excel.")

if __name__ == "__main__":
    main()

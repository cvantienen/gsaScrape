from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from concurrent.futures import ThreadPoolExecutor
import os
import time
import traceback

def download_contractor_page(driver, link, output_dir):
    try:
        driver.get(link)
        time.sleep(3)  # Allow the page to load

        # Save the HTML content of the page
        contractor_name = driver.find_element(By.XPATH, "//h1").text.replace("/", "_").replace("\\", "_")
        html_content = driver.page_source

        # Create a file for the contractor's HTML page
        file_path = os.path.join(output_dir, f"{contractor_name}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"Saved HTML for contractor: {contractor_name}")
    except Exception as e:
        print(f"An error occurred while processing link {link}: {e}")
        print(traceback.format_exc())

def download_contractor_pages(driver, starting_letter, output_dir):
    try:
        letter = starting_letter.upper()
        driver.get(f"https://www.gsaelibrary.gsa.gov/ElibMain/contractorList.do?contractorListFor={letter}")
        time.sleep(5)

        elems = driver.find_elements(By.XPATH, "//a[@href]")
        links = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href")[:58] == 'https://www.gsaelibrary.gsa.gov/ElibMain/contractorInfo.do']

        # Use ThreadPoolExecutor to download pages in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            for link in links:
                executor.submit(download_contractor_page, driver, link, output_dir)
    except Exception as e:
        print(f"An error occurred for letter {starting_letter}: {e}")
        print(traceback.format_exc())

def main():
    # Set up the output directory
    output_dir = "contractor_html_pages"
    os.makedirs(output_dir, exist_ok=True)

    # Set up Selenium WebDriver with headless mode
    options = Options()
    options.add_argument("--headless")  # Run Firefox in headless mode
    driver = webdriver.Firefox(options=options)

    try:
        # Iterate through all letters of the alphabet
        for by_letter in range(ord('a'), ord('z') + 1):
            download_contractor_pages(driver, chr(by_letter), output_dir)
    finally:
        driver.close()

    print(f"All contractor HTML pages have been saved to the '{output_dir}' directory.")

if __name__ == "__main__":
    main()
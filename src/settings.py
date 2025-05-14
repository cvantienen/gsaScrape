# settings.py - XPath constants for scraping


# Base URL for the website
BASE_URL = (
    "https://www.gsaelibrary.gsa.gov/ElibMain/contractorList.do?contractorListFor="
)

# XPaths for various elements on the contractor details page
CONTRACT_NUMBER_XPATH = (
    "//td[font[contains(text(), 'Contract #:')]]/following-sibling::td/font"
)
CONTRACTOR_XPATH = (
    "//td[font[contains(text(), 'Contractor:')]]/following-sibling::td/font"
)
ADDRESS_XPATH = "//td[font[contains(text(), 'Address:')]]/following-sibling::td/font"
PHONE_XPATH = "//td[font[contains(text(), 'Call:')]]/following-sibling::td/font"
EMAIL_XPATH = "//td[font[contains(text(), 'Email:')]]/following-sibling::td/font/a"
WEB_ADDRESS_XPATH = (
    "//td[font[contains(text(), 'Web Address:')]]/following-sibling::td/font/a"
)
SAM_UEI_XPATH = "//td[font[contains(text(), 'SAM UEI:')]]/following-sibling::td/font"
NAICS_XPATH = "//td[font[contains(text(), 'NAICS:')]]/following-sibling::td/font"
OPTION_XPATH = "//td[font[contains(text(), 'Current Option Period End Date :')]]/following-sibling::td/font"
ULTIMATE_XPATH = "//td[font[contains(text(), 'Ultimate Contract End Date :')]]/following-sibling::td/font"
CONTRACT_OFFICER_XPATH = "//td[font[contains(text(), 'Govt. POC:')]]/font[2]"
SINS_XPATH = "//td[font[contains(text(), 'Category')]]/following-sibling::td/font/a"
SINS_XPATH = "//td[contains(., 'Category')]/following-sibling::td//a"
SOURCE_XPATH = "//td[contains(., 'Source')]/following-sibling::td//a"

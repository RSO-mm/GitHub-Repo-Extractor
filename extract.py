import re
from playwright.sync_api import sync_playwright
import json


DOMAIN = "https://github.com"
DOMAIN_RAW = "https://raw.githubusercontent.com"
FILE_PATH = 'output.txt'
filesLinks = []

def click_element_and_get_files(page, onclick_urls):
    for url in onclick_urls:
        page.goto(url)
        page.wait_for_timeout(2000)
        # Get all sub-elements (header items)
        table_loc = 'table[aria-labelledby="folders-and-files"]'
        directory_locator = 'table[aria-labelledby="folders-and-files"] a[aria-label*="(Directory)"].Link--primary:visible'
        table_exists = page.is_visible(table_loc)
        if table_exists:
            elements = page.locator(directory_locator).all()

            # Get text elements (files)
            files_locator = 'table[aria-labelledby="folders-and-files"] a[aria-label*="(File)"].Link--primary:visible'
            files = page.locator(files_locator).all()
            for file in files:
                filesLinks.append(file.get_attribute('href'))

            if elements:
                urls = []
                for element in elements:
                    urls.append(DOMAIN + element.get_attribute('href'))
                click_element_and_get_files(page, urls)


def get_raw_page_content(page, filesLinks):
    contents = ""
    for fileLink in filesLinks:
        path_without_blob = re.sub(r'/blob/', '/', fileLink)
        if path_without_blob.endswith('.jkl') or path_without_blob.endswith('.jks'):
            continue
        page.goto(DOMAIN_RAW + path_without_blob)
        page.wait_for_timeout(2000)
        page_content = page.content()
        path_after_master = re.sub(r'^.*?/master/', '', fileLink)

        #contents += page_content + '\n' + path_after_master + '\n\n\n\n\n'
        contents += "File path: " + path_after_master + '\n' + page_content + '\n\n\n\n\n'


    with open(FILE_PATH, 'w', encoding='utf-8') as file:
        file.write(contents)

def get_urls(page_url):
    onclick_urls = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        response = page.goto(page_url)
        if not response.ok:
            return onclick_urls
        #page.pause()
        locator = 'div[aria-labelledby="files"] a.Link--primary'
        #locator = 'div[role="gridcell"] > svg[aria-label="Directory"] + div[role="rowheader"] a.Link--primary'
        #locator = "div[role='gridcell'] > svg[aria-label='Directory'] ~ div[role='rowheader'] > a.Link--primary"
        #locator = 'div[role="rowheader"]:above(div[role="gridcell"] > svg[aria-label="Directory"]) a.Link--primary'
        #locatorTable = 'table[aria-labelledby="folders-and-files"]'
        page.wait_for_selector(locator, state='visible')
        elements = page.locator(locator).all()
        #elements = page.locator('.PRIVATE_TreeView-item[aria-expanded="false"]').all() #dobi neodprt header
        #print(elements)
        for element in elements:
            onclick_urls.append(DOMAIN + element.get_attribute('href'))


        click_element_and_get_files(page, onclick_urls) #dodelava

        get_raw_page_content(page, list(set(filesLinks)))  # Remove duplicate elements


get_urls("https://github.com/kumuluz/kumuluzee-samples/tree/master/")
print(filesLinks)











from scrapy import Spider
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class LoginSpider(Spider):
    name = 'login_spider'
    start_urls = ['https://northwestern.zoom.us/']

    def __init__(self):
        # Setup Chrome with Selenium
        service = ChromeService(executable_path='D:\Aqualab\chromedriver_win32\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service)

    def parse(self, response):
        self.driver.get(response.url)

        # Wait for the page to load and for the login button to be clickable
        # This example assumes you're selecting the button by its text, but you can use any attribute
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Login' or text()='Log in' or text()='My Account'] | //a/span[text()='Login' or text()='Log in' or text()='My Account']"
            ))
        )

        # Click the login button
        login_button.click()

        # Optional: Wait for some condition after clicking the button, like a new page or a dialog to appear
        # This is just a placeholder for whatever condition you need to wait for
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "someElementAfterLogin"))
        )

        # At this point, you can continue with your scraping logic, extract data, etc.
        # For example, getting the page source: html = self.driver.page_source

        # Don't forget to close the browser window once you're done
        self.driver.quit()

import os
import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class CrawlProducts:
    def __init__(self):
        self.browser = None
        self.HOME_LINK = 'https://ananas.vn/product-list/'
        self.init_driver()
        self.get_into_link(self.HOME_LINK)
        self.scroll_to_bottom()

    def options_driver(self):
        CHROMEDRIVER_PATH = './chromedriver'
        WINDOW_SIZE = "1000,2000"
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_argument(
            '--disable-gpu') if os.name == 'nt' else None  # Windows workaround
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument(
            "--disable-feature=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--ignore-certificate-error-spki-list")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControllered")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # open Browser in maximized mode
        chrome_options.add_argument("--start-maximized")
        # overcome limited resource problems
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument('disable-infobars')
        chrome_options.page_load_strategy = 'none'
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                                  options=chrome_options
                                  )
        return driver

    def init_driver(self):
        self.browser = self.options_driver()

    def scroll_to_bottom(self):
        SCROLL_PAUSE_TIME = 2.5
        sleep(0.5)
        last_height = self.browser.execute_script(
            "return document.body.scrollHeight")
        while True:
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(SCROLL_PAUSE_TIME)
            new_height = self.browser.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_into_link(self, link):
        self.browser.get(link)

    def write_csv(self, content, file_name):
        with open(file_name, 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(content)

    def get_all_prods_page(self):
        link_tag = self.browser.find_elements_by_xpath(
            "//a[contains(@href, 'https://ananas.vn/product-detail/')]")
        return set([link.get_attribute('href') for link in link_tag])

    def get_product_details(self):
        title = self.browser.find_element_by_class_name(
            'prd-detail-right').find_element_by_tag_name('h4').text
        result = [title]
        details = self.browser.find_elements_by_class_name('detail1')
        for detail in details:
            result.append(detail.text)
        buttons = self.browser.find_elements_by_xpath(
            "//a[@data-toggle='collapse' and @role='button']")
        self.browser.execute_script("arguments[0].click();", buttons[0])
        for i in range(len(buttons)):
            self.browser.execute_script("arguments[0].click();", buttons[i])
            sleep(0.3)
            panel = self.browser.find_elements_by_class_name('panel')[i]
            result.append(panel.text)
        return result

    def crawl(self):
        sleep(2)
        product_links = list(self.get_all_prods_page())
        for product in product_links:
            self.get_into_link(product)
            infos = self.get_product_details()
            self.write_csv(infos, 'products.csv')
        self.browser.close()


if __name__ == '__main__':
    crawl_obj = CrawlProducts()
    crawl_obj.crawl()

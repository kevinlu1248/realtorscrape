import time

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from fake_useragent import UserAgent
from tqdm import tqdm

KEYS = open("keys_raw.txt").read().strip().split('\n')
URLS = open("realtorurlstoscrape.txt").read().strip().split('\n')
ICON_SELECTOR = "#headerLeft > a > img"
NEW_IMAGE_SELECTOR = "#ctl00 > div > a > div.smallListingCardBodyWrap > img"
NEXT_BUTTON_SELECTOR = "#SideBarPagination > div > a.lnkNextResultsPage.paginationLink.paginationLinkForward.btn.small"
CARD_SELECTOR = ".cardCon > span > div > a"

ua = UserAgent()

option = Options()
option.add_argument(" — incognito")
option.add_argument("--window-size=1080,800")
option.add_argument(f"user-agent={ua.google}")

browser = webdriver.Chrome(executable_path="/home/kevin/Downloads/chromedriver", options=option)

class wait_for_text_change(object):
    def __init__(self, locator, value):
        self.locator = locator
        self.value = value
    def __call__(self, driver):
        try:
            element_text = EC._find_element(driver, self.locator).text
            return element_text == self.value
        except:
            print("stale!")
            return False

timeout1 = 90
timeout2 = 5
sleeptime1 = 2
sleeptime2 = 5
timeout_per_page = 0.6

url_lsts = [set() for _ in URLS]
totals = []
refresh_counter = 0

pbar = tqdm(total=1)

for index, url_to_scrape in enumerate(URLS):
    browser.get(url_to_scrape)
    if index > 0:
        browser.refresh()

    try:
        WebDriverWait(browser, timeout1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ICON_SELECTOR)))
    except TimeoutException:
        print("Timeout waiting for recapcha to finish")
        browser.quit()

    time.sleep(sleeptime1)

    TARGET_TEXT_SELECTOR = "#mapSidebarBodyCon > div:last-child > div > a > div.smallListingCardBodyWrap > div > div.smallListingCardAddress, #ctl00 > div > a > div.smallListingCardBodyWrap > div > div.smallListingCardAddress"
    CURRENT_PAGE_SELECTOR = ".select2-selection.select2-selection--single.paginationDDLCon > .select2-selection__rendered"
    TOTAL_PAGES_SELECTOR = "#SideBarPagination > div > div > div > span.paginationTotalPagesNum"
    TOTAL_LISTINGS_SELECTOR = "#mapResultsNumVal"

    totals.append(int(browser.find_element_by_css_selector(TOTAL_LISTINGS_SELECTOR).text))

    # pbar = tqdm(total=int(browser.find_element_by_css_selector(TOTAL_PAGES_SELECTOR).text), desc=f"Part {index + 1}/{len(URLS)}")
    pbar.n = 0
    pbar.total = int(browser.find_element_by_css_selector(TOTAL_PAGES_SELECTOR).text)
    pbar.desc = f"Part {index + 1}/{len(URLS)}"
    pbar.refresh()

    def check_if_last_page():
        return browser.find_element_by_css_selector(CURRENT_PAGE_SELECTOR).text == browser.find_element_by_css_selector(TOTAL_PAGES_SELECTOR).text

    while True:
        next_button = browser.find_element_by_css_selector(NEXT_BUTTON_SELECTOR)

        def get_urls():
            tmp_url_lst = set()
            total_tries = 5
            for _ in range(total_tries):
                doRestart = False
                for card in browser.find_elements_by_css_selector(CARD_SELECTOR):
                    try:
                        href = card.get_attribute("href")
                        tmp_url_lst.add(href)
                    except StaleElementReferenceException:
                        doRestart = True
                        browser.refresh()
                        global refresh_counter
                        refresh_counter += 1
                        time.sleep(3)
                        global next_button
                        next_button = browser.find_element_by_css_selector(NEXT_BUTTON_SELECTOR)
                        break
                if doRestart == False:
                    break
                if _ == total_tries - 1:
                    raise Exception("Too many tries, still stale")
            return tmp_url_lst

        tmp_url_lst = get_urls()

        while len(tmp_url_lst) < 12 and not check_if_last_page():
            tmp_url_lst = get_urls()
        
        for tmp_url in tmp_url_lst:
            url_lsts[index].add(tmp_url)

        if next_button.get_attribute("disabled") and check_if_last_page():
            break
        try:
            next_button.click()
        except ElementClickInterceptedException:
            browser.find_element_by_id("acsFocusFirst").click()
            time.sleep(0.5)
            next_button.click()
        target_text = browser.find_element_by_css_selector(TARGET_TEXT_SELECTOR)
        # WebDriverWait(browser, sleeptime2).until(wait_for_text_change((By.CSS_SELECTOR, TARGET_TEXT_SELECTOR), target_text.text))
        # WebDriverWait(browser, sleeptime2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, NEW_IMAGE_SELECTOR)))
        pbar.update(1)
        pbar.refresh()
        time.sleep(timeout_per_page)

    if totals[index] != len(url_lsts[index]):
        print(f"Warning: lengths don't match (total indicated is {totals[index]} but found {len(url_lsts[index])} urls)")

old_urls = set(open("realtorurls.txt", "r").read().strip().split('\n'))
url_lst = set()
for lst in url_lsts:
    url_lst = url_lst.union(lst)
print(f"Before, there were {len(old_urls)} listings")
print(f"Now, there are {len(url_lst)} ({' + '.join(list(map(str, totals)))}) listings")
print(f"Number of refreshes: {refresh_counter}")
new_urls = url_lst - old_urls
if new_urls:
    print("New listings have been found!")
    for new_url in new_urls:
        print(f"  - {new_url}")
else:
    print("--- No new listings found! ---")

with open("realtorurls.txt", "w") as f:
    for url in url_lst.union(old_urls):
        f.write(url + '\n')
    
browser.quit()
print("Done!")

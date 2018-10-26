#!/home/wangh/anaconda3/bin/python

from selenium import webdriver  
from selenium.webdriver.chrome.options import Options

from PIL import Image
from io import BytesIO

CHROME_PATH = '/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/home/wangh/local/bin/chromedriver'
WINDOW_SIZE = "1920,3240"

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH

def make_screenshot(url):
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    driver.get(url)
    driver.save_screenshot('full.png')
    element = driver.find_element_by_id('main-content-column')
    with open('data.txt', 'w') as fout:
        fout.write(element.text)
    driver.close()

if __name__ == '__main__':
    make_screenshot('https://www.barchart.com/options/unusual-activity')

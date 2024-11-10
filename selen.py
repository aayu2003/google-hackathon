from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def save_ss(city,map_path):

    # Get absolute path to map1.html assuming it's in the same directory as selen.py
    html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), map_path))

    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")  # Set window size to a large value for high resolution
    # driver_path = '/snap/chromium/2953/usr/lib/chromium-browser/chromedriver'  # Change this to the path where you placed chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the HTML file
    driver.get('file://' + html_file_path) 

    time.sleep(5)


    screenshot_path = "seg_ss/"+city+".png"
    driver.save_screenshot(screenshot_path)

    # Close the WebDriver
    driver.quit()
    return screenshot_path

def save_ss_satellite(city,map_path):
    # Get absolute path to map1.html assuming it's in the same directory as selen.py
    html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), map_path))

    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")  # Set window size to a large value for high resolution
    # driver_path = '/home/aryan/croma/chromedriver-linux64/chromedriver'  # Change this to the path where you placed chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the HTML file
    driver.get('file://' + html_file_path) 

    time.sleep(10)


    screenshot_path = "seg_ss/satellite/"+city+".png"
    driver.save_screenshot(screenshot_path)

    # Close the WebDriver
    driver.quit()
    return screenshot_path


def selen_zoom(city,map_path,id):
    # Get absolute path to map1.html assuming it's in the same directory as selen.py
    html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), map_path))

    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")
    options.add_argument("--window-size=1080,1080")  # Set window size to a large value for high resolution
    # driver_path = '/home/aryan/croma/chromedriver-linux64/chromedriver'  # Change this to the path where you placed chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the HTML file
    driver.get('file://' + html_file_path) 

    time.sleep(5)

    # Zoom in by 2 levels
    # for i in range(2):
    #     driver.execute_script("document.body.style.zoom='50%'")
    #     time.sleep(2)

    screenshot_path = f"land_zoom/img/{city}_{id}.png"
    driver.save_screenshot(screenshot_path)

    # Close the WebDriver
    driver.quit()
    return screenshot_path

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.common.by import By

# options = webdriver.ChromeOptions()
# options.binary_location = "/usr/bin/chromium-browser"  # Adjust the path if necessary

# # Initialize WebDriver
# service = ChromeService(executable_path="/usr/bin/chromedriver")
# driver = webdriver.Chrome(service=service, options=options)

# # Open a webpage
# driver.get("http://www.google.com")

# # Print the title of the webpage
# print(driver.title)

# # Close the WebDriver
# # driver.quit()
# while(True):
#     pass


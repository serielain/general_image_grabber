import os
from bs4 import BeautifulSoup
from PIL import Image
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import argparse
from pinterest import *
from general_functions import *

class NoNewImageException(Exception):
    pass


#make sure you change the URL and the folder path to your own
default_type = "universal" # Default type universal
default_url = "https://example.com"
default_folder_path = "PASTE FOLDER PATH HERE"

# Call the function and get the arguments --websitetype, --url, --folder_path, --retries
args = parse_arguments(default_type, default_url, default_folder_path)

# Get the values of the arguments
website_type = args.websitetype
url = args.url
folder_path = args.folder_path
retries = args.retries

driver = webdriver.Firefox() # Create a new Firefox browser instance
driver.get(url) # Navigate to the webpage
start_time = time.time() #counts time to run the code
image_urls = set() # Set of image URLs

# Call the appropriate function based on the website type
if(website_type == "pinterest"):
    pinterest_image_grabber(driver, image_urls, website_type, folder_path)
else:
    universal_image_grabber(driver, image_urls, website_type, folder_path)

# Count and print the number of elements in folder_path
print(f"Number of Elements in Folder: {count_folder_elements(folder_path)}")

#prints to run the code
end_time = time.time()
total_time = end_time - start_time
print(f'The total time used to run the code is: {total_time:.2f} seconds')
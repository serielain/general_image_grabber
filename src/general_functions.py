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
from datetime import datetime

class NoNewImageException(Exception):
    pass

def count_folder_elements(folder_path):
    return len(os.listdir(folder_path))

def parse_arguments(default_type, default_url, default_folder_path):
    # Create an argument parser
    parser = argparse.ArgumentParser()

    # Add the --url, --folder_path, and --retries arguments
    parser.add_argument("--websitetype", default=default_type, help="The URL to download images from (default: Pinterest)")
    parser.add_argument("--url", default=default_url, help="The URL to download images from")
    parser.add_argument("--folder_path", default=default_folder_path, help="The path to the folder where the images will be saved")
    parser.add_argument("--retries", type=int, default=25, help="The number of times to retry downloading an image")

    # Parse the command-line arguments
    args = parser.parse_args()

    return args

def universal_image_grabber(driver, image_urls, website_type, folder_path):

    scroll_position = 0 # Initial scroll position
    no_new_image_counter = 0 # Counter for the number of retries with no new image
    no_new_image_limit = 30 # Maximum number of retries with no new image

    try:
        # Scroll and extract image URLs 
        while(True):
            # Scroll the webpage to load more images
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Adjust this value based on your needs

            # image urls before adding new ones
            image_counter_prev = len(image_urls)

            # Parse the webpage's content
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # Find all image elements on the page
            image_elements = soup.find_all("img")

            # Extract and save the image URLs
            for image_element in image_elements:
                image_url = image_element.get("src")
                if image_url:
                    image_urls.add(image_url)
            print(f"Number of URLs: {len(image_urls)}")
            # Check if there are no new images
            if (len(image_urls) == image_counter_prev):
                no_new_image_counter += 1
                print(f"No new images found after {no_new_image_counter} retries")
                if no_new_image_counter >= no_new_image_limit:
                    raise NoNewImageException
            else:
                no_new_image_counter = 0


    except WebDriverException:
        print("Browser closed. Starting to process the image URLs...")
    except NoNewImageException:
        print(f"No new images were found after {no_new_image_counter} retries. Starting to process the image URLs...")
        driver.quit()
    # Create or open a .txt file to save the modified image URLs
    with open("image_links.txt", "w") as file:
        # Save each unique image URL to the .txt file
        for image_url in image_urls:
            file.write(image_url + "\n")

    print("All image URLs saved successfully!")

    # Count the number of saved URLs
    with open("image_links.txt", "r") as file:
        url_count = sum(1 for line in file)
    print(f"Number of saved URLs: {url_count}")

    # Read the modified image URLs from the .txt file and download each image
    image_counter = 0
    with open("image_links.txt", "r") as file:
        for line in file:
            image_url = line.strip()
            # Get the current date and time in the format dd_mm_yyyy_hh_min_sec
            current_time = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
            image_name = f"image_{current_time}_{image_counter}.jpg"
            save_path = os.path.join(folder_path, image_name)

            # Send a GET request to download the image
            image_response = requests.get(image_url)

            # Save the image to the specified directory
            with open(save_path, "wb") as image_file:
                image_file.write(image_response.content)
            image_counter += 1
            print(f"Number {image_counter} / {len(image_urls)} downloaded: {image_name}")
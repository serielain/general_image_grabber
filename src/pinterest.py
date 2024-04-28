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

class NoNewImageException(Exception):
    pass

def pinterest_image_grabber(driver, image_urls, website_type, folder_path):

    scroll_position = 0 # Initial scroll position
    no_new_image_counter = 0 # Counter for the number of retries with no new image
    no_new_image_limit = 30 # Maximum number of retries with no new image

    try:
        # Scroll and extract image URLs 
        while(True):
            # Scroll down the page in steps
            for _ in range(2):  # Adjust this value based on your needs (default:2)
                scroll_position += 150  # Scroll down 150 default
                driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(0.05)  # Adjust this value based on your needs

            # Click the "Mehr anzeigen" button if it appears
            try:
                button = WebDriverWait(driver, 0).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Mehr anzeigen']"))
                )
                print("Clicked 'Mehr anzeigen' button")
                button.click()
            except TimeoutException:
                time.sleep(0)

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
                if no_new_image_counter >= no_new_image_limit:
                    raise NoNewImageException
            else:
                no_new_image_counter = 0
            if(no_new_image_counter != 0):
                print(f"No new images found after {no_new_image_counter} retries")


    except WebDriverException:
        print("Browser closed. Starting to process the image URLs...")
    except NoNewImageException:
        print(f"No new images were found after {no_new_image_counter} retries. Starting to process the image URLs...")
        driver.quit()
    # Create or open a .txt file to save the modified image URLs
    with open("changed_list.txt", "w") as file:
        # Save each unique image URL to the .txt file
        for image_url in image_urls:
            # Replace "75x75_RS" and "236x" with "originals"
            modified_url = image_url.replace("75x75_RS", "originals").replace("140x140_RS", "originals").replace("170x", "originals").replace("222x", "originals").replace("236x", "originals").replace("280x280_RS", "originals").replace("1200x", "originals").replace("236x", "originals").replace("236x", "originals")
            file.write(modified_url + "\n")

    print("All modified image URLs saved successfully!")

    # Count the number of saved URLs
    with open("changed_list.txt", "r") as file:
        url_count = sum(1 for line in file)
    print(f"Number of saved URLs: {url_count}")

    # Read the modified image URLs from the .txt file and download each image
    image_counter = 0
    with open("changed_list.txt", "r") as file:
        for line in file:
            image_url = line.strip()
            image_name = image_url.split("/")[-1]
            save_path = os.path.join(folder_path, image_name)

            # Send a GET request to download the image
            image_response = requests.get(image_url)

            # Save the image to the specified directory
            with open(save_path, "wb") as image_file:
                image_file.write(image_response.content)
            image_counter += 1
            print(f"Number {image_counter} / {len(image_urls)} downloaded: {image_name}")

        

    def check_and_redownload_images_pinterest():
        # Read the modified image URLs from the .txt file
        with open("changed_list.txt", "r") as file:
            for line in file:
                image_url = line.strip()
                image_name = image_url.split("/")[-1]
                save_path = os.path.join(folder_path, image_name)

                # Check if the image file exists and is valid
                if os.path.isfile(save_path):
                    try:
                        # Open the image file
                        img = Image.open(save_path)
                        img.verify()
                    except (IOError, SyntaxError) as e:
                        print(f"Invalid image: {image_name}")
                        # If the image is invalid, re-download it with "564x" instead of "originals"
                        redownload_url = image_url.replace("originals", "564x")
                        redownload_image(redownload_url, save_path)
                else:
                    print(f"Image not found: {image_name}")
                    # If the image file does not exist, download it
                    download_image(image_url, save_path)

    def download_image(image_url, save_path):
        # Send a GET request to download the image
        image_response = requests.get(image_url)

        # Save the image to the specified directory
        with open(save_path, "wb") as image_file:
            image_file.write(image_response.content)

        print(f"Downloaded: {os.path.basename(save_path)}")

    def redownload_image(image_url, save_path):
        # Delete the invalid image file
        os.remove(save_path)

        # Re-download the image
        download_image(image_url, save_path)

    # Call the function to check and re-download images
    check_and_redownload_images_pinterest()
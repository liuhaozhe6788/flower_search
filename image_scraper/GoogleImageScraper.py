# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:01:02 2020

@author: OHyic
"""
#import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException       

#import helper libraries
import time
import urllib.request
import os
import requests
import io
from PIL import Image

#custom patch libraries
import image_scraper.patch 

class GoogleImageScraper():
    def __init__(self,webdriver_path, number_of_images, search_key, headless=False,min_resolution=(0,0),max_resolution=(1920,1080)):
        #check parameter types
        if (type(number_of_images)!=int):
            print("[Error] Number of images must be integer value.")
            return
        self.number_of_images = number_of_images
        self.search_key = search_key
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(search_key) # Searching by keyword
        #check if chromedriver is updated
        while(True):
            try:
                #try going to www.google.com
                options = Options()
                if(headless):
                    options.add_argument('--headless')
                driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                driver.set_window_size(1400,1050)
                driver.get("https://www.google.com")
                break
            except:
                #patch chromedriver if not available or outdated
                try:
                    driver
                except NameError:
                    is_patched = image_scraper.patch.download_lastest_chromedriver()
                else:
                    is_patched = image_scraper.patch.download_lastest_chromedriver(driver.capabilities['version'])
                if (not is_patched): 
                    exit("[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")
                    
        self.driver = driver
        self.webdriver_path = webdriver_path
        self.headless=headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
        
    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls = google_image_scraper.find_image_urls()
                
        """
        print("[INFO] Scraping for image link... Please wait.")
        image_urls=[]
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)
        indx = 1
        while self.number_of_images > count:
            try:
                #find and click image
                imgurl = self.driver.find_element(By.XPATH, '//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img'%(str(indx)))
                imgurl.click()
                missed_count = 0 
            except Exception:
                #print("[-] Unable to click this photo.")
                missed_count = missed_count + 1
                if (missed_count>10):
                    print("[INFO] No more photos.")
                    break
                 
            try:
                #select image from the popup
                time.sleep(1)

                # class_names = ["n3VNCb", "pT0Scc", "KAlRDb", "v4dQwb"]
                # images = [self.driver.find_elements(By.CLASS_NAME, class_name) for class_name in class_names if len(self.driver.find_elements(By.CLASS_NAME, class_name)) != 0 ][0]
                # for image in images:
                #     #only download images that starts with http
                #     src_link = image.get_attribute("src")
                #     print(src_link)
                #     if(("http" in  src_link) and (not "encrypted" in src_link)):
                #         print("[INFO] %d. %s"%(count,src_link))
                #         image_urls.append(src_link)
                #         count +=1
                #         break

                # XPath of the image display 
                fir_img = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]/c-wiz/div/div[1]/div[2]/div[2]/div/a/img')
                
                # Wait between interaction
                time.sleep(3)
                # fir_img.click()
                
                # Retrieve attribute of src from the element
                img_src = fir_img.get_attribute('src')
                if(("http" in img_src) and (not "encrypted" in img_src)):
                    image = requests.get(img_src, headers=self.headers, timeout=3, stream=True)
                    if image.status_code == 200:
                        print("[INFO] %d. %s"%(count, img_src))
                        image_urls.append(img_src)
                        count +=1

            except Exception:
                print("[INFO] Unable to get link")   
                
            try:
                #scroll page to load next image
                if(count%3==0):
                    self.driver.execute_script("window.scrollTo(0, "+str(indx*60)+");")
                element = self.driver.find_element(By.CLASS_NAME, "mye4qd")
                element.click()
                print("[INFO] Loading more photos")
                time.sleep(3)
            except Exception:  
                time.sleep(1)
            indx += 1

        
        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls

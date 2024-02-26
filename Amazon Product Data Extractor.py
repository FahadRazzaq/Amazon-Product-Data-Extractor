# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 20:49:04 2022

@author: abrartareen@gmail.com
"""

from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import os
import time
import re
import random
from random import choice
from requests.exceptions import ProxyError
from datetime import datetime



start_time = time.time()
print('Reading input data.....')
prev_time = start_time
# input data (URLs)
data = pd.read_csv('Amazon_URLs.csv')
urls = data['URLs']
partnumbers = data['partnumber']
search_count = data['Search Results']
# output data
df = pd.DataFrame(columns=['part_no', 'url', 'search_count', 'title', 'main_image_link', 'price', 'description',
                           'features', 'full_description', 'replace', 'prod_offers'])
                           
# Paid proxies
proxies = {
    "http": "http://zain.acgile.com:a5jgtk@gate1.proxyfuel.com:2000",
    "https": "http://zain.acgile.com:a5jgtk@gate1.proxyfuel.com:2000",
}

# Pretend to be Firefox
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'
}

s = requests.Session()

# loop through links
for index, url in enumerate(urls):    
    part_no = partnumbers[index]
    if url == 'Not Found':  # it is the case when the part_no search on CarID gave zero results in 
                            # previous script to scrape car_id_urls.py
        df.loc[df.shape[0]] = [part_no, url, 0, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
        continue             
    # if index < 3000:
        # continue
    # if index > 2999:
    #     break
    
    time.sleep(random.randint(1, 3))         
    print(index)
    r = None
    # an infinite loop until the desired response is received! However, this may run infinitely if the pages is not present on server
    while True:
        try:
            r = s.get(url=url, proxies=proxies, headers=headers, timeout=120)
            soup = bs(r.content, 'html.parser')
            if soup.title.text == 'Security Check' or r.status_code > 200:
                # print(r.status_code)
                print("Security Check")
                # time.sleep(random.randint(10,15))                                 
                s.close()
                s = requests.Session()
                continue 
            else:
                break
        except Exception as e:
            print(e)
            s.close()
            s = requests.Session()
            continue
            # time.sleep(5)
            
    
    # Using BeautifulSoup to extract desired data points
    try:
        title = soup.find('title').text.strip()
    except:
        title = 'N/A'
    try:
        price = soup.find("span", {"class": "prod-price"}).text.strip()
    except:
        price = 'N/A'
    try:
        main_image_link = soup.find("div",{"class":"main-img"}).find("img", {"class":"item"}).get('src')
    except:
        main_image_link = 'N/A'
    try:
        prod_description = soup.find("section",{"id":"product-details"}).find("p", {"class":"prod-detail-img"}).next_sibling.text
        #product-details > div > div > div.js-spoiler-block.spoiler-block.-gradient-fade > p:nth-child(2)
    except:
        prod_description = 'N/A'
    features_list = []
    try:
        features = soup.find("h2",{"id":"features"}).next_sibling.children
        for feature in features:
            features_list.append(feature.text)
    except:
        features_list.append("N/A")
    try:
        paras = soup.find("div", {"class":"prod-full-descr"}).find_all("p")
        full_description = []
        for para in paras:
            full_description.append(para.text)
    except:
        full_description = 'N/A'
    try:
        replace = soup.find("div", {"class":"prod-full-descr"}).find_next_sibling().text
    except:
        replace = ''
    try:
        offers = soup.find("div",{"class":"prod_offer"}).children
        prod_offers = ''
        for offer in offers:
            prod_offers += offer.text + '\n'
        prod_offers = prod_offers.strip()
    except:
        prod_offers = "N/A"
    df.loc[df.shape[0]] = [part_no, url, search_count[index], title, main_image_link, price, prod_description,
                           features_list, full_description, replace, prod_offers]
    # print(part_no, title, price)
                    

df.to_excel('LKQ_output.xlsx', index=False)

print('Done')
end_time = time.time()
time_taken = int ((end_time - start_time)/60)
print('Time taken: ' + str(time_taken))
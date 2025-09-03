#!/usr/bin/env python
# coding: utf-8

# ### Scrape all recipes on Italy website

# In[1]:


# import packages
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import json
import re
from google_trans_new import google_translator 
import requests
from parsel import Selector
from pprint import pprint
import ast
import pandas as pd
from lxml import html
import requests
import pandas as pd
import numpy as np


# For this website, we have several different categories.
# 
# 1. Latest receipes
# 2. Appetizers
# 3. First courses
# 4. Main courses
# 5. Desserts
# 6. Leavened products
# 
# Logic:
# 
# 1. we get the html of one recipe on one page of one category
# 2. create a dictionary to store all recipe htmls on one page of one category
# 3. go through all pages in one category and get all recipe htmls of one category
# 4. go through all categories and get all recipe htmls (Note: we need to delete duplicated htmls so that we can know the total number of recipes on the Italy website.)
# dictionary structure:
# htmlDic = {
# name of the recipe: "html link"
# }
# 
# method to check if there are duplicates:
# method 1: Using Naive approach. In this method first, we convert dictionary values to keys with the inverse mapping and then find the duplicate keys.
# method 2: Using flipping dictionary.
# method 3: Using chain and set.
# 
# 5. go through all recipe htmls and scrape the data we want
# dictionry structure:
# Italydata = {
# "name of the recipe": [],
# "Number of ingredients": [],
# "Total time": [],
# "Prep time": [],
# "Cook time": [],
# "Number of servings": [],
# "List of ingredients": [],
# "List of instructions":[],
# "estimatedCost":[],
# "recipeCategory":[],
# "description" :[],
# "nutrition": []
# }
# 
# 6. Convert dictionary to data frame

# ##### Latest receipes

# ###### page 1:https://www.giallozafferano.com/latest-recipes/

# #### 1.get the html of one recipe on the web
# 

#   <article class="gz-card gz-card-horizontal gz-mBottom3x">
#     <div class="gz-image-recipe gz-photo">
#       <a href="https://www.giallozafferano.com/recipes/Watermelon-pizza.html" title="Watermelon pizza">
#         <picture>
#           <img src="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%206%205'%3E%3C/svg%3E" data-src="https://www.giallozafferano.com/images/236-23625/Watermelon-pizza_360x300.jpg" width="360" height="300" alt="Watermelon pizza" class="lazyload" loading="lazy" />
#         </picture>
#         
#       </a>
#     </div>
#     <div class="gz-content-recipe-horizontal">
#       <div class="gz-wrap-recipe-top">
#         <div class="gz-category"><a href="/recipes-list/Sweets-and-desserts/" title="Watermelon pizza">Sweets and desserts</a></div>
#         <h2 class="gz-title"><a href="https://www.giallozafferano.com/recipes/Watermelon-pizza.html" title="Watermelon pizza">Watermelon pizza</a></h2>
#               </div>
#       <div class="gz-wrap-recipe-bottom">
#         <div class="gz-description"><a href="https://www.giallozafferano.com/recipes/Watermelon-pizza.html" title="Watermelon pizza">Watermelon pizza is a great alternative way of serving sliced watermelon: fresh, colorful and original.  A perfect, healthy snack for the summer.</a></div>
#         <div class="gz-col-flex gz-double  gz-mTop10">
#           <div class="gz-col">
#             <ul class="gz-data-recipe">
#               <li class="gz-single-data-recipe">
#                 <span class="gz-icon">
#                   <svg viewBox="0 0 19 19">
#                     <use xlink:href="/style/images/icons.svg?cb=bf954a32f26ccffba356fcc370f41afbfe135b8c#difficolta-grey" />
#                   </svg>
#                 </span>
#                 Very easy
#               </li>
#               <li class="gz-single-data-recipe">
#                 <span class="gz-icon">
#                   <svg viewBox="0 0 20 19">
#                     <use xlink:href="/style/images/icons.svg?cb=bf954a32f26ccffba356fcc370f41afbfe135b8c#tempo-grey" />
#                   </svg>
#                 </span>
#                 15 min
#               </li>
#                           </ul>
#           </div>
#           <div class="gz-col">
#             <div class="gz-link-more-recipe">
#               <a href="https://www.giallozafferano.com/recipes/Watermelon-pizza.html" title="Watermelon pizza">
#                 READ <span>RECIPE</span>
#               </a>
#             </div>
#           </div>
#         </div>
#       </div>
#     </div>
#   </article>

# #### 2. create a dictionary to store all recipe htmls on one page of one category

# In[2]:


# initialize htmlDic to store the htmls of all recipes
htmlDic = {}


# In[3]:


def htmlOnePageSpider(category_url, dic):
    """
    input: category_url, the url of first page of one category
    input: the initial htmlDic
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_gid=GA1.2.2044917405.1628215509; push_notification_viewed=1; push_notification_token=cl1Q918JjaA:APA91bF77xlKJBzu_enBJMT2huk4AYCH1YzBwWcq5qyRcmcLczPuwycyYqA0A0kijCGTkuVQHrjCARU_wImnacoG0A3X9sis8X7bM0liRn_luMm2orfTkttqTQXazHN-C9xxJP1_HRe3; push_notification_topics=default; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _pbjs_userid_consent_data=3524755945110770; _pubcid=44caf923-8f3b-4c5a-a115-b07cbef2d915; cto_bidid=zx7NAV91eHZmc2JjVldMY2NGU0JzNiUyQlhyN0FzaVgwZXVtdWwyZHp2Y2oxQnpFb2xuYmdmR2UlMkIyWFVLeWFpZ25lRWNscFBpcWVpTEd3ZTklMkIxQjBBdDV2TjROaW9kdUpNRWpiajNWZXI4NGtqallMTFF2S0lmU1VjVlA2aG1ydXkzYkl4WUdPJTJCZXNHTzlGTlVpdUtoa04zTDFsZyUzRCUzRA; cto_bundle=GApBq19nQWxwMlZMd1JiUjdTU01UbEltT0lPMU1LUTFncm5MNlNNTmhNdkZIeThrZjVXbHY3S2NYSmRtJTJGeFg4ek8xeEFBa2RPR0YwdGhja3djcmpPSDhvNnVTWWdFcW5mM2thN29IT2V1NHNXJTJCYXVRWVFpTlVLNTJONlNnaE5ZS3FJTndTS0pVOTV6SWlEQXR4JTJGZGxOUHBzNXlKUEpSRmFnVzVaUExsNWRtSlhNS0VRN0RXWmE2VDJoYnBlbUFyVG5pM0NGdXFNdDRwVUxJazUyJTJCSUNrWE5aR1ElM0QlM0Q; _lr_retry_request=true; _lr_env_src_ats=false; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-07-06T02:47:48"}; idl_env=AsVWbVw3m6dkmdKUdBHZ25o6aMy3ZU2ZRKnSFe71GxSD88dKs6rClb9Qp3O9EhJk7ZDvTZSPHpo4XscnTw-Mr-o71yfp0yc0lvBmblDx80Gpe7R8bL8HC0E12tC3VD6gNeesuSCOwhHbXYsmEPhBKrbiTDnOdTvvIQxdI0AXHDYg2CbVlJzP5sGGn5PhR0V3u7mYavaW0LHoJUkOlDke1Xfy41dJ; panoramaId_expiry=1628822868533; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=e26b57d52221e1431bf4644287ab4945a702d1dbb46dcc6c67d2ca44575af3b9; _ga=GA1.2.1751180775.1628215509; utag_main=v_id:017b193500560012646692ae8fc303078002007000942$_sn:2$_se:28$_ss:0$_st:1628222873205$ses_id:1628218041231;exp-session$_pn:14;exp-session; _iub_cs-87184196={"consent":true,"timestamp":"2021-08-06T02:05:12.513Z","version":"1.31.1","id":87184196}; euconsent-v2=CPKffhePKffh1B7EABENBlCsAP_AAH_AAAAAIJNf_X__bX9j-_59f_t0eY1P9_r_v-Qzjhfdt-8F2L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzPsak2Mr6NKJ7LEmnMZO2dYGHtfn91TuZKY7_78__fz3z-v_v___9f3r-3_3__5_X---_e_V399zLv9_____9nN___9BBIAkw1L6ALsyxwZNo0qhRAjCsJDoBQAUUAwtE1gAwOCnZWAR6ghYAITUBGBECDEFGLAIABBIAkIiAkALBAIgCIBAACAFSAhAARMAgsALAwCAAUA0LECKAIQJCDI4KjlMCAqRaKCeysASi72NMIQy3wIoFH9FRgI1miBYGQkLBzHAEgJYAAA; _iub_cs-87184196-granular={"gac":"MX4mAQMBAgEIAQUBBAEDAQwBBQEDAQ4BCAEEAQEBBgEDAgYCAgEBAQkBAgEEAQMBFAEDAQUBCAEGAQkBAQEIAQEBCwEFAQYBBQENAQQBEwEFAQQCAgIKARwBAwENAQMBBAECAQkBBQEBAQgBBQEFAQMBBAEDAQMBHAEDAQQBAgIFAQEBAQEQAhABCQEIAgcBBQEBAQcBAgEDAcKNAQMBBwEiAQYBDgINAQICBwEJAQ0BCgECAQYBGAEEAREBCAEGASgBAQEDAREBFAECAQMBAQIFAQUBBAEBAQ0BEQEGAQIBAQEBAQcBEwEHAQcBBQECAQkBAwETAQEBAwEIAQMBBQEDAQoCAgEVAQ8BAQEFAQcBAQEDAQoBBQEEARABDwEKAQcCCQEbAQsCAgEUAQEBBgEFAggBHQEQAQMBCAEOAQcBBgECAQUBBQEGAQEBAwIGAQsBDAEVAQwBAQELAQEBCQIDAQ4BAQEDAQgBAwEEAgIBBgEMAQQBDgEDAQwBAwENAQcBAQEOAQEBBAEEAgEBAQIBAQ0BBgEDAQcBAQEIAQkBEQELAQwBAQERAwIDCAEYAQMCEgEHAQMBBAEBAgQBAwEHAQMBAQEBAQEBDQEBAQwBAwEBAQUBCAEFAQIBAwECAQQBAQECAQUBCQEKAQEBAwECAQ8BAgEKAQICAQECAQgBEgEKAQ4BAgEJAQYBBQEDAQIBAwEIAQIBAgECBAUBCgECAwYBAwEFAgkBBAEBAQUBAgEBAQEBAwECAQEBAQEGAQEBDAEGAQsBAQIFAQMBBAEDAQIBAQEBAQMCAgQBAQgCBQEIAgQBAQIGAQEBBwEKAgIDAQICAQEBBQIEAQUCBAECAgIDAQEBAQYBBgIDAgEBBQIBAwIDAwMBAgcCBgEDAQIBAQICAQQBAgEIAQUCDgEJARsCAQMLAQIBAwIFAQIBAwEGAgIDAgIEAQICAgEBAQEDAwEBAgEEAQEBAQMBAQIBAQEBAQEDBAEMAQEBAwECAQIGAgEEAQUBAwIBAQMHBAQBAQIFAQQGAQEBAQIDAwMBAQEDAwEBAwEBAQIBAgEBAgUDBAQCCAECAgQDAgEDAgEBAgIDAQECAQEBAQEHCgICAwEBAQIDAQEBAgEBAgMGAgEBAwEBBAIIAQMDAgIDAQICAwEEAgYBAQQBBAMBAQILAwICAQEBAQICAQQBAwEFAQICAgQCAQEDAQIB"}; _ga_8Y361YYB64=GS1.1.1628215509.1.1.1628221077.0; __gads=ID=548313b9f032f4fb:T=1628221079:S=ALNI_MbIYdnnrHf0BQX5TvGFFmn-ybf_wQ',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(category_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath('//article[@class="gz-card gz-card-horizontal gz-mBottom3x"]'):
        htmlLink = i.xpath('.//div[@class="gz-link-more-recipe"]/a/@href').get('')
        recipeName = i.xpath('.//div[@class="gz-link-more-recipe"]/a/@title').get('')
        dic[recipeName] = htmlLink
    
    return dic


# In[4]:


htmlOnePageSpider("https://www.giallozafferano.com/latest-recipes/",htmlDic)


# #### 3. go through all pages in one category and get all recipe htmls of one category

# In[5]:


# initialize pageLst to store the htmls of all pages
pageLst = []


# In[6]:


def selSpider(url):
    """
    input: url
    output: sel of url
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_gid=GA1.2.2044917405.1628215509; push_notification_viewed=1; push_notification_token=cl1Q918JjaA:APA91bF77xlKJBzu_enBJMT2huk4AYCH1YzBwWcq5qyRcmcLczPuwycyYqA0A0kijCGTkuVQHrjCARU_wImnacoG0A3X9sis8X7bM0liRn_luMm2orfTkttqTQXazHN-C9xxJP1_HRe3; push_notification_topics=default; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _pbjs_userid_consent_data=3524755945110770; _pubcid=44caf923-8f3b-4c5a-a115-b07cbef2d915; cto_bidid=zx7NAV91eHZmc2JjVldMY2NGU0JzNiUyQlhyN0FzaVgwZXVtdWwyZHp2Y2oxQnpFb2xuYmdmR2UlMkIyWFVLeWFpZ25lRWNscFBpcWVpTEd3ZTklMkIxQjBBdDV2TjROaW9kdUpNRWpiajNWZXI4NGtqallMTFF2S0lmU1VjVlA2aG1ydXkzYkl4WUdPJTJCZXNHTzlGTlVpdUtoa04zTDFsZyUzRCUzRA; cto_bundle=GApBq19nQWxwMlZMd1JiUjdTU01UbEltT0lPMU1LUTFncm5MNlNNTmhNdkZIeThrZjVXbHY3S2NYSmRtJTJGeFg4ek8xeEFBa2RPR0YwdGhja3djcmpPSDhvNnVTWWdFcW5mM2thN29IT2V1NHNXJTJCYXVRWVFpTlVLNTJONlNnaE5ZS3FJTndTS0pVOTV6SWlEQXR4JTJGZGxOUHBzNXlKUEpSRmFnVzVaUExsNWRtSlhNS0VRN0RXWmE2VDJoYnBlbUFyVG5pM0NGdXFNdDRwVUxJazUyJTJCSUNrWE5aR1ElM0QlM0Q; _lr_retry_request=true; _lr_env_src_ats=false; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-07-06T02:47:48"}; idl_env=AsVWbVw3m6dkmdKUdBHZ25o6aMy3ZU2ZRKnSFe71GxSD88dKs6rClb9Qp3O9EhJk7ZDvTZSPHpo4XscnTw-Mr-o71yfp0yc0lvBmblDx80Gpe7R8bL8HC0E12tC3VD6gNeesuSCOwhHbXYsmEPhBKrbiTDnOdTvvIQxdI0AXHDYg2CbVlJzP5sGGn5PhR0V3u7mYavaW0LHoJUkOlDke1Xfy41dJ; panoramaId_expiry=1628822868533; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=e26b57d52221e1431bf4644287ab4945a702d1dbb46dcc6c67d2ca44575af3b9; _ga=GA1.2.1751180775.1628215509; utag_main=v_id:017b193500560012646692ae8fc303078002007000942$_sn:2$_se:28$_ss:0$_st:1628222873205$ses_id:1628218041231;exp-session$_pn:14;exp-session; _iub_cs-87184196={"consent":true,"timestamp":"2021-08-06T02:05:12.513Z","version":"1.31.1","id":87184196}; euconsent-v2=CPKffhePKffh1B7EABENBlCsAP_AAH_AAAAAIJNf_X__bX9j-_59f_t0eY1P9_r_v-Qzjhfdt-8F2L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzPsak2Mr6NKJ7LEmnMZO2dYGHtfn91TuZKY7_78__fz3z-v_v___9f3r-3_3__5_X---_e_V399zLv9_____9nN___9BBIAkw1L6ALsyxwZNo0qhRAjCsJDoBQAUUAwtE1gAwOCnZWAR6ghYAITUBGBECDEFGLAIABBIAkIiAkALBAIgCIBAACAFSAhAARMAgsALAwCAAUA0LECKAIQJCDI4KjlMCAqRaKCeysASi72NMIQy3wIoFH9FRgI1miBYGQkLBzHAEgJYAAA; _iub_cs-87184196-granular={"gac":"MX4mAQMBAgEIAQUBBAEDAQwBBQEDAQ4BCAEEAQEBBgEDAgYCAgEBAQkBAgEEAQMBFAEDAQUBCAEGAQkBAQEIAQEBCwEFAQYBBQENAQQBEwEFAQQCAgIKARwBAwENAQMBBAECAQkBBQEBAQgBBQEFAQMBBAEDAQMBHAEDAQQBAgIFAQEBAQEQAhABCQEIAgcBBQEBAQcBAgEDAcKNAQMBBwEiAQYBDgINAQICBwEJAQ0BCgECAQYBGAEEAREBCAEGASgBAQEDAREBFAECAQMBAQIFAQUBBAEBAQ0BEQEGAQIBAQEBAQcBEwEHAQcBBQECAQkBAwETAQEBAwEIAQMBBQEDAQoCAgEVAQ8BAQEFAQcBAQEDAQoBBQEEARABDwEKAQcCCQEbAQsCAgEUAQEBBgEFAggBHQEQAQMBCAEOAQcBBgECAQUBBQEGAQEBAwIGAQsBDAEVAQwBAQELAQEBCQIDAQ4BAQEDAQgBAwEEAgIBBgEMAQQBDgEDAQwBAwENAQcBAQEOAQEBBAEEAgEBAQIBAQ0BBgEDAQcBAQEIAQkBEQELAQwBAQERAwIDCAEYAQMCEgEHAQMBBAEBAgQBAwEHAQMBAQEBAQEBDQEBAQwBAwEBAQUBCAEFAQIBAwECAQQBAQECAQUBCQEKAQEBAwECAQ8BAgEKAQICAQECAQgBEgEKAQ4BAgEJAQYBBQEDAQIBAwEIAQIBAgECBAUBCgECAwYBAwEFAgkBBAEBAQUBAgEBAQEBAwECAQEBAQEGAQEBDAEGAQsBAQIFAQMBBAEDAQIBAQEBAQMCAgQBAQgCBQEIAgQBAQIGAQEBBwEKAgIDAQICAQEBBQIEAQUCBAECAgIDAQEBAQYBBgIDAgEBBQIBAwIDAwMBAgcCBgEDAQIBAQICAQQBAgEIAQUCDgEJARsCAQMLAQIBAwIFAQIBAwEGAgIDAgIEAQICAgEBAQEDAwEBAgEEAQEBAQMBAQIBAQEBAQEDBAEMAQEBAwECAQIGAgEEAQUBAwIBAQMHBAQBAQIFAQQGAQEBAQIDAwMBAQEDAwEBAwEBAQIBAgEBAgUDBAQCCAECAgQDAgEDAgEBAgIDAQECAQEBAQEHCgICAwEBAQIDAQEBAgEBAgMGAgEBAwEBBAIIAQMDAgIDAQICAwEEAgYBAQQBBAMBAQILAwICAQEBAQICAQQBAwEFAQICAgQCAQEDAQIB"}; _ga_8Y361YYB64=GS1.1.1628215509.1.1.1628221077.0; __gads=ID=548313b9f032f4fb:T=1628221079:S=ALNI_MbIYdnnrHf0BQX5TvGFFmn-ybf_wQ',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    sel = Selector(response.text)
    return sel


# In[7]:


def nextPageSpider(category_url,lst):
    """
    input: category_url, the url of first page of one category
    input: the initial list to store htmls of all pages
    output: list with htmls of all pages
    """
    lst.append(category_url)
    sel = selSpider(category_url)
    next_page_url = sel.xpath('//a[@title="Next page"]/@href').get('')
    while next_page_url:
            next_page = 'https://www.giallozafferano.com/' + next_page_url
            lst.append(next_page)
            next_page_url = selSpider(next_page).xpath('//a[@title="Next page"]/@href').get('')
    
    return lst


# In[8]:


pageLst = nextPageSpider("https://www.giallozafferano.com/latest-recipes/",pageLst)
pageLst


# In[9]:


htmlDic = {}
for i in pageLst:
    htmlDic = htmlOnePageSpider(i,htmlDic)  
htmlDic


# In[10]:


len(htmlDic)


# #### 4. go through all categories and get all recipe htmls

# In[11]:


CategoryDic = {
    "Latest recipes": "https://www.giallozafferano.com/latest-recipes/",
    "Appetizers": "https://www.giallozafferano.com/recipes-list/Appetizers/",
    "First Courses": "https://www.giallozafferano.com/recipes-list/First-Courses/",
    "Main Courses": "https://www.giallozafferano.com/recipes-list/Main-Courses/",
    "Sweets and desserts": "https://www.giallozafferano.com/recipes-list/Sweets-and-Desserts/",
    "Leavened products": "https://www.giallozafferano.com/recipes-list/Leavened-products/"
}


# In[12]:


pageLst = []
for key in CategoryDic:
    category_url = CategoryDic[key]
    pageLst = nextPageSpider(category_url,pageLst)
    
pageLst


# In[13]:


htmlDic = {}
for i in pageLst:
    htmlDic = htmlOnePageSpider(i,htmlDic)  
htmlDic


# In[14]:


# the total number of recipes
len(htmlDic)


# #### 5. go through all recipe htmls and scrape the data we want

# In[15]:


Italydata = {
"name of the recipe": [],
"Total time": [],
"Prep time": [],
"Cook time": [],
"Number of servings": [],
"List of ingredients": [],
"List of instructions":[],
"estimatedCost":[],
"recipeCategory":[],
"description" :[],
}


# In[16]:


def Italyspider(recipes_url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_gid=GA1.2.2044917405.1628215509; push_notification_viewed=1; push_notification_token=cl1Q918JjaA:APA91bF77xlKJBzu_enBJMT2huk4AYCH1YzBwWcq5qyRcmcLczPuwycyYqA0A0kijCGTkuVQHrjCARU_wImnacoG0A3X9sis8X7bM0liRn_luMm2orfTkttqTQXazHN-C9xxJP1_HRe3; push_notification_topics=default; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _pbjs_userid_consent_data=3524755945110770; _pubcid=44caf923-8f3b-4c5a-a115-b07cbef2d915; cto_bidid=zx7NAV91eHZmc2JjVldMY2NGU0JzNiUyQlhyN0FzaVgwZXVtdWwyZHp2Y2oxQnpFb2xuYmdmR2UlMkIyWFVLeWFpZ25lRWNscFBpcWVpTEd3ZTklMkIxQjBBdDV2TjROaW9kdUpNRWpiajNWZXI4NGtqallMTFF2S0lmU1VjVlA2aG1ydXkzYkl4WUdPJTJCZXNHTzlGTlVpdUtoa04zTDFsZyUzRCUzRA; cto_bundle=GApBq19nQWxwMlZMd1JiUjdTU01UbEltT0lPMU1LUTFncm5MNlNNTmhNdkZIeThrZjVXbHY3S2NYSmRtJTJGeFg4ek8xeEFBa2RPR0YwdGhja3djcmpPSDhvNnVTWWdFcW5mM2thN29IT2V1NHNXJTJCYXVRWVFpTlVLNTJONlNnaE5ZS3FJTndTS0pVOTV6SWlEQXR4JTJGZGxOUHBzNXlKUEpSRmFnVzVaUExsNWRtSlhNS0VRN0RXWmE2VDJoYnBlbUFyVG5pM0NGdXFNdDRwVUxJazUyJTJCSUNrWE5aR1ElM0QlM0Q; _lr_retry_request=true; _lr_env_src_ats=false; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-07-06T02:47:48"}; idl_env=AsVWbVw3m6dkmdKUdBHZ25o6aMy3ZU2ZRKnSFe71GxSD88dKs6rClb9Qp3O9EhJk7ZDvTZSPHpo4XscnTw-Mr-o71yfp0yc0lvBmblDx80Gpe7R8bL8HC0E12tC3VD6gNeesuSCOwhHbXYsmEPhBKrbiTDnOdTvvIQxdI0AXHDYg2CbVlJzP5sGGn5PhR0V3u7mYavaW0LHoJUkOlDke1Xfy41dJ; panoramaId_expiry=1628822868533; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=e26b57d52221e1431bf4644287ab4945a702d1dbb46dcc6c67d2ca44575af3b9; _ga=GA1.2.1751180775.1628215509; utag_main=v_id:017b193500560012646692ae8fc303078002007000942$_sn:2$_se:28$_ss:0$_st:1628222873205$ses_id:1628218041231;exp-session$_pn:14;exp-session; _iub_cs-87184196={"consent":true,"timestamp":"2021-08-06T02:05:12.513Z","version":"1.31.1","id":87184196}; euconsent-v2=CPKffhePKffh1B7EABENBlCsAP_AAH_AAAAAIJNf_X__bX9j-_59f_t0eY1P9_r_v-Qzjhfdt-8F2L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzPsak2Mr6NKJ7LEmnMZO2dYGHtfn91TuZKY7_78__fz3z-v_v___9f3r-3_3__5_X---_e_V399zLv9_____9nN___9BBIAkw1L6ALsyxwZNo0qhRAjCsJDoBQAUUAwtE1gAwOCnZWAR6ghYAITUBGBECDEFGLAIABBIAkIiAkALBAIgCIBAACAFSAhAARMAgsALAwCAAUA0LECKAIQJCDI4KjlMCAqRaKCeysASi72NMIQy3wIoFH9FRgI1miBYGQkLBzHAEgJYAAA; _iub_cs-87184196-granular={"gac":"MX4mAQMBAgEIAQUBBAEDAQwBBQEDAQ4BCAEEAQEBBgEDAgYCAgEBAQkBAgEEAQMBFAEDAQUBCAEGAQkBAQEIAQEBCwEFAQYBBQENAQQBEwEFAQQCAgIKARwBAwENAQMBBAECAQkBBQEBAQgBBQEFAQMBBAEDAQMBHAEDAQQBAgIFAQEBAQEQAhABCQEIAgcBBQEBAQcBAgEDAcKNAQMBBwEiAQYBDgINAQICBwEJAQ0BCgECAQYBGAEEAREBCAEGASgBAQEDAREBFAECAQMBAQIFAQUBBAEBAQ0BEQEGAQIBAQEBAQcBEwEHAQcBBQECAQkBAwETAQEBAwEIAQMBBQEDAQoCAgEVAQ8BAQEFAQcBAQEDAQoBBQEEARABDwEKAQcCCQEbAQsCAgEUAQEBBgEFAggBHQEQAQMBCAEOAQcBBgECAQUBBQEGAQEBAwIGAQsBDAEVAQwBAQELAQEBCQIDAQ4BAQEDAQgBAwEEAgIBBgEMAQQBDgEDAQwBAwENAQcBAQEOAQEBBAEEAgEBAQIBAQ0BBgEDAQcBAQEIAQkBEQELAQwBAQERAwIDCAEYAQMCEgEHAQMBBAEBAgQBAwEHAQMBAQEBAQEBDQEBAQwBAwEBAQUBCAEFAQIBAwECAQQBAQECAQUBCQEKAQEBAwECAQ8BAgEKAQICAQECAQgBEgEKAQ4BAgEJAQYBBQEDAQIBAwEIAQIBAgECBAUBCgECAwYBAwEFAgkBBAEBAQUBAgEBAQEBAwECAQEBAQEGAQEBDAEGAQsBAQIFAQMBBAEDAQIBAQEBAQMCAgQBAQgCBQEIAgQBAQIGAQEBBwEKAgIDAQICAQEBBQIEAQUCBAECAgIDAQEBAQYBBgIDAgEBBQIBAwIDAwMBAgcCBgEDAQIBAQICAQQBAgEIAQUCDgEJARsCAQMLAQIBAwIFAQIBAwEGAgIDAgIEAQICAgEBAQEDAwEBAgEEAQEBAQMBAQIBAQEBAQEDBAEMAQEBAwECAQIGAgEEAQUBAwIBAQMHBAQBAQIFAQQGAQEBAQIDAwMBAQEDAwEBAwEBAQIBAgEBAgUDBAQCCAECAgQDAgEDAgEBAgIDAQECAQEBAQEHCgICAwEBAQIDAQEBAgEBAgMGAgEBAwEBBAIIAQMDAgIDAQICAwEEAgYBAQQBBAMBAQILAwICAQEBAQICAQQBAwEFAQICAgQCAQEDAQIB"}; _ga_8Y361YYB64=GS1.1.1628215509.1.1.1628221077.0; __gads=ID=548313b9f032f4fb:T=1628221079:S=ALNI_MbIYdnnrHf0BQX5TvGFFmn-ybf_wQ',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipes_url,headers=headers)
    sel = Selector(response.text)
    content = sel.xpath('//script[@type="application/ld+json"]/text()')[0].get()
    content_dic = json.loads(content.replace("\n", ""))
    return content_dic


# In[17]:


def fillItalyData(recipes_url,dic):
    content = Italyspider(recipes_url)
    dic["name of the recipe"].append(content['name'])
    dic["Total time"].append(content['totalTime'])
    dic["Prep time"].append(content['prepTime'])
    dic["Cook time"].append(content['cookTime'])
    dic["Number of servings"].append(content['recipeYield'])
    dic["List of ingredients"].append(content['recipeIngredient'])
    dic["List of instructions"].append(content['recipeInstructions'])
    dic["estimatedCost"].append(content['estimatedCost'])
    dic["recipeCategory"].append(content['recipeCategory'])
    dic["description"].append(content['description'])


# In[18]:


for key in htmlDic:
    fillItalyData(htmlDic[key],Italydata)


# In[19]:


Italydata


# #### 6. Convert dictionary to data frame

# In[20]:


output = pd.DataFrame(Italydata)
output


# In[21]:


# save dataset
output.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Italy.csv")


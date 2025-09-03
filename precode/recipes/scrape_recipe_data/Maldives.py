#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Maldives

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


# #### https://maldivescook.com/

# In[5]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

begin = time.time()

options = Options()
options.headless = True
options.add_argument('--log-level=3')
driver = webdriver.Chrome(options=options)


# In[2]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.100886390.1650383260; _gid=GA1.2.44648308.1652105655',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://maldivescook.com/',headers=headers)
sel = Selector(response.text)


# In[3]:


sel.xpath('//article[@class="cooked-recipe has-post-thumbnail"]')


# In[12]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlDic to store the htmls of all recipes
htmlLst = []

def htmlOnePageSpider(category_url, lst):
    """
    input: category_url, the url of first page of the recipe web
    input: the initial htmlLst
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.100886390.1650383260; _gid=GA1.2.44648308.1652105655',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
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
    for i in json.loads(sel.xpath("//script[@type='application/ld+json' and @data-testid='itemlist-structured-data']/text()").get())['itemListElement']:
        lst.append(i['url'])
    
    return lst


# In[13]:


htmlOnePageSpider("https://www.smulweb.nl/recepten/surinaamse", htmlLst)


# In[14]:


for i in range(2,35):
    htmlOnePageSpider("https://www.smulweb.nl/recepten/surinaamse?page={}".format(i), htmlLst)


# In[15]:


# the number of recipes we have in total
len(htmlLst)


# In[20]:


# 3. go through all recipe htmls and scrape the data we want

Surinamedata = {
    "Name of the recipe":[],
    "Total time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def SurinameSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'gdpr-auditId=b1cb8b3bc7854799859cd2d666906233; _gid=GA1.2.147087361.1650840976; _gcl_au=1.1.1379485883.1650840976; _fbp=fb.1.1650840976551.1613766413; __gads=ID=97f196eca720ccbe:T=1650840977:S=ALNI_Map_2onE-12Fms1UaCFvK-RY58OPQ; uuid=6349D6CA-853F-4EED-B4E7-94140B5D51C0; _pbjs_userid_consent_data=3987350328898063; smulweb_session=eyJpdiI6InMwVzczdE92WXRXMWIwbnhEdXJ0RWc9PSIsInZhbHVlIjoiUUNNMzkyQngrQ2lxRWd6cU5IYUpQNXo1a08vZjk5VmhtekwxTHdtclNIcUlNQkR2SHh3RDJWOTFyV3FoZGxvVE1wdHluaGgzZ2ZqRmVPRXBaSVlnSGZFUkQ0MHJPZmQ1anhjeTVrcFVTb0pESnNRK0JUb0xvRHE3dVFENVpvYUUiLCJtYWMiOiI5MDcxNWUzMGY2NjliN2E4NmE3MGU1YjI2YTViNTNjZmVlNDBiYjdkODYzMjY2NDE1ODg0ZDgzZDNlNGRjN2EzIiwidGFnIjoiIn0=; _ga_N8ZDS058S2=GS1.1.1650984098.3.0.1650984098.0; _ga=GA1.1.2041041978.1650840976; geo-location={"country":"US","region":"DC"}; gdpr-dau=true; gdpr-dau-log-sent=true; __gpi=UID=0000045a01d42da7:T=1650840977:RT=1650984100:S=ALNI_Mbnk4AfF1xvEUrBiDzK7baJF75Bow; pbjs-id5id={"created_at":"2021-03-07T05:21:53Z","id5_consent":true,"original_uid":"ID5*hzYfToEIksPcBtxqrnSdwMjPFxXZ9_uYvGghhm9Zel8P6YXfMwcBK5krHB2JyTLlD-r-My7SldtFNeS99jUxtQ_rxBQPuKpFjYiDfpQeXjoP7C_TA9W6hYO_kW6nQikKD-3HFAH-aQ2PzBqNb-CUtg_u3UPAZhRPG-VBirRp1HEP8ZRxYxxoP4Vz3mFVLhyED_RSzDbFJZxIe4SctQkt3g_1gMcAH_re8AzFnIRqAqQP96N5lO8RdmxCd2i-caLXD_g5-dMb1GVrcivg-vQ1og_5oeIrI0vPr8O7ZByXlCQQAhTHF06KAuV8JT5Cv5XhEAQu8bKnbpEI2RaNbh9vSxAF7lIDYAmxp3RWSaR6FRk","universal_uid":"ID5*6wBD3QUORyRu5YEN06VLscci8qkStd6uUkCDY4BFrIEP6TCEWSpOzhJtF0rU6DhND-qw5nCkCcOLjIxB9PJT7w_r_ZLkI2M2XcS_eukrbNcP7FYVhwM0aalaWi-VemGyD-145Xj13ucr8hzsqQZdOg_u1se9dS50SDFe76rPK_EP8SgTEg8qyIsraczQnF3kD_T27D6aTtV_NwfomW_UHg_13sbR__ref9Xs3nobO58P9zIusunYrkOhuEuERn9BD_jvlR5Qu6mrv-tw2L2AoA_5cW_Dqx2Hp1_7tdEiBvkQAiISc5WBdiR9_1Z5iVfiEAROP8dBvSv0j3p70MEVABAFVkKDJ8UYFF-era-8HmE","signature":"ID5_Af-jHcZifRPNNdV45iDm10bcEu3qM2uqHbbmSSH1TeSX2ErKiPh7xddOE0_Htsmz3wAqXYpR8JtYb6ZfbP13Rt8","link_type":2,"cascade_needed":false,"privacy":{"jurisdiction":"gdpr","id5_consent":true}}; pbjs-id5id_last=Tue, 26 Apr 2022 14:41:43 GMT; stat_track_u_id=uid=996583224&f=4847%3A481&st=3&sy=&ls=1650826577&off=&noacts=&dg=&hs=0; _stat_track_s_id=_si=1650984100&_sid=1650969700&_inew=0&_ls=1650826577&_lurl=-70655051&_lrfr=1994577240&_la=1650969715&_so=&_pp=&_bh=379&_ane=&_te=&_nay=&_nae=&_nac=',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipe_url,headers=headers)
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type="application/ld+json" and @data-testid="recipe-structured-data"]/text()').get())
    
    return content

def fillSurinameData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = SurinameSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
                
    try:
        dic['Cook time'].append(content['cookTime'])
    except:
        dic['Cook time'].append('')
    
    try:
        dic['List of ingredients'].append(content['recipeIngredient'])
    except:
        dic['List of ingredients'].append('')
        
    try:
        dic['List of instructions'].append(content['recipeInstructions'])
    except:
        dic['List of instructions'].append('')
        
    try:
        dic['Number of servings'].append(content['recipeYield'])
    except:
        dic['Number of servings'].append('')
        
    try:
        dic['Category'].append(content['recipeCategory'])
    except:
        dic['Category'].append('')

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillSurinameData(html,Surinamedata)
    except:
        time.sleep(5)

# convert data to dataframe
Suriname = pd.DataFrame(Surinamedata)
print(Suriname.shape)
Suriname.head()


# In[21]:


Suriname["Source"] = ["Web1" for i in range(len(Suriname))]
Suriname.head()


# In[22]:


# save dataset
Suriname.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Suriname.csv")


# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Pakistan

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


# #### https://www.pakistaneats.com/recipe-index/

# In[14]:


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
        'cookie':'_pbjs_userid_consent_data=3524755945110770; permutive-id=a96c8267-5c39-4285-89fe-9e49edaaa316; cto_bundle=QcUwaF9DSGN6SEd2dDVmWHUxUjI3bjBDZXl5akRwZWtaem9RMG1qanlwMVJDdHl5QlRnVDNaa2dBZ21DTDRFRlA4VCUyRnZHRVU4WG1HRUMlMkJISDlwJTJCbnhQR3pMSm9TUnppS1Y5ZERMT1N3TGllQUx2anJVMjhaMVEzJTJGcFB5SVdxcURuQVAwemJVUSUyRlpseEhyVUdjR1p3MVc2bjlzYmUlMkJBelBIZDR4REx1emR0cVpudE5nN1dhRWUlMkZxRWlhbkRSbnRxUGUwNWlySXNBZnJyUXNNeTR2M3l0M21wYUElM0QlM0Q; _lr_env_src_ats=false; _gid=GA1.2.2079734694.1651852160; _ga_RY7MQKYES3=GS1.1.1651852159.3.0.1651852159.0; _gat_gtag_UA_143772196_1=1; _ga=GA1.2.1343176687.1650825575; _gat_pmcBoomerang=1; _gat_gtag_UA_143772196_2=1; _lr_geo_location=US; __gads=ID=00c90538d28fea03:T=1650825575:S=ALNI_Mb8z_Q85cu3LbXI9NKcgLFqF8i3cw; __gpi=UID=000004b6f9eee3eb:T=1650825576:RT=1651852161:S=ALNI_MbHDr4kaUw0nB9bmKQ002MzokEh6w; _lr_retry_request=true',
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
    for i in sel.xpath('//div[@class="widget-wrap"]/article/a/@href'):
        lst.append(i.get())
    return lst


# In[15]:


htmlOnePageSpider("https://www.pakistaneats.com/recipe-index/", htmlLst)


# In[16]:


# the number of recipes we have in total
len(htmlLst)


# In[17]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_pbjs_userid_consent_data=3524755945110770; permutive-id=a96c8267-5c39-4285-89fe-9e49edaaa316; cto_bundle=QcUwaF9DSGN6SEd2dDVmWHUxUjI3bjBDZXl5akRwZWtaem9RMG1qanlwMVJDdHl5QlRnVDNaa2dBZ21DTDRFRlA4VCUyRnZHRVU4WG1HRUMlMkJISDlwJTJCbnhQR3pMSm9TUnppS1Y5ZERMT1N3TGllQUx2anJVMjhaMVEzJTJGcFB5SVdxcURuQVAwemJVUSUyRlpseEhyVUdjR1p3MVc2bjlzYmUlMkJBelBIZDR4REx1emR0cVpudE5nN1dhRWUlMkZxRWlhbkRSbnRxUGUwNWlySXNBZnJyUXNNeTR2M3l0M21wYUElM0QlM0Q; _lr_env_src_ats=false; _gid=GA1.2.2079734694.1651852160; _ga_RY7MQKYES3=GS1.1.1651852159.3.0.1651852159.0; _gat_gtag_UA_143772196_1=1; _ga=GA1.2.1343176687.1650825575; _gat_pmcBoomerang=1; _gat_gtag_UA_143772196_2=1; _lr_geo_location=US; __gads=ID=00c90538d28fea03:T=1650825575:S=ALNI_Mb8z_Q85cu3LbXI9NKcgLFqF8i3cw; __gpi=UID=000004b6f9eee3eb:T=1650825576:RT=1651852161:S=ALNI_MbHDr4kaUw0nB9bmKQ002MzokEh6w; _lr_retry_request=true',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://www.pakistaneats.com/recipes/khagina-scrambled-eggs-with-potatoes/',headers=headers)
sel = Selector(response.text)
    


# In[31]:


# 3. go through all recipe htmls and scrape the data we want

Pakistandata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def PakistanSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_pbjs_userid_consent_data=3524755945110770; permutive-id=a96c8267-5c39-4285-89fe-9e49edaaa316; cto_bundle=QcUwaF9DSGN6SEd2dDVmWHUxUjI3bjBDZXl5akRwZWtaem9RMG1qanlwMVJDdHl5QlRnVDNaa2dBZ21DTDRFRlA4VCUyRnZHRVU4WG1HRUMlMkJISDlwJTJCbnhQR3pMSm9TUnppS1Y5ZERMT1N3TGllQUx2anJVMjhaMVEzJTJGcFB5SVdxcURuQVAwemJVUSUyRlpseEhyVUdjR1p3MVc2bjlzYmUlMkJBelBIZDR4REx1emR0cVpudE5nN1dhRWUlMkZxRWlhbkRSbnRxUGUwNWlySXNBZnJyUXNNeTR2M3l0M21wYUElM0QlM0Q; _lr_env_src_ats=false; _gid=GA1.2.2079734694.1651852160; _ga_RY7MQKYES3=GS1.1.1651852159.3.0.1651852159.0; _gat_gtag_UA_143772196_1=1; _ga=GA1.2.1343176687.1650825575; _gat_pmcBoomerang=1; _gat_gtag_UA_143772196_2=1; _lr_geo_location=US; __gads=ID=00c90538d28fea03:T=1650825575:S=ALNI_Mb8z_Q85cu3LbXI9NKcgLFqF8i3cw; __gpi=UID=000004b6f9eee3eb:T=1650825576:RT=1651852161:S=ALNI_MbHDr4kaUw0nB9bmKQ002MzokEh6w; _lr_retry_request=true',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get())['@graph'][-1]
    
    return content

def fillPakistanData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = PakistanSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
        
    try:
        dic['Prep time'].append(content['prepTime'])
    except:
        dic['Prep time'].append('')
                
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
        fillPakistanData(html,Pakistandata)
    except:
        time.sleep(5)

# convert data to dataframe
Pakistan = pd.DataFrame(Pakistandata)
print(Pakistan.shape)
Pakistan.head()


# In[32]:


Pakistan["Source"] = ["Web1" for i in range(len(Pakistan))]
Pakistan.head()


# In[33]:


# save dataset
Pakistan.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Pakistan.csv")


# In[ ]:




